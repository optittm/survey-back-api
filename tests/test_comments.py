from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from survey_logic import comments as logic
from models.comment import Comment
from models.rule import Rule
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from utils.encryption import Encryption
from utils.nlp import SentimentAnalysis


class TestComments(unittest.IsolatedAsyncioTestCase):
    """
    Tests for the comments logic

    For reference of testing with dependency_injector, see:
    https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.html#tests
    (Not needed anymore but I leave the link just in case)
    """

    def setUp(self):
        self.user_id = "3"
        self.feature_url = "http://test.com"
        self.rating = 5
        self.comment = "This is a test comment"
        self.datetime = datetime.now()
        self.mock_yaml = Mock(spec=YamlRulesRepository)
        self.mock_rule = Mock(spec=Rule)
        self.mock_repo = Mock(spec=SQLiteRepository)
        self.mock_nlp = Mock(spec=SentimentAnalysis)
        self.config = {"use_fingerprint": False}
        self.crypt_key = "rg3ENcA7oBCxtxvJ1kk4oAXLizePSnGqPykRi4hvWqY="
        self.encryption = Encryption(self.crypt_key)

    async def test_create_comment(self):
        project_name = "project1"
        cookie_user_id = "123"
        return_comment = Comment(
            id=1,
            project_id=2,
            user_id=cookie_user_id,
            timestamp=self.datetime.isoformat(),
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment",
            language="en",
            sentiment=None,
            sentiment_score=None,
        )
        self.mock_yaml.getProjectNameFromFeature.return_value = project_name
        self.mock_yaml.getRuleFromFeature.return_value = self.mock_rule
        self.mock_rule.delay_to_answer = 5
        self.mock_nlp.analyze.return_value = None, None
        self.mock_repo.create_comment.return_value = return_comment

        with patch("survey_logic.comments.get_encryption_from_project_name") as mock_crypto:
            mock_crypto.return_value = self.encryption
            result = await logic.create_comment(
                self.feature_url,
                self.rating,
                self.comment,
                self.user_id,
                cookie_user_id,
                self.encryption.encrypt(
                    str(self.datetime.timestamp())
                ),
                sqlite_repo=self.mock_repo,
                rules_config=self.mock_yaml,
                sentiment_analysis=self.mock_nlp,
                config=self.config,
            )

        self.assertEqual(result, return_comment)
        self.mock_repo.create_comment.assert_called_once_with(
            self.feature_url,
            self.rating,
            self.comment,
            cookie_user_id,
            self.datetime.isoformat(),
            project_name,
            "en",
            None,
            None,
        )

    async def test_create_comment_fingerprint(self):
        """
        Same as test_create_comment but checks if the user_id is taken from the body instead of the cookie
        """
        project_name = "project1"
        cookie_user_id = "123"
        return_comment = Comment(
            id=1,
            project_id=2,
            user_id=self.user_id,
            timestamp=self.datetime.isoformat(),
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment",
            language="en",
            sentiment=None,
            sentiment_score=None,
        )
        self.mock_yaml.getProjectNameFromFeature.return_value = project_name
        self.mock_yaml.getRuleFromFeature.return_value = self.mock_rule
        self.mock_rule.delay_to_answer = 5
        self.mock_nlp.analyze.return_value = None, None
        config = {"use_fingerprint": True}
        self.mock_repo.create_comment.return_value = return_comment
        
        with patch("survey_logic.comments.get_encryption_from_project_name") as mock_crypto:
            mock_crypto.return_value = self.encryption
            result = await logic.create_comment(
                self.feature_url,
                self.rating,
                self.comment,
                self.user_id,
                cookie_user_id,
                self.encryption.encrypt(
                    str(self.datetime.timestamp())
                ),
                sqlite_repo=self.mock_repo,
                rules_config=self.mock_yaml,
                sentiment_analysis=self.mock_nlp,
                config=config,
            )

        self.assertEqual(result, return_comment)
        self.mock_repo.create_comment.assert_called_once_with(
            self.feature_url,
            self.rating,
            self.comment,
            self.user_id,
            self.datetime.isoformat(),
            project_name,
            "en",
            None,
            None,
        )

    async def test_create_comment_unknown_feature(self):
        """
        Test case when feature/project is not found in the YAML config
        """
        self.mock_yaml.getProjectNameFromFeature.return_value = None
        
        with self.assertRaises(HTTPException) as cm:
            await logic.create_comment(
                self.feature_url,
                self.rating,
                self.comment,
                self.user_id,
                self.user_id,
                self.encryption.encrypt(
                    str(self.datetime.timestamp())
                ),
                sqlite_repo=self.mock_repo,
                rules_config=self.mock_yaml,
                sentiment_analysis=self.mock_nlp,
                config=self.config,
            )
        self.assertEqual(cm.exception.status_code, 404)

    async def test_create_comment_no_cookies(self):
        """
        Test case when cookies are missing
        """
        self.mock_yaml.getProjectNameFromFeature.return_value = "project1"

        with self.assertRaises(HTTPException) as cm:
            await logic.create_comment(
                self.feature_url,
                self.rating,
                self.comment,
                self.user_id,
                None,
                None,
                sqlite_repo=self.mock_repo,
                rules_config=self.mock_yaml,
                sentiment_analysis=self.mock_nlp,
                config=self.config,
            )
        self.assertEqual(cm.exception.status_code, 422)

    async def test_create_comment_delay_elapsed(self):
        """
        Test case when the delay to submit a comment has elapsed
        """
        self.mock_yaml.getProjectNameFromFeature.return_value = "project1"
        self.mock_yaml.getRuleFromFeature.return_value = self.mock_rule
        self.mock_rule.delay_to_answer = 5
        elpased_datetime = self.datetime - timedelta(minutes=10)
        
        with patch("survey_logic.comments.get_encryption_from_project_name") as mock_crypto, \
        self.assertRaises(HTTPException) as cm:
            mock_crypto.return_value = self.encryption
            await logic.create_comment(
                self.feature_url,
                self.rating,
                self.comment,
                self.user_id,
                self.user_id,
                self.encryption.encrypt(
                    str(elpased_datetime.timestamp())
                ),
                sqlite_repo=self.mock_repo,
                rules_config=self.mock_yaml,
                sentiment_analysis=self.mock_nlp,
                config=self.config,
            )

        self.assertEqual(cm.exception.status_code, 408)

    async def test_create_comment_invalid_timestamp(self):
        """
        Test case when the timestamp is invalid/cannot be decrypted
        """
        self.mock_yaml.getProjectNameFromFeature.return_value = "project1"

        with patch("survey_logic.comments.get_encryption_from_project_name") as mock_crypto, \
        self.assertRaises(HTTPException) as cm:
            mock_crypto.return_value = self.encryption
            await logic.create_comment(
                self.feature_url,
                self.rating,
                self.comment,
                self.user_id,
                self.user_id,
                "jdsodkcvhjsdknv",
                sqlite_repo=self.mock_repo,
                rules_config=self.mock_yaml,
                sentiment_analysis=self.mock_nlp,
                config=self.config,
            )

        self.assertEqual(cm.exception.status_code, 422)

    