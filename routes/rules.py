from typing import Union
from fastapi import APIRouter, Depends, Response, Cookie, Security, status
from dependency_injector.wiring import Provide, inject
import logging
from datetime import datetime, timedelta
from uuid import uuid4
import random
from models.security import ScopeEnum

from repository.sqlite_repository import SQLiteRepository
from utils.container import Container
from models.rule import Rule
from repository.yaml_rule_repository import YamlRulesRepository
from utils.encryption import Encryption
from routes.middlewares import check_jwt, remove_search_hash_from_url


router = APIRouter()


@router.get(
    "/rules",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.CLIENT.value])],
    response_model=Union[bool, dict],
)
@inject
async def show_modal(
    response: Response,
    featureUrl: str = Depends(remove_search_hash_from_url),
    user_id: Union[str, None] = Cookie(default=None),
    timestamp: Union[str, None] = Cookie(default=None),
    rulesYamlConfig: YamlRulesRepository = Depends(Provide[Container.rules_config]),
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
) -> bool:
    # Get rules from featureUrl query
    rulesFromFeature: Union[Rule, None] = rulesYamlConfig.getRuleFromFeature(
        feature_url=featureUrl
    )
    if rulesFromFeature is None:
        logging.error("GET rules::Feature not found")
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": "Feature not found"}

    # Retrieve the encryption key of the project
    project_name = rulesYamlConfig.getProjectNameFromFeature(featureUrl)
    project = await sqlite_repo.get_project_by_name(project_name)
    encryption_db = await sqlite_repo.get_encryption_by_project_id(project.id)
    encryption = Encryption(encryption_db.encryption_key)

    # Set user_id Cookie if is None
    if user_id is None:
        logging.info("GET rules::Setting a new user_id cookie")
        user_id = str(uuid4())
        response.set_cookie(key="user_id", value=user_id)

    # Get current timestamp
    dateToday: datetime = datetime.now()

    if timestamp is not None:
        try:
            decrypted_timestamp = encryption.decrypt(timestamp)
        except Exception:
            logging.error("GET rules::Invalid timestamp, cannot decrypt")
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return {"Error": "Invalid timestamp, cannot decrypt"}
        previous_timestamp: datetime = datetime.fromtimestamp(
            float(decrypted_timestamp)
        )
        logging.debug(f"GET rules::Previous timestamp {previous_timestamp}")
        isOverDelay: bool = (
            timedelta(days=rulesFromFeature.delay_before_reanswer)
            <= dateToday - previous_timestamp
        )
    else:
        logging.debug("GET rules::No timestamp cookie given")
        isOverDelay = True

    isWithinRatio: bool = random.random() <= rulesFromFeature.ratio
    isDisplay: bool = rulesFromFeature.is_active and isOverDelay and isWithinRatio

    # Set timestamp Cookie to current timestamp when display survey modal
    if isDisplay:
        logging.info("GET rules::Setting a new timestamp cookie")
        # Encrypt the timestamp to prevent user modification
        timestamp_bytes = str(dateToday.timestamp())
        encrypted_timestamp = encryption.encrypt(timestamp_bytes)
        # Add the encrypted timestamp as cookie to the response
        response.set_cookie(key="timestamp", value=encrypted_timestamp)
        # Store the timestamp when it's displayed
        iso_timestamp = dateToday.isoformat()
        await sqlite_repo.create_display(
            project_name, user_id, iso_timestamp, featureUrl
        )
    return isDisplay
