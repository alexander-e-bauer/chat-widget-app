from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import config
import logging


import os
import dotenv
import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_security import RegisterForm, LoginForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from xyz.llm import llm_blueprint
from xyz.database import database, models


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])

class ExtendedLoginForm(LoginForm):
    email = StringField('Email Address', [DataRequired()])


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

openai_client = config.openai_client
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

username_db = os.getenv('POSTGRES_USER')
password_db = os.getenv('POSTGRES_PASSWORD')
database_name = os.getenv('POSTGRES_DB')
postgres_uri = f'postgresql://{username_db}:{password_db}@localhost/{database_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = postgres_uri

app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT")


# Create database connection object
db = database.init_app(app)

# Define models
User, Role, roles_users = models.define_models(db)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_REGISTER_URL'] = '/register'
app.config['SECURITY_LOGIN_URL'] = '/login'
app.config['SECURITY_LOGOUT_URL'] = '/logout'
app.config['SECURITY_RESET_URL'] = '/reset'
app.config['SECURITY_CHANGE_URL'] = '/change'

security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm,
                    login_form=ExtendedLoginForm)

# CSRF
csrf = CSRFProtect(app)

# Bootstrap
Bootstrap(app)

# Blueprints
oai = llm_blueprint.init_app(app)

# Update CORS configuration
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://alexander-e-bauer.github.io"]}})

# In-memory storage for conversation history
conversation_history = {}


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
            tools=tools,
            tool_choice="auto",
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


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    conversation_id = data.get('conversationId', 'default')
    logger.debug(f"Received chat request. Message: {message}, Conversation ID: {conversation_id}")
    logger.debug(f"Current conversation history: {conversation_history.get(conversation_id, [])}")

    try:
        completion = chat_completion(user_input=message, conversation_id=conversation_id, tools=None)
        response = f"{completion}"
        logger.debug(f"Sending response: {response}")
        logger.debug(f"Updated conversation history: {conversation_history[conversation_id]}")
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}", exc_info=True)
        return jsonify({"error": f"An error occurred while processing your request: {str(e)}"}), 500

