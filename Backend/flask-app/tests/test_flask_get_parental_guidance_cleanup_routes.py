import unittest
from unittest.mock import patch
from app import app

class TestFlaskParentalGuidanceRoute(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True

    @patch('route_handlers.parent.get_parental_guidance.assess_activity')
    @patch('route_handlers.parent.get_parental_guidance.create_spider_chart')
    def test_get_parental_guidance_basic(self, mock_create_spider_chart, mock_assess_activity):
        # Mock the internal functions to return simple dummy values
        mock_assess_activity.return_value = {
            'status': {'meets_criteria': True, 'outdoor_play': False, 'screen_time': True},
            'recommendations': "Recommendations based on the mock assessment.",
            'scores': [50, 75, 100, 60]
        }
        mock_create_spider_chart.return_value = 'static/spider_chart_mock.png'

        # Example input data
        data = {
            "outdoorTime": 2,
            "outdoorFrequency": 3,
            "screenTime": 1,
            "peFrequency": 4,
            "physicalActivityDays": 3,
            "walkOrCycle": "often"
        }

        # Send a POST request to /api/parent/get_parental_guidance
        response = self.app.post('/api/parent/get_parental_guidance', json=data)
        
        # Basic checks
        self.assertEqual(response.status_code, 200)
        self.assertIn("feedback", response.json)
        self.assertIn("detailedAssessment", response.json)
        self.assertIn("plotImageUrl", response.json)

        # Validate mock outputs are used correctly
        self.assertEqual(response.json['plotImageUrl'], '/static/spider_chart_mock.png')
        self.assertEqual(response.json['feedback']['meets_criteria'], True)

    def test_cleanup_spider_chart_png_noop(self):
        # Test /api/parent/cleanup_spider_chart_png route with no actual file
        response = self.app.post('/api/parent/cleanup_spider_chart_png', json={"filename": "/static/images/parent/spider_chart_dummy.png"})
        self.assertEqual(response.status_code, 204)

if __name__ == '__main__':
    unittest.main()
