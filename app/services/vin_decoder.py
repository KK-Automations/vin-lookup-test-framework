import requests
import logging
from http import HTTPStatus
from config.settings import CARAPI_API_ENDPOINT, CARAPI_API_KEY
from utils.validators import is_valid_vin

logger = logging.getLogger(__name__)

def decode_vin(vin):
    """Decode a VIN using CarAPI."""
    if not is_valid_vin(vin):
        logger.error(f"Invalid VIN provided: {vin}")
        return None

    url = f"{CARAPI_API_ENDPOINT}/{vin}"
    headers = {
        "Authorization": f"Bearer {CARAPI_API_KEY}",
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            logger.info(f"Successfully decoded VIN: {vin}")
            return data
        else:
            logger.error(f"Failed to decode VIN {vin}: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while decoding VIN {vin}: {e}")
        return None