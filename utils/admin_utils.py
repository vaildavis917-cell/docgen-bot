"""
Утилиты для администрирования бота
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Пути к файлам данных
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
BANNED_FILE = os.path.join(DATA_DIR, "banned.json")
BOT_STATE_FILE = os.path.join(DATA_DIR, "bot_state.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# Администраторы (задаётся через переменную окружения ADMIN_IDS)
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]


def _ensure_data_dir():
    """Создаёт директорию data если её нет"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _load_json(filepath: str, default: dict = None) -> dict:
    """Загружает JSON файл"""
    _ensure_data_dir()
    if default is None:
        default = {}
    
    if not os.path.exists(filepath):
        return default
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def _save_json(filepath: str, data: dict) -> bool:
    """Сохраняет JSON файл"""
    _ensure_data_dir()
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error(f"Ошибка сохранения {filepath}: {e}")
        return False


# === Система бана ===

def is_banned(user_id: int) -> bool:
    """Проверяет, забанен ли пользователь"""
    data = _load_json(BANNED_FILE, {"banned_users": {}})
    return str(user_id) in data.get("banned_users", {})


def ban_user(user_id: int, banned_by: int, reason: str = None) -> bool:
    """Банит пользователя"""
    data = _load_json(BANNED_FILE, {"banned_users": {}})
    
    if "banned_users" not in data:
        data["banned_users"] = {}
    
    data["banned_users"][str(user_id)] = {
        "banned_at": datetime.now().isoformat(),
        "banned_by": banned_by,
        "reason": reason
    }
    
    return _save_json(BANNED_FILE, data)


def unban_user(user_id: int) -> bool:
    """Разбанивает пользователя"""
    data = _load_json(BANNED_FILE, {"banned_users": {}})
    
    if str(user_id) in data.get("banned_users", {}):
        del data["banned_users"][str(user_id)]
        return _save_json(BANNED_FILE, data)
    
    return False


def get_banned_list() -> List[Dict]:
    """Получает список забаненных пользователей"""
    data = _load_json(BANNED_FILE, {"banned_users": {}})
    banned = data.get("banned_users", {})
    
    result = []
    for user_id, info in banned.items():
        result.append({
            "user_id": int(user_id),
            "banned_at": info.get("banned_at"),
            "banned_by": info.get("banned_by"),
            "reason": info.get("reason")
        })
    
    return result


# === Режим обслуживания ===

def is_maintenance_mode() -> bool:
    """Проверяет, включен ли режим обслуживания"""
    data = _load_json(BOT_STATE_FILE, {"maintenance": False})
    return data.get("maintenance", False)


def set_maintenance_mode(enabled: bool, message: str = None) -> bool:
    """Устанавливает режим обслуживания"""
    data = _load_json(BOT_STATE_FILE, {})
    data["maintenance"] = enabled
    data["maintenance_message"] = message or "🔧 Бот на техническом обслуживании. Пожалуйста, подождите."
    data["maintenance_updated"] = datetime.now().isoformat()
    return _save_json(BOT_STATE_FILE, data)


def get_maintenance_message() -> str:
    """Получает сообщение о режиме обслуживания"""
    data = _load_json(BOT_STATE_FILE, {})
    return data.get("maintenance_message", "🔧 Бот на техническом обслуживании. Пожалуйста, подождите.")


# === Управление пользователями ===

def register_user(user_id: int, username: str = None, first_name: str = None, language: str = "ru"):
    """Регистрирует нового пользователя"""
    data = _load_json(USERS_FILE, {"users": {}})
    
    if "users" not in data:
        data["users"] = {}
    
    user_key = str(user_id)
    
    if user_key not in data["users"]:
        data["users"][user_key] = {
            "registered_at": datetime.now().isoformat(),
            "username": username,
            "first_name": first_name,
            "language": language,
            "last_active": datetime.now().isoformat()
        }
    else:
        # Обновляем данные
        data["users"][user_key]["username"] = username
        data["users"][user_key]["first_name"] = first_name
        data["users"][user_key]["last_active"] = datetime.now().isoformat()
    
    _save_json(USERS_FILE, data)


def get_user_info(user_id: int) -> Optional[Dict]:
    """Получает информацию о пользователе"""
    data = _load_json(USERS_FILE, {"users": {}})
    return data.get("users", {}).get(str(user_id))


def get_all_users() -> List[int]:
    """Получает список всех ID пользователей"""
    data = _load_json(USERS_FILE, {"users": {}})
    return [int(uid) for uid in data.get("users", {}).keys()]


def get_users_count() -> int:
    """Получает количество пользователей"""
    data = _load_json(USERS_FILE, {"users": {}})
    return len(data.get("users", {}))


def get_active_users_today() -> int:
    """Получает количество активных пользователей за сегодня"""
    data = _load_json(USERS_FILE, {"users": {}})
    today = datetime.now().strftime("%Y-%m-%d")
    
    count = 0
    for user_data in data.get("users", {}).values():
        last_active = user_data.get("last_active", "")
        if last_active.startswith(today):
            count += 1
    
    return count


# === Статистика ===

def get_bot_stats() -> Dict[str, Any]:
    """Получает общую статистику бота"""
    from utils.subscription import load_subscriptions, SUBSCRIPTION_PLANS
    
    users_data = _load_json(USERS_FILE, {"users": {}})
    subs_data = load_subscriptions()
    
    total_users = len(users_data.get("users", {}))
    active_today = get_active_users_today()
    
    # Подсчёт подписок
    subscriptions = {"free": 0, "basic": 0, "pro": 0, "premium": 0, "lifetime": 0}
    
    for user_id, user_sub in subs_data.get("users", {}).items():
        plan = user_sub.get("plan", "free")
        if plan in subscriptions:
            subscriptions[plan] += 1
    
    # VIP из вайтлиста
    try:
        from utils.whitelist import get_vip_count
        vip_count = get_vip_count()
    except:
        vip_count = 0
    
    # Забаненные
    banned_data = _load_json(BANNED_FILE, {"banned_users": {}})
    banned_count = len(banned_data.get("banned_users", {}))
    
    return {
        "total_users": total_users,
        "active_today": active_today,
        "subscriptions": subscriptions,
        "vip_count": vip_count,
        "banned_count": banned_count
    }


def get_top_users(limit: int = 10) -> List[Dict]:
    """Получает топ активных пользователей по использованию"""
    from utils.subscription import load_subscriptions
    
    subs_data = load_subscriptions()
    usage_data = subs_data.get("usage", {})
    
    # Считаем общее использование за все дни
    user_totals = {}
    
    for user_id, dates in usage_data.items():
        total = 0
        for date, usage in dates.items():
            total += sum(usage.values())
        user_totals[user_id] = total
    
    # Сортируем и берём топ
    sorted_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    result = []
    for user_id, total in sorted_users:
        user_info = get_user_info(int(user_id))
        result.append({
            "user_id": int(user_id),
            "username": user_info.get("username") if user_info else None,
            "total_usage": total
        })
    
    return result
