from fastapi import APIRouter, Request, Response
from dependency_injector.wiring import inject
from models.Rule import Rule
from repository.FeatureConfig import FeatureConfig

from datetime import date, datetime, timedelta
from uuid import uuid4
import random

router = APIRouter()

@router.get("/rules")
@inject
def show_modal(featureUrl: str, request: Request, response: Response) -> bool:
    # Get rules from featureUrl query
    rulesFromFeature: Rule | None = FeatureConfig.getRuleFromFeature(feature_url=featureUrl)

    # Get Cookie user_id
    userCookie: str | None = request._cookies.get('user_id')
    # Set user_id Cookie if is None
    if(userCookie == None):
        response.set_cookie(key="user_id", value=str(uuid4()))

    # Get current timestamp
    dateToday: date = date.today()
    # Get Cookie timestamp and format into date
    dateTimestamp: date = date.fromtimestamp(float(request._cookies.get('timestamp')))

    isOverDelay: bool = timedelta(days=rulesFromFeature.delay_before_reanswer * 30.5) <= dateToday - dateTimestamp
    isWithinRatio: bool = random.random() <= rulesFromFeature.ratio
    isDisplay: bool = rulesFromFeature.is_active and isOverDelay and isWithinRatio

    # Set timestamp Cookie to current timestamp when display survey modal
    if(isDisplay):
        response.set_cookie(key="timestamp", value=datetime.now().timestamp())

    return isDisplay