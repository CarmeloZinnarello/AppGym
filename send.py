import requests
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": "Test bot OK"
    }
)


TELEGRAM_TOKEN=8816384773:AAEojPOw9jnFTidTHumTfkwb5KJIm9ZBjug
TELEGRAM_CHAT_ID=47162967