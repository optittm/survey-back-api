from collections import namedtuple
import sqlite3
import unittest

from datetime import datetime
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from models.comment import Comment, CommentPostBody
from models.display import Display
from models.project import Project, ProjectEncryption
from models.views import NumberDisplayByProject
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
            user_id="123",
        )
           
    async def test_create_comment(self):
        timestamp = "03/24/23 12:00:00"
        timestamp_dt = datetime.strptime(timestamp, "%m/%d/%y %H:%M:%S").isoformat()
        self.repository.create_project = AsyncMock(
            return_value=Project(id=1, name="test_project")
        )
        Comment.insert = AsyncMock(return_value=5)
        Project.filter = AsyncMock(return_value=[Project(id=1, name="test_project")])
        result = await self.repository.create_comment(
            feature_url=self.comment_body.feature_url,
            rating=self.comment_body.rating,
            comment=self.comment_body.comment,
            user_id=self.comment_body.user_id,
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
                user_id=self.comment_body.user_id,
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

        with patch('models.comment.Comment.filter') as mock_filter:
            mock_filter.return_value = [comment_a]
            Comment.feature_url = AsyncMock(return_value=comment_a.feature_url)
            result = await self.repository.read_comments(feature_url="http://test.com/test")
            mock_filter.assert_called_once_with(Comment.feature_url == "http://test.com/test")
            self.assertEqual(result, [comment_a])

    async def test_read_comments_with_project_name(self):
        comment_a = Comment(
            id=1,
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        project = Project(
            id=1,
            name="project1",
        )
        with patch('models.comment.Comment.filter') as mock_filter:
            mock_filter.return_value = [comment_a]
            Comment.project_id = AsyncMock(return_value=comment_a.project_id)
            result = await self.repository.read_comments(project_name=project.name)
            mock_filter.assert_called_once_with(Comment.project_id == 1)
            self.assertEqual(result, [comment_a])

    async def test_read_comments_with_timestamp_start(self):
        comment_a = Comment(
            id=1,
            project_id=1,
            user_id="1",
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com/test",
            rating=4,
            comment="test",
        )
        timestamp_start = datetime(2023, 5, 1).isoformat()

        with patch('models.comment.Comment.filter') as mock_filter:
            mock_filter.return_value = [comment_a]
            Comment.timestamp = PropertyMock(return_value=comment_a.timestamp)
            result = await self.repository.read_comments(timestamp_start=timestamp_start)
            mock_filter.assert_called_once_with(Comment.timestamp >= timestamp_start)
            self.assertEqual(result, [comment_a])
            
    async def test_create_display(self):
        user_id = "123"
        timestamp_dt = datetime.now().isoformat()
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

    def test_get_number_of_display_with_existing_project_id(self):
        # Mocking the Session object and query method
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mockMeta = namedtuple("__metadata__", ["database"])
        mockdb = namedtuple("database", ["engine"])
        
        mock_metadata = mockMeta(database=mockdb(engine=Mock()))
        mock_metadata.database.engine.keys.return_value = yield [0, 1]
        Comment.__metadata__ = mock_metadata
        
        # Mocking the result of the query
        mock_result = [(10,)]  # Assuming the result is [(10,)]
        mock_query.all.return_value = mock_result

        # Patching the Session class to return the mock_session
        with patch('sqlalchemy.orm.Session', return_value=mock_session):
            project_id = 1
            result = self.repository.get_number_of_display(project_id)
            expected_result = 10
            self.assertEqual(result, expected_result)

            # Assert that the query was called with the correct filter
            mock_query.filter.assert_called_once_with(NumberDisplayByProject.project_id == project_id)

    def test_get_number_of_display_with_non_existing_project_id(self):
        # Mocking the Session object and query method
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mockMeta = namedtuple("__metadata__", ["database"])
        mockdb = namedtuple("database", ["engine"])
        
        mock_metadata = mockMeta(database=mockdb(engine=Mock()))
        mock_metadata.database.engine.keys.return_value = yield [0, 1]
        Comment.__metadata__ = mock_metadata

        # Patching the Session class to return the mock_session
        with patch('sqlalchemy.orm.Session', return_value=mock_session):
            project_id = 2
            result = self.repository.get_number_of_display(project_id)
            expected_result = 0
            self.assertEqual(result, expected_result)

            # Assert that the query was called with the correct filter
            mock_query.filter.assert_called_once_with(NumberDisplayByProject.project_id == project_id)


    def test_get_number_of_comment_with_existing_project_id(self):
        # Mocking the Session object and query method
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mockMeta = namedtuple("__metadata__", ["database"])
        mockdb = namedtuple("database", ["engine"])
        
        mock_metadata = mockMeta(database=mockdb(engine=Mock()))
        mock_metadata.database.engine.keys.return_value = yield [0, 1]
        Comment.__metadata__ = mock_metadata
        
        # Mocking the result of the query
        mock_result = [(10,)]  # Assuming the result is [(10,)]
        mock_query.all.return_value = mock_result

        # Patching the Session class to return the mock_session
        with patch('sqlalchemy.orm.Session', return_value=mock_session):
            project_id = 1
            result = self.repository.get_number_of_comment(project_id)
            expected_result = 10
            self.assertEqual(result, expected_result)

            # Assert that the query was called with the correct filter
            mock_query.filter.assert_called_once_with(NumberDisplayByProject.project_id == project_id)

    def test_get_number_of_comment_with_non_existing_project_id(self):
        # Mocking the Session object and query method
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mockMeta = namedtuple("__metadata__", ["database"])
        mockdb = namedtuple("database", ["engine"])
        
        mock_metadata = mockMeta(database=mockdb(engine=Mock()))
        mock_metadata.database.engine.keys.return_value = yield [0, 1]
        Comment.__metadata__ = mock_metadata

        # Patching the Session class to return the mock_session
        with patch('sqlalchemy.orm.Session', return_value=mock_session):
            project_id = 2
            result = self.repository.get_number_of_comment(project_id)
            expected_result = 0
            self.assertEqual(result, expected_result)

            # Assert that the query was called with the correct filter
            mock_query.filter.assert_called_once_with(NumberDisplayByProject.project_id == project_id)

    def test_get_feature_avg_rating_with_existing_project_id(self):
        # Mocking the Session object and query method
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mockMeta = namedtuple("__metadata__", ["database"])
        mockdb = namedtuple("database", ["engine"])
        
        mock_metadata = mockMeta(database=mockdb(engine=Mock()))
        mock_metadata.database.engine.keys.return_value = yield [0, 1]
        Comment.__metadata__ = mock_metadata
        
        # Mocking the result of the query
        mock_result = [(10,)]  # Assuming the result is [(10,)]
        mock_query.all.return_value = mock_result

        # Patching the Session class to return the mock_session
        with patch('sqlalchemy.orm.Session', return_value=mock_session):
            project_id = 1
            result = self.repository.get_feature_avg_rating(project_id)
            expected_result = 10
            self.assertEqual(result, expected_result)

            # Assert that the query was called with the correct filter
            mock_query.filter.assert_called_once_with(NumberDisplayByProject.project_id == project_id)

    def test_get_feature_avg_rating_with_non_existing_project_id(self):
        # Mocking the Session object and query method
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mockMeta = namedtuple("__metadata__", ["database"])
        mockdb = namedtuple("database", ["engine"])
        
        mock_metadata = mockMeta(database=mockdb(engine=Mock()))
        mock_metadata.database.engine.keys.return_value = yield [0, 1]
        Comment.__metadata__ = mock_metadata

        # Patching the Session class to return the mock_session
        with patch('sqlalchemy.orm.Session', return_value=mock_session):
            project_id = 2
            result = self.repository.get_feature_avg_rating(project_id)
            expected_result = 0
            self.assertEqual(result, expected_result)

            # Assert that the query was called with the correct filter
            mock_query.filter.assert_called_once_with(NumberDisplayByProject.project_id == project_id)

    def test_get_project_avg_rating_with_existing_project_id(self):
        # Mocking the Session object and query method
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mockMeta = namedtuple("__metadata__", ["database"])
        mockdb = namedtuple("database", ["engine"])
        
        mock_metadata = mockMeta(database=mockdb(engine=Mock()))
        mock_metadata.database.engine.keys.return_value = yield [0, 1]
        Comment.__metadata__ = mock_metadata
        
        # Mocking the result of the query
        mock_result = [(10,)]  # Assuming the result is [(10,)]
        mock_query.all.return_value = mock_result

        # Patching the Session class to return the mock_session
        with patch('sqlalchemy.orm.Session', return_value=mock_session):
            project_id = 1
            result = self.repository.get_project_avg_rating(project_id)
            expected_result = 10
            self.assertEqual(result, expected_result)

            # Assert that the query was called with the correct filter
            mock_query.filter.assert_called_once_with(NumberDisplayByProject.project_id == project_id)

    def test_get_project_avg_rating_with_non_existing_project_id(self):
        # Mocking the Session object and query method
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mockMeta = namedtuple("__metadata__", ["database"])
        mockdb = namedtuple("database", ["engine"])
        
        mock_metadata = mockMeta(database=mockdb(engine=Mock()))
        mock_metadata.database.engine.keys.return_value = yield [0, 1]
        Comment.__metadata__ = mock_metadata

        # Patching the Session class to return the mock_session
        with patch('sqlalchemy.orm.Session', return_value=mock_session):
            project_id = 2
            result = self.repository.get_project_avg_rating(project_id)
            expected_result = 0
            self.assertEqual(result, expected_result)

            # Assert that the query was called with the correct filter
            mock_query.filter.assert_called_once_with(NumberDisplayByProject.project_id == project_id)