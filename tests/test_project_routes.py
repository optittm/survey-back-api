import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from models.project import Project
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository


class TestProjectRoute(unittest.TestCase):

    def setUp(self):
        self.prefix = "/api/v1"
        self.client = TestClient(app)
        self.mock_sqlite_repo = MagicMock(spec=SQLiteRepository)
        self.mock_yaml_repo = MagicMock(spec=YamlRulesRepository)
        self.app = self.client.app

    def test_get_project_rating(self):
        # Arrange

        project_id = 1
        project_name = "test_name"
        expected_rating = 4.5
        mock_project = MagicMock(spec=Project)
        mock_project.id = project_id
        mock_project.name = project_name
        mock_project.rating = expected_rating
        self.mock_sqlite_repo.get_project_avg_rating.return_value = expected_rating
        self.mock_yaml_repo.getProjectNames.return_value = [project_name]
        self.mock_sqlite_repo.get_project_by_id.return_value = mock_project

        with app.container.sqlite_repo.override(self.mock_sqlite_repo),\
            app.container.rules_config.override(self.mock_yaml_repo):
                
            # Act
            response = self.client.get(self.prefix + f"/project/{project_id}/avg_rating")

            # Assert
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"id": project_id, "rating": expected_rating})
            self.mock_sqlite_repo.get_project_avg_rating.assert_called_once_with(project_id)

    def test_get_project_rating_wrong_id(self):
        # Arrange

        project_id = 1
        project_name = "test_name"
        expected_rating = 4.5
        mock_project = MagicMock(spec=Project)
        mock_project.id = project_id
        mock_project.name = project_name
        mock_project.rating = expected_rating
        self.mock_sqlite_repo.get_project_avg_rating.return_value = expected_rating
        self.mock_yaml_repo.getProjectNames.return_value = []
        self.mock_sqlite_repo.get_project_by_id.return_value = None

        with app.container.sqlite_repo.override(self.mock_sqlite_repo),\
            app.container.rules_config.override(self.mock_yaml_repo):
                
            # Act
            response = self.client.get(self.prefix + f"/project/{2}/avg_rating")

            # Assert
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"id": 2, "Error": "Project not found"})
            self.mock_sqlite_repo.get_project_avg_rating.assert_not_called()

    def tearDown(self):
        self.app.dependency_overrides.clear()