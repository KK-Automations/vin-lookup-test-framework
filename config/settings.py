import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def get_env_variable(var_name, default=None, required=False):
    """
    Retrieve an environment variable or raise an error if it's required and not set.
    """
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value

# CarAPI Configuration
CARAPI_BASE_URL = get_env_variable("CARAPI_BASE_URL", "https://carapi.app")
CARAPI_API_ENDPOINT = get_env_variable("CARAPI_API_ENDPOINT", "https://api.carapi.app/vin")
CARAPI_API_KEY = get_env_variable("CARAPI_API_KEY")
if CARAPI_API_KEY is None:
    raise ValueError("Environment variable 'CARAPI_API_KEY' is required but not set.")
CARAPI_API_SECRET = get_env_variable("CARAPI_API_SECRET", required=True)
CARAPI_USERNAME = get_env_variable("CARAPI_USERNAME")
CARAPI_PASSWORD = get_env_variable("CARAPI_PASSWORD")

# NHTSA Configuration
NHTSA_API_ENDPOINT = get_env_variable("NHTSA_API_ENDPOINT", "https://api.nhtsa.gov/vin")

# VIN Audit Configuration
VINAUDIT_API_KEY = get_env_variable("VINAUDIT_API_KEY")

# Carfax Configuration
CARFAX_API_KEY = get_env_variable("CARFAX_API_KEY")

# Application Settings
DEBUG = get_env_variable("DEBUG", "False").lower() == "true"
ENV = get_env_variable("ENV", "development")