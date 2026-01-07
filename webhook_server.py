"""
Webhook сервер для приёма уведомлений от Crypto Bot
Автоматически активирует подписки после оплаты
"""

import json
import hashlib
import hmac
import asyncio
from flask import Flask, request, jsonify
from config import CRYPTO_BOT_TOKEN, BOT_TOKEN
from utils.subscription import set_user_subscription
from utils.crypto_pay import parse_invoice_payload
import requests

app = Flask(__name__)

# Telegram Bot API URL
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def verify_crypto_bot_signature(body: bytes, signature: str) -> bool:
    """Проверка подписи от Crypto Bot"""
    secret = hashlib.sha256(CRYPTO_BOT_TOKEN.encode()).digest()
    expected_signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


def send_telegram_message(chat_id: int, text: str):
    """Отправка сообщения через Telegram Bot API"""
    url = f"{TELEGRAM_API}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None


@app.route('/webhook/crypto', methods=['POST'])
def crypto_webhook():
    """Обработка Webhook от Crypto Bot"""
    try:
        # Получаем данные
        body = request.get_data()
        signature = request.headers.get('crypto-pay-api-signature', '')
        
        # Проверяем подпись (опционально, но рекомендуется)
        # if not verify_crypto_bot_signature(body, signature):
        #     return jsonify({"error": "Invalid signature"}), 403
        
        data = request.get_json()
        print(f"Received webhook: {json.dumps(data, indent=2)}")
        
        # Проверяем тип события
        update_type = data.get('update_type')
        
        if update_type == 'invoice_paid':
            payload = data.get('payload', {})
            
            # Получаем данные из payload
            invoice_payload = payload.get('payload', '')
            status = payload.get('status')
            
            if status == 'paid' and invoice_payload:
                # Парсим payload (user_id:plan_id)
                parsed = parse_invoice_payload(invoice_payload)
                
                if parsed:
                    user_id = parsed['user_id']
                    plan_id = parsed['plan_id']
                    
                    # Активируем подписку
                    if set_user_subscription(user_id, plan_id):
                        # Отправляем уведомление пользователю
                        plan_names = {
                            "basic": ("⭐ Базовый", 30),
                            "pro": ("💎 Профессионал", 30),
                            "unlimited": ("👑 Безлимитный", 30)
                        }
                        
                        plan_info = plan_names.get(plan_id, (plan_id, 30))
                        
                        message = (
                            f"✅ **Подписка активирована!**\n\n"
                            f"{plan_info[0]}\n"
                            f"📅 Срок: {plan_info[1]} дней\n\n"
                            f"Спасибо за покупку! Теперь вам доступны расширенные лимиты.\n\n"
                            f"📢 Канал проекта: https://t.me/+VGUeNxCWYLEzYzU0"
                        )
                        
                        send_telegram_message(user_id, message)
                        print(f"Subscription activated for user {user_id}: {plan_id}")
                        
                        return jsonify({"status": "ok", "message": "Subscription activated"})
                    else:
                        print(f"Failed to activate subscription for user {user_id}")
                        return jsonify({"status": "error", "message": "Failed to activate"}), 500
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Проверка работоспособности сервера"""
    return jsonify({"status": "ok", "service": "crypto-webhook"})


@app.route('/', methods=['GET'])
def index():
    """Главная страница"""
    return jsonify({
        "service": "DocGen Bot Crypto Webhook",
        "status": "running",
        "endpoints": {
            "/webhook/crypto": "POST - Crypto Bot webhook",
            "/health": "GET - Health check"
        }
    })


if __name__ == '__main__':
    print("Starting Crypto Bot Webhook Server...")
    app.run(host='0.0.0.0', port=5000, debug=False)
