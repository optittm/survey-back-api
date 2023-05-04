
import unittest
import sqlite3
from models.project import Project
from repository.db_warehouse import DBWarehouse

from repository.db_warehouse import DBWarehouse


class TestDBWarehouse(unittest.TestCase):

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

    def setUp(self):
        self.warehouse = DBWarehouse(self.db_name)

    def tearDown(self):
        self.warehouse.close()

    def test_get_project_avg_rating(self):
        project_a = Project(id=1, name='Project A')
        project_b = Project(id=2, name='Project B')

        self.assertAlmostEqual(self.warehouse.get_project_avg_rating(project_a.id), 4.0)
        self.assertAlmostEqual(self.warehouse.get_project_avg_rating(project_b.id), 2.0)

    def test_get_feature_avg_rating(self):
        project_a = Project(id=1, name='Project A')

        self.assertAlmostEqual(self.warehouse.get_feature_avg_rating(project_a.id, 'http://example.com/feature1'), 4.0)
        self.assertAlmostEqual(self.warehouse.get_feature_avg_rating(project_a.id, 'http://example.com/feature2'), 4.0)

    def test_get_number_of_comment(self):
        project_a = Project(id=1, name='Project A')
        project_b = Project(id=2, name='Project B')

        self.assertEqual(self.warehouse.get_number_of_comment(project_a.id), 3)
        self.assertEqual(self.warehouse.get_number_of_comment(project_b.id), 1)

    def test_get_number_of_display(self):
        project_a = Project(id=1, name='Project A')
        project_b = Project(id=2, name='Project B')

        self.assertEqual(self.warehouse.get_number_of_display(project_a.id), 2)
        self.assertEqual(self.warehouse.get_number_of_display(project_b.id), 1)