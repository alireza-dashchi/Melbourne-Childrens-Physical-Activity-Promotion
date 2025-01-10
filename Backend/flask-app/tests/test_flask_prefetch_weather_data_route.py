import unittest
from app import app

class TestFlaskPrefetchWeatherDataRoute(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True

    def test_prefetch_weather_data_default(self):
        # Test the /api/parks/prefetch_weather_data route with no percentage specified (default to 100%)
        response = self.app.post('/api/parks/prefetch_weather_data', json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "Prefetch started"})

    def test_prefetch_weather_data_specific_percentage(self):
        # Test the /api/parks/prefetch_weather_data route with a specific percentage
        response = self.app.post('/api/parks/prefetch_weather_data', json={"percentage": 50})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "Prefetch started"})

    def test_prefetch_weather_data_invalid_percentage(self):
        # Test the /api/parks/prefetch_weather_data route with an invalid percentage (negative value)
        response = self.app.post('/api/parks/prefetch_weather_data', json={"percentage": -10})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "Prefetch started"})  # Check if it still starts

if __name__ == '__main__':
    unittest.main()
