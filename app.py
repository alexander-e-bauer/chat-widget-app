

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import eventlet
import pandas as pd
import ast
import config
import logging
from xyz.llm import embedding_model, embedding_generator, llm_blueprint

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

openai_client = config.openai_client
eventlet.monkey_patch()


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://alexander-e-bauer.github.io"]}})
socketio = SocketIO(app, cors_allowed_origins=["https://alexander-e-bauer.github.io"], async_mode='eventlet')
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
                                    system_input: str = "You are a helpful assistant who researches and discusses provided documents.",
                                    model: str = "gpt-4", streaming: bool = False,
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
    df= read_embedding('embeddings/resume_test.csv')

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
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
