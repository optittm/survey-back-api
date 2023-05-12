from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject
import jwt
from models.security import AuthToken, OAuthBody

from utils.container import Container


router = APIRouter()


@inject
def _create_jwtoken(
    data: dict,
    expires_delta: timedelta,
    config=Depends(Provide[Container.config]),
):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config["secret_key"])
    return encoded_jwt


@router.post("/token", response_model=AuthToken)
@inject
async def login_for_access_token(
    data: OAuthBody, config=Depends(Provide[Container.config])
):
    # TODO auth
    # user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    # if not user:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    if data.grant_type == "authorization_code":
        access_token_expires = timedelta(minutes=config["access_token_expire_minutes"])
        access_token = _create_jwtoken(
            data={"scopes": data.scope.split(" ")},
            expires_delta=access_token_expires,
        )
        refresh_token_expires = timedelta(days=config["refresh_token_expire_days"])
        refresh_token = _create_jwtoken(
            data={"scopes": data.scope.split(" ")},
            expires_delta=refresh_token_expires,
        )
        return AuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=access_token_expires.seconds,
            scope=data.scope,
            refresh_token=refresh_token,
        )

    elif data.grant_type == "refresh_token":
        # TODO check expiry
        access_token_expires = timedelta(minutes=config["access_token_expire_minutes"])
        access_token = _create_jwtoken(
            data={"scope": data.scope},
            expires_delta=access_token_expires,
        )
        return AuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=access_token_expires.seconds,
            scope=data.scope,
        )

    else:
        logging.error(f"Unsupported grant type: {data.grant_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type",
        )
