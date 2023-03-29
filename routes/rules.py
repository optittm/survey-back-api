from fastapi import APIRouter, Request
from dependency_injector.wiring import inject
from models.Rule import Rule
from repository.FeatureConfig import FeatureConfig

from datetime import date, timedelta 
import random

router = APIRouter()

@router.get("/rules")
@inject
def show_modal(featureUrl: str, request: Request) -> bool:
    # Get rules from featureUrl query
    rulesFromFeature: Rule | None = FeatureConfig.getRuleFromFeature(feature_url=featureUrl)

    # Get current timestamp
    dateToday: date = date.today()
    # Get Cookie timestamp
    dateTimestamp: date = date.fromtimestamp(float(request._cookies.get('timestamp')))

    isOverDelay: bool = timedelta(days=rulesFromFeature.delay_before_reanswer * 30.5) <= dateToday - dateTimestamp
    isWithinRatio = random.random() <= rulesFromFeature.ratio

    return rulesFromFeature.is_active and isOverDelay and isWithinRatio