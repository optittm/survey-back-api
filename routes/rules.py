from typing import Union
from fastapi import APIRouter, Depends, Response, Cookie, Security
from models.security import ScopeEnum

from survey_logic import rules as logic
from routes.middlewares.feature_url import remove_search_hash_from_url
from routes.middlewares.security import check_jwt


router = APIRouter()


@router.get(
    "/rules",
    dependencies=[Security(check_jwt, scopes=[ScopeEnum.CLIENT.value])],
    response_model=Union[bool, dict],
)
async def show_modal(
    response: Response,
    featureUrl: str = Depends(remove_search_hash_from_url),
    user_id: Union[str, None] = Cookie(default=None),
    timestamp: Union[str, None] = Cookie(default=None),
) -> bool:
    return await logic.show_modal_or_not(response, featureUrl, user_id, timestamp)
