import logging
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes
import jwt
from dependency_injector.wiring import Provide, inject

from models.security import JWTokenData, ScopeEnum
from utils.container import Container


class EnabledOAuth2ACB(OAuth2AuthorizationCodeBearer):
    """
    Same class as FastAPI's OAuth2AuthorizationCodeBearer except the
    401 response can be controlled via an environment variable
    """

    @inject
    async def __call__(
        self,
        request: Request,
        config=Depends(Provide[Container.config]),
    ) -> Optional[str]:
        if config["secret_key"] != "":
            return await super().__call__(request)


oauth2_scheme = EnabledOAuth2ACB(
    # These urls are only for the autogenerated docs
    authorizationUrl="/api/v1/authorize",
    tokenUrl="/api/v1/token",
    scopes={
        ScopeEnum.CLIENT.value: "Check if the modal should be displayed and post user comments.",
        ScopeEnum.DATA.value: "Read comments, projects, rules and statistics.",
    },
)


@inject
def check_jwt(
    security_scopes: SecurityScopes,
    token: Optional[str] = Depends(oauth2_scheme),
    config=Depends(Provide[Container.config]),
):
    # OAuth security is disabled if no key is present
    if token is None and config["secret_key"] == "":
        return None

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    exception_headers = {"WWW-Authenticate": authenticate_value}

    try:
        payload = jwt.decode(
            token,
            config["secret_key"],
            algorithms=["HS256"],
            options={"require": ["exp"]},
        )
        token_data = JWTokenData(scopes=payload.get("scopes", []))
    except jwt.ExpiredSignatureError:
        logging.error("JWT is expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is expired",
            headers=exception_headers,
        )
    except Exception as e:
        # JWT could not be decoded, doesn't have an exp or scopes claims, or the claims are invalid
        logging.exception("Invalid JWT", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers=exception_headers,
        )

    # Checking if the JWT has the scopes required for this route
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            logging.error("Unauthorized JWT scope")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers=exception_headers,
            )
