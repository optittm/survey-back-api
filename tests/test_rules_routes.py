import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from main import app
from models.rule import Rule
from repository.yaml_rule_repository import YamlRulesRepository


class TestRulesRoutes(unittest.TestCase):
    """
    Tests for the /rules endpoints
    """

    def setUp(self):
        self.client = TestClient(app)
        self.mock_repo = Mock(spec=YamlRulesRepository)

    def mockRulesConfig(self, rule: Rule, timestamp: datetime):
        
        self.mock_repo.getRuleFromFeature.return_value = rule

        with app.container.rules_config.override(self.mock_repo):
            response = self.client.get(
                "/rules",
                params={'featureUrl': '/test'},
                cookies={
                    "user_id": "1",
                    "timestamp": timestamp
                }
            )

        return response

    def test_show_modal(self):
        timestamp = datetime(2023, 2, 4).timestamp()
        rule = Rule(
            feature_url='/test',
            ratio=0.6,
            delay_before_reanswer=1,
            delay_to_answer=3,
            is_active=True)
        
        with patch('routes.rules.random.random') as mock_random:
            mock_random.return_value = 0.4
            response = self.mockRulesConfig(rule, str(timestamp))
            
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), True)
        self.mock_repo.getRuleFromFeature.assert_called_once()

    def test_not_show_modal_not_active(self):
        timestamp = datetime(2023, 2, 4).timestamp()
        rule = Rule(
            feature_url='/test',
            ratio=0.6,
            delay_before_reanswer=1,
            delay_to_answer=3,
            is_active=False)
        
        with patch('routes.rules.random.random') as mock_random:
            mock_random.return_value = 0.4
            response = self.mockRulesConfig(rule, str(timestamp))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), False)
        self.mock_repo.getRuleFromFeature.assert_called_once()

    def test_not_show_modal_not_overDelay(self):
        timestamp = datetime.now().timestamp() + timedelta(days=60).microseconds
        rule = Rule(
            feature_url='/test',
            ratio=0.6,
            delay_before_reanswer=1,
            delay_to_answer=3,
            is_active=True)
        
        with patch('routes.rules.random.random') as mock_random:
            mock_random.return_value = 0.4
            response = self.mockRulesConfig(rule, str(timestamp))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), False)
        self.mock_repo.getRuleFromFeature.assert_called_once()

    def test_not_show_modal_notWithinRatio(self):
        timestamp = datetime(2023, 2, 4).timestamp()
        rule = Rule(
            feature_url='/test',
            ratio=0.6,
            delay_before_reanswer=1,
            delay_to_answer=3,
            is_active=False)
        
        with patch('routes.rules.random.random') as mock_random:
            mock_random.return_value = 1
            response = self.mockRulesConfig(rule, str(timestamp))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), False)
        self.mock_repo.getRuleFromFeature.assert_called_once()
        
