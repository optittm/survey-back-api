from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from models.comment import Comment, CommentGetBody, CommentPostBody
from models.rule import Rule
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from main import app
from utils.encryption import Encryption


class TestCommentsRoutes(unittest.TestCase):
    """
    Tests for the /comments endpoints

    For reference of testing with dependency_injector, see:
    https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.html#tests
    """

    def setUp(self):
        self.client = TestClient(app)
        self.route = "/api/v1/comments"

        self.user_id = "3"
        self.comment_body = CommentPostBody(
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment",
            user_id=self.user_id,
        )
        self.datetime = datetime.now()
        self.mock_yaml = Mock(spec=YamlRulesRepository)
        self.mock_rule = Mock(spec=Rule)
        self.mock_repo = Mock(spec=SQLiteRepository)
        self.crypt_key = "rg3ENcA7oBCxtxvJ1kk4oAXLizePSnGqPykRi4hvWqY="
        self.encryption = Encryption(self.crypt_key)

    def test_create_comment_endpoint(self):
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
        )
        self.mock_yaml.getProjectNameFromFeature.return_value = project_name
        self.mock_repo.get_project_by_name.return_value = Mock()
        project_encryption_mock = Mock()
        project_encryption_mock.encryption_key = self.crypt_key
        self.mock_repo.get_encryption_by_project_id.return_value = (
            project_encryption_mock
        )
        self.mock_rule.delay_to_answer = 5
        self.mock_yaml.getRuleFromFeature.return_value = self.mock_rule
        self.mock_repo.create_comment.return_value = return_comment

        with app.container.sqlite_repo.override(
            self.mock_repo
        ), app.container.rules_config.override(
            self.mock_yaml
        ), app.container.config.override(
            {"use_fingerprint": False}
        ):
            response = self.client.post(
                self.route,
                # Somehow CommentPostBody isn't json serializable when passed to this parameter, so passing it as dict instead
                json=self.comment_body.dict(),
                cookies={
                    "user_id": cookie_user_id,
                    "timestamp": self.encryption.encrypt(
                        str(self.datetime.timestamp())
                    ),
                },
            )

        self.assertEqual(response.status_code, 201)
        # response.json() returns a dict, so comparing it against the comment as a dict
        compare_comment = return_comment.dict()
        self.assertEqual(response.json(), compare_comment)
        self.mock_yaml.getProjectNameFromFeature.assert_called_once()
        self.mock_repo.create_comment.assert_called_once_with(
            self.comment_body.feature_url,
            self.comment_body.rating,
            self.comment_body.comment,
            cookie_user_id,
            self.datetime.isoformat(),
            project_name,
        )

    def test_create_comment_endpoint_fingerprint(self):
        """
        Same as test_create_comment_endpoint but checks if the user_id is taken from the body instead of the cookie
        """
        project_name = "project1"
        cookie_user_id = "123"
        return_comment = Comment(
            id=1,
            project_id=2,
            user_id=self.comment_body.user_id,
            timestamp=self.datetime.isoformat(),
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment",
        )
        self.mock_yaml.getProjectNameFromFeature.return_value = project_name
        self.mock_repo.get_project_by_name.return_value = Mock()
        project_encryption_mock = Mock()
        project_encryption_mock.encryption_key = self.crypt_key
        self.mock_repo.get_encryption_by_project_id.return_value = (
            project_encryption_mock
        )
        self.mock_rule.delay_to_answer = 5
        self.mock_yaml.getRuleFromFeature.return_value = self.mock_rule
        self.mock_repo.create_comment.return_value = return_comment

        with app.container.sqlite_repo.override(
            self.mock_repo
        ), app.container.rules_config.override(
            self.mock_yaml
        ), app.container.config.override(
            {"use_fingerprint": True}
        ):
            response = self.client.post(
                self.route,
                # Somehow CommentPostBody isn't json serializable when passed to this parameter, so passing it as dict instead
                json=self.comment_body.dict(),
                cookies={
                    "user_id": cookie_user_id,
                    "timestamp": self.encryption.encrypt(
                        str(self.datetime.timestamp())
                    ),
                },
            )

        self.assertEqual(response.status_code, 201)
        # response.json() returns a dict, so comparing it against the comment as a dict
        compare_comment = return_comment.dict()
        self.assertEqual(response.json(), compare_comment)
        self.mock_yaml.getProjectNameFromFeature.assert_called_once()
        self.mock_repo.create_comment.assert_called_once_with(
            self.comment_body.feature_url,
            self.comment_body.rating,
            self.comment_body.comment,
            self.comment_body.user_id,
            self.datetime.isoformat(),
            project_name,
        )

    def test_create_comment_endpoint_unknown_feature(self):
        """
        Test case when feature/project is not found in the YAML config
        """
        self.mock_yaml.getProjectNameFromFeature.return_value = None

        with app.container.rules_config.override(self.mock_yaml):
            response = self.client.post(
                self.route,
                # Somehow CommentPostBody isn't json serializable when passed to this parameter, so passing it as dict instead
                json=self.comment_body.dict(),
                cookies={
                    "user_id": self.user_id,
                    "timestamp": self.encryption.encrypt(
                        str(self.datetime.timestamp())
                    ),
                },
            )
        self.assertEqual(response.status_code, 404)

    def test_create_comment_endpoint_no_cookies(self):
        """
        Test case when cookies are missing
        """
        self.mock_yaml.getProjectNameFromFeature.return_value = "project1"

        with app.container.rules_config.override(self.mock_yaml):
            response = self.client.post(
                self.route,
                # Somehow CommentPostBody isn't json serializable when passed to this parameter, so passing it as dict instead
                json=self.comment_body.dict(),
            )
        self.assertEqual(response.status_code, 422)

    def test_create_comment_endpoint_delay_elapsed(self):
        """
        Test case when the delay to submit a comment has elapsed
        """
        self.mock_yaml.getProjectNameFromFeature.return_value = "project1"
        self.mock_repo.get_project_by_name.return_value = Mock()
        project_encryption_mock = Mock()
        project_encryption_mock.encryption_key = self.crypt_key
        self.mock_repo.get_encryption_by_project_id.return_value = (
            project_encryption_mock
        )
        self.mock_rule.delay_to_answer = 5
        self.mock_yaml.getRuleFromFeature.return_value = self.mock_rule
        elpased_datetime = self.datetime - timedelta(minutes=10)

        with app.container.sqlite_repo.override(
            self.mock_repo
        ), app.container.rules_config.override(self.mock_yaml):
            response = self.client.post(
                self.route,
                # Somehow CommentPostBody isn't json serializable when passed to this parameter, so passing it as dict instead
                json=self.comment_body.dict(),
                cookies={
                    "user_id": "3",
                    "timestamp": self.encryption.encrypt(
                        str(elpased_datetime.timestamp())
                    ),
                },
            )

        self.assertEqual(response.status_code, 408)

    def test_create_comment_endpoint_invalid_timestamp(self):
        """
        Test case when the timestamp is invalid/cannot be decrypted
        """
        self.mock_yaml.getProjectNameFromFeature.return_value = "project1"
        self.mock_repo.get_project_by_name.return_value = Mock()
        project_encryption_mock = Mock()
        project_encryption_mock.encryption_key = self.crypt_key
        self.mock_repo.get_encryption_by_project_id.return_value = (
            project_encryption_mock
        )

        with app.container.sqlite_repo.override(
            self.mock_repo
        ), app.container.rules_config.override(self.mock_yaml):
            response = self.client.post(
                self.route,
                # Somehow CommentPostBody isn't json serializable when passed to this parameter, so passing it as dict instead
                json=self.comment_body.dict(),
                cookies={
                    "user_id": "3",
                    "timestamp": "jdsodkcvhjsdknv",
                },
            )

        self.assertEqual(response.status_code, 422)

    def test_create_comment_endpoint_invalid_feature(self):
        self.comment_body.feature_url = "http://tes[t.com/test"
        response = self.client.post(
            self.route,
            # Somehow CommentPostBody isn't json serializable when passed to this parameter, so passing it as dict instead
            json=self.comment_body.dict(),
            cookies={
                "user_id": "3",
                "timestamp": "jdsodkcvhjsdknv",
            },
        )
        self.assertEqual(response.status_code, 422)
