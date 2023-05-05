import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, Mock
from main import app
from repository.sqlite_repository import SQLiteRepository


class TestProjectRating(unittest.TestCase):

    def setUp(self):
        self.prefix = "/api/v1"
        self.client = TestClient(app)
        self.mock_repo = MagicMock(spec=SQLiteRepository)
        self.app = self.client.app

    def test_get_project_rating(self):
        # Arrange
        project_id = 1
        expected_rating = 4.5
        self.mock_repo.get_project_avg_rating.return_value = expected_rating

        with app.container.sqlite_repo.override(self.mock_repo):
                
            # Act
            response = self.client.get(self.prefix + f"/project/{project_id}/rating")

            # Assert
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"id": project_id, "rating": expected_rating})
            self.mock_repo.get_project_avg_rating.assert_called_once_with(project_id)

    def tearDown(self):
        self.app.dependency_overrides.clear()