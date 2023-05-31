from datetime import timedelta
import unittest
from fastapi import HTTPException
from fastapi.security import SecurityScopes
from models.security import ScopeEnum

from routes.middlewares.feature_url import remove_search_hash_from_url
from main import app
from routes.middlewares.security import check_jwt
from utils.encryption import create_jwtoken


class TestURLMiddleware(unittest.TestCase):
    def test_remove_search_hash_from_url(self):
        main_url = "https://test.com/segment"
        full_url = main_url + "?query=value#something"
        result = remove_search_hash_from_url(full_url)
        self.assertEqual(result, main_url)


class TestJWTVerification(unittest.TestCase):
    def setUp(self):
        self.secret_key = (
            "e7d7ca53cc5093f3853c00bd9e4d634e6e68a41c33b3f7077487b610185790aa"
        )
        app.container.config.secret_key.from_value(self.secret_key)
        self.security_scopes = SecurityScopes([ScopeEnum.DATA.value])

    def test_security_disabled(self):
        app.container.config.secret_key.from_value("")
        result = check_jwt(self.security_scopes, None)
        self.assertIsNone(result)

    def test_token_expired(self):
        token = create_jwtoken(
            {"scopes": [ScopeEnum.DATA.value]},
            timedelta(milliseconds=1),
            self.secret_key,
        )
        try:
            check_jwt(self.security_scopes, token)
        except HTTPException as e:
            self.assertEqual(e.status_code, 401)

    def test_token_decode_fail(self):
        # For instance if token was signed with a different key,
        # but could be any other issue with the token
        different_key = (
            "f0b5844c362ee0080db193004524f21ccdee8dbd9c76f7b483b1d08748586751"
        )
        token = create_jwtoken(
            {"scopes": [ScopeEnum.DATA.value]},
            timedelta(minutes=10),
            different_key,
        )
        try:
            check_jwt(self.security_scopes, token)
        except HTTPException as e:
            self.assertEqual(e.status_code, 401)

    def test_missing_required_scope(self):
        token = create_jwtoken(
            {"scopes": [ScopeEnum.CLIENT.value]},
            timedelta(minutes=10),
            self.secret_key,
        )
        try:
            check_jwt(self.security_scopes, token)
        except HTTPException as e:
            self.assertEqual(e.status_code, 401)
