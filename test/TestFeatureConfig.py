
import unittest

from models.Rule import Rule
from repository.FeatureConfig import FeatureConfig


class TestGetRuleFromFeature(unittest.TestCase):
    def test_existing_feature(self):
        feature_url = '/test2'
        rule = FeatureConfig.getRuleFromFeature(feature_url)
        self.assertIsInstance(rule, Rule)
        self.assertEqual(rule.feature_url, feature_url)
        self.assertEqual(rule.ratio, 0.4)
        self.assertEqual(rule.delay_before_reanswer, 1)
        self.assertEqual(rule.delay_to_answer, 5)
        self.assertEqual(rule.is_active, True)
    
    def test_nonexisting_feature(self):
        feature_url = '/invalid'
        rule = FeatureConfig.getRuleFromFeature(feature_url)
        self.assertIsNone(rule)

class TestGetProjectNameFromFeature(unittest.TestCase):
    def test_existing_feature(self):
        feature_url = '/test1'
        project_name = FeatureConfig.getProjectNameFromFeature(feature_url)
        self.assertEqual(project_name, 'project1')

    def test_nonexisting_feature(self):
        feature_url = '/invalid'
        project_name = FeatureConfig.getProjectNameFromFeature(feature_url)
        self.assertIsNone(project_name)

    def test_multiple_projects(self):
        feature_url = '/test2'
        project_name = FeatureConfig.getProjectNameFromFeature(feature_url)
        self.assertEqual(project_name, 'project2')

    def test_multiple_rules(self):
        feature_url = '/test'
        project_name = FeatureConfig.getProjectNameFromFeature(feature_url)
        self.assertEqual(project_name, 'project1')


if __name__ == '__main__':
    unittest.main()
