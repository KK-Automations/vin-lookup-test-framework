import unittest
from unittest.mock import patch
from app.services.vin_decoder import decode_vin

class TestVinDecoder(unittest.TestCase):
    @patch("app.services.vin_decoder.requests.get")
    def test_valid_vin(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"make": "Honda", "model": "Civic", "year": 2020}
        vin = "1HGCM82633A123456"
        result = decode_vin(vin)
        self.assertIsNotNone(result)
        self.assertEqual(result["make"], "Honda")

    def test_invalid_vin(self):
        vin = "INVALIDVIN123"
        result = decode_vin(vin)
        self.assertIsNone(result)

    def test_empty_vin(self):
        vin = ""
        result = decode_vin(vin)
        self.assertIsNone(result)

    @patch("app.services.vin_decoder.requests.get")
    def test_api_error(self, mock_get):
        mock_get.side_effect = Exception("API Error")
        vin = "1HGCM82633A123456"
        result = decode_vin(vin)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()