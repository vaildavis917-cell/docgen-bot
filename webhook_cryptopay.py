# webhook_cryptopay.py
"""
CryptoPay Webhook для автоматической активации подписок
"""
from aiohttp import web
import hmac
import hashlib
import json
import os
import logging

logger = logging.getLogger(__name__)

CRYPTO_BOT_TOKEN = os.getenv('CRYPTO_BOT_TOKEN', '')

class CryptoPayWebhook:
    def __init__(self, token, sub_manager, bot=None):
        self.token = token
        self.sub_manager = sub_manager
        self.bot = bot
    
    def verify_signature(self, body: bytes, signature: str) -> bool:
        """Проверка подписи вебхука"""
        if not signature:
            return False
        secret = hashlib.sha256(self.token.encode()).digest()
        check = hmac.new(secret, body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(check, signature)
    
    async def handle_webhook(self, request):
        """Обработка вебхука от CryptoPay"""
        signature = request.headers.get('Crypto-Pay-Api-Signature', '')
        body = await request.read()
        
        if not self.verify_signature(body, signature):
            logger.warning("Invalid CryptoPay webhook signature")
            return web.Response(status=401, text='Invalid signature')
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return web.Response(status=400, text='Invalid JSON')
        
        logger.info(f"CryptoPay webhook received: {data.get('update_type')}")
        
        # Обработка успешной оплаты
        if data.get('update_type') == 'invoice_paid':
            invoice = data.get('payload', {})
            
            # Получаем данные из payload
            try:
                payload_data = json.loads(invoice.get('payload', '{}'))
                user_id = payload_data.get('user_id')
                plan = payload_data.get('plan', 'pro')
            except (json.JSONDecodeError, TypeError):
                # Fallback: пробуем получить из description
                user_id = invoice.get('payload')
                plan = 'pro'
            
            if user_id:
                # Активация подписки
                self.sub_manager.upgrade_subscription(
                    user_id=int(user_id),
                    plan=plan,
                    invoice_id=str(invoice.get('invoice_id', ''))
                )
                
                logger.info(f"Subscription activated for user {user_id}: {plan}")
                
                # Уведомление юзеру
                if self.bot:
                    try:
                        await self.bot.send_message(
                            chat_id=int(user_id),
                            text=f"✅ **Подписка активирована!**\n\n"
                                 f"План: {plan.upper()}\n"
                                 f"Спасибо за покупку! 🎉",
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        logger.error(f"Failed to notify user {user_id}: {e}")
        
        return web.Response(status=200, text='OK')


async def start_webhook(sub_manager, bot=None, port=8443):
    """Запуск вебхук сервера"""
    handler = CryptoPayWebhook(CRYPTO_BOT_TOKEN, sub_manager, bot)
    
    app = web.Application()
    app.router.add_post('/webhook/cryptopay', handler.handle_webhook)
    
    # Health check endpoint
    async def health_check(request):
        return web.Response(text='OK')
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"🌐 CryptoPay Webhook запущен на порту {port}")
    return runner
