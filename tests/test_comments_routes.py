from datetime import datetime
import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from models.comment import Comment, CommentGetBody, CommentPostBody
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from main import app

class TestCommentsRoutes(unittest.TestCase):
    """
    Tests for the /comments endpoints

    For reference of testing with dependency_injector, see:
    https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.html#tests
    """

    def setUp(self):
        self.client = TestClient(app)

        self.comment_body = CommentPostBody(
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment"
        )
        self.timestamp = datetime.now()
        self.timestamp_str = self.timestamp.strftime("%m/%d/%y %H:%M:%S")

    def test_create_comment_endpoint(self):
        user_id = "3"
        project_name = "project1"
        return_comment = Comment(
            id=1,
            project_id=2,
            user_id=user_id,
            timestamp=self.timestamp,
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment"
        )
        mock_repo = Mock(spec=SQLiteRepository)
        mock_repo.create_comment.return_value = return_comment

        mock_yaml = Mock(spec=YamlRulesRepository)
        mock_yaml.getProjectNameFromFeature.return_value = project_name

        with app.container.sqlite_repo.override(mock_repo), app.container.rules_config.override(mock_yaml):
            response = self.client.post(
                "/comments",
                # Somehow CommentPostBody isn't json serializable when passed to this parameter, so passing it as dict instead
                json=self.comment_body.dict(),
                cookies={
                    "user_id": user_id,
                    "timestamp": self.timestamp_str
                }
            )

        self.assertEqual(response.status_code, 201)
        # response.json() returns a dict, so comparing it against the comment as a dict
        compare_comment = return_comment.dict()
        compare_comment["timestamp"] = self.timestamp.isoformat()
        self.assertEqual(response.json(), compare_comment)
        mock_yaml.getProjectNameFromFeature.assert_called_once()
        mock_repo.create_comment.assert_called_once_with(self.comment_body, user_id, self.timestamp_str, project_name)
        
    def test_create_comment_endpoint_fail(self):
        """
        Test case when feature/project is not found in the YAML config
        """
        user_id = "3"
        comment = Comment(
            id=1,
            project_id=2,
            user_id=user_id,
            timestamp=self.timestamp,
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment"
        )
        mock_yaml = Mock(spec=YamlRulesRepository)
        mock_yaml.getProjectNameFromFeature.return_value = None

        with app.container.rules_config.override(mock_yaml):
            response = self.client.post(
                "/comments",
                # Somehow CommentPostBody isn't json serializable when passed to this parameter, so passing it as dict instead
                json=self.comment_body.dict(),
                cookies={
                    "user_id": user_id,
                    "timestamp": self.timestamp_str
                }
            )
        self.assertEqual(response.status_code, 404)

    def test_get_all_comments_endpoint(self):
        comment_a = Comment(
            id=1,
            project_id=1,
            user_id="1",
            timestamp=self.timestamp,
            feature_url="http://test.com/test",
            rating=4,
            comment="test"
        )

        comment_abis = CommentGetBody(
            id=1,
            project_name="project1",
            user_id="1",
            timestamp=self.timestamp,
            feature_url="http://test.com/test",
            rating=4,
            comment="test"
        )

        mock_repo = Mock(spec=SQLiteRepository)
        mock_repo.read_comments.return_value = [comment_a]

        with patch('routes.comments.comment_to_comment_get_body') as mock_method:
            with app.container.sqlite_repo.override(mock_repo):
                mock_method.return_value=comment_abis
                response = self.client.get("/comments")

        self.assertEqual(response.status_code, 200)
        
        comment_A = comment_abis.dict()
        comment_A["timestamp"] = self.timestamp.isoformat()

        self.assertEqual(response.json(), [comment_A])
        mock_repo.read_comments.assert_called_once()
