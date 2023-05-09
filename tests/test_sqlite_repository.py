import unittest

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
import uuid

from models.comment import Comment, CommentPostBody
from models.project import Project, ProjectEncryption
from repository.sqlite_repository import SQLiteRepository

class TestSQLiteRepository(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.repository = SQLiteRepository()
        self.project_name = "test_project"


    
    async def test_create_comment(self):
        comment_body = CommentPostBody(
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment",
        )
        user_id = 123
        timestamp = "03/24/23 12:00:00"
        timestamp_dt = datetime.strptime(timestamp, "%m/%d/%y %H:%M:%S").isoformat()
        self.repository.create_project = AsyncMock(
            return_value=Project(id=1, name="test_project")
        )
        Comment.insert = AsyncMock(return_value=5)
        Project.filter = AsyncMock(return_value=[Project(id=1, name="test_project")])
        result = await self.repository.create_comment(
            comment_body=comment_body,
            user_id=user_id,
            timestamp=timestamp_dt,
            project_name=self.project_name,
        )
        Comment.insert.assert_called_once()
        self.assertEqual(
            result,
            Comment(
                id=5,
                project_id=1,
                feature_url=comment_body.feature_url,
                user_id=user_id,
                timestamp=timestamp_dt,
                rating=comment_body.rating,
                comment=comment_body.comment,
            ),
        )
        
    async def test_create_project(self):
        project = Project(name=self.project_name)
        Project.filter = AsyncMock(return_value=[])
        Project.insert = AsyncMock(return_value=5)
        ProjectEncryption.insert = AsyncMock()

        result = await self.repository.create_project(project)

        self.assertEqual(result, Project(id=5, name=self.project_name))
        Project.insert.assert_called_once()
        ProjectEncryption.insert.assert_called_once()

    async def test_create_project_already_exists(self):
        project = Project(name=self.project_name)
        db_project = Project(id=5, name=self.project_name)
        Project.filter = AsyncMock(return_value=[db_project])
        Project.insert = AsyncMock()
        ProjectEncryption.insert = AsyncMock()

        result = await self.repository.create_project(project)

        self.assertEqual(result, db_project)
        Project.insert.assert_not_called()
        ProjectEncryption.insert.assert_not_called()

    
    async def test_get_all_comments(self):
        comment_a = Comment(
            id=1,
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            id=2,
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=5,
            comment="test2",
        )

        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        result = await self.repository.get_all_comments()
        self.assertEqual(result, [comment_a, comment_b])

        Comment.all.assert_called_once()

    async def test_read_comments(self):
        comment_a = Comment(
            id=1,
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            id=2,
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=5,
            comment="test2",
        )

        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        result = await self.repository.read_comments()
        self.assertEqual(result, [comment_a, comment_b])

        Comment.all.assert_called_once()

    async def test_read_comments_with_feature_url(self):
        comment_a = Comment(
            id=1,
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            id=2,
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=5,
            comment="test2",
        )

        with patch("repository.sqlite_repository.SQLiteRepository.get_all_comments") as mock:
            mock.return_value =[comment_a, comment_b]
            result = await self.repository.read_comments(feature_url=comment_a.feature_url)
        
        self.assertEqual(result, [comment_a])

        Comment.all.assert_called_once()