from flask import Flask, request, jsonify
import requests
import os
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
API_TOKEN = os.environ.get('ABACUS_API_TOKEN')  # Bunu Render.com'da ekleyeceğiz
DEPLOYMENT_ID = "d497588e2"

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
            # Prediction isteği gönder
            predict_url = f"https://api.abacus.ai/api/v0/deployment/{DEPLOYMENT_ID}/predict"
            
            headers = {
                'Authorization': f'Bearer {API_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            predict_payload = {
                "inputs": {
                    "message": text
                }
            }
            
            logging.info(f"Sending request to Abacus API: {predict_url}")
            logging.info(f"Request payload: {json.dumps(predict_payload)}")
            
            response = requests.post(
                predict_url,
                headers=headers,
                json=predict_payload
            )
            
            logging.info(f"Abacus API response: {response.status_code} - {response.text}")
            
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
                logging.error(f"Abacus API error: {response.text}")
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
