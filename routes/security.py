from fastapi import APIRouter

from models.security import AuthToken, OAuthBody
from survey_logic import security as logic


router = APIRouter()


@router.post("/authorize")
def authorize():
    return logic.authorize_user()


@router.post("/token", response_model=AuthToken)
def token_request(data: OAuthBody):
    return logic.token_request(data)
