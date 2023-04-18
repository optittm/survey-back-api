from typing import Union
from fastapi import APIRouter, Depends, Response, Cookie, status
from dependency_injector.wiring import Provide, inject
import logging
from datetime import datetime, timedelta
from uuid import uuid4
import random

from repository.sqlite_repository import SQLiteRepository
from utils.container import Container
from models.rule import Rule
from repository.yaml_rule_repository import YamlRulesRepository
from utils.encryption import Encryption


router = APIRouter()


@router.get("/rules")
@inject
async def show_modal(
    featureUrl: str,
    response: Response,
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
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": "Feature not found"}

    # Retrieve the encryption key of the project
    project_name = rulesYamlConfig.getProjectNameFromFeature(featureUrl)
    project = await sqlite_repo.get_project_by_name(project_name)
    encryption_db = await sqlite_repo.get_encryption_by_project_id(project.id)
    encryption = Encryption(encryption_db.encryption_key)

    # Set user_id Cookie if is None
    if user_id is None:
        logging.info("Setting a new user_id cookie")
        response.set_cookie(key="user_id", value=str(uuid4()))

    # Get current timestamp
    dateToday: datetime = datetime.now()

    if timestamp is not None:
        decrypted_timestamp = encryption.decrypt(timestamp)
        previous_timestamp: datetime = datetime.fromtimestamp(
            float(decrypted_timestamp)
        )
        isOverDelay: bool = (
            timedelta(days=rulesFromFeature.delay_before_reanswer)
            <= dateToday - previous_timestamp
        )
    else:
        isOverDelay = True

    isWithinRatio: bool = random.random() <= rulesFromFeature.ratio
    isDisplay: bool = rulesFromFeature.is_active and isOverDelay and isWithinRatio

    # Set timestamp Cookie to current timestamp when display survey modal
    if isDisplay:
        logging.info("Setting a new timestamp cookie")
        # Encrypt the timestamp to prevent user modification
        timestamp_bytes = str(dateToday.timestamp())
        encrypted_timestamp = encryption.encrypt(timestamp_bytes)
        # Add the encrypted timestamp as cookie to the response
        response.set_cookie(key="timestamp", value=encrypted_timestamp)

    return isDisplay
