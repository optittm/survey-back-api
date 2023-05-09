import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from models.project import Project

from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository
from main import app

class TestProjectRoute(unittest.TestCase):

    def setUp(self):
        self.prefix = "/api/v1"
        self.client = TestClient(app)    
        self.mock_sqlite_repo = MagicMock(spec=SQLiteRepository)
        self.mock_yaml_repo = MagicMock(spec=YamlRulesRepository)
        self.app = self.client.app

    def test_get_projects(self):
        expected_output = [
            {"id": 1, "name": "project1"},
            {"id": 2, "name": "project2"},
        ]

        # Create mock SQLiteRepository instance with a get_project_by_name method that returns a dummy project object
        self.mock_sqlite_repo.get_project_by_name.side_effect = lambda name: Project(
            id = next((p["id"] for p in expected_output if p["name"] == name), None),
            name = name
        )

        # Create mock YamlRulesRepository instance with a getProjectNames method that returns a list of project names
        self.mock_yaml_repo.getProjectNames.return_value = ["project1", "project2"]

        # Replace Container.sqlite_repo and Container.rules_config with the mock repositories
        with app.container.sqlite_repo.override(self.mock_sqlite_repo),\
            app.container.rules_config.override(self.mock_yaml_repo):
            # Make request to /projects endpoint
            response = self.client.get(self.prefix + "/projects")

        # Check that the response is valid and matches the expected output
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_output)