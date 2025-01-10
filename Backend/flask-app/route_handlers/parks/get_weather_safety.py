import os
import time
from util.api_caching import make_api_request


def round_coordinates(lat, lon, precision=2):
    """
    Round latitude and longitude to the specified precision.
    """
    return round(lat, precision), round(lon, precision)


def default_retry_strategy(e, attempt, max_retries):
    """
    Default retry strategy that performs exponential backoff.

    Parameters:
    - e (Exception): The exception raised.
    - attempt (int): Current retry attempt.
    - max_retries (int): Maximum number of retries.

    Returns:
    - bool: Whether to retry (True) or not (False).
    """
    print(f"Request failed: {e}. Attempt {attempt + 1} of {max_retries}. Retrying...")
    if attempt < max_retries - 1:
        time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s, etc.
        return True
    return False


def get_weather_data(lat, lon, max_age_sec=900, onError=None):
    """
    Fetch weather data from OpenWeather API, using cache if available and fresh.

    Parameters:
    - lat (float): Latitude of the location.
    - lon (float): Longitude of the location.
    - max_age_sec (int): Maximum cache age in seconds (default: 900 seconds).
    - onError (function): Custom error handling function (default: None).

    Returns:
    - dict: Weather data for the location.

    Raises:
    - Exception: Raises the last exception if all retries are exhausted.
    """
    # Retrieve API key from environment variables
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        raise EnvironmentError("WEATHER_API_KEY is not set in the environment variables.")

    # OpenWeather API endpoint
    url = 'http://api.openweathermap.org/data/2.5/weather'

    # Round coordinates to improve cache efficiency
    lat, lon = round_coordinates(lat, lon)

    params = {'lat': lat, 'lon': lon, 'units': 'metric'}
    confidential_params = {'appid': api_key}

    # Set default error handling strategy if none is provided
    if onError is None:
        onError = default_retry_strategy

    # Retry logic for the API request
    max_retries = 3
    last_exception = None
    for attempt in range(max_retries):
        try:
            # Make API request with caching
            return make_api_request(
                url=url,
                params=params,
                confidential_params=confidential_params,
                use_cache=True,
                max_cache_age_sec=max_age_sec,
            )
        except Exception as e:
            last_exception = e
            if not onError(e, attempt, max_retries):
                break

    # If all retries are exhausted, raise the last exception
    raise last_exception
