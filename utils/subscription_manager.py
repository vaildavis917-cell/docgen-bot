"""
Система подписок с интеграцией CryptoPay
Поддержка: FREE, PRO, UNLIMITED тарифов
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Subscription:
    user_id: int
    plan: str  # 'free', 'pro', 'unlimited'
    start_date: str
    end_date: str
    generations_used: int = 0
    is_active: bool = True
    invoice_id: Optional[str] = None

class SubscriptionManager:
    """Менеджер подписок с персистентностью в JSON"""
    
    # Тарифные планы
    PLANS = {
        'free': {
            'name': '🆓 Free',
            'price': 0,
            'generations_daily': 5,
            'generations_total': None,
            'priority': False,
            'features': ['5 генераций/день', 'Базовые шаблоны']
        },
        'pro': {
            'name': '⭐ Pro',
            'price': 4.99,
            'currency': 'USD',
            'generations_daily': None,
            'generations_total': 500,
            'priority': True,
            'duration_days': 30,
            'features': ['500 генераций/месяц', 'Приоритетная обработка', 'Все шаблоны', 'История генераций']
        },
        'unlimited': {
            'name': '💎 Unlimited',
            'price': 19.99,
            'currency': 'USD',
            'generations_daily': None,
            'generations_total': -1,  # -1 = безлимит
            'priority': True,
            'duration_days': 30,
            'features': ['∞ Безлимит генераций', 'Максимальный приоритет', 'API доступ', 'Batch генерация', 'Приоритетная поддержка']
        }
    }
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.subs_file = self.data_dir / 'subscriptions.json'
        self.usage_file = self.data_dir / 'usage_daily.json'
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных из JSON"""
        # Подписки
        if self.subs_file.exists():
            with open(self.subs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.subscriptions = {
                    int(k): Subscription(**v) for k, v in data.items()
                }
        else:
            self.subscriptions = {}
        
        # Дневное использование
        if self.usage_file.exists():
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                self.daily_usage = json.load(f)
        else:
            self.daily_usage = {}
    
    def _save_data(self):
        """Сохранение данных в JSON"""
        # Подписки
        with open(self.subs_file, 'w', encoding='utf-8') as f:
            data = {str(k): asdict(v) for k, v in self.subscriptions.items()}
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Дневное использование
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(self.daily_usage, f, indent=2)
    
    def get_subscription(self, user_id: int) -> Subscription:
        """Получить подписку пользователя (создаёт FREE если нет)"""
        if user_id not in self.subscriptions:
            self.create_subscription(user_id, 'free')
        
        sub = self.subscriptions[user_id]
        
        # Проверка истечения
        if sub.plan != 'free' and datetime.fromisoformat(sub.end_date) < datetime.now():
            self.downgrade_to_free(user_id)
            sub = self.subscriptions[user_id]
        
        return sub
    
    def create_subscription(self, user_id: int, plan: str, invoice_id: Optional[str] = None):
        """Создать новую подписку"""
        now = datetime.now()
        
        if plan == 'free':
            end_date = now + timedelta(days=36500)  # 100 лет для free
        else:
            duration = self.PLANS[plan]['duration_days']
            end_date = now + timedelta(days=duration)
        
        sub = Subscription(
            user_id=user_id,
            plan=plan,
            start_date=now.isoformat(),
            end_date=end_date.isoformat(),
            generations_used=0,
            is_active=True,
            invoice_id=invoice_id
        )
        
        self.subscriptions[user_id] = sub
        self._save_data()
    
    def upgrade_subscription(self, user_id: int, plan: str, invoice_id: str):
        """Апгрейд подписки после оплаты"""
        self.create_subscription(user_id, plan, invoice_id)
    
    def downgrade_to_free(self, user_id: int):
        """Возврат на FREE план"""
        self.create_subscription(user_id, 'free')
    
    def can_generate(self, user_id: int) -> tuple[bool, str]:
        """
        Проверка возможности генерации
        Returns: (можно ли, причина отказа)
        """
        sub = self.get_subscription(user_id)
        plan_info = self.PLANS[sub.plan]
        
        # FREE план — проверка дневного лимита
        if sub.plan == 'free':
            today = datetime.now().date().isoformat()
            daily_key = f"{user_id}_{today}"
            used_today = self.daily_usage.get(daily_key, 0)
            
            if used_today >= plan_info['generations_daily']:
                return False, f"🚫 Дневной лимит исчерпан ({plan_info['generations_daily']}/день)\n\n💡 Апгрейд до Pro для 500 генераций/месяц"
        
        # PRO план — проверка месячного лимита
        elif sub.plan == 'pro':
            if sub.generations_used >= plan_info['generations_total']:
                return False, f"🚫 Месячный лимит исчерпан ({plan_info['generations_total']})\n\n💎 Перейди на Unlimited для безлимита"
        
        # UNLIMITED — всегда можно
        return True, ""
    
    def increment_usage(self, user_id: int):
        """Увеличить счётчик использования"""
        sub = self.get_subscription(user_id)
        
        # FREE — дневной счётчик
        if sub.plan == 'free':
            today = datetime.now().date().isoformat()
            daily_key = f"{user_id}_{today}"
            self.daily_usage[daily_key] = self.daily_usage.get(daily_key, 0) + 1
        
        # PRO/UNLIMITED — общий счётчик
        else:
            sub.generations_used += 1
        
        self._save_data()
    
    def get_usage_info(self, user_id: int) -> str:
        """Информация об использовании"""
        sub = self.get_subscription(user_id)
        plan_info = self.PLANS[sub.plan]
        
        lines = [
            f"📊 **Твоя подписка:** {plan_info['name']}",
            ""
        ]
        
        if sub.plan == 'free':
            today = datetime.now().date().isoformat()
            daily_key = f"{user_id}_{today}"
            used = self.daily_usage.get(daily_key, 0)
            limit = plan_info['generations_daily']
            lines.append(f"Использовано сегодня: {used}/{limit}")
        
        elif sub.plan == 'pro':
            used = sub.generations_used
            limit = plan_info['generations_total']
            lines.append(f"Использовано в месяце: {used}/{limit}")
            
            end = datetime.fromisoformat(sub.end_date)
            days_left = (end - datetime.now()).days
            lines.append(f"До окончания: {days_left} дней")
        
        else:  # unlimited
            lines.append(f"Использовано: {sub.generations_used} (безлимит)")
            end = datetime.fromisoformat(sub.end_date)
            days_left = (end - datetime.now()).days
            lines.append(f"До окончания: {days_left} дней")
        
        return "\n".join(lines)
    
    def get_pricing_message(self) -> str:
        """Красивое сообщение с тарифами"""
        msg = "💳 **ТАРИФНЫЕ ПЛАНЫ**\n\n"
        
        for plan_id, plan in self.PLANS.items():
            if plan_id == 'free':
                continue
            
            msg += f"{plan['name']}\n"
            msg += f"💰 ${plan['price']}/месяц\n\n"
            
            for feature in plan['features']:
                msg += f"  ✓ {feature}\n"
            
            msg += "\n"
        
        msg += "🎁 **ПЕРВЫЕ 3 ДНЯ PRO БЕСПЛАТНО**\n"
        msg += "🔥 Скидка 20% при оплате на год"
        
        return msg
    
    def cleanup_old_usage(self):
        """Очистка старых записей (запускать раз в день)"""
        cutoff = (datetime.now() - timedelta(days=7)).date().isoformat()
        
        keys_to_remove = [
            k for k in self.daily_usage.keys()
            if k.split('_')[1] < cutoff
        ]
        
        for key in keys_to_remove:
            del self.daily_usage[key]
        
        self._save_data()
    
    def get_admin_stats(self) -> str:
        """Статистика подписок для админа"""
        total = len(self.subscriptions)
        free_count = sum(1 for s in self.subscriptions.values() if s.plan == 'free')
        pro_count = sum(1 for s in self.subscriptions.values() if s.plan == 'pro')
        unlimited_count = sum(1 for s in self.subscriptions.values() if s.plan == 'unlimited')
        
        # Активные сегодня
        today = datetime.now().date().isoformat()
        active_today = sum(1 for k in self.daily_usage.keys() if today in k)
        
        # Общее количество генераций сегодня
        total_gens_today = sum(v for k, v in self.daily_usage.items() if today in k)
        
        return (
            f"👥 Всего пользователей: {total}\n"
            f"🆓 Free: {free_count}\n"
            f"⭐ Pro: {pro_count}\n"
            f"💎 Unlimited: {unlimited_count}\n\n"
            f"📊 Активных сегодня: {active_today}\n"
            f"🔄 Генераций сегодня: {total_gens_today}"
        )
