import unittest
from unittest.mock import MagicMock
from fastapi import HTTPException

from survey_logic import projects as logic
from models.project import Project
from models.rule import Rule
from repository.sqlite_repository import SQLiteRepository
from repository.yaml_rule_repository import YamlRulesRepository


class TestProjects(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_sqlite_repo = MagicMock(spec=SQLiteRepository)
        self.mock_yaml_repo = MagicMock(spec=YamlRulesRepository)

    async def test_get_all_projects(self):
        expected_output = [
            {"id": 1, "name": "project1"},
            {"id": 2, "name": "project2"},
        ]

        # Create mock SQLiteRepository instance with a get_project_by_name method that returns a dummy project object
        self.mock_sqlite_repo.get_project_by_name.side_effect = lambda name: Project(
            id=next((p["id"] for p in expected_output if p["name"] == name), None),
            name=name,
        )

        # Create mock YamlRulesRepository instance with a getProjectNames method that returns a list of project names
        self.mock_yaml_repo.getProjectNames.return_value = ["project1", "project2"]
        
        response = await logic.get_all_projects(
            sqlite_repo=self.mock_sqlite_repo,
            yaml_repo=self.mock_yaml_repo,
        )

        self.assertEqual(response, expected_output)

    async def test_get_projects_feature_rating(self):
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
        self.mock_yaml_repo.getFeatureUrlsFromProjectName.return_value = [
            "http://example.com/feature1",
            "http://example.com/feature2",
        ]

        # Create a mock YamlRulesRepository instance with a getFeatureUrlsFromProjectName method that returns a list with the feature_url
        self.mock_yaml_repo.getProjectNames.return_value = ["project1"]
        
        response = await logic.get_avg_rating_by_feature_from_project_id(
            1,
            sqlite_repo=self.mock_sqlite_repo,
            yaml_repo=self.mock_yaml_repo,
        )

        self.assertEqual(response, expected_output)

    async def test_get_projects_feature_rating_with_wrong_id(self):
        # Create a mock SQLiteRepository instance with a get_project_by_id method that returns None
        self.mock_sqlite_repo.get_project_by_id.return_value = None
        
        with self.assertRaises(HTTPException) as cm:
            response = await logic.get_avg_rating_by_feature_from_project_id(
                1,
                sqlite_repo=self.mock_sqlite_repo,
                yaml_repo=self.mock_yaml_repo,
            )
        
        self.assertEqual(cm.exception.status_code, 404)

    async def test_get_project_rules(self):
        expected_output = [
            Rule(
                feature_url="http://example.com/feature1",
                ratio=0.5,
                delay_before_reanswer=30,
                delay_to_answer=10,
                is_active=True,
            )
        ]
        mock_project = Project(id=1, name="project1")

        # Create a mock SQLiteRepository instance with a get_project_by_id method that returns the mock project
        self.mock_sqlite_repo.get_project_by_id.return_value = mock_project

        # Create a mock YamlRulesRepository instance with a getProjectNames method that returns a list with the mock project name
        self.mock_yaml_repo.getProjectNames.return_value = [mock_project.name]

        # Create a mock YamlRulesRepository instance with a getRulesFromProjectName method that returns a Rule
        self.mock_yaml_repo.getRulesFromProjectName.return_value = [
            Rule(
                feature_url=expected_output[0].feature_url,
                ratio=expected_output[0].ratio,
                delay_before_reanswer=expected_output[0].delay_before_reanswer,
                delay_to_answer=expected_output[0].delay_to_answer,
                is_active=expected_output[0].is_active,
            )
        ]
        
        response = await logic.get_rules_from_project_id(
            1,
            sqlite_repo=self.mock_sqlite_repo,
            yaml_repo=self.mock_yaml_repo,
        )

        self.assertEqual(response, expected_output)

    async def test_get_project_rules_with_wrong_id(self):
        # Create a mock SQLiteRepository instance with a get_project_by_id method that returns the mock project
        self.mock_sqlite_repo.get_project_by_id.return_value = None
        
        with self.assertRaises(HTTPException) as cm:
            response = await logic.get_rules_from_project_id(
                1,
                sqlite_repo=self.mock_sqlite_repo,
                yaml_repo=self.mock_yaml_repo,
            )

        self.assertEqual(cm.exception.status_code, 404)

    async def test_get_project_rating(self):
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
        
        response = await logic.get_avg_project_rating_from_id(
            project_id,
            sqlite_repo=self.mock_sqlite_repo,
            yaml_repo=self.mock_yaml_repo,
        )

        # Assert
        self.assertEqual(response, expected_rating)
        self.mock_sqlite_repo.get_project_avg_rating.assert_called_once_with(project_id)

    async def test_get_project_rating_wrong_id(self):
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
        
        with self.assertRaises(HTTPException) as cm:
            response = await logic.get_avg_project_rating_from_id(
                2,
                sqlite_repo=self.mock_sqlite_repo,
                yaml_repo=self.mock_yaml_repo,
            )

        # Assert
        self.assertEqual(cm.exception.status_code, 404)
        self.mock_sqlite_repo.get_project_avg_rating.assert_not_called()
