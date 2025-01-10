from flask import jsonify, request
from random import sample
import threading
from util.database import SafetyMapDatabaseContextManager
from route_handlers.parks.get_crime_accident_safety import get_safety_data
from route_handlers.parks.get_weather_safety import get_weather_data


# Global variables for background thread management
prefetch_thread = None
cancel_prefetch = False


def is_valid_coordinate(lat, lon):
    """
    Check if latitude and longitude are valid numerical values.
    Latitude must be between -90 and 90.
    Longitude must be between -180 and 180.
    """
    try:
        lat = float(lat)
        lon = float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


def get_suburb_locations():
    """
    Retrieve a dictionary of suburb locations with mean coordinates (latitude, longitude).
    """
    suburb_dict = {}
    with SafetyMapDatabaseContextManager() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT latitude, longitude, suburb_id FROM Location")
        all_locations = cursor.fetchall()

    # Organize locations by suburb_id
    locations_by_suburb = {}
    for lat, lon, suburb_id in all_locations:
        if suburb_id not in locations_by_suburb:
            locations_by_suburb[suburb_id] = []
        locations_by_suburb[suburb_id].append((lat, lon))

    # Calculate mean lat/lon for each suburb
    for suburb_id, coordinates in locations_by_suburb.items():
        valid_coords = [(lat, lon) for lat, lon in coordinates if is_valid_coordinate(lat, lon)]
        if valid_coords:
            mean_lat = sum(lat for lat, lon in valid_coords) / len(valid_coords)
            mean_lon = sum(lon for lat, lon in valid_coords) / len(valid_coords)
            suburb_dict[suburb_id] = (mean_lat, mean_lon)

    return suburb_dict


def prefetch_weather_data_task(percentage):
    """
    Background task to prefetch weather data for a random selection of suburbs.
    """
    global cancel_prefetch
    suburb_locations = get_suburb_locations()

    if not suburb_locations:
        return

    total_suburbs = len(suburb_locations)
    num_suburbs_to_prefetch = max(1, int((percentage / 100) * total_suburbs))
    selected_suburbs = sample(list(suburb_locations.items()), num_suburbs_to_prefetch)

    for suburb_id, (lat, lon) in selected_suburbs:
        if cancel_prefetch:
            return
        try:
            get_weather_data(lat, lon, max_age_sec=720)
        except Exception as e:
            print(f"Error during weather prefetch: {e}")


def prefetch_weather_data():
    """
    API endpoint to start a background thread for prefetching weather data.
    """
    global prefetch_thread, cancel_prefetch

    data = request.json
    percentage = data.get("percentage", 100)

    if prefetch_thread and prefetch_thread.is_alive():
        cancel_prefetch = True
        prefetch_thread.join()

    cancel_prefetch = False
    prefetch_thread = threading.Thread(target=prefetch_weather_data_task, args=(percentage,))
    prefetch_thread.start()

    return jsonify({"status": "Prefetch started"})


def get_parks():
    """
    API endpoint to fetch park data including user location and safety details.
    """
    global cancel_prefetch

    if prefetch_thread and prefetch_thread.is_alive():
        cancel_prefetch = True
        prefetch_thread.join()

    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    geojson_response = {"type": "FeatureCollection", "features": []}

    if latitude is not None and longitude is not None:
        try:
            user_location_weather = get_weather_data(latitude, longitude)
            geojson_response["features"].append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                "properties": {"type": "user_location", "name": "Your Location", "weather": user_location_weather},
            })
        except Exception as e:
            print(f"Error fetching user location weather: {e}")

    with SafetyMapDatabaseContextManager() as connection:
        safety_data = get_safety_data(connection, latitude, longitude)
        if isinstance(safety_data, dict) and "features" in safety_data:
            geojson_response["features"].extend(safety_data["features"])

    # Hardcoded park names for a special property
    park_name_list = ["Fitzroy Gardens", "Flagstaff Gardens", "Carlton Gardens South", "Royal Botanic Gardens"]
    for feature in geojson_response["features"]:
        feature_name = feature["properties"].get("name")
        feature["properties"]["gameParkName"] = feature_name if feature_name in park_name_list else None

    return jsonify(geojson_response)
