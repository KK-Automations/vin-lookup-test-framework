import os
import sys
import unittest
import logging
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(project_root, '.env'))

class TestCarAPIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Class-level setup method to run once before all tests
        """
        logger.info("Setting up Car API Integration Test")
        
        # Verify virtual environment
        cls._verify_virtual_environment()
    
    @staticmethod
    def _verify_virtual_environment():
        """
        Verify that the test is running in the correct virtual environment
        """
        import sys
        venv_path = os.path.abspath(os.path.join(project_root, '..', 'testenv'))
        
        # Check if virtual environment is activated
        is_venv_active = (
            hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        # Log virtual environment details
        logger.info(f"Virtual Environment Path: {venv_path}")
        logger.info(f"Python Executable: {sys.executable}")
        logger.info(f"Virtual Environment Active: {is_venv_active}")
    
    def setUp(self):
        """
        Method-level setup for each test method
        """
        # Load API credentials from .env file
        self.api_key = os.getenv('CAR_API_KEY')
        logger.info(f"API Key Loaded: {'Yes' if self.api_key else 'No'}")
    
    def test_api_key_exists(self):
        """
        Test to verify API key is set in the environment
        """
        self.assertIsNotNone(
            self.api_key, 
            "CAR_API_KEY must be set in .env file"
        )
    
    def test_api_key_format(self):
        """
        Additional test to validate API key format
        """
        if self.api_key:
            # Example basic validation (customize as needed)
            self.assertTrue(
                len(self.api_key) >= 10, 
                "API Key seems too short"
            )
            self.assertFalse(
                self.api_key.isspace(), 
                "API Key cannot be just whitespace"
            )
    
    @classmethod
    def tearDownClass(cls):
        """
        Class-level teardown method
        """
        logger.info("Completed Car API Integration Test")

if __name__ == '__main__':
    unittest.main()