from flask import Flask, request, jsonify
import requests
import os
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ABACUS_URL = "https://api.abacus.ai/api/v0/inference"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    logging.info(f"Telegram API response: {response.status_code} - {response.text}")
    return response

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logging.info(f"Received webhook data: {data}")
        
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        logging.info(f"Extracted - chat_id: {chat_id}, text: {text}")

        if text and chat_id:
            # Chat isteği gönder
            chat_payload = {
                "deployment_id": "d497588e2",
                "inputs": {
                    "message": text,
                    "conversation_id": str(chat_id)
                }
            }
            
            logging.info(f"Sending request to Abacus: {ABACUS_URL}")
            logging.info(f"Request payload: {json.dumps(chat_payload)}")
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                ABACUS_URL,
                json=chat_payload,
                headers=headers
            )
            
            logging.info(f"Abacus response: {response.status_code} - {response.text}")
            
            if response.ok:
                try:
                    response_data = response.json()
                    bot_response = response_data.get('outputs', {}).get('response', 'Üzgünüm, bir hata oluştu.')
                    logging.info(f"Bot response: {bot_response}")
                    send_telegram_message(chat_id, bot_response)
                except Exception as e:
                    logging.error(f"Error parsing response: {str(e)}")
                    send_telegram_message(chat_id, "Üzgünüm, yanıtı işlerken bir hata oluştu.")
            else:
                error_msg = "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."
                logging.error(f"Abacus error: {response.text}")
                send_telegram_message(chat_id, error_msg)

        return jsonify({"ok": True})
    
    except Exception as e:
        logging.error(f"Error in webhook: {str(e)}")
        return jsonify({"ok": False, "error": str(e)})

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 10000))
