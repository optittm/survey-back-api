from fastapi import APIRouter
from dependency_injector.wiring import inject
from models.Rule import Rule
from repository.FeatureConfig import FeatureConfig

router = APIRouter()

@router.get("/rules")
@inject
def show_modal(featureUrl: str) -> bool:
    # Get rules from featureUrl query
    rulesFromFeature: Rule | None = FeatureConfig.getRuleFromFeature(feature_url=featureUrl)

    return rulesFromFeature.is_active