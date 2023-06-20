from fastapi import APIRouter

from models.security import AuthToken, OAuthBody
from survey_logic.security import authorize_user, token_request


router = APIRouter()


@router.post("/authorize")
def authorize():
    return authorize_user()


@router.post("/token", response_model=AuthToken)
def token_request(data: OAuthBody):
    return token_request(data)
