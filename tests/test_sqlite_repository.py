import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from models.comment import Comment, CommentPostBody
from models.project import Project, ProjectEncryption
from repository.sqlite_repository import SQLiteRepository


class TestSQLiteRepository(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.repository = SQLiteRepository()
        self.project_name = "test_project"
        self.comment_body = CommentPostBody(
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment",
        )

    async def test_create_comment(self):
        user_id = 123
        timestamp = "03/24/23 12:00:00"
        timestamp_dt = datetime.strptime(timestamp, "%m/%d/%y %H:%M:%S").isoformat()
        self.repository.create_project = AsyncMock(
            return_value=Project(id=1, name="test_project")
        )
        Comment.insert = AsyncMock(return_value=5)
        Project.filter = AsyncMock(return_value=[Project(id=1, name="test_project")])
        result = await self.repository.create_comment(
            comment_body=self.comment_body,
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
                feature_url=self.comment_body.feature_url,
                user_id=user_id,
                timestamp=timestamp_dt,
                rating=self.comment_body.rating,
                comment=self.comment_body.comment,
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

    async def test_read_comments_with_no_filters(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        result = await self.repository.read_comments()

        self.assertEqual(result, [comment_a, comment_b])
        Comment.all.assert_called_once()


    async def test_read_comments_with_feature_url_filter(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        
        feature_url = "http://test.com/test2"

        result = await self.repository.read_comments(feature_url=feature_url)

        self.assertEqual(result, [comment_b])
        Comment.all.assert_called_once()

    async def test_read_comments_with_invalide_feature_url_filter(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        
        feature_url = "http://test.com/test3"

        result = await self.repository.read_comments(feature_url=feature_url)

        self.assertEqual(result, [])
        Comment.all.assert_called_once()

    async def test_read_comments_with_project_name(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        comment_c = Comment(
            project_id=2,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        filtered_comments = await self.repository.read_comments(project_name="project1")

        self.assertEqual(filtered_comments, [comment_a,comment_b])
        Comment.all.assert_called_once()


    async def test_read_comments_with_user_id_filter(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        
        user_id = "2"

        result = await self.repository.read_comments(user_id=user_id)

        self.assertEqual(result, [comment_b])
        Comment.all.assert_called_once()

    async def test_read_comments_with_unknown_user_id_filter(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        
        user_id = "4"

        result = await self.repository.read_comments(user_id=user_id)

        self.assertEqual(result, [])
        Comment.all.assert_called_once()

    async def test_read_comments_with_timestampbegin_filter(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=(datetime.now() - timedelta(days=2)).isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        
        timestampbegin = (datetime.now() - timedelta(days=1)).isoformat()

        result = await self.repository.read_comments(timestampbegin=timestampbegin)

        self.assertEqual(result, [comment_b])
        Comment.all.assert_called_once()

    async def test_read_comments_with_timestampend_filter(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=(datetime.now() - timedelta(days=2)).isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        
        timestampend = datetime.now().isoformat()

        result = await self.repository.read_comments(timestampend=timestampend)

        self.assertEqual(result, [comment_a, comment_b])
        Comment.all.assert_called_once()

    async def test_read_comments_with_search_query_filter(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        
        search_query = "test2"

        result = await self.repository.read_comments(search_query=search_query)

        self.assertEqual(result, [comment_b])
        Comment.all.assert_called_once()

    async def test_read_comments_with_invalide_search_query_filter(self):
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=1,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b])
        
        search_query = "essai"

        result = await self.repository.read_comments(search_query=search_query)

        self.assertEqual(result, [])
        Comment.all.assert_called_once()

    async def test_read_comments_with_multiple_filters(self):
        # Create comments
        comment_a = Comment(
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        comment_b = Comment(
            project_id=2,
            user_id="2",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test2",
            rating=4,
            comment="test2",
        )
        comment_c = Comment(
            project_id=3,
            user_id="3",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test3",
            rating=4,
            comment="test3",
        )
        Comment.all = AsyncMock(return_value=[comment_a, comment_b, comment_c])

        # Set filters
        project_name = "project2"
        feature_url = "http://test.com/test2"
        user_id = "2"

        # Call method
        filtered_comments = await self.repository.read_comments(
            project_name=project_name, feature_url=feature_url, user_id=user_id
        )

        # Assert results
        self.assertEqual(filtered_comments, [comment_b])
        Comment.all.assert_called_once()
