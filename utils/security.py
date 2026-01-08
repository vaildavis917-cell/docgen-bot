"""
Модуль безопасности для DocGen Bot
Защита от спама, флуда, инъекций и других атак
"""

import os
import re
import time
import hashlib
import logging
import threading
from collections import defaultdict
from typing import Optional, Tuple, List, Set
from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Админы исключены из проверок безопасности
ADMIN_IDS = set()
admin_str = os.getenv('ADMIN_IDS', '')
if admin_str:
    ADMIN_IDS = set(int(x.strip()) for x in admin_str.split(',') if x.strip().isdigit())
admin_operator = os.getenv('ADMIN_OPERATOR_ID', '')
if admin_operator and admin_operator.isdigit():
    ADMIN_IDS.add(int(admin_operator))


class AntiFlood:
    """
    Защита от флуда - ограничение частоты сообщений
    Более мягкие лимиты для нормальной работы
    """
    
    def __init__(
        self,
        max_messages: int = 30,  # 30 сообщений
        window_seconds: int = 60,  # за 60 секунд
        ban_duration: int = 60  # 1 минута бан
    ):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.ban_duration = ban_duration
        self.messages: dict = defaultdict(list)
        self.banned_until: dict = {}
        self._lock = threading.Lock()
        self.enabled = True  # Флаг включения
    
    def check(self, user_id: int) -> Tuple[bool, Optional[int]]:
        """
        Проверяет, разрешено ли сообщение
        Returns: (allowed, ban_seconds_remaining)
        """
        # Если антифлуд выключен
        if not self.enabled:
            return True, None
        
        # Админы всегда разрешены
        if user_id in ADMIN_IDS:
            return True, None
        
        now = time.time()
        
        with self._lock:
            # Проверяем бан
            if user_id in self.banned_until:
                if now < self.banned_until[user_id]:
                    remaining = int(self.banned_until[user_id] - now)
                    return False, remaining
                else:
                    del self.banned_until[user_id]
            
            # Очищаем старые сообщения
            self.messages[user_id] = [
                t for t in self.messages[user_id]
                if now - t < self.window_seconds
            ]
            
            # Проверяем лимит
            if len(self.messages[user_id]) >= self.max_messages:
                # Баним за флуд
                self.banned_until[user_id] = now + self.ban_duration
                logger.warning(f"User {user_id} banned for flooding")
                return False, self.ban_duration
            
            self.messages[user_id].append(now)
            return True, None
    
    def is_banned(self, user_id: int) -> bool:
        """Проверяет, забанен ли пользователь"""
        if user_id in ADMIN_IDS:
            return False
        with self._lock:
            if user_id in self.banned_until:
                if time.time() < self.banned_until[user_id]:
                    return True
                del self.banned_until[user_id]
            return False
    
    def unban(self, user_id: int):
        """Разбанивает пользователя"""
        with self._lock:
            if user_id in self.banned_until:
                del self.banned_until[user_id]


class AntiSpam:
    """
    Защита от спама - обнаружение повторяющихся сообщений
    """
    
    def __init__(
        self,
        duplicate_threshold: int = 10,  # 10 одинаковых сообщений
        window_seconds: int = 60
    ):
        self.duplicate_threshold = duplicate_threshold
        self.window_seconds = window_seconds
        self.message_hashes: dict = defaultdict(list)
        self._lock = threading.Lock()
    
    def _hash_message(self, text: str) -> str:
        """Создаёт хэш сообщения"""
        normalized = text.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def check(self, user_id: int, message: str) -> Tuple[bool, str]:
        """
        Проверяет сообщение на спам
        Returns: (is_spam, reason)
        """
        # Админы не проверяются
        if user_id in ADMIN_IDS:
            return False, None
        
        now = time.time()
        msg_hash = self._hash_message(message)
        
        with self._lock:
            # Очищаем старые записи
            self.message_hashes[user_id] = [
                (h, t) for h, t in self.message_hashes[user_id]
                if now - t < self.window_seconds
            ]
            
            # Считаем дубликаты
            duplicates = sum(1 for h, _ in self.message_hashes[user_id] if h == msg_hash)
            
            if duplicates >= self.duplicate_threshold:
                logger.warning(f"Spam detected from user {user_id}: duplicate messages")
                return True, "duplicate_messages"
            
            self.message_hashes[user_id].append((msg_hash, now))
            return False, None


class InputValidator:
    """
    Валидация и санитизация пользовательского ввода
    """
    
    # Опасные паттерны (только самые критичные)
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__',
        r'subprocess',
        r'os\.system',
    ]
    
    MAX_LENGTHS = {
        'message': 4096,
        'username': 64,
        'url': 2048,
        'filename': 255,
    }
    
    ALLOWED_PATTERNS = {
        'username': r'^[a-zA-Z0-9_]{1,64}$',
        'user_id': r'^\d{1,20}$',
        'url': r'^https?://[^\s<>"{}|\\^`\[\]]+$',
        'filename': r'^[a-zA-Z0-9_\-\.]+$',
    }
    
    def __init__(self):
        self._dangerous_regex = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.DANGEROUS_PATTERNS]
    
    def sanitize_text(self, text: str, max_length: int = 4096) -> str:
        """Санитизирует текст"""
        if not text:
            return ""
        text = text[:max_length]
        text = text.replace('\x00', '')
        return text.strip()
    
    def check_dangerous(self, text: str) -> Tuple[bool, Optional[str]]:
        """Проверяет на опасные паттерны"""
        if not text:
            return False, None
        
        for i, regex in enumerate(self._dangerous_regex):
            if regex.search(text):
                return True, self.DANGEROUS_PATTERNS[i]
        
        return False, None
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Валидирует URL"""
        if not url:
            return False, "URL пустой"
        
        if len(url) > self.MAX_LENGTHS['url']:
            return False, "URL слишком длинный"
        
        if not re.match(self.ALLOWED_PATTERNS['url'], url):
            return False, "Некорректный формат URL"
        
        blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0']
        for host in blocked_hosts:
            if host in url.lower():
                return False, "Локальные адреса запрещены"
        
        return True, "OK"
    
    def validate_user_id(self, user_id: str) -> Tuple[bool, str]:
        """Валидирует ID пользователя"""
        if not user_id:
            return False, "ID пустой"
        
        if not re.match(self.ALLOWED_PATTERNS['user_id'], str(user_id)):
            return False, "Некорректный ID"
        
        return True, "OK"


class SecurityLogger:
    """Логирование событий безопасности"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.events: List[dict] = []
        self.max_events = 1000
    
    def log_event(self, event_type: str, user_id: int, details: str, severity: str = "INFO"):
        """Записывает событие"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "user_id": user_id,
            "details": details,
            "severity": severity
        }
        
        with self._lock:
            self.events.append(event)
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
        
        if severity == "WARNING":
            logger.warning(f"[{event_type}] User {user_id}: {details}")
        elif severity == "ERROR":
            logger.error(f"[{event_type}] User {user_id}: {details}")


class BotDetector:
    """Простой детектор ботов (заглушка)"""
    
    def __init__(self):
        self.actions = defaultdict(list)
    
    def record_action(self, user_id: int, action: str):
        """Records user action"""
        self.actions[user_id].append((time.time(), action))
        # Keep only last 100 actions
        if len(self.actions[user_id]) > 100:
            self.actions[user_id] = self.actions[user_id][-100:]
    
    def is_likely_bot(self, user_id: int) -> bool:
        """Always returns False - disabled"""
        return False


# Глобальные экземпляры с мягкими лимитами
anti_flood = AntiFlood(max_messages=30, window_seconds=60, ban_duration=60)
anti_spam = AntiSpam(duplicate_threshold=10, window_seconds=60)
input_validator = InputValidator()
security_logger = SecurityLogger()
bot_detector = BotDetector()


def security_check(func):
    """
    Декоратор для проверки безопасности
    Админы пропускаются без проверок
    """
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        if not user:
            return await func(update, context, *args, **kwargs)
        
        user_id = user.id
        
        # Админы пропускаются без проверок
        if user_id in ADMIN_IDS:
            return await func(update, context, *args, **kwargs)
        
        # 1. Проверка на флуд
        allowed, ban_time = anti_flood.check(user_id)
        if not allowed:
            try:
                if update.callback_query:
                    await update.callback_query.answer(
                        f"⚠️ Подождите {ban_time} сек.",
                        show_alert=True
                    )
                elif update.message:
                    await update.message.reply_text(
                        f"⚠️ Слишком много запросов! Подождите {ban_time} секунд."
                    )
            except:
                pass
            return
        
        # 2. Проверка на спам (только для текста)
        if update.message and update.message.text:
            is_spam, reason = anti_spam.check(user_id, update.message.text)
            if is_spam:
                try:
                    await update.message.reply_text(
                        "⚠️ Пожалуйста, не отправляйте одинаковые сообщения."
                    )
                except:
                    pass
                return
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def validate_url_input(url: str) -> Tuple[bool, str]:
    """Валидирует URL"""
    return input_validator.validate_url(url)


def sanitize_user_input(text: str, max_length: int = 4096) -> str:
    """Санитизирует ввод"""
    return input_validator.sanitize_text(text, max_length)


def get_security_stats() -> dict:
    """Статистика безопасности"""
    return {
        "flood_bans": len(anti_flood.banned_until),
        "security_events": len(security_logger.events),
        "max_messages": anti_flood.max_messages,
        "window_seconds": anti_flood.window_seconds,
        "ban_duration": anti_flood.ban_duration,
        "enabled": anti_flood.enabled if hasattr(anti_flood, 'enabled') else True,
    }


def set_antiflood_limit(max_messages: int):
    """Устанавливает лимит сообщений"""
    anti_flood.max_messages = max(5, min(100, max_messages))
    return anti_flood.max_messages


def set_antiflood_ban_duration(seconds: int):
    """Устанавливает длительность бана"""
    anti_flood.ban_duration = max(10, min(3600, seconds))
    return anti_flood.ban_duration


def reset_all_flood_bans():
    """Сбрасывает все баны за флуд"""
    with anti_flood._lock:
        count = len(anti_flood.banned_until)
        anti_flood.banned_until.clear()
        anti_flood.messages.clear()
    return count


def enable_antiflood():
    """Включает антифлуд"""
    anti_flood.enabled = True


def disable_antiflood():
    """Выключает антифлуд"""
    anti_flood.enabled = False
