from datetime import timedelta
from fastapi import HTTPException
import unittest
from unittest.mock import patch
from jwcrypto import jwk
import jwt
from jwt.api_jwk import PyJWK

from survey_logic import security as logic
from models.security import OAuthBody, ScopeEnum
from utils.encryption import create_jwtoken


class TestSecurityGrant(unittest.TestCase):

    def test_unsupported_grant_type(self):
        body = OAuthBody(grant_type="something else")
        with self.assertRaises(HTTPException) as cm:
            logic.token_request(body)
        self.assertEqual(cm.exception.status_code, 400)


class TestAuthCodeFlow(unittest.TestCase):
    def setUp(self):
        self.secret_key = (
            "e7d7ca53cc5093f3853c00bd9e4d634e6e68a41c33b3f7077487b610185790aa"
        )
        self.config = {
            "secret_key": self.secret_key,
            "access_token_expire_minutes": 10,
            "jwk_url": "http://localhost:8080/jwk"
        }

        key = jwk.JWK.generate(kty="RSA", size=2048, alg="RS256", use="sig", kid="1234")
        self.public_key_dict = key.export_public(as_dict=True)
        self.pem_private_key = key.export_to_pem(private_key=True, password=None)
        self.auth_code = create_jwtoken(
            {}, timedelta(minutes=15), self.pem_private_key, "RS256"
        )

    def test_auth_code_correct(self):
        jwk = PyJWK(self.public_key_dict, algorithm="RS256")

        token_type = "Bearer"
        expires_in = 600
        scope = ScopeEnum.CLIENT.value

        with patch("survey_logic.security.PyJWKClient") as jwk_client:
            mock_client = jwk_client.return_value
            mock_client.get_signing_keys.return_value = [jwk]
            response = logic.authorization_code_flow(self.auth_code, config=self.config)

        response_dict = response.dict()
        self.assertEqual(response_dict["token_type"], token_type)
        self.assertEqual(response_dict["expires_in"], expires_in)
        self.assertEqual(response_dict["scope"], scope)
        payload = jwt.decode(
            response_dict["access_token"],
            self.secret_key,
            algorithms=["HS256"],
            options={"require": ["exp"]},
        )
        self.assertEqual(payload["scopes"], [scope])

    def test_auth_code_missing(self):
        with self.assertRaises(HTTPException) as cm:
            logic.authorization_code_flow(None, config=self.config)
        self.assertEqual(cm.exception.status_code, 400)

    def test_auth_code_invalid(self):
        """
        Test case where auth code is invalid or there is an issue with JWK
        """
        jwk = PyJWK(self.public_key_dict, algorithm="RS256")

        with patch("survey_logic.security.PyJWKClient") as jwk_client:
            mock_client = jwk_client.return_value
            mock_client.get_signing_keys.return_value = [jwk]
            with self.assertRaises(HTTPException) as cm:
                logic.authorization_code_flow("1234", config=self.config)

        self.assertEqual(cm.exception.status_code, 401)


class TestClientCredentialsFlow(unittest.TestCase):
    def setUp(self):
        self.secret_key = (
            "e7d7ca53cc5093f3853c00bd9e4d634e6e68a41c33b3f7077487b610185790aa"
        )
        self.config = {
            "secret_key": self.secret_key,
            "access_token_expire_minutes": 10,
            "client_secrets": "625de0b7cc7ad2b1356b8f0c17ac67bf,18884759548e7ac1dafddd5a841f96c9",
        }
        self.client_id = 1
        self.client_secret = "625de0b7cc7ad2b1356b8f0c17ac67bf"

    def test_credentials_correct(self):
        token_type = "Bearer"
        expires_in = 600
        scope = ScopeEnum.DATA.value

        response = logic.client_credentials_flow(self.client_id, self.client_secret, config=self.config)

        response_dict = response.dict()
        self.assertEqual(response_dict["token_type"], token_type)
        self.assertEqual(response_dict["expires_in"], expires_in)
        self.assertEqual(response_dict["scope"], scope)
        payload = jwt.decode(
            response_dict["access_token"],
            self.secret_key,
            algorithms=["HS256"],
            options={"require": ["exp"]},
        )
        self.assertEqual(payload["scopes"], [scope])

    def test_credentials_missing(self):
        with self.assertRaises(HTTPException) as cm:
            logic.client_credentials_flow(None, None, config=self.config)
        self.assertEqual(cm.exception.status_code, 400)

    def test_invalid_client_id(self):
        with self.assertRaises(HTTPException) as cm:
            logic.client_credentials_flow(4, self.client_secret, config=self.config)
        self.assertEqual(cm.exception.status_code, 401)

    def test_invalid_client_secret(self):
        with self.assertRaises(HTTPException) as cm:
            logic.client_credentials_flow(self.client_id, "something", config=self.config)
        self.assertEqual(cm.exception.status_code, 401)
