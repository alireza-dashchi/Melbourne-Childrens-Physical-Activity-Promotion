import requests
import time
import json
import re
from datetime import datetime
from util.database import AppDatabaseContextManager

# Initialization
def initialize_cache_table():
    """Create the API cache table if it does not exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS api_cache (
        cache_key TEXT PRIMARY KEY,
        response TEXT,
        timestamp TEXT
    )
    """
    with AppDatabaseContextManager() as conn:
        conn.cursor().execute(create_table_sql)
        conn.commit()

# Cache Utilities
def default_cache_key_gen(url, params):
    """Generate a unique cache key based on URL and sorted parameters."""
    sorted_params = json.dumps(params, sort_keys=True)
    return f"{url}_{sorted_params}"

def get_cached_response(cache_key):
    """Retrieve a cached response using the cache key."""
    with AppDatabaseContextManager() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT response FROM api_cache WHERE cache_key=?", (cache_key,))
        result = cursor.fetchone()
    return json.loads(result[0]) if result else None

def cache_response(cache_key, response):
    """Store a response in the cache."""
    with AppDatabaseContextManager() as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute(
            "INSERT OR REPLACE INTO api_cache (cache_key, response, timestamp) VALUES (?, ?, ?)",
            (cache_key, json.dumps(response), timestamp),
        )
        conn.commit()

def get_cache_timestamp(cache_key):
    """Retrieve the timestamp of a cached response."""
    with AppDatabaseContextManager() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp FROM api_cache WHERE cache_key=?", (cache_key,))
        result = cursor.fetchone()
    return result[0] if result else None

def flush_cache_entry(cache_key):
    """Remove a cache entry using its cache key."""
    with AppDatabaseContextManager() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM api_cache WHERE cache_key=?", (cache_key,))
        conn.commit()

# API Request with Caching and Retry Logic
def make_api_request(
    url,
    cache_key_gen_func=default_cache_key_gen,
    params=None,
    confidential_params=None,
    use_cache=True,
    max_cache_age_sec=None,
    max_retries=3,
    retry_delay=1
):
    """
    Make an API request with optional caching and retry logic.

    Parameters:
    - url (str): The URL for the API request.
    - cache_key_gen_func (function): Function to generate cache key.
    - params (dict): Query parameters for the API request.
    - confidential_params (dict): Confidential parameters like API keys.
    - use_cache (bool): Enable or disable caching.
    - max_cache_age_sec (int): Maximum age of cache in seconds.
    - max_retries (int): Number of retry attempts for failed requests.
    - retry_delay (int): Delay (in seconds) between retries.

    Returns:
    - dict: The JSON response from the API if successful.
    """
    if params is None:
        params = {}
    if confidential_params is None:
        confidential_params = {}

    cache_key = cache_key_gen_func(url, params)

    # Use cached response if available and fresh
    if use_cache:
        cache_timestamp = get_cache_timestamp(cache_key)
        if cache_timestamp:
            cache_time = datetime.fromisoformat(cache_timestamp)
            if max_cache_age_sec and (datetime.now() - cache_time).total_seconds() > max_cache_age_sec:
                flush_cache_entry(cache_key)
            else:
                cached_response = get_cached_response(cache_key)
                if cached_response:
                    return cached_response

    # Merge public and confidential parameters
    merged_params = {**params, **confidential_params}

    # Retry logic for API requests
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=merged_params)
            response.raise_for_status()
            response_json = response.json()

            if use_cache:
                cache_response(cache_key, response_json)

            return response_json

        except requests.RequestException as e:
            print(f"Request failed: {e}. Attempt {attempt + 1} of {max_retries}.")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

        except json.JSONDecodeError:
            print(f"Failed to decode JSON response. Attempt {attempt + 1} of {max_retries}.")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise ValueError("Failed to decode JSON response after multiple attempts.")

# Cache Cleanup
def clean_cache(regex_pattern, max_age):
    """
    Clean cache entries based on a regex pattern and maximum age.

    Parameters:
    - regex_pattern (str): Regex to match cache keys.
    - max_age (int): Maximum age of cache entries in seconds.
    """
    compiled_regex = re.compile(regex_pattern)
    current_time = datetime.now()

    with AppDatabaseContextManager() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cache_key, timestamp FROM api_cache")
        all_cache_entries = cursor.fetchall()

    for cache_key, timestamp in all_cache_entries:
        if compiled_regex.match(cache_key):
            cache_time = datetime.fromisoformat(timestamp)
            if (current_time - cache_time).total_seconds() > max_age:
                flush_cache_entry(cache_key)
