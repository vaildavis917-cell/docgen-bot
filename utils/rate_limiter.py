"""
Rate Limiter с защитой от флуда
Адаптивные лимиты в зависимости от тарифа
"""
from functools import wraps
from time import time
from typing import Dict, List
from collections import defaultdict

class RateLimiter:
    """Rate limiter с поддержкой разных лимитов по тарифам"""
    
    # Конфигурация лимитов (запросов в минуту)
    LIMITS = {
        'free': {
            'requests': 10,
            'window': 60,  # секунд
            'message': '⏱ Слишком быстро! Free план: макс 10 запросов/минуту.\n\n💡 Upgrade до Pro для снятия ограничений'
        },
        'pro': {
            'requests': 30,
            'window': 60,
            'message': '⏱ Превышен лимит запросов. Подожди минуту.'
        },
        'unlimited': {
            'requests': 100,
            'window': 60,
            'message': '⏱ Антифлуд защита. Подожди 30 секунд.'
        }
    }
    
    def __init__(self):
        self.user_requests: Dict[int, List[float]] = defaultdict(list)
        self.blocked_until: Dict[int, float] = {}
    
    def is_rate_limited(self, user_id: int, plan: str = 'free') -> tuple[bool, str]:
        """
        Проверка rate limit
        Returns: (заблокирован ли, сообщение)
        """
        now = time()
        
        # Проверка временной блокировки (при злоупотреблении)
        if user_id in self.blocked_until:
            if now < self.blocked_until[user_id]:
                remaining = int(self.blocked_until[user_id] - now)
                return True, f"🚫 Временная блокировка. Осталось: {remaining}с"
            else:
                del self.blocked_until[user_id]
        
        config = self.LIMITS.get(plan, self.LIMITS['free'])
        window = config['window']
        max_requests = config['requests']
        
        # Очистка старых запросов
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if now - req_time < window
        ]
        
        # Проверка лимита
        if len(self.user_requests[user_id]) >= max_requests:
            # Для free — блокировка на 2 минуты при злоупотреблении
            if plan == 'free' and len(self.user_requests[user_id]) > max_requests * 2:
                self.blocked_until[user_id] = now + 120
                return True, "🚫 Обнаружен флуд. Блокировка на 2 минуты."
            
            return True, config['message']
        
        # Добавление запроса
        self.user_requests[user_id].append(now)
        return False, ""
    
    def reset_user(self, user_id: int):
        """Сброс лимитов для пользователя (админ команда)"""
        if user_id in self.user_requests:
            del self.user_requests[user_id]
        if user_id in self.blocked_until:
            del self.blocked_until[user_id]
    
    def get_stats(self, user_id: int) -> Dict:
        """Статистика по пользователю"""
        now = time()
        recent_requests = [
            req for req in self.user_requests.get(user_id, [])
            if now - req < 60
        ]
        
        return {
            'requests_last_minute': len(recent_requests),
            'is_blocked': user_id in self.blocked_until,
            'blocked_until': self.blocked_until.get(user_id, 0)
        }

# Декоратор для хендлеров
def rate_limit(subscription_manager):
    """
    Декоратор для защиты хендлеров
    
    Usage:
        @rate_limit(sub_manager)
        async def my_handler(update, context):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            user_id = update.effective_user.id
            
            # Получаем план пользователя
            from utils.subscription_manager import SubscriptionManager
            sub_manager = subscription_manager
            sub = sub_manager.get_subscription(user_id)
            
            # Проверяем rate limit
            limiter = context.bot_data.get('rate_limiter')
            if not limiter:
                limiter = RateLimiter()
                context.bot_data['rate_limiter'] = limiter
            
            is_limited, message = limiter.is_rate_limited(user_id, sub.plan)
            
            if is_limited:
                await update.message.reply_text(message)
                return
            
            return await func(update, context)
        
        return wrapper
    return decorator
