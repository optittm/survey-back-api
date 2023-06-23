import unittest
from unittest.mock import ANY, Mock, patch
from fastapi import HTTPException, Response
from datetime import datetime, timedelta

from main import app
from models.rule import Rule
from survey_logic import rules as logic
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.encryption import Encryption


class TestRules(unittest.IsolatedAsyncioTestCase):
    """
    Tests for the modal display decision logic
    """

    def setUp(self):
        self.response = Mock(spec=Response)
        self.mock_yaml_repo = Mock(spec=YamlRulesRepository)
        self.mock_db_repo = Mock(spec=SQLiteRepository)
        self.crypt_key = "rg3ENcA7oBCxtxvJ1kk4oAXLizePSnGqPykRi4hvWqY="
        self.encryption = Encryption(self.crypt_key)
        self.timestamp = (datetime.now() - timedelta(days=40)).timestamp()
        self.rule =Rule(
            feature_url="/test",
            ratio=0.6,
            delay_before_reanswer=30,
            delay_to_answer=3,
            is_active=True,
        )

    async def test_show_modal(self):
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"

        with patch("survey_logic.rules.random.random") as mock_random, \
            patch("survey_logic.rules._get_rule_from_feature") as mock_rule, \
            patch("survey_logic.rules.get_encryption_from_project_name") as mock_crypto, \
            patch("survey_logic.rules._log_display"):

            mock_random.return_value = 0.4
            mock_rule.return_value = self.rule
            mock_crypto.return_value = self.encryption

            result = await logic.show_modal_or_not(
                self.response,
                "/test",
                "1",
                self.encryption.encrypt(str(self.timestamp)),
                rulesYamlConfig=self.mock_yaml_repo,
            )

        self.assertEqual(result, True)
        self.response.set_cookie.assert_called_once_with(key="timestamp", value=ANY)
        # No user_id cookie is provided since a user_id was received
        with self.assertRaises(AssertionError):
            self.response.set_cookie.assert_called_once_with(key="user_id", value=ANY)

    async def test_not_show_modal_not_active(self):
        self.rule.is_active = False
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"

        with patch("survey_logic.rules.random.random") as mock_random, \
            patch("survey_logic.rules._get_rule_from_feature") as mock_rule, \
            patch("survey_logic.rules.get_encryption_from_project_name") as mock_crypto, \
            patch("survey_logic.rules._log_display"):

            mock_random.return_value = 0.4
            mock_rule.return_value = self.rule
            mock_crypto.return_value = self.encryption

            result = await logic.show_modal_or_not(
                self.response,
                "/test",
                "1",
                self.encryption.encrypt(str(self.timestamp)),
                rulesYamlConfig=self.mock_yaml_repo,
            )
        self.assertEqual(result, False)

    async def test_not_show_modal_not_overDelay(self):
        """
        Case when the last modal display is too recent compared to the delay_before_reanswer
        """
        short_timestamp = (datetime.now() - timedelta(days=10)).timestamp()
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"

        with patch("survey_logic.rules.random.random") as mock_random, \
            patch("survey_logic.rules._get_rule_from_feature") as mock_rule, \
            patch("survey_logic.rules.get_encryption_from_project_name") as mock_crypto, \
            patch("survey_logic.rules._log_display"):

            mock_random.return_value = 0.4
            mock_rule.return_value = self.rule
            mock_crypto.return_value = self.encryption

            result = await logic.show_modal_or_not(
                self.response,
                "/test",
                "1",
                self.encryption.encrypt(str(short_timestamp)),
                rulesYamlConfig=self.mock_yaml_repo,
            )
        self.assertEqual(result, False)

    async def test_not_show_modal_notWithinRatio(self):
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"

        with patch("survey_logic.rules.random.random") as mock_random, \
            patch("survey_logic.rules._get_rule_from_feature") as mock_rule, \
            patch("survey_logic.rules.get_encryption_from_project_name") as mock_crypto, \
            patch("survey_logic.rules._log_display"):

            mock_random.return_value = 1
            mock_rule.return_value = self.rule
            mock_crypto.return_value = self.encryption

            result = await logic.show_modal_or_not(
                self.response,
                "/test",
                "1",
                self.encryption.encrypt(str(self.timestamp)),
                rulesYamlConfig=self.mock_yaml_repo,
            )
        self.assertEqual(result, False)

    async def test_no_cookies(self):
        """
        Case when no input cookies are provided
        - new user who doesn't have a user_id
        - no previous display of the modal so no timestamp
        """
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"
        
        with patch("survey_logic.rules.random.random") as mock_random, \
            patch("survey_logic.rules._get_rule_from_feature") as mock_rule, \
            patch("survey_logic.rules.get_encryption_from_project_name") as mock_crypto, \
            patch("survey_logic.rules._log_display"):

            mock_random.return_value = 0.4
            mock_rule.return_value = self.rule
            mock_crypto.return_value = self.encryption

            result = await logic.show_modal_or_not(
                self.response,
                "/test",
                rulesYamlConfig=self.mock_yaml_repo,
            )

        self.assertEqual(result, True)
        # New cookies should be provided
        self.response.set_cookie.assert_any_call(key="timestamp", value=ANY)
        self.response.set_cookie.assert_any_call(key="user_id", value=ANY)

    async def test_invalid_timestamp(self):
        self.mock_yaml_repo.getProjectNameFromFeature.return_value = "project1"

        with patch("survey_logic.rules.random.random") as mock_random, \
            patch("survey_logic.rules._get_rule_from_feature") as mock_rule, \
            patch("survey_logic.rules.get_encryption_from_project_name") as mock_crypto, \
            patch("survey_logic.rules._log_display"):

            mock_random.return_value = 0.4
            mock_rule.return_value = self.rule
            mock_crypto.return_value = self.encryption
            
            with self.assertRaises(HTTPException) as cm:
                result = await logic.show_modal_or_not(
                    self.response,
                    "/test",
                    "1",
                    "hdhskokvhsnvj",
                    rulesYamlConfig=self.mock_yaml_repo,
                )
        self.assertEqual(cm.exception.status_code, 422)


class TestRuleFromFeature(unittest.TestCase):
    def setUp(self):
        self.feature_url = "/test"
        self.mock_yaml = Mock(spec=YamlRulesRepository)

    def test_get_rule(self):
        return_rule = Rule(
            feature_url="/test",
            ratio=0.6,
            delay_before_reanswer=30,
            delay_to_answer=3,
            is_active=True,
        )
        self.mock_yaml.getRuleFromFeature.return_value = return_rule
        result = logic._get_rule_from_feature(self.feature_url, rulesYamlConfig=self.mock_yaml)
        self.assertEqual(result, return_rule)
        
    def test_feature_not_found(self):
        self.mock_yaml.getRuleFromFeature.return_value = None
        with self.assertRaises(HTTPException) as cm:
            logic._get_rule_from_feature(self.feature_url, rulesYamlConfig=self.mock_yaml)
        self.assertEqual(cm.exception.status_code, 404)
