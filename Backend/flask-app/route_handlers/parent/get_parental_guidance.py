import os
from flask import jsonify, request
from ..learning_hub.get_questionare import assess_activity, create_spider_chart


def get_parental_guidance():
    """
    Process survey data and provide parental guidance based on the child's activity levels.

    Expects a JSON payload with:
        - outdoorTime: Level of outdoor playtime (1-4).
        - outdoorFrequency: Frequency of outdoor play (1-4).
        - screenTime: Screen time level (1-4).
        - peFrequency: Physical education frequency (1-4).
        - physicalActivityDays: Active days per week (1-4).
        - walkOrCycle: Walking or cycling frequency (string).

    Returns:
        - JSON response with feedback, recommendations, and a spider chart URL.
    """
    try:
        data = request.json

        # Map survey responses to numerical values
        outdoor_play_minutes_map = {1: 15, 2: 45, 3: 90, 4: 150}
        outdoor_play_days_map = {1: 0.5, 2: 1.5, 3: 3.5, 4: 6}
        screen_time_map = {1: 0.5, 2: 1.5, 3: 3.0, 4: 5.0}
        physical_education_map = {1: 0.5, 2: 1, 3: 2, 4: 5.5}
        active_days_map = {1: 0.5, 2: 1.5, 3: 3.5, 4: 6}

        outdoor_play_minutes = outdoor_play_minutes_map.get(data.get('outdoorTime'))
        outdoor_play_days = outdoor_play_days_map.get(data.get('outdoorFrequency'))
        screen_time = screen_time_map.get(data.get('screenTime'))
        physical_education = physical_education_map.get(data.get('peFrequency'))
        active_days = active_days_map.get(data.get('physicalActivityDays'))
        walk_or_cycle = data.get('walkOrCycle', '')

        # Validate input
        if None in [outdoor_play_minutes, outdoor_play_days, screen_time, physical_education, active_days]:
            return jsonify({"error": "Invalid survey data provided"}), 400

        # Assess activity levels
        result = assess_activity(
            outdoor_play_days, outdoor_play_minutes, screen_time,
            physical_education, active_days, walk_or_cycle
        )

        # Generate spider chart
        spider_chart_url = create_spider_chart(result['scores'])

        # Prepare response
        response = {
            "feedback": result['status'],
            "detailedAssessment": result['recommendations'],
            "plotImageUrl": f'/{spider_chart_url}',
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": "An error occurred while processing the survey data", "details": str(e)}), 500


def cleanup_spider_chart_png():
    """
    Cleanup spider chart PNG files from the server.

    Expects a JSON payload with:
        - filename: Path of the file to be deleted.

    Returns:
        - HTTP 204 No Content if successful.
        - HTTP 400 Bad Request if the filename is invalid.
    """
    try:
        data = request.json
        file_name = data.get('filename')

        if file_name and file_name.startswith('/static/images/parent/spider_chart_') and file_name.endswith('.png'):
            file_path = file_name.lstrip('/')
            if os.path.exists(file_path):
                os.remove(file_path)
            return '', 204
        else:
            return jsonify({"error": "Invalid filename provided"}), 400

    except Exception as e:
        return jsonify({"error": "An error occurred while cleaning up the chart file", "details": str(e)}), 500
