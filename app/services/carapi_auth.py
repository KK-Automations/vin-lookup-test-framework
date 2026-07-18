import requests
import logging
from config.settings import CARAPI_BASE_URL, CARAPI_API_KEY, CARAPI_API_SECRET

logger = logging.getLogger(__name__)

def authenticate_with_carapi():
    """Authenticate with CarAPI and retrieve a token."""
    url = f"{CARAPI_BASE_URL}/auth"
    payload = {
        "api_key": CARAPI_API_KEY,
        "api_secret": CARAPI_API_SECRET,
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        token = response.json().get("token")
        logger.info("Successfully authenticated with CarAPI")
        return token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to authenticate with CarAPI: {e}")
        raise