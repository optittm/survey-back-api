from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class ScopeEnum(Enum):
    CLIENT = "client"
    DATA = "data"


class OAuthBody(BaseModel):
    grant_type: str
    code: Optional[str]
    client_id: Optional[int]
    client_secret: Optional[str]


class AuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str


class JWTokenData(BaseModel):
    scopes: List[str]
