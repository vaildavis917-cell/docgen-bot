"""
Система локализации бота
"""

import json
import os
from typing import Dict, Any, Optional

# Путь к файлам локализации
LOCALES_DIR = "/home/ubuntu/docgen_bot/locales"

# Путь к файлу с настройками пользователей
USER_SETTINGS_FILE = "/home/ubuntu/docgen_bot/data/user_settings.json"

# Кэш загруженных локализаций
_locales_cache: Dict[str, Dict] = {}

# Доступные языки
AVAILABLE_LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "ua": "🇺🇦 Українська"
}

DEFAULT_LANGUAGE = "ru"


def load_locale(lang_code: str) -> Dict:
    """Загрузка файла локализации"""
    if lang_code in _locales_cache:
        return _locales_cache[lang_code]
    
    locale_file = os.path.join(LOCALES_DIR, f"{lang_code}.json")
    
    if not os.path.exists(locale_file):
        locale_file = os.path.join(LOCALES_DIR, f"{DEFAULT_LANGUAGE}.json")
    
    try:
        with open(locale_file, 'r', encoding='utf-8') as f:
            locale_data = json.load(f)
            _locales_cache[lang_code] = locale_data
            return locale_data
    except Exception as e:
        print(f"Error loading locale {lang_code}: {e}")
        return {}


def load_user_settings() -> Dict:
    """Загрузка настроек пользователей"""
    if not os.path.exists(USER_SETTINGS_FILE):
        return {}
    
    try:
        with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def save_user_settings(settings: Dict):
    """Сохранение настроек пользователей"""
    os.makedirs(os.path.dirname(USER_SETTINGS_FILE), exist_ok=True)
    
    with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def is_new_user(user_id: int) -> bool:
    """Проверка, новый ли пользователь (не выбирал язык)"""
    settings = load_user_settings()
    user_data = settings.get(str(user_id), {})
    return "language" not in user_data


def get_user_language(user_id: int) -> str:
    """Получение языка пользователя"""
    settings = load_user_settings()
    return settings.get(str(user_id), {}).get("language", DEFAULT_LANGUAGE)


def set_user_language(user_id: int, lang_code: str) -> bool:
    """Установка языка пользователя"""
    if lang_code not in AVAILABLE_LANGUAGES:
        return False
    
    settings = load_user_settings()
    
    if str(user_id) not in settings:
        settings[str(user_id)] = {}
    
    settings[str(user_id)]["language"] = lang_code
    save_user_settings(settings)
    
    # Очистить кэш для обновления
    _locales_cache.clear()
    
    return True


def get_text(key: str, user_id: int = None, **kwargs) -> str:
    """
    Получение локализованного текста
    
    Пример использования:
    get_text("subscription.activated", user_id)
    get_text("welcome", user_id)
    """
    if user_id is None:
        lang_code = DEFAULT_LANGUAGE
    else:
        lang_code = get_user_language(user_id)
    
    locale = load_locale(lang_code)
    
    # Разбиваем ключ по точкам для вложенных значений
    keys = key.split(".")
    value = locale
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # Если ключ не найден, пробуем русскую локализацию
            ru_locale = load_locale(DEFAULT_LANGUAGE)
            value = ru_locale
            for k2 in keys:
                if isinstance(value, dict) and k2 in value:
                    value = value[k2]
                else:
                    return key  # Возвращаем ключ, если не найдено
            break
    
    # Подставляем переменные
    if isinstance(value, str) and kwargs:
        try:
            value = value.format(**kwargs)
        except:
            pass
    
    return value if isinstance(value, str) else key


def t(key: str, user_id: int = None, **kwargs) -> str:
    """Короткий алиас для get_text"""
    return get_text(key, user_id, **kwargs)
