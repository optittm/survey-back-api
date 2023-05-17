

import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
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

    def test_get_projects_feature_rating(self):
        # Define the expected output
        expected_output = [
            {"url": "http://example.com/feature1", "rating": 4.5},
            {"url": "http://example.com/feature2", "rating": 3.2},
        ]

        # Create a mock project
        mock_project = Project(id=1, name="project1")

        # Create a mock SQLiteRepository instance with a get_project_by_id method that returns the mock project
        self.mock_sqlite_repo.get_project_by_id.return_value = mock_project

        # Create a mock SQLiteRepository instance with a get_feature_avg_rating method that returns the expected ratings
        self.mock_sqlite_repo.get_feature_avg_rating.side_effect = [4.5, 3.2]

        # Create a mock YamlRulesRepository instance with a getProjectNames method that returns a list with the mock project name
        self.mock_yaml_repo.getFeatureUrlsFromProjectName.return_value = ["http://example.com/feature1", "http://example.com/feature2"]

        # Create a mock YamlRulesRepository instance with a getFeatureUrlsFromProjectName method that returns a list with the feature_url
        self.mock_yaml_repo.getProjectNames.return_value = ["project1"]

        # Replace Container.sqlite_repo and Container.rules_config with the mock repositories
        with app.container.sqlite_repo.override(self.mock_sqlite_repo),\
                app.container.rules_config.override(self.mock_yaml_repo):

            # Make request to /projects/{id}/feature_rating endpoint
            response = self.client.get(self.prefix + "/projects/1/avg_feature_rating")

            # Check that the response is valid and matches the expected output
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_output)

    def test_get_projects_feature_rating_with_wrong_id(self):

        # Create a mock SQLiteRepository instance with a get_project_by_id method that returns None
        self.mock_sqlite_repo.get_project_by_id.return_value = None

        # Replace Container.sqlite_repo and Container.rules_config with the mock repositories
        with app.container.sqlite_repo.override(self.mock_sqlite_repo),\
                app.container.rules_config.override(self.mock_yaml_repo):

            # Make request to /projects/{id}/feature_rating endpoint
            response = self.client.get(self.prefix + "/projects/1/avg_feature_rating")

            # Check that the response is valid and matches the expected output
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"id": 1, "Error": "Project not found"})