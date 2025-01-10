import os
import time
from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
from typing_extensions import override

# Load environment variables
load_dotenv()

# Retrieve the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY is not set in the environment variables.")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Define the system prompt for the assistant
SYSTEM_PROMPT = """
You are an AI-powered chatbot designed to help immigrant children aged between 5 and 14 with health advice, motivational messages, safe exercise suggestions, and website navigation assistance. 
- Keep responses brief and simple (maximum 100 words).
- Always use a friendly, encouraging, and supportive tone.
- Focus on health, safety, and website navigation questions. Suggest asking an adult for unrelated topics.
- If needed, switch to the child’s preferred language for responses or translations.

Website features:
- **Parks Section**: Provides safe parks with safety ratings and weather updates.
- **Learning Hub**: Offers exercise tips and safety advice.
- **Scavenger Hunt**: Encourages exploration through interactive challenges.
- **Parental Guidance**: Supplies personalized activity recommendations.
- **Safety Zone**: Teaches safety and first aid tips.
- **Chatbot "Pal"**: Assists with health tips, exercises, and translations.
"""

# Create the assistant
assistant = client.beta.assistants.create(
    name="Pal",
    instructions=SYSTEM_PROMPT,
    tools=[],
    model="gpt-4o-mini",
)


class EventHandler(AssistantEventHandler):
    """
    Custom event handler to handle assistant responses.
    """

    def __init__(self):
        super().__init__()
        self.response_text = []

    @override
    def on_text_delta(self, delta, snapshot):
        """
        Append incoming text deltas to the response.
        """
        if hasattr(delta, "value"):
            self.response_text.append(delta.value)

    def get_response(self):
        """
        Combine all text deltas into the final response.
        """
        return "".join(self.response_text)


def send_prompt_and_get_response(prompt, thread_id=None):
    """
    Send a user prompt to the assistant and get its response.

    Parameters:
        - prompt (str): The user's input message.
        - thread_id (str): Optional thread ID for ongoing conversations.

    Returns:
        - Tuple: Assistant's response and the thread ID.
    """
    # Create a new thread if no thread ID is provided
    if thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id

    # Send the user prompt to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt,
    )

    # Initialize event handler
    event_handler = EventHandler()

    # Stream assistant's response
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant.id,
        instructions=SYSTEM_PROMPT,
        event_handler=event_handler,
    ) as stream:
        stream.until_done()

    # Return the complete response and the thread ID
    return event_handler.get_response(), thread_id
