from typing import Optional
from fastapi import Depends, Response, status, HTTPException
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

@inject
def _get_rule_from_feature(
    feature_url: str,
    rulesYamlConfig: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> Rule:
    # Get rules from featureUrl query
    rulesFromFeature: Optional[Rule] = rulesYamlConfig.getRuleFromFeature(
        feature_url=feature_url
    )
    if rulesFromFeature is None:
        logging.error("GET rules::Feature not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found",
        )
    return rulesFromFeature

@inject
async def _get_encryption_from_project_name(
    project_name: str,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
) -> Encryption:
    # Retrieve the encryption key of the project
    project = await sqlite_repo.get_project_by_name(project_name)
    encryption_db = await sqlite_repo.get_encryption_by_project_id(project.id)
    encryption = Encryption(encryption_db.encryption_key)
    return encryption

@inject
async def _log_display(
    project_name: str,
    user_id: str,
    feature_url: str,
    date: datetime,
    sqlite_repo: SQLiteRepository = Depends(Provide[Container.sqlite_repo]),
):
    # Store the timestamp when it's displayed
    iso_timestamp = date.isoformat()
    await sqlite_repo.create_display(
        project_name, user_id, iso_timestamp, feature_url
    )

@inject
async def show_modal_or_not(
    response: Response,
    featureUrl: str,
    user_id: Optional[str] = None,
    timestamp: Optional[str] = None,
    rulesYamlConfig: YamlRulesRepository = Depends(Provide[Container.rules_config]),
) -> bool:
    rulesFromFeature = _get_rule_from_feature(featureUrl)
    project_name = rulesYamlConfig.getProjectNameFromFeature(featureUrl)
    encryption = await _get_encryption_from_project_name(project_name)    

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
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid timestamp, cannot decrypt",
            )
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

        await _log_display(project_name, user_id, featureUrl, dateToday)
        
    return isDisplay
