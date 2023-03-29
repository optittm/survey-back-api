import unittest
from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from models.comment import Comment, CommentPostBody

# TODO: fix tests
class TestCommentsRoutes(unittest.TestCase):

    def setUp(self):
        self.comment_cookie = CommentPostBody(
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment"
        )

    def test_create_comment_endpoint(self):
        app = FastAPI()
        client = TestClient(app)

        response = client.post(
            "/comments",
            json={"comment_cookie": self.comment_cookie.dict()}
        )
        assert response.status_code == 201
        assert response.json() == {"id": 1}

    def test_get_all_comments_endpoint(self):
        app = FastAPI()
        client = TestClient(app)

        Comment.all = AsyncMock(return_value=[Comment(id=1), Comment(id=2)])
        response = client.get("/comments")
        assert response.status_code == 200
        assert response.json() == [{"id": 1}, {"id": 2}]
        Comment.all.assert_called_once()
