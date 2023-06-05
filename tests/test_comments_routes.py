from datetime import datetime, timedelta
import unittest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from math import ceil

from models.comment import Comment, CommentPostBody
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
        # Disable OAuth security for these tests
        app.container.config.secret_key.from_value("")

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

        app.container.config.use_fingerprint.from_value(False)
        with app.container.sqlite_repo.override(
            self.mock_repo
        ), app.container.rules_config.override(self.mock_yaml):
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

        app.container.config.use_fingerprint.from_value(True)
        with app.container.sqlite_repo.override(
            self.mock_repo
        ), app.container.rules_config.override(self.mock_yaml):
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

    def test_read_comments_pagination(self):
        comments = [
            Comment(
                id=1,
                project_id=1,
                user_id="1",
                timestamp=datetime.now().isoformat(),
                feature_url="http://test.com/test",
                rating=4,
                comment="test",
            ),
            Comment(
                id=2,
                project_id=1,
                user_id="2",
                timestamp=datetime.now().isoformat(),
                feature_url="http://test.com/test",
                rating=5,
                comment="test2",
            ),
            Comment(
                id=3,
                project_id=1,
                user_id="3",
                timestamp=datetime.now().isoformat(),
                feature_url="http://test.com/test",
                rating=3,
                comment="test3",
            ),
            Comment(
                id=4,
                project_id=1,
                user_id="4",
                timestamp=datetime.now().isoformat(),
                feature_url="http://test.com/test",
                rating=2,
                comment="test4",
            ),
            Comment(
                id=5,
                project_id=1,
                user_id="4",
                timestamp=datetime.now().isoformat(),
                feature_url="http://test.com/test",
                rating=2,
                comment="test4",
            ),
        ]

        self.mock_repo.read_comments.return_value = comments
        format_mock = AsyncMock(side_effect=lambda x: x)
        page_size = 2
        expected_total_pages = ceil(len(comments) / page_size)

        # Test first page
        expected_results = comments[:page_size]
        expected_total = len(comments)
        expected_page = 1
        expected_page_size = page_size
        expected_next_page = f"/comments?page={expected_page + 1}&pageSize={expected_page_size}"
        expected_prev_page = None

        with app.container.sqlite_repo.override(self.mock_repo), \
        patch('routes.comments.comment_to_comment_get_body', format_mock):
            response = self.client.get(self.route, params={
                "page": 1,
                "page_size": page_size,
            })
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["results"], expected_results)
        self.assertEqual(result["total_comments"], expected_total)
        self.assertEqual(result["total_pages"], expected_total_pages)
        self.assertEqual(result["page"], expected_page)
        self.assertEqual(result["page_size"], expected_page_size)
        self.assertEqual(result["next_page"], expected_next_page)
        self.assertEqual(result["prev_page"], expected_prev_page)

        # Test second page
        expected_results = comments[page_size : page_size * 2]
        expected_total = len(comments)
        expected_page = 2
        expected_page_size = page_size
        expected_next_page = f"/comments?page={expected_page + 1}&pageSize={expected_page_size}"
        expected_prev_page = f"/comments?page={expected_page - 1}&pageSize={expected_page_size}"

        with app.container.sqlite_repo.override(self.mock_repo), \
        patch('routes.comments.comment_to_comment_get_body', format_mock):
            response = self.client.get(self.route, params={
                "page": 2,
                "page_size": page_size,
            })
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["results"], expected_results)
        self.assertEqual(result["total_comments"], expected_total)
        self.assertEqual(result["total_pages"], expected_total_pages)
        self.assertEqual(result["page"], expected_page)
        self.assertEqual(result["page_size"], expected_page_size)
        self.assertEqual(result["next_page"], expected_next_page)
        self.assertEqual(result["prev_page"], expected_prev_page)

        # Test last page
        expected_results = comments[page_size * 2 :]
        expected_total = len(comments)
        expected_page = 3
        expected_page_size = page_size
        expected_next_page = None
        expected_prev_page = f"/comments?page={expected_page - 1}&pageSize={expected_page_size}"

        with app.container.sqlite_repo.override(self.mock_repo), \
        patch('routes.comments.comment_to_comment_get_body', format_mock):
            response = self.client.get(self.route, params={
                "page": 3,
                "page_size": page_size,
            })
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["results"], expected_results)
        self.assertEqual(result["total_comments"], expected_total)
        self.assertEqual(result["total_pages"], expected_total_pages)
        self.assertEqual(result["page"], expected_page)
        self.assertEqual(result["page_size"], expected_page_size)
        self.assertEqual(result["next_page"], expected_next_page)
        self.assertEqual(result["prev_page"], expected_prev_page)