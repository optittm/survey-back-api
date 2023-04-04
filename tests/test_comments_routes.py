from datetime import datetime
import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from models.comment import Comment, CommentPostBody
from repository.sqlite_repository import SQLiteRepository
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

        with app.container.sqlite_repo.override(mock_repo):
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
        mock_repo.create_comment.assert_called_once_with(self.comment_body, user_id, self.timestamp_str, "test.com")
        

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
        comment_b = Comment(
            id=2,
            project_id=1,
            user_id="2",
            timestamp=self.timestamp,
            feature_url="http://test.com/test",
            rating=4,
            comment="test2"
        )
        mock_repo = Mock(spec=SQLiteRepository)
        mock_repo.read_comments.return_value = [comment_a, comment_b]

        with app.container.sqlite_repo.override(mock_repo):
            response = self.client.get("/comments")

        self.assertEqual(response.status_code, 200)
        
        comment_A = comment_a.dict()
        comment_A["timestamp"] = self.timestamp.isoformat()
        comment_B = comment_b.dict()
        comment_B["timestamp"] = self.timestamp.isoformat()
        self.assertEqual(response.json(), [comment_A, comment_B])
        mock_repo.read_comments.assert_called_once()
