from flask import jsonify, request
import math
from util.database import AppDatabaseContextManager
from route_handlers.parks.get_weather_safety import get_weather_data


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two geographic coordinates using the Haversine formula.
    """
    R = 6371.0  # Earth radius in kilometers

    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlat, dlon = lat2_rad - lat1_rad, lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_safety_rating(weather_score, crime_score, accident_score):
    """
    Calculate a composite safety rating based on weather, crime, and accident scores.
    """
    weighted_score = (0.4 * weather_score) + (0.3 * crime_score) + (0.3 * accident_score)
    if weighted_score >= 9:
        return 5
    elif weighted_score >= 7:
        return 4
    elif weighted_score >= 5:
        return 3
    elif weighted_score >= 3:
        return 2
    else:
        return 1


def get_safety_data(connection, latitude=None, longitude=None):
    """
    Fetch and calculate safety data for parks, including weather, crime, and accident scores.
    """
    cursor = connection.cursor()

    # Fetch max values for normalization
    cursor.execute("SELECT MAX(incidents_recorded_2014_2023) FROM Crime")
    max_crime = cursor.fetchone()[0] or 1  # Prevent division by zero

    cursor.execute("SELECT MAX(total_accidents) FROM Accident")
    max_accidents = cursor.fetchone()[0] or 1

    query = """
        SELECT L.location_id, L.latitude, L.longitude, L.suburb_id,
               C.incidents_recorded_2014_2023, A.total_accidents,
               LM.landmark_name, LM.landmark_type, 
               F.facility_name, F.sports_played, P.playground_name
        FROM Location L
        LEFT JOIN Crime C ON L.suburb_id = C.suburb_id
        LEFT JOIN Accident A ON L.suburb_id = A.suburb_id
        LEFT JOIN Landmark LM ON L.location_id = LM.location_id
        LEFT JOIN Facility F ON L.location_id = F.location_id
        LEFT JOIN Playground P ON L.location_id = P.location_id
    """
    cursor.execute(query)
    locations = cursor.fetchall()

    if not locations:
        return {'error': 'No location data found in the database'}, 404

    features = []
    for location in locations:
        location_id, lat, lon, _, crime, accidents, landmark_name, landmark_type, facility_name, sports_played, playground_name = location

        # Determine facility type and name
        facility = landmark_type if landmark_name else ('sports' if sports_played else 'parks')
        name = landmark_name or facility_name or playground_name or "Unknown"

        # Calculate scores
        weather_data = get_weather_data(lat, lon)
        weather_main = weather_data.get('weather', [{}])[0].get('main', 'Unknown')
        weather_score = 10 if weather_main in ["Clear", "Clouds"] else (5 if weather_main in ["Drizzle", "Mist", "Fog"] else 0)

        crime_score = max(0, 10 - (crime or 0) / max_crime * 10)
        accident_score = max(0, 10 - (accidents or 0) / max_accidents * 10)
        safety_rating = calculate_safety_rating(weather_score, crime_score, accident_score)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "facility": facility,
                "name": name,
                "safetyRating": safety_rating,
                "weather": weather_main,
                "crime": crime or 0,
                "accidents": accidents or 0,
            },
        })

    return {"type": "FeatureCollection", "features": features}


def get_crime_safety_data():
    """
    Flask route handler to fetch crime and safety data for parks.
    """
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    try:
        with AppDatabaseContextManager() as connection:
            data = get_safety_data(connection, latitude, longitude)
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
