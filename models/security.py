from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class ScopeEnum(Enum):
    CLIENT = "client"
    DATA = "data"


class OAuthBody(BaseModel):
    grant_type: str
    scope: str
    code: Optional[str]
    refresh_token: Optional[str]


class AuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str
    refresh_token: Optional[str]


class JWTokenData(BaseModel):
    scopes: List[str]
