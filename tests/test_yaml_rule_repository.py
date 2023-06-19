import unittest
from unittest.mock import MagicMock, patch

from models.rule import Rule
from repository.yaml_rule_repository import YamlRulesRepository


class TestGetRulesFromProjectName(unittest.TestCase):
    def setUp(self):
        self.data = {
            "projects": {
                "project1": {
                    "rules": [
                        {
                            "feature_url": "/test1",
                            "ratio": 0.5,
                            "delay_before_reanswer": 10,
                            "delay_to_answer": 2,
                            "is_active": True,
                        },
                        {
                            "feature_url": "/test",
                            "ratio": 0.8,
                            "delay_before_reanswer": 20,
                            "delay_to_answer": 3,
                            "is_active": False,
                        },
                    ]
                },
                "project2": {
                    "rules": [
                        {
                            "feature_url": "/test2",
                            "ratio": 0.4,
                            "delay_before_reanswer": 30,
                            "delay_to_answer": 5,
                            "is_active": True,
                        }
                    ]
                },
            }
        }

    def test_existing_project(self):
        project_name = "project2"
        rules = YamlRulesRepository.getRulesFromProjectName(project_name)
        self.assertIsInstance(rules, list)
        self.assertIsInstance(rules[0], Rule)
        
        self.assertEqual(rules[0].ratio, 0.4)
        self.assertEqual(rules[0].delay_before_reanswer, 30)
        self.assertEqual(rules[0].delay_to_answer, 5)
        self.assertEqual(rules[0].is_active, True)

    def test_noexisting_project(self):
        project_name = "projectInvalid"
        rules = YamlRulesRepository.getRulesFromProjectName(project_name)
        self.assertIsNone(rules)

    def test_regex_matching(self):
        project_name = "project2"
        with patch(
            "repository.yaml_rule_repository.YamlRulesRepository._getRulesConfig",
            return_value=self.data,
        ):
            rules = YamlRulesRepository.getRulesFromProjectName(project_name)

        self.assertIsInstance(rules[0], Rule)
        self.assertEqual(rules[0].ratio, 0.4)
        self.assertEqual(rules[0].delay_before_reanswer, 30)
        self.assertEqual(rules[0].delay_to_answer, 5)
        self.assertEqual(rules[0].is_active, True)

    def test_regex_non_matching(self):
        project_name = "projectInvalid"
        with patch(
            "repository.yaml_rule_repository.YamlRulesRepository._getRulesConfig",
            return_value=self.data,
        ):
            rules = YamlRulesRepository.getRulesFromProjectName(project_name)
        self.assertIsNone(rules)


class TestGetRuleFromFeature(unittest.TestCase):
    def setUp(self):
        YamlRulesRepository._RULES_CONFIG_FILE = "tests/mocks/test_rules.yaml"
        self.data = {
            "projects": {
                "project1": {
                    "rules": [
                        {
                            "feature_url": "/test1",
                            "ratio": 0.5,
                            "delay_before_reanswer": 10,
                            "delay_to_answer": 2,
                            "is_active": True,
                        },
                        {
                            "feature_url": "/test",
                            "ratio": 0.8,
                            "delay_before_reanswer": 20,
                            "delay_to_answer": 3,
                            "is_active": False,
                        },
                    ]
                },
                "project2": {
                    "rules": [
                        {
                            "feature_url": "/test2",
                            "ratio": 0.4,
                            "delay_before_reanswer": 30,
                            "delay_to_answer": 5,
                            "is_active": True,
                        }
                    ]
                },
            }
        }

    def test_existing_feature(self):
        feature_url = "https://www.example.com/test2"
        rule = YamlRulesRepository.getRuleFromFeature(feature_url)
        self.assertIsInstance(rule, Rule)
        self.assertEqual(rule.feature_url, feature_url)
        self.assertEqual(rule.ratio, 0.4)
        self.assertEqual(rule.delay_before_reanswer, 30)
        self.assertEqual(rule.delay_to_answer, 5)
        self.assertEqual(rule.is_active, True)

    def test_nonexisting_feature(self):
        feature_url = "https://www.example.com/invalid"
        rule = YamlRulesRepository.getRuleFromFeature(feature_url)
        self.assertIsNone(rule)

    def test_regex_matching(self):
        feature_url = "https://www.example.com/test2"
        with patch(
            "repository.yaml_rule_repository.YamlRulesRepository._getRulesConfig",
            return_value=self.data,
        ):
            rule = YamlRulesRepository.getRuleFromFeature(feature_url)

        self.assertIsInstance(rule, Rule)
        self.assertEqual(rule.feature_url, "/test2")
        self.assertEqual(rule.ratio, 0.4)
        self.assertEqual(rule.delay_before_reanswer, 30)
        self.assertEqual(rule.delay_to_answer, 5)
        self.assertEqual(rule.is_active, True)

    def test_regex_non_matching(self):
        feature_url = "https://www.example.com/nonmatching"
        with patch(
            "repository.yaml_rule_repository.YamlRulesRepository._getRulesConfig",
            return_value=self.data,
        ):
            rule = YamlRulesRepository.getRuleFromFeature(feature_url)

        self.assertIsNone(rule)


class TestGetProjectNameFromFeature(unittest.TestCase):
    def setUp(self):
        YamlRulesRepository._RULES_CONFIG_FILE = "tests/mocks/test_rules.yaml"

        self.data = {
            "projects": {
                "project1": {
                    "rules": [
                        {
                            "feature_url": "/test1",
                            "ratio": 0.5,
                            "delay_before_reanswer": 10,
                            "delay_to_answer": 2,
                            "is_active": True,
                        },
                        {
                            "feature_url": "/test",
                            "ratio": 0.8,
                            "delay_before_reanswer": 20,
                            "delay_to_answer": 3,
                            "is_active": False,
                        },
                    ]
                },
                "project2": {
                    "rules": [
                        {
                            "feature_url": "/test2",
                            "ratio": 0.4,
                            "delay_before_reanswer": 30,
                            "delay_to_answer": 5,
                            "is_active": True,
                        }
                    ]
                },
            }
        }

    def test_existing_feature(self):
        feature_url = "https://www.example.com/test1"
        project_name = YamlRulesRepository.getProjectNameFromFeature(feature_url)
        self.assertEqual(project_name, "project1")

    def test_nonexisting_feature(self):
        feature_url = "https://www.example.com/invalid"
        project_name = YamlRulesRepository.getProjectNameFromFeature(feature_url)
        self.assertIsNone(project_name)

    def test_multiple_projects(self):
        feature_url = "https://www.example.com/test2"
        project_name = YamlRulesRepository.getProjectNameFromFeature(feature_url)
        self.assertEqual(project_name, "project2")

    def test_multiple_rules(self):
        feature_url = "https://www.example.com/test"
        project_name = YamlRulesRepository.getProjectNameFromFeature(feature_url)
        self.assertEqual(project_name, "project1")


class TestGetFeatureUrlsFromProjectName(unittest.TestCase):
    def setUp(self):
        self.data = {
            "projects": {
                "Project 1": {
                    "rules": [
                        {"feature_url": "http://example.com/feature1"},
                        {"feature_url": "http://example.com/feature2"},
                    ]
                },
                "Project 2": {
                    "rules": [
                        {"feature_url": "http://example.com/feature3"},
                        {"feature_url": "http://example.com/feature4"},
                    ]
                },
            }
        }

        self.yaml_repo = YamlRulesRepository()

    def test_getFeatureUrlsFromProjectName_returns_list_of_feature_urls(self):
        # Arrange
        name = "Project 1"

        with patch(
            "repository.yaml_rule_repository.YamlRulesRepository._getRulesConfig",
            return_value=self.data,
        ):
            # Act
            feature_urls = self.yaml_repo.getFeatureUrlsFromProjectName(name)

        # Assert
        self.assertEqual(
            sorted(feature_urls),
            sorted(["http://example.com/feature1", "http://example.com/feature2"]),
        )

    def test_getFeatureUrlsFromProjectName_returns_none_if_project_name_not_found(self):
        # Arrange
        name = "Project 3"

        with patch(
            "repository.yaml_rule_repository.YamlRulesRepository._getRulesConfig",
            return_value=self.data,
        ):
            # Act
            feature_urls = self.yaml_repo.getFeatureUrlsFromProjectName(name)

        # Assert
        self.assertIsNone(feature_urls)

    def test_getFeatureUrlsFromProjectName_returns_empty_set_if_project_has_no_rules(
        self,
    ):
        # Arrange
        name = "Project 1"
        data = {
            "projects": {
                "Project 1": {"rules": []},
                "Project 2": {
                    "rules": [
                        {"feature_url": "http://example.com/feature3"},
                        {"feature_url": "http://example.com/feature4"},
                    ]
                },
            }
        }
        self.yaml_repo._getRulesConfig = MagicMock(return_value=data)

        with patch(
            "repository.yaml_rule_repository.YamlRulesRepository._getRulesConfig",
            return_value=data,
        ):
            # Act
            feature_urls = self.yaml_repo.getFeatureUrlsFromProjectName(name)

        # Assert
        self.assertEqual(feature_urls, [])


if __name__ == "__main__":
    unittest.main()
