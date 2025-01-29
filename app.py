import dotenv
dotenv.load_dotenv()
import eventlet
eventlet.monkey_patch(thread=False)  # Add thread=False to help with recursion issues

# Existing imports
import sys
import ssl  # Add this import
import urllib3  # Add this import

# Increase recursion limit and configure SSL
sys.setrecursionlimit(3000)


import os
import requests
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import pandas as pd
import ast
import config
import logging
from xyz.llm import embedding_model
from xyz.llm.tools.telegram_update import send_telegram_message


# Increase recursion limit and configure SSL
sys.setrecursionlimit(3000)

# SSL Configuration
def create_ssl_context():
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    except Exception as e:
        logger.error(f"Failed to create SSL context: {e}")
        return None

# Configure SSL for requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl_context = create_ssl_context()


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

openai_client = config.openai_client

# Load the system input from the text file
system_input_path = 'xyz/llm/embeddings/system_input.txt'
try:
    with open(system_input_path, 'r', encoding='utf-8') as file:
        system_input_txt = file.read()
except FileNotFoundError:
    raise FileNotFoundError(f"System input file not found at: {system_input_path}")

app = Flask(__name__)
# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",  # React development server
            "http://localhost:5000",  # Flask development server
            "http://localhost:6379",  # Flask development server
            "https://chat-widget-app-8c3cca0ff3c0.herokuapp.com",  # Production URL
            "https://alexander-e-bauer.github.io"  # Add your frontend domain
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure SocketIO with CORS settings
socketio = SocketIO(app, cors_allowed_origins=[
    "http://localhost:3000",
    "http://localhost:5000",
    "https://chat-widget-app-8c3cca0ff3c0.herokuapp.com",
    "https://alexander-e-bauer.github.io"], async_mode='eventlet'
)
# In-memory storage for conversation history
conversation_history = {}


def read_embedding(embedding_path):
    return pd.read_csv(
        embedding_path,
        index_col=0,
        converters={
            'embedding': lambda x: ast.literal_eval(x)
        }
    )
df = read_embedding('xyz/llm/embeddings/resume_test.csv')
print(df)


def chat_completion(user_input, conversation_id, system_input="You are a helpful assistant",
                    tools=None, streaming=False):
    if conversation_id not in conversation_history:
        conversation_history[conversation_id] = []

    # Append user message to conversation history
    conversation_history[conversation_id].append({"role": "user", "content": user_input})

    messages = [
        {"role": "system", "content": system_input},
    ] + conversation_history[conversation_id]

    logger.debug(f"Messages sent to API: {messages}")

    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=streaming
        )

        if not streaming:
            output = completion.choices[0].message.content
        else:
            output = ""
            for chunk in completion:
                output += str(chunk.choices[0].delta.content or '')
                print(chunk.choices[0].delta.content)

        # Append assistant's response to conversation history
        conversation_history[conversation_id].append({"role": "assistant", "content": output})

        logger.debug(f"Updated conversation history: {conversation_history[conversation_id]}")
        return output
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}", exc_info=True)
        raise


def chat_completion_with_embeddings(user_input: str, df: pd.DataFrame, conversation_id: str,
                                    system_input: str = system_input_txt,
                                    model: str = "gpt-4o", streaming: bool = False,
                                    print_message: bool = False) -> str:
    """
    Performs chat completion using GPT, incorporating conversation history and document embeddings.
    """
    if conversation_id not in conversation_history:
        conversation_history[conversation_id] = []

    # Create the query message using the dataframe
    query_msg = embedding_model.query_message(user_input, df, model=model)

    if print_message:
        print(f"Query message: {query_msg}")

    # Append user message to conversation history
    conversation_history[conversation_id].append({"role": "user", "content": query_msg})

    messages = [
                   {"role": "system", "content": system_input},
               ] + conversation_history[conversation_id]

    logger.debug(f"Messages sent to API: {messages}")

    try:
        completion = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            stream=streaming,
            temperature=0
        )

        if not streaming:
            output = completion.choices[0].message.content
        else:
            output = ""
            for chunk in completion:
                output += str(chunk.choices[0].delta.content or '')
                print(chunk.choices[0].delta.content or '', end='', flush=True)

        # Append assistant's response to conversation history
        conversation_history[conversation_id].append({"role": "assistant", "content": output})

        logger.debug(f"Updated conversation history: {conversation_history[conversation_id]}")
        # Format the Telegram message
        truncated_output = output[:150]  # Limit the output to the first 150 characters
        message = (
            f"🤖 Chatbot Interaction Log\n\n"
            f"Conversation ID: `{conversation_id}`\n\n"
            f"User Input:\n{user_input}\n\n"
            f"Bot Output (First 200 chars):\n{truncated_output}...\n\n"
            f"**Model Used:** {model}"
        )

        send_telegram_message(message)  # Send the formatted message to Telegram
        return output
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}", exc_info=True)
        raise

@socketio.on('typing')
def handle_typing(data):
    emit('typing', data, broadcast=True, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    emit('stop_typing', data, broadcast=True, include_self=False)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    conversation_id = data.get('conversationId', 'default')
    logger.debug(f"Received chat request. Message: {message}, Conversation ID: {conversation_id}")
    logger.debug(f"Current conversation history: {conversation_history.get(conversation_id, [])}")


    try:
        completion = chat_completion_with_embeddings(user_input=message, conversation_id=conversation_id, df=df)
        response = f"{completion}"
        logger.debug(f"Sending response: {response}")
        logger.debug(f"Updated conversation history: {conversation_history[conversation_id]}")
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}", exc_info=True)
        return jsonify({"error": f"An error occurred while processing your request: {str(e)}"}), 500


if __name__ == '__main__':
    socketio.run(app,
                host='0.0.0.0',
                port=5000,
                debug=True,
                allow_unsafe_werkzeug=True)
