"""
Система подписок и премиум функций (Crypto Bot)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Путь к файлу с подписками
SUBSCRIPTIONS_FILE = "/home/ubuntu/docgen_bot/data/subscriptions.json"

# Ссылка на канал проекта
PROJECT_CHANNEL = "https://t.me/+VGUeNxCWYLEzYzU0"

# Тарифные планы с ценами в USD (для Crypto Bot) и Stars
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "icon": "🆓",
        "price_usd": 0,
        "price_stars": 0,
        "duration_days": 0,  # Бессрочно
        "limits": {
            "photos_per_day": 3,
            "videos_per_day": 1,
            "exif_per_day": 3,
            "selfies_per_day": 2,
            "addresses_per_day": 5,
            "cards_per_day": 3,
            "twofa_per_day": 5,
            "antidetect_per_day": 2,
            "text_per_day": 3,
            "gplay_per_day": 2,
            "site_per_day": 1,
            "tiktok_per_day": 2,
        },
        "features": [
            "Уникализация фото (3/день)",
            "Уникализация видео (1/день)",
            "EXIF редактор (3/день)",
            "Генератор селфи (2/день)",
            "Генератор адресов (5/день)",
        ]
    },
    "basic": {
        "name": "Basic",
        "icon": "⭐",
        "price_usd": 15,
        "price_stars": 150,
        "duration_days": 30,
        "limits": {
            "photos_per_day": 30,
            "videos_per_day": 10,
            "exif_per_day": 30,
            "selfies_per_day": 20,
            "addresses_per_day": 50,
            "cards_per_day": 30,
            "twofa_per_day": 50,
            "antidetect_per_day": 20,
            "text_per_day": 30,
            "gplay_per_day": 20,
            "site_per_day": 10,
            "tiktok_per_day": 20,
        },
        "features": [
            "Уникализация фото (30/день)",
            "Уникализация видео (10/день)",
            "EXIF редактор (30/день)",
            "Генератор селфи (20/день)",
            "Генератор адресов (50/день)",
            "Генератор карт (30/день)",
            "Приоритетная обработка",
        ]
    },
    "pro": {
        "name": "Professional",
        "icon": "💎",
        "price_usd": 20,
        "price_stars": 200,
        "duration_days": 30,
        "limits": {
            "photos_per_day": 100,
            "videos_per_day": 30,
            "exif_per_day": 100,
            "selfies_per_day": 50,
            "addresses_per_day": 200,
            "cards_per_day": 100,
            "twofa_per_day": 200,
            "antidetect_per_day": 50,
            "text_per_day": 100,
            "gplay_per_day": 50,
            "site_per_day": 30,
            "tiktok_per_day": 50,
        },
        "features": [
            "Уникализация фото (100/день)",
            "Уникализация видео (30/день)",
            "EXIF редактор (100/день)",
            "Генератор селфи (50/день)",
            "Все генераторы (100+/день)",
            "Максимальная скорость",
            "Приоритетная поддержка",
        ]
    },
    "premium": {
        "name": "Premium",
        "icon": "👑",
        "price_usd": 30,
        "price_stars": 300,
        "duration_days": 30,
        "limits": {
            "photos_per_day": -1,
            "videos_per_day": -1,
            "exif_per_day": -1,
            "selfies_per_day": -1,
            "addresses_per_day": -1,
            "cards_per_day": -1,
            "twofa_per_day": -1,
            "antidetect_per_day": -1,
            "text_per_day": -1,
            "gplay_per_day": -1,
            "site_per_day": -1,
            "tiktok_per_day": -1,
        },
        "features": [
            "Безлимитная уникализация фото/видео",
            "Безлимитные генераторы",
            "Полный EXIF редактор",
            "Антидетект профили без лимитов",
            "VIP поддержка",
        ]
    },
    "lifetime": {
        "name": "Lifetime",
        "icon": "💎",
        "price_usd": 200,
        "price_stars": 2000,
        "duration_days": -1,  # -1 = пожизненно
        "limits": {
            "photos_per_day": -1,
            "videos_per_day": -1,
            "exif_per_day": -1,
            "selfies_per_day": -1,
            "addresses_per_day": -1,
            "cards_per_day": -1,
            "twofa_per_day": -1,
            "antidetect_per_day": -1,
            "text_per_day": -1,
            "gplay_per_day": -1,
            "site_per_day": -1,
            "tiktok_per_day": -1,
        },
        "features": [
            "Все функции НАВСЕГДА",
            "Безлимитная уникализация",
            "Безлимитные генераторы",
            "Максимальная скорость",
            "VIP поддержка навсегда",
            "Все будущие обновления",
        ]
    }
}


def ensure_data_dir():
    """Создание директории для данных"""
    os.makedirs(os.path.dirname(SUBSCRIPTIONS_FILE), exist_ok=True)


def load_subscriptions() -> Dict[str, Any]:
    """Загрузка данных о подписках"""
    ensure_data_dir()
    if os.path.exists(SUBSCRIPTIONS_FILE):
        with open(SUBSCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "usage": {}}


def save_subscriptions(data: Dict[str, Any]):
    """Сохранение данных о подписках"""
    ensure_data_dir()
    with open(SUBSCRIPTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_subscription(user_id: int) -> str:
    """Получение текущей подписки пользователя"""
    # Проверяем VIP вайтлист (бесплатная пожизненная подписка)
    try:
        from utils.whitelist import is_vip
        if is_vip(user_id):
            return "lifetime"
    except ImportError:
        pass
    
    data = load_subscriptions()
    user_data = data.get("users", {}).get(str(user_id), {})
    
    if not user_data:
        return "free"
    
    plan = user_data.get("plan", "free")
    
    # Пожизненная подписка не истекает
    if plan == "lifetime":
        return "lifetime"
    
    # Проверка срока действия
    if user_data.get("expires_at"):
        expires = datetime.fromisoformat(user_data["expires_at"])
        if datetime.now() > expires:
            return "free"
    
    return plan


def set_user_subscription(user_id: int, plan: str, duration_days: int = None):
    """Установка подписки пользователю"""
    if plan not in SUBSCRIPTION_PLANS:
        return False
    
    data = load_subscriptions()
    if "users" not in data:
        data["users"] = {}
    
    if duration_days is None:
        duration_days = SUBSCRIPTION_PLANS[plan]["duration_days"]
    
    expires_at = None
    if duration_days > 0:
        expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
    elif duration_days == -1:
        # Пожизненная подписка
        expires_at = None
    
    data["users"][str(user_id)] = {
        "plan": plan,
        "activated_at": datetime.now().isoformat(),
        "expires_at": expires_at
    }
    
    save_subscriptions(data)
    return True


def get_user_limits(user_id: int) -> Dict[str, int]:
    """Получение лимитов пользователя"""
    plan = get_user_subscription(user_id)
    return SUBSCRIPTION_PLANS[plan]["limits"]


def get_user_usage(user_id: int, date: str = None) -> Dict[str, int]:
    """Получение использования за день"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    data = load_subscriptions()
    usage = data.get("usage", {}).get(str(user_id), {}).get(date, {})
    
    return {
        "photos": usage.get("photos", 0),
        "videos": usage.get("videos", 0),
        "exif": usage.get("exif", 0),
        "selfies": usage.get("selfies", 0),
        "addresses": usage.get("addresses", 0),
        "cards": usage.get("cards", 0),
        "twofa": usage.get("twofa", 0),
        "antidetect": usage.get("antidetect", 0),
        "text": usage.get("text", 0),
        "gplay": usage.get("gplay", 0),
        "site": usage.get("site", 0),
        "tiktok": usage.get("tiktok", 0),
    }


def increment_usage(user_id: int, usage_type: str, count: int = 1):
    """Увеличение счётчика использования"""
    date = datetime.now().strftime("%Y-%m-%d")
    
    data = load_subscriptions()
    if "usage" not in data:
        data["usage"] = {}
    if str(user_id) not in data["usage"]:
        data["usage"][str(user_id)] = {}
    if date not in data["usage"][str(user_id)]:
        data["usage"][str(user_id)][date] = {}
    
    current = data["usage"][str(user_id)][date].get(usage_type, 0)
    data["usage"][str(user_id)][date][usage_type] = current + count
    
    save_subscriptions(data)


def check_limit(user_id: int, usage_type: str) -> tuple[bool, int, int]:
    """
    Проверка лимита
    Возвращает: (можно_использовать, использовано, лимит)
    """
    limits = get_user_limits(user_id)
    usage = get_user_usage(user_id)
    
    limit_map = {
        "photos": "photos_per_day",
        "videos": "videos_per_day",
        "exif": "exif_per_day",
        "selfies": "selfies_per_day",
        "addresses": "addresses_per_day",
        "cards": "cards_per_day",
        "twofa": "twofa_per_day",
        "antidetect": "antidetect_per_day",
        "text": "text_per_day",
        "gplay": "gplay_per_day",
        "site": "site_per_day",
        "tiktok": "tiktok_per_day",
    }
    
    limit_key = limit_map.get(usage_type)
    if not limit_key:
        return True, 0, -1
    
    limit = limits.get(limit_key, 0)
    used = usage.get(usage_type, 0)
    
    if limit == -1:  # Безлимит
        return True, used, -1
    
    return used < limit, used, limit


def format_subscription_info(user_id: int) -> str:
    """Форматирование информации о подписке"""
    # Проверяем VIP статус
    is_vip_user = False
    try:
        from utils.whitelist import is_vip
        is_vip_user = is_vip(user_id)
    except ImportError:
        pass
    
    plan_id = get_user_subscription(user_id)
    plan = SUBSCRIPTION_PLANS[plan_id]
    usage = get_user_usage(user_id)
    limits = plan["limits"]
    
    data = load_subscriptions()
    user_data = data.get("users", {}).get(str(user_id), {})
    
    # Если VIP от админа - показываем специальное сообщение
    if is_vip_user:
        text = "👑 **Ваша подписка: VIP от Админа**\n\n"
        text += "⏳ Срок: **НАВСЕГДА** ♾\n\n"
    else:
        text = f"{plan['icon']} **Ваша подписка: {plan['name']}**\n\n"
        
        if plan_id == "lifetime":
            text += "⏳ Срок: **НАВСЕГДА** ♾\n\n"
        elif user_data.get("expires_at"):
            expires = datetime.fromisoformat(user_data["expires_at"])
            days_left = (expires - datetime.now()).days
            text += f"⏳ Осталось дней: **{days_left}**\n\n"
    
    text += "📊 **Использование сегодня:**\n"
    
    usage_items = [
        ("photos", "photos_per_day", "🖼 Фото"),
        ("videos", "videos_per_day", "🎬 Видео"),
        ("exif", "exif_per_day", "📷 EXIF"),
        ("selfies", "selfies_per_day", "🤳 Селфи"),
        ("addresses", "addresses_per_day", "🏠 Адреса"),
        ("cards", "cards_per_day", "💳 Карты"),
        ("twofa", "twofa_per_day", "🔐 2FA"),
        ("antidetect", "antidetect_per_day", "🤖 Антидетект"),
    ]
    
    for usage_key, limit_key, label in usage_items:
        used = usage.get(usage_key, 0)
        limit = limits.get(limit_key, 0)
        if limit == -1:
            text += f"   {label}: {used} / ∞\n"
        else:
            text += f"   {label}: {used} / {limit}\n"
    
    text += f"\n📢 Канал проекта: {PROJECT_CHANNEL}"
    
    return text


def format_plans_list() -> str:
    """Форматирование списка тарифов"""
    text = "💎 **Тарифные планы**\n\n"
    text += "Оплата: 💰 Криптовалюта | ⭐ Telegram Stars\n\n"
    
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        if plan_id == "free":
            text += f"{plan['icon']} **{plan['name']}** — Бесплатно\n\n"
        elif plan_id == "lifetime":
            text += f"{plan['icon']} **{plan['name']}** — ${plan['price_usd']} / {plan['price_stars']}⭐ (навсегда)\n\n"
        else:
            text += f"{plan['icon']} **{plan['name']}** — ${plan['price_usd']}/мес / {plan['price_stars']}⭐\n\n"
    
    text += f"📢 Канал проекта: {PROJECT_CHANNEL}"
    
    return text


def get_plan_details(plan_id: str) -> str:
    """Детальная информация о тарифе"""
    if plan_id not in SUBSCRIPTION_PLANS:
        return "Тариф не найден"
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    limits = plan["limits"]
    
    text = f"{plan['icon']} **Подписка {plan['name']}**\n\n"
    
    if plan['price_usd'] > 0:
        text += f"💰 **Стоимость:** ${plan['price_usd']} / {plan['price_stars']}⭐\n"
        if plan['duration_days'] == -1:
            text += f"📅 **Срок:** НАВСЕГДА ♾\n"
        else:
            text += f"📅 **Срок:** {plan['duration_days']} дней\n"
        text += f"💎 **Оплата:** Криптовалюта или Telegram Stars\n\n"
    else:
        text += "💰 **Стоимость:** Бесплатно\n\n"
    
    text += "✨ **Возможности:**\n"
    for feature in plan['features']:
        text += f"   ✓ {feature}\n"
    
    text += "\n📊 **Дневные лимиты:**\n"
    
    limit_names = {
        "photos_per_day": "🖼 Уникализация фото",
        "videos_per_day": "🎬 Уникализация видео",
        "exif_per_day": "📷 EXIF редактор",
        "selfies_per_day": "🤳 Генератор селфи",
        "addresses_per_day": "🏠 Генератор адресов",
        "cards_per_day": "💳 Генератор карт",
        "twofa_per_day": "🔐 Генератор 2FA",
        "antidetect_per_day": "🤖 Антидетект данные",
        "text_per_day": "📝 Уникализация текста",
        "gplay_per_day": "✅ Чекер Google Play",
        "site_per_day": "🌐 Скачать сайт",
        "tiktok_per_day": "🎵 Скачать TikTok",
    }
    
    for key, name in limit_names.items():
        value = limits.get(key, 0)
        if value == -1:
            text += f"   {name}: ∞\n"
        else:
            text += f"   {name}: {value}\n"
    
    return text


def get_plan_price_usd(plan_id: str) -> float:
    """Получение цены тарифа в USD"""
    if plan_id not in SUBSCRIPTION_PLANS:
        return 0
    return SUBSCRIPTION_PLANS[plan_id]["price_usd"]


def get_plan_stars_price(plan_id: str) -> int:
    """Получение цены тарифа в Telegram Stars"""
    if plan_id not in SUBSCRIPTION_PLANS:
        return 0
    return SUBSCRIPTION_PLANS[plan_id].get("price_stars", 0)
