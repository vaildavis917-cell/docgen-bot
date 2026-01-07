"""
Система вайтлиста для бесплатных пожизненных подписок
"""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Путь к файлу вайтлиста
WHITELIST_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "whitelist.json")

# Администраторы, которые могут управлять вайтлистом
# Задаётся через переменную окружения ADMIN_IDS (через запятую)
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]


def _ensure_data_dir():
    """Создаёт директорию data если её нет"""
    data_dir = os.path.dirname(WHITELIST_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


def _load_whitelist():
    """Загружает вайтлист из файла"""
    _ensure_data_dir()
    
    if not os.path.exists(WHITELIST_FILE):
        return {"vip_users": {}}
    
    try:
        with open(WHITELIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"vip_users": {}}


def _save_whitelist(data):
    """Сохраняет вайтлист в файл"""
    _ensure_data_dir()
    
    try:
        with open(WHITELIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error(f"Ошибка сохранения вайтлиста: {e}")
        return False


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    return user_id in ADMIN_IDS


def is_vip(user_id: int) -> bool:
    """Проверяет, есть ли пользователь в вайтлисте (VIP)"""
    data = _load_whitelist()
    return str(user_id) in data.get("vip_users", {})


def add_vip(user_id: int, added_by: int, note: str = None) -> bool:
    """
    Добавляет пользователя в вайтлист
    
    Args:
        user_id: ID пользователя для добавления
        added_by: ID администратора, который добавил
        note: Примечание (опционально)
    
    Returns:
        True если успешно, False если ошибка
    """
    data = _load_whitelist()
    
    if "vip_users" not in data:
        data["vip_users"] = {}
    
    data["vip_users"][str(user_id)] = {
        "added_at": datetime.now().isoformat(),
        "added_by": added_by,
        "note": note
    }
    
    return _save_whitelist(data)


def remove_vip(user_id: int) -> bool:
    """
    Удаляет пользователя из вайтлиста
    
    Args:
        user_id: ID пользователя для удаления
    
    Returns:
        True если успешно удалён, False если не найден или ошибка
    """
    data = _load_whitelist()
    
    if str(user_id) in data.get("vip_users", {}):
        del data["vip_users"][str(user_id)]
        return _save_whitelist(data)
    
    return False


def get_vip_list() -> list:
    """
    Получает список всех VIP пользователей
    
    Returns:
        Список словарей с информацией о VIP пользователях
    """
    data = _load_whitelist()
    vip_users = data.get("vip_users", {})
    
    result = []
    for user_id, info in vip_users.items():
        result.append({
            "user_id": int(user_id),
            "added_at": info.get("added_at"),
            "added_by": info.get("added_by"),
            "note": info.get("note")
        })
    
    return result


def get_vip_count() -> int:
    """Возвращает количество VIP пользователей"""
    data = _load_whitelist()
    return len(data.get("vip_users", {}))
