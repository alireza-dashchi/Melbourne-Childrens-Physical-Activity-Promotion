from dotenv import load_dotenv
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Import utilities and route handlers
from util.api_caching import initialize_cache_table
from route_handlers.parks.get_parks import get_parks, prefetch_weather_data
from route_handlers.parks.get_directions import get_directions
from route_handlers.parent.get_parental_guidance import get_parental_guidance, cleanup_spider_chart_png
from route_handlers.chat.get_chat_response import get_chat_response

# Initialize environment variables and cache table
load_dotenv()
initialize_cache_table()

# Create and configure Flask app
app = Flask(__name__)
CORS(app)

# Static file serving route
@app.route('/api/static/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory('static', filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Routes for park-related functionality
@app.route('/api/parks/prefetch_weather_data', methods=['POST'])
def prefetch_weather_data_route():
    try:
        return prefetch_weather_data()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/parks/get_parks', methods=['POST'])
def get_parks_route():
    try:
        return get_parks()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/parks/get_directions', methods=['POST'])
def get_directions_route():
    try:
        return get_directions()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Routes for parent-related functionality
@app.route('/api/parent/get_parental_guidance', methods=['POST'])
def get_parental_guidance_route():
    try:
        return get_parental_guidance()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/parent/cleanup_spider_chart_png', methods=['POST'])
def cleanup_spider_chart_png_route():
    try:
        return cleanup_spider_chart_png()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Routes for chatbot functionality
@app.route('/api/chat/get_chat_response', methods=['POST'])
def get_chat_response_route():
    try:
        return get_chat_response()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app in development mode
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)  # Use gunicorn for production
