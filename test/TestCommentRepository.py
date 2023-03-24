import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from models.comment import Comment
from models.commentcookie import CommentCookie
from models.project import Project
from repository.DBrepository import CommentRepository


class TestCommentRepository(unittest.TestCase):

    async def asyncSetUp(self):
        self.repository = CommentRepository()
        self.project_name = "test_project"
        self.comment_cookie = CommentCookie(
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment"
        )

    async def test_create_comment(self):
        user_id = 123
        timestamp = "03/24/23 12:00:00"

        self.repository.create_project = AsyncMock()
        Comment.create = AsyncMock()
        new_comment = MagicMock()
        Comment.insert = AsyncMock()
        Comment.save = AsyncMock()
        Comment.filter = AsyncMock(return_value=[Project(id=1)])
        Comment.create.return_value = new_comment
        result = await self.repository.create_comment(
            comment_cookie=self.comment_cookie,
            user_id=user_id,
            timestamp=timestamp,
            project_name=self.project_name,
        )

        self.assertEqual(result, new_comment)
        Comment.create.assert_called_once_with(
            project_id=1,
            feature_url=self.comment_cookie.feature_url,
            user_id=user_id,
            timestamp=datetime.strptime(timestamp, '%m/%d/%y %H:%M:%S'),
            rating=self.comment_cookie.rating,
            comment=self.comment_cookie.comment,
        )
        Comment.insert.assert_called_once()
        Comment.save.assert_called_once()

    async def test_read_comments(self):
        Comment.all = AsyncMock(return_value=[Comment(id=1), Comment(id=2)])
        result = await self.repository.read_comments()
        self.assertEqual(result, [Comment(id=1), Comment(id=2)])
        Comment.all.assert_called_once()

    async def test_create_project(self):
        project = Project(name=self.project_name)
        Project.create = AsyncMock(return_value=Project(id=1))
        Project.insert = AsyncMock()
        Project.save = AsyncMock()
        result = await self.repository.create_project(project)
        self.assertEqual(result, Project(id=1))
        Project.create.assert_called_once_with(name=self.project_name)
        Project.insert.assert_called_once()
        Project.save.assert_called_once()

    async def test_create_comment_endpoint(self):
        app = FastAPI()
        client = TestClient(app)

        response = client.post(
            "/comments",
            json={"comment_cookie": self.comment_cookie.dict()}
        )
        assert response.status_code == 201
        assert response.json() == {"id": 1}

    async def test_get_all_comments_endpoint(self):
        app = FastAPI()
        client = TestClient(app)

        Comment.all = AsyncMock(return_value=[Comment(id=1), Comment(id=2)])
        response = client.get("/comments")
        assert response.status_code == 200
        assert response.json() == [{"id": 1}, {"id": 2}]
        Comment.all.assert_called_once()
