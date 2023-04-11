import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from models.comment import Comment, CommentPostBody
from models.project import Project
from repository.sqlite_repository import SQLiteRepository

# TODO: fix tests
class TestSQLiteRepository(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.repository = SQLiteRepository()
        self.project_name = "test_project"
        self.comment_cookie = CommentPostBody(
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment"
        )

    async def test_create_comment(self):
        user_id = 123
        timestamp = "03/24/23 12:00:00"
        timestamp_dt = datetime.strptime(timestamp, '%m/%d/%y %H:%M:%S').isoformat()
        self.repository.create_project = AsyncMock(return_value=Project(id=1, name="test_project"))
        Comment.insert = AsyncMock(return_value=5)
        Project.filter = AsyncMock(return_value=[Project(id=1, name="test_project")])
        result = await self.repository.create_comment(
            commentcookie=self.comment_cookie,
            user_id=user_id,
            timestamp=timestamp_dt,
            project_name=self.project_name,
        )

        Comment.insert.assert_called_once()
        self.assertEqual(result, Comment(
            id=5,
            project_id=1,
            feature_url=self.comment_cookie.feature_url,
            user_id=user_id,
            timestamp=timestamp_dt,
            rating=self.comment_cookie.rating,
            comment=self.comment_cookie.comment,
        ))

    async def test_read_comments(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test"
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test2"
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        result = await self.repository.read_comments()
        self.assertEqual(result, [comment_a, comment_b])
        Comment.all.assert_called_once()

    async def test_create_project(self):
        project = Project(name=self.project_name)
        Project.insert = AsyncMock(return_value=5)
        result = await self.repository.create_project(project)
        self.assertEqual(result, Project(id=5, name="test_project"))
        Project.insert.assert_called_once()
