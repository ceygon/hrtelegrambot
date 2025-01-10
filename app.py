from flask import Flask, request, jsonify, send_file
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    logging.info(f"Telegram API response: {response.status_code} - {response.text}")
    return response

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        
        # Chat widget URL'sini gönder
        chat_url = "https://hrtelegrambot.onrender.com"
        response_text = f"""Değerli çalışanımız,

İK sorularınız için chat arayüzümüzü kullanabilirsiniz:
<a href="{chat_url}">HR Asistan Chat</a>

İyi çalışmalar dileriz."""
        
        send_telegram_message(chat_id, response_text)
        return jsonify({"ok": True})
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"ok": False, "error": str(e)})

@app.route('/')
def home():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 10000))
