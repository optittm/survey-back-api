from datetime import timedelta
import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
from jwcrypto import jwk
import jwt
from jwt.api_jwk import PyJWK

from main import app
from routes.security import router
from models.security import OAuthBody, ScopeEnum
from utils.encryption import create_jwtoken


class TestSecurityRoute(unittest.TestCase):
    def setUp(self):
        # Router has to be included here because it doesn't register
        # if there is no secret key to start with in .env
        app.include_router(router, prefix="/api/v1")
        self.client = TestClient(app)
        self.token_route = "/api/v1/token"

    def test_unsupported_grant_type(self):
        body = OAuthBody(grant_type="something else")
        response = self.client.post(
            self.token_route,
            json=body.dict(),
        )
        self.assertEqual(response.status_code, 400)


class TestAuthCodeFlow(unittest.TestCase):
    def setUp(self):
        # Router has to be included here because it doesn't register
        # if there is no secret key to start with in .env
        app.include_router(router, prefix="/api/v1")
        self.client = TestClient(app)
        self.route = "/api/v1/token"

        self.secret_key = (
            "e7d7ca53cc5093f3853c00bd9e4d634e6e68a41c33b3f7077487b610185790aa"
        )
        app.container.config.secret_key.from_value(self.secret_key)
        app.container.config.access_token_expire_minutes.from_value(10)

        key = jwk.JWK.generate(kty="RSA", size=2048, alg="RS256", use="sig", kid="1234")
        self.public_key_dict = key.export_public(as_dict=True)
        self.pem_private_key = key.export_to_pem(private_key=True, password=None)
        self.token_body = OAuthBody(
            grant_type="authorization_code",
            code=create_jwtoken(
                {}, timedelta(minutes=15), self.pem_private_key, "RS256"
            ),
        )

    def test_auth_code_correct(self):
        jwk = PyJWK(self.public_key_dict, algorithm="RS256")

        token_type = "Bearer"
        expires_in = 600
        scope = ScopeEnum.CLIENT.value

        with patch("routes.security.PyJWKClient") as jwk_client:
            mock_client = jwk_client.return_value
            mock_client.get_signing_keys.return_value = [jwk]
            response = self.client.post(
                self.route,
                json=self.token_body.dict(),
            )

        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
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
        body = OAuthBody(grant_type="authorization_code")
        response = self.client.post(
            self.route,
            json=body.dict(),
        )
        self.assertEqual(response.status_code, 400)

    def test_auth_code_invalid(self):
        """
        Test case where auth code is invalid or there is an issue with JWK
        """
        jwk = PyJWK(self.public_key_dict, algorithm="RS256")
        self.token_body.code = "1234"

        with patch("routes.security.PyJWKClient") as jwk_client:
            mock_client = jwk_client.return_value
            mock_client.get_signing_keys.return_value = [jwk]
            response = self.client.post(
                self.route,
                json=self.token_body.dict(),
            )

        self.assertEqual(response.status_code, 401)


class TestClientCredentialsFlow(unittest.TestCase):
    def setUp(self):
        # Router has to be included here because it doesn't register
        # if there is no secret key to start with in .env
        app.include_router(router, prefix="/api/v1")
        self.client = TestClient(app)
        self.route = "/api/v1/token"

        self.secret_key = (
            "e7d7ca53cc5093f3853c00bd9e4d634e6e68a41c33b3f7077487b610185790aa"
        )
        app.container.config.secret_key.from_value(self.secret_key)
        app.container.config.access_token_expire_minutes.from_value(10)
        app.container.config.client_secrets.from_value(
            "625de0b7cc7ad2b1356b8f0c17ac67bf,18884759548e7ac1dafddd5a841f96c9"
        )
        self.token_body = OAuthBody(
            grant_type="client_credentials",
            client_id=1,
            client_secret="625de0b7cc7ad2b1356b8f0c17ac67bf",
        )

    def test_credentials_correct(self):
        token_type = "Bearer"
        expires_in = 600
        scope = ScopeEnum.DATA.value

        response = self.client.post(
            self.route,
            json=self.token_body.dict(),
        )

        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
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
        body = OAuthBody(grant_type="client_credentials")
        response = self.client.post(
            self.route,
            json=body.dict(),
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_client_id(self):
        self.token_body.client_id = 4
        response = self.client.post(
            self.route,
            json=self.token_body.dict(),
        )
        self.assertEqual(response.status_code, 401)

    def test_invalid_client_secret(self):
        self.token_body.client_secret = "something"
        response = self.client.post(
            self.route,
            json=self.token_body.dict(),
        )
        self.assertEqual(response.status_code, 401)
