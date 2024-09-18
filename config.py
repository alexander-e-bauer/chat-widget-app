import os
import dotenv
from openai import OpenAI
import logging

dotenv.load_dotenv()
# Create a file handler that logs debug and higher level messages to a file
file_handler = logging.FileHandler('isadora.log')
file_handler.setLevel(logging.DEBUG)

# Create a console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Apply the formatter to the handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger = logging.getLogger('isadora')
logger.setLevel(logging.DEBUG)  # This sets the logger to handle all messages DEBUG and above
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log(msg):
    logger.debug(msg)
    print(msg)


class Config:
    """Base configuration variables."""

    # Configure PostgreSQL Database
    username_db = os.getenv('POSTGRES_USER')
    password_db = os.getenv('POSTGRES_PASSWORD')
    database_name = os.getenv('POSTGRES_DB')
    postgres_uri = f'postgresql://{username_db}:{password_db}@localhost/{database_name}'


class OAI:
    """OpenAI configuration variables."""
    # OpenAI Client
    client = None
    # Models
    gpt4o = "gpt-4o"
    gpt4o_mini = "gpt-4o-mini"
    embedding3 = "text-embedding-3-large"
    dall_e_3 = "dall-e-3"
    tts = "tts-1"
    tts_hd = 'tts-1-hd'
    whisper = "whisper-1"
    moderation = "text-moderation-latest"


openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
OAI.client = openai_client
