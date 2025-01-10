from flask import request, jsonify
import datetime
import uuid
from .openAi_chatbot import send_prompt_and_get_response

# In-memory session storage
sessions = {}

def get_chat_response():
    """
    Handle chat requests by interacting with the OpenAI-powered chatbot.
    Each session maintains a conversation context using in-memory storage.

    Returns:
        - JSON response with AI reply and session ID.
    """
    data = request.get_json()

    # Validate the input message
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message']
    session_id = data.get('sessionId', None)

    # Create a new session if no sessionId is provided or the session is invalid
    if session_id is None or session_id not in sessions:
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = f"{timestamp}_{uuid.uuid4().hex[:8]}"
        session_id = str(unique_id)
        sessions[session_id] = {'thread_id': None, 'conversation': []}

    # Retrieve the thread ID for the session
    thread_id = sessions[session_id].get('thread_id')

    # Get response from the chatbot
    ai_response, thread_id = send_prompt_and_get_response(user_message, thread_id)

    # Update session with thread ID and conversation
    sessions[session_id]['thread_id'] = thread_id
    sessions[session_id]['conversation'].append({"user": user_message, "ai": ai_response})

    return jsonify({'reply': ai_response, 'sessionId': session_id}), 200
