import dotenv
dotenv.load_dotenv()
import os
import requests

# Get the bot token from the environment variable
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Bot token not found! Please set the TELEGRAM_BOT_TOKEN environment variable.")

# Replace with your chat ID
CHAT_ID = "6310217725"

# Message to send
MESSAGE = "Hello! This is a test message from your Telegram bot."

# Telegram API URL
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Parameters for the request
params = {
    "chat_id": CHAT_ID,
    "text": MESSAGE
}

# Send the message
response = requests.get(url, params=params)

# Check the response
if response.status_code == 200:
    print("Message sent successfully!")
else:
    print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
