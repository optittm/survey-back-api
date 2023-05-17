import sqlite3
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from models.comment import Comment, CommentPostBody
from models.display import Display
from models.project import Project, ProjectEncryption
from repository.sqlite_repository import SQLiteRepository


class TestSQLiteRepository(unittest.IsolatedAsyncioTestCase):

    
    @classmethod
    def setUpClass(cls):
        cls.db_name = 'tests/mocks/test_db'
        cls.conn = sqlite3.connect(cls.db_name)
        cls.cursor = cls.conn.cursor()

        # create test tables
        cls.cursor.execute('''
            CREATE TABLE Project (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );
        ''')

        cls.cursor.execute('''
            CREATE TABLE Comment (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                feature_url TEXT NOT NULL,
                rating INTEGER NOT NULL,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY(project_id) REFERENCES Project(id)
            );
        ''')

        cls.cursor.execute('''
            CREATE TABLE Display (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY(project_id) REFERENCES Project(id)
            );
        ''')

        cls.cursor.execute('''
            INSERT INTO Project (id, name) VALUES
            (1, 'Project A'),
            (2, 'Project B');
        ''')

        cls.cursor.execute('''
            INSERT INTO Comment (id, project_id, feature_url, rating, timestamp) VALUES
            (1, 1, 'http://example.com/feature1', 3, '2023-05-01 10:00:00'),
            (2, 1, 'http://example.com/feature1', 5, '2023-05-01 11:00:00'),
            (3, 1, 'http://example.com/feature2', 4, '2023-05-01 12:00:00'),
            (4, 2, 'http://example.com/feature1', 2, '2023-05-01 13:00:00');
        ''')

        cls.cursor.execute('''
            INSERT INTO Display (id, project_id, timestamp) VALUES
            (1, 1, '2023-05-01 10:00:00'),
            (2, 1, '2023-05-01 11:00:00'),
            (3, 2, '2023-05-01 12:00:00');
        ''')

        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.cursor.execute('DROP TABLE Comment')
        cls.cursor.execute('DROP TABLE Display')
        cls.cursor.execute('DROP TABLE Project')

    async def asyncSetUp(self):
        self.config = {"survey_db": self.db_name}
        self.repository = SQLiteRepository(self.config)
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

    async def test_read_comments(self):
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

    async def test_create_display(self):
        user_id = 123
        timestamp = "03/24/23 12:00:00"
        timestamp_dt = datetime.strptime(timestamp, "%m/%d/%y %H:%M:%S").isoformat()
        self.repository.create_project = AsyncMock(
            return_value=Project(id=1, name="test_project")
        )
        Display.insert = AsyncMock(return_value=5)
        Project.filter = AsyncMock(return_value=[Project(id=1, name="test_project")])
        result = await self.repository.create_display(
            feature_url=self.comment_body.feature_url,
            user_id=user_id,
            timestamp=timestamp_dt,
            project_name=self.project_name,
        )

        Display.insert.assert_called_once()
        self.assertEqual(
            result,
            Display(
                id=5,
                project_id=1,
                feature_url=self.comment_body.feature_url,
                user_id=user_id,
                timestamp=timestamp_dt
            ),
        )

        
    def test_get_project_avg_rating(self):
        project_a = Project(id=1, name='Project A')
        project_b = Project(id=2, name='Project B')

        self.assertAlmostEqual(self.repository.get_project_avg_rating(project_a.id), 4.0)
        self.assertAlmostEqual(self.repository.get_project_avg_rating(project_b.id), 2.0)

    def test_get_feature_avg_rating(self):
        project_a = Project(id=1, name='Project A')

        self.assertAlmostEqual(self.repository.get_feature_avg_rating(project_a.id, 'http://example.com/feature1'), 4.0)
        self.assertAlmostEqual(self.repository.get_feature_avg_rating(project_a.id, 'http://example.com/feature2'), 4.0)

    def test_get_number_of_comment(self):
        project_a = Project(id=1, name='Project A')
        project_b = Project(id=2, name='Project B')

        self.assertEqual(self.repository.get_number_of_comment(project_a.id), 3)
        self.assertEqual(self.repository.get_number_of_comment(project_b.id), 1)

    def test_get_number_of_display(self):
        project_a = Project(id=1, name='Project A')
        project_b = Project(id=2, name='Project B')

        self.assertEqual(self.repository.get_number_of_display(project_a.id), 2)
        self.assertEqual(self.repository.get_number_of_display(project_b.id), 1)