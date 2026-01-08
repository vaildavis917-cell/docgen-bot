"""
Модуль оптимизации производительности для 300+ пользователей
"""

import asyncio
import time
import logging
from collections import defaultdict
from functools import wraps
from typing import Dict, Optional, Callable, Any
import threading

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter для ограничения запросов от пользователей
    Предотвращает спам и DDoS
    """
    
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[int, list] = defaultdict(list)
        self._lock = threading.Lock()
    
    def is_allowed(self, user_id: int) -> bool:
        """Проверяет, разрешён ли запрос для пользователя"""
        now = time.time()
        
        with self._lock:
            # Очищаем старые запросы
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if now - req_time < self.window_seconds
            ]
            
            if len(self.requests[user_id]) >= self.max_requests:
                return False
            
            self.requests[user_id].append(now)
            return True
    
    def get_wait_time(self, user_id: int) -> int:
        """Возвращает время ожидания до следующего разрешённого запроса"""
        if not self.requests[user_id]:
            return 0
        
        oldest = min(self.requests[user_id])
        wait = self.window_seconds - (time.time() - oldest)
        return max(0, int(wait))


class TaskQueue:
    """
    Очередь задач для тяжёлых операций
    Ограничивает одновременное количество обработок
    """
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.queue_size = 0
        self._lock = asyncio.Lock()
    
    async def execute(self, coro):
        """Выполняет задачу с ограничением параллельности"""
        async with self._lock:
            self.queue_size += 1
        
        try:
            async with self.semaphore:
                return await coro
        finally:
            async with self._lock:
                self.queue_size -= 1
    
    @property
    def pending_count(self) -> int:
        """Количество задач в очереди"""
        return self.queue_size


class SimpleCache:
    """
    Простой кэш с TTL для часто запрашиваемых данных
    """
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self.cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша"""
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Устанавливает значение в кэш"""
        with self._lock:
            self.cache[key] = (value, time.time())
    
    def clear_expired(self):
        """Очищает просроченные записи"""
        now = time.time()
        with self._lock:
            expired = [k for k, (v, t) in self.cache.items() if now - t >= self.ttl]
            for k in expired:
                del self.cache[k]


class UserSessionManager:
    """
    Менеджер сессий пользователей для оптимизации памяти
    Автоматически очищает неактивные сессии
    """
    
    def __init__(self, max_sessions: int = 1000, session_ttl: int = 3600):
        self.max_sessions = max_sessions
        self.session_ttl = session_ttl
        self.sessions: Dict[int, dict] = {}
        self.last_activity: Dict[int, float] = {}
        self._lock = threading.Lock()
    
    def get_session(self, user_id: int) -> dict:
        """Получает или создаёт сессию пользователя"""
        with self._lock:
            self.last_activity[user_id] = time.time()
            
            if user_id not in self.sessions:
                self._cleanup_if_needed()
                self.sessions[user_id] = {}
            
            return self.sessions[user_id]
    
    def _cleanup_if_needed(self):
        """Очищает старые сессии если превышен лимит"""
        if len(self.sessions) >= self.max_sessions:
            now = time.time()
            # Удаляем сессии старше TTL
            expired = [
                uid for uid, last in self.last_activity.items()
                if now - last > self.session_ttl
            ]
            for uid in expired:
                self.sessions.pop(uid, None)
                self.last_activity.pop(uid, None)
            
            # Если всё ещё много - удаляем самые старые
            if len(self.sessions) >= self.max_sessions:
                sorted_users = sorted(self.last_activity.items(), key=lambda x: x[1])
                to_remove = len(self.sessions) - self.max_sessions + 100
                for uid, _ in sorted_users[:to_remove]:
                    self.sessions.pop(uid, None)
                    self.last_activity.pop(uid, None)


class PerformanceMonitor:
    """
    Мониторинг производительности бота
    """
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times: list = []
        self.start_time = time.time()
        self._lock = threading.Lock()
    
    def record_request(self, response_time: float, error: bool = False):
        """Записывает метрики запроса"""
        with self._lock:
            self.request_count += 1
            if error:
                self.error_count += 1
            
            self.response_times.append(response_time)
            # Храним только последние 1000 замеров
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
    
    def get_stats(self) -> dict:
        """Возвращает статистику производительности"""
        with self._lock:
            uptime = time.time() - self.start_time
            avg_response = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
            return {
                "uptime_seconds": int(uptime),
                "total_requests": self.request_count,
                "errors": self.error_count,
                "error_rate": f"{(self.error_count / self.request_count * 100):.2f}%" if self.request_count else "0%",
                "avg_response_ms": f"{avg_response * 1000:.2f}",
                "requests_per_minute": f"{self.request_count / (uptime / 60):.2f}" if uptime > 0 else "0"
            }


# Глобальные экземпляры
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)
video_queue = TaskQueue(max_concurrent=10)
image_queue = TaskQueue(max_concurrent=20)
network_queue = TaskQueue(max_concurrent=15)
cache = SimpleCache(ttl_seconds=300)
session_manager = UserSessionManager(max_sessions=1000)
performance_monitor = PerformanceMonitor()


def rate_limit(func):
    """Декоратор для rate limiting"""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id if update.effective_user else 0
        
        if not rate_limiter.is_allowed(user_id):
            wait_time = rate_limiter.get_wait_time(user_id)
            try:
                await update.message.reply_text(
                    f"⏳ Слишком много запросов. Подождите {wait_time} секунд."
                )
            except:
                pass
            return
        
        start_time = time.time()
        error = False
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            error = True
            raise
        finally:
            response_time = time.time() - start_time
            performance_monitor.record_request(response_time, error)
    
    return wrapper


def with_queue(queue: TaskQueue):
    """Декоратор для выполнения через очередь"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await queue.execute(func(*args, **kwargs))
        return wrapper
    return decorator
