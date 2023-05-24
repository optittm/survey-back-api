import unittest
from unittest.mock import MagicMock, patch
from xml.sax.handler import feature_validation
from fastapi.testclient import TestClient
from main import app
from models.project import Project
from models.rule import Rule
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository


class TestProjectRoute(unittest.TestCase):
    
    def setUp(self):
        self.prefix = "/api/v1"
        self.client = TestClient(app)
        # Disable OAuth security for these tests
        app.container.config.secret_key.from_value("")

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
            response = self.client.get(self.prefix + "/project/1/avg_feature_rating")

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
            response = self.client.get(self.prefix + "/project/1/avg_feature_rating")

            # Check that the response is valid and matches the expected output
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"detail" :{"id": 1, "Error": "Project not found"}})

    def test_get_project_rules(self):
        expected_output = [
            {
                "feature_url": "http://example.com/feature1",
                "ratio": 0.5,
                "delay_before_reanswer": 30,
                "delay_to_answer": 10,
                "is_active": True
            }
        ]
        mock_project = Project(id=1, name="project1")

        # Create a mock SQLiteRepository instance with a get_project_by_id method that returns the mock project
        self.mock_sqlite_repo.get_project_by_id.return_value = mock_project
        
        # Create a mock YamlRulesRepository instance with a getProjectNames method that returns a list with the mock project name
        self.mock_yaml_repo.getProjectNames.return_value = [mock_project.name]

        # Create a mock YamlRulesRepository instance with a getFeatureUrlsFromProjectName method that returns a list with the feature url
        self.mock_yaml_repo.getFeatureUrlsFromProjectName.return_value = ["http://example.com/feature1"]

        # Create a mock YamlRulesRepository instance with a getRuleFromFeature method that returns a Rule
        self.mock_yaml_repo.getRuleFromFeature.return_value = Rule(
            feature_url=expected_output[0]["feature_url"],
            ratio=expected_output[0]["ratio"],
            delay_before_reanswer=expected_output[0]["delay_before_reanswer"],
            delay_to_answer=expected_output[0]["delay_to_answer"],
            is_active=expected_output[0]["is_active"]
        )
            
        with app.container.sqlite_repo.override(self.mock_sqlite_repo),\
            app.container.rules_config.override(self.mock_yaml_repo):
            # Make request to /projects/{id}/rules endpoint
            response = self.client.get(self.prefix + "/projects/1/rules")

        # Check that the response is valid and matches the expected output
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_output)

    def test_get_project_rules_with_wrong_id(self):


        # Create a mock SQLiteRepository instance with a get_project_by_id method that returns the mock project
        self.mock_sqlite_repo.get_project_by_id.return_value = None
            
        with app.container.sqlite_repo.override(self.mock_sqlite_repo),\
            app.container.rules_config.override(self.mock_yaml_repo):
            # Make request to /projects/{id}/rules endpoint
            response = self.client.get(self.prefix + "/projects/1/rules")

        # Check that the response is valid and matches the expected output
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail" :{"id": 1, "Error": "Project not found"}})

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
            self.assertEqual(response.json(), {"detail" :{"id": 2, "Error": "Project not found"}})
            self.mock_sqlite_repo.get_project_avg_rating.assert_not_called()

    def tearDown(self):
        self.app.dependency_overrides.clear()
 