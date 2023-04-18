import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from main import app
from models.rule import Rule
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.encryption import Encryption


class TestRulesRoutes(unittest.TestCase):
    """
    Tests for the /rules endpoints
    """

    def setUp(self):
        self.client = TestClient(app)
        self.mock_yaml_repo = Mock(spec=YamlRulesRepository)
        self.mock_db_repo = Mock(spec=SQLiteRepository)
        self.crypt_key = "rg3ENcA7oBCxtxvJ1kk4oAXLizePSnGqPykRi4hvWqY="
        self.encryption = Encryption(self.crypt_key)

    def send_request(self, timestamp: str):
        with app.container.rules_config.override(
            self.mock_yaml_repo
        ), app.container.sqlite_repo.override(self.mock_db_repo):
            response = self.client.get(
                "/rules",
                params={"featureUrl": "/test"},
                cookies={
                    "user_id": "1",
                    "timestamp": self.encryption.encrypt(timestamp),
                },
            )
        return response

    def test_show_modal(self):
        timestamp = (datetime.now() - timedelta(days=40)).timestamp()
        rule = Rule(
            feature_url="/test",
            ratio=0.6,
            delay_before_reanswer=30,
            delay_to_answer=3,
            is_active=True,
        )
        self.mock_yaml_repo.getRuleFromFeature.return_value = rule
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"
        self.mock_db_repo.get_project_by_name.return_value = Mock()
        project_encryption_mock = Mock()
        project_encryption_mock.encryption_key = self.crypt_key
        self.mock_db_repo.get_encryption_by_project_id.return_value = (
            project_encryption_mock
        )

        with patch("routes.rules.random.random") as mock_random:
            mock_random.return_value = 0.4
            response = self.send_request(str(timestamp))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), True)
        self.assertIsNotNone(response.cookies.get("timestamp"))
        self.assertIsNone(response.cookies.get("user_id"))

    def test_not_show_modal_not_active(self):
        timestamp = (datetime.now() - timedelta(days=40)).timestamp()
        rule = Rule(
            feature_url="/test",
            ratio=0.6,
            delay_before_reanswer=30,
            delay_to_answer=3,
            is_active=False,
        )
        self.mock_yaml_repo.getRuleFromFeature.return_value = rule
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"
        self.mock_db_repo.get_project_by_name.return_value = Mock()
        project_encryption_mock = Mock()
        project_encryption_mock.encryption_key = self.crypt_key
        self.mock_db_repo.get_encryption_by_project_id.return_value = (
            project_encryption_mock
        )

        with patch("routes.rules.random.random") as mock_random:
            mock_random.return_value = 0.4
            response = self.send_request(str(timestamp))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), False)

    def test_not_show_modal_not_overDelay(self):
        timestamp = (datetime.now() - timedelta(days=10)).timestamp()
        rule = Rule(
            feature_url="/test",
            ratio=0.6,
            delay_before_reanswer=30,
            delay_to_answer=3,
            is_active=True,
        )
        self.mock_yaml_repo.getRuleFromFeature.return_value = rule
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"
        self.mock_db_repo.get_project_by_name.return_value = Mock()
        project_encryption_mock = Mock()
        project_encryption_mock.encryption_key = self.crypt_key
        self.mock_db_repo.get_encryption_by_project_id.return_value = (
            project_encryption_mock
        )

        with patch("routes.rules.random.random") as mock_random:
            mock_random.return_value = 0.4
            response = self.send_request(str(timestamp))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), False)

    def test_not_show_modal_notWithinRatio(self):
        timestamp = (datetime.now() - timedelta(days=40)).timestamp()
        rule = Rule(
            feature_url="/test",
            ratio=0.6,
            delay_before_reanswer=30,
            delay_to_answer=3,
            is_active=True,
        )
        self.mock_yaml_repo.getRuleFromFeature.return_value = rule
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"
        self.mock_db_repo.get_project_by_name.return_value = Mock()
        project_encryption_mock = Mock()
        project_encryption_mock.encryption_key = self.crypt_key
        self.mock_db_repo.get_encryption_by_project_id.return_value = (
            project_encryption_mock
        )

        with patch("routes.rules.random.random") as mock_random:
            mock_random.return_value = 1
            response = self.send_request(str(timestamp))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), False)

    def test_no_cookies(self):
        rule = Rule(
            feature_url="/test",
            ratio=0.6,
            delay_before_reanswer=30,
            delay_to_answer=3,
            is_active=True,
        )
        self.mock_yaml_repo.getRuleFromFeature.return_value = rule
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"
        self.mock_db_repo.get_project_by_name.return_value = Mock()
        project_encryption_mock = Mock()
        project_encryption_mock.encryption_key = self.crypt_key
        self.mock_db_repo.get_encryption_by_project_id.return_value = (
            project_encryption_mock
        )

        with patch("routes.rules.random.random") as mock_random:
            mock_random.return_value = 0.4
            with app.container.rules_config.override(
                self.mock_yaml_repo
            ), app.container.sqlite_repo.override(self.mock_db_repo):
                response = self.client.get(
                    "/rules",
                    params={"featureUrl": "/test"},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), True)
        self.assertIsNotNone(response.cookies.get("timestamp"))
        self.assertIsNotNone(response.cookies.get("user_id"))
