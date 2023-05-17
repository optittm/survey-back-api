from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from dependency_injector.wiring import Provide, inject
import jwt
from jwt import PyJWKClient
from models.security import AuthToken, OAuthBody, ScopeEnum

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


@router.post("/authorize")
@inject
def authorize_redirect(config=Depends(Provide[Container.config])):
    return RedirectResponse(config["auth_url"])


@router.post("/token", response_model=AuthToken)
@inject
async def token_request(
    data: OAuthBody,
    config=Depends(Provide[Container.config]),
):
    if data.grant_type == "authorization_code":
        if data.code is None:
            logging.error(f"Missing authorization code")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing authorization code",
            )

        try:
            jwks_client = PyJWKClient(config["jwk_url"])
            signing_key = jwks_client.get_signing_keys()[0]
            jwt.decode(
                data.code,
                signing_key.key,
                algorithms=["RS256"],
                options={"require": ["exp"]},
            )
        except Exception:
            logging.error("Invalid authorization code")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid code",
            )

        scope = ScopeEnum.CLIENT.value
        access_token_expires = timedelta(minutes=config["access_token_expire_minutes"])
        access_token = _create_jwtoken(
            data={"scopes": [scope]},
            expires_delta=access_token_expires,
        )
        return AuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=access_token_expires.seconds,
            scope=scope,
        )

    elif data.grant_type == "client_credentials":
        if data.client_id is None or data.client_secret is None:
            logging.error(f"Missing client id or secret")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing client id or secret",
            )
        secrets = config["client_secrets"].split(",")
        if data.client_secret != secrets[data.client_id]:
            logging.error(f"Invalid client credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        scope = ScopeEnum.DATA.value
        access_token_expires = timedelta(minutes=config["access_token_expire_minutes"])
        access_token = _create_jwtoken(
            data={"scopes": [scope]},
            expires_delta=access_token_expires,
        )
        return AuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=access_token_expires.seconds,
            scope=scope,
        )

    else:
        logging.error(f"Unsupported grant type: {data.grant_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type",
        )
