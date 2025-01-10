import unittest
from app import app

class TestFlaskGetParksRoute(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True

    def test_get_parks_route_known_location(self):
        # Test case for parks data retrieval known loaction
        response = self.app.post('/api/parks/get_parks', json={
            'latitude': -37.81847,
            'longitude': 144.947109
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue('features' in response.json)
        feature_types = [x['properties']['type'] for x in response.json['features']]
        self.assertTrue('user_location' in feature_types)

    def test_get_parks_route_null_location(self):
        # Test case for parks data retrieval null location
        response = self.app.post('/api/parks/get_parks', json={
            'latitude': None,
            'longitude': None
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue('features' in response.json)
        feature_types = [x['properties']['type'] for x in response.json['features']]
        self.assertFalse('user_location' in feature_types)

if __name__ == '__main__':
    unittest.main()
