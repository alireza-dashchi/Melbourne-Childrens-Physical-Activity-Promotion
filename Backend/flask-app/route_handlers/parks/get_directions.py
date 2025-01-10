import os
import polyline
from flask import jsonify, request
from util.api_caching import make_api_request


def get_directions():
    """
    Fetch directions between two locations using Google Maps Directions API.
    
    Expects a JSON payload with:
        - `start`: Dictionary containing `lat` and `lng` for the start location.
        - `end`: Dictionary containing `lat` and `lng` for the end location.
        - `mode`: String indicating the mode of transport ('ride' for bicycling, else walking).

    Returns:
        - A list of waypoints for the route if successful.
        - Error message if inputs are invalid or API request fails.
    """
    data = request.json

    # Validate input
    start_location = data.get('start')
    end_location = data.get('end')
    mode = 'bicycling' if 'ride' in data.get('mode', '').lower() else 'walking'

    if not start_location or not end_location:
        return jsonify({"error": "Start and end locations are required"}), 400

    # Google Maps Directions API endpoint and parameters
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json'
    params = {
        'origin': f"{start_location['lat']},{start_location['lng']}",
        'destination': f"{end_location['lat']},{end_location['lng']}",
        'alternatives': 'false',
        'mode': mode,
    }
    confidential_params = {'key': os.getenv('GOOGLE_MAPS_API_KEY')}

    try:
        # Make the API request
        directions_data = make_api_request(url=endpoint, params=params, confidential_params=confidential_params)

        # Parse the response
        if directions_data.get('status') == 'OK':
            route = directions_data['routes'][0]['overview_polyline']['points']
            waypoints = polyline.decode(route)

            # Return the decoded waypoints to the client
            return jsonify({"waypoints": waypoints}), 200
        else:
            return jsonify({"error": "Failed to fetch directions", "details": directions_data.get('error_message', '')}), 500

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred while fetching directions", "details": str(e)}), 500
