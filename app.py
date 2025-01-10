from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ABACUS_CHAT_URL = os.environ.get('ABACUS_URL')

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    message = data.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    if text:
        response = requests.post(
            ABACUS_CHAT_URL,
            json={"message": text}
        )
        
        if response.ok:
            bot_response = response.json().get('response', 'Üzgünüm, bir hata oluştu.')
            send_telegram_message(chat_id, bot_response)

    return jsonify({"ok": True})

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    app.run()
