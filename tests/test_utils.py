import unittest
from datetime import datetime
from unittest.mock import AsyncMock

from models.comment import Comment, CommentGetBody
from models.project import Project
from repository.sqlite_repository import SQLiteRepository
from utils.formatter import comment_to_comment_get_body


class TestUtils(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.sqliterepo = AsyncMock(spec=SQLiteRepository)
        self.comment = Comment(
            id=1,
            project_id=1,
            user_id=123,
            timestamp=datetime.now(),
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment"
        )

    async def test_comment_to_comment_get_body(self):
        self.sqliterepo.get_project_by_id = AsyncMock(return_value=Project(id=1, name="test_project"))
        result = await comment_to_comment_get_body(self.comment, sqliterepo=self.sqliterepo)
        self.assertEqual(result, CommentGetBody(
            id=1,
            project_name="test_project",
            user_id=123,
            timestamp=self.comment.timestamp,
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment",
        ))
        self.sqliterepo.get_project_by_id.assert_called_once_with(1)
