from fastapi import APIRouter, Depends, Request, Response
from dependency_injector.wiring import Provide,inject
from utils.container import Container

from models.rule import Rule
from repository.yaml_rule_repository import YamlRulesRepository
from utils.encryption import Encryption

from datetime import datetime, timedelta
from uuid import uuid4
import random

router = APIRouter()
encryption = Encryption()
fernet = encryption.fernet

@router.get("/rules")
@inject
def show_modal(featureUrl: str, request: Request, response: Response, rulesYamlConfig: YamlRulesRepository = Depends(Provide[Container.rules_config])) -> bool:
    # Get rules from featureUrl query
    rulesFromFeature: Rule | None = rulesYamlConfig.getRuleFromFeature(feature_url=featureUrl)

    # Get Cookie user_id
    userCookie: str | None = request._cookies.get('user_id')
    # Set user_id Cookie if is None
    if userCookie is None:
        response.set_cookie(key="user_id", value=str(uuid4()))

    # Get current timestamp
    dateToday: datetime = datetime.now()
    # Get Cookie timestamp and format into date
    encrypted_timestamp = request._cookies.get('timestamp')
    if encrypted_timestamp is not None:
        decrypted_timestamp = fernet.decrypt(encrypted_timestamp.encode()).decode()
        dateTimestamp: datetime = datetime.fromtimestamp(float(decrypted_timestamp))
        isOverDelay: bool = timedelta(days=rulesFromFeature.delay_before_reanswer * 30.5) <= dateToday - dateTimestamp
    else:
        dateTimestamp = datetime.now()
        isOverDelay=True

    isWithinRatio: bool = random.random() <= rulesFromFeature.ratio
    isDisplay: bool = rulesFromFeature.is_active and isOverDelay and isWithinRatio

    # Set timestamp Cookie to current timestamp when display survey modal
    if(isDisplay):
        # Chiffrer le timestamp en bytes avec la clé
        timestamp_bytes = str(datetime.now().timestamp()).encode()
        encrypted_timestamp = fernet.encrypt(timestamp_bytes)
        # Ajouter le cookie chiffré à la réponse
        response.set_cookie(key="timestamp", value=encrypted_timestamp.decode())

    return isDisplay
