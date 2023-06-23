from datetime import timedelta
import logging
from typing import Optional
from fastapi import Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from dependency_injector.wiring import Provide, inject
import jwt
from jwt import PyJWKClient
from models.security import AuthToken, OAuthBody, ScopeEnum

from utils.container import Container
from utils.encryption import create_jwtoken

@inject
def authorize_user(config=Depends(Provide[Container.config])):
    return RedirectResponse(config["auth_url"])

@inject
def authorization_code_flow(auth_code: Optional[str], config=Depends(Provide[Container.config])):
    if auth_code is None:
        logging.error(f"Missing authorization code")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code",
        )

    try:
        jwks_client = PyJWKClient(config["jwk_url"])
        signing_key = jwks_client.get_signing_keys()[0]
        jwt.decode(
            auth_code,
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
    access_token = create_jwtoken(
        data={"scopes": [scope]},
        expires_delta=access_token_expires,
        encode_key=config["secret_key"],
    )
    return AuthToken(
        access_token=access_token,
        token_type="Bearer",
        expires_in=access_token_expires.seconds,
        scope=scope,
    )

@inject
def client_credentials_flow(
    client_id: Optional[int],
    client_secret: Optional[str],
    config=Depends(Provide[Container.config]),
):
    if client_id is None or client_secret is None:
        logging.error(f"Missing client id or secret")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing client id or secret",
        )

    secrets = config["client_secrets"].split(",")
    try:
        stored_secret = secrets[client_id - 1]
        if client_secret != stored_secret:
            raise Exception()
    except (IndexError, Exception):
        logging.error(f"Invalid client credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    scope = ScopeEnum.DATA.value
    access_token_expires = timedelta(minutes=config["access_token_expire_minutes"])
    access_token = create_jwtoken(
        data={"scopes": [scope]},
        expires_delta=access_token_expires,
        encode_key=config["secret_key"],
    )
    return AuthToken(
        access_token=access_token,
        token_type="Bearer",
        expires_in=access_token_expires.seconds,
        scope=scope,
    )

def token_request(data: OAuthBody):
    if data.grant_type == "authorization_code":
        return authorization_code_flow(data.code)

    elif data.grant_type == "client_credentials":
        return client_credentials_flow(data.client_id, data.client_secret)

    else:
        logging.error(f"Unsupported grant type: {data.grant_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type",
        )