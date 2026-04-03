import requests
from django.conf import settings


def send_telegram_message(chat_id, text):
    token = settings.TELEGRAM_BOT_API
    url = f"https://telegram.org{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, data=payload)


