from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ABACUS_CHAT_URL = "https://apps.abacus.ai/chatllm/9d43b9ec0"  # Direkt chat URL'si

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
                "messages": [{"role": "user", "content": text}],
                "stream": False
            }
            
            logging.info(f"Sending request to Abacus Chat: {ABACUS_CHAT_URL}")
            response = requests.post(
                ABACUS_CHAT_URL,
                json=chat_payload
            )
            
            logging.info(f"Abacus Chat response: {response.status_code} - {response.text}")
            
            if response.ok:
                try:
                    bot_response = response.json().get('message', 'Üzgünüm, bir hata oluştu.')
                    logging.info(f"Bot response: {bot_response}")
                    send_telegram_message(chat_id, bot_response)
                except Exception as e:
                    logging.error(f"Error parsing response: {str(e)}")
                    send_telegram_message(chat_id, "Üzgünüm, yanıtı işlerken bir hata oluştu.")
            else:
                error_msg = "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."
                logging.error(f"Abacus Chat error: {response.text}")
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
