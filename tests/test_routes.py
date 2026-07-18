import unittest
from app.routes import app

class TestRoutes(unittest.TestCase):
    def setUp(self):
        # Create a test client for the Flask app
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        # Test the index route
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'VIN Lookup', response.data)  # Ensure 'VIN Lookup' is in the response

    def test_search_vin_route_no_vin(self):
        # Test the /search route with no VIN provided
        response = self.app.post('/search', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'VIN is required', response.data)

if __name__ == '__main__':
    unittest.main()