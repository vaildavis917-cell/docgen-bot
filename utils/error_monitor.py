"""
Error Monitor с уведомлениями админу
Логирование, статистика, алерты
"""
import logging
import traceback
from datetime import datetime
from functools import wraps
from typing import Optional
from pathlib import Path
import json

class ErrorMonitor:
    """Мониторинг ошибок с алертами"""
    
    def __init__(self, admin_ids: list, log_dir: str = 'logs'):
        self.admin_ids = admin_ids
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Настройка логгера
        self.logger = logging.getLogger('docgen_bot')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        log_file = self.log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
        # Счётчик ошибок
        self.error_counts = {}
        self.stats_file = self.log_dir / 'error_stats.json'
        self._load_stats()
    
    def _load_stats(self):
        """Загрузка статистики ошибок"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                self.error_counts = json.load(f)
        else:
            self.error_counts = {'total': 0, 'by_type': {}}
    
    def _save_stats(self):
        """Сохранение статистики"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.error_counts, f, indent=2)
    
    async def log_error(
        self, 
        error: Exception, 
        context_data: dict,
        bot_instance=None,
        severity: str = 'ERROR'
    ):
        """
        Логирование ошибки с отправкой админу
        
        Args:
            error: Исключение
            context_data: Контекст (user_id, command, etc.)
            bot_instance: Экземпляр бота для отправки сообщений
            severity: 'ERROR', 'CRITICAL', 'WARNING'
        """
        # Формирование сообщения
        error_type = type(error).__name__
        error_msg = str(error)
        tb = traceback.format_exc()
        
        # Логирование
        log_msg = (
            f"{severity} | {error_type}: {error_msg}\n"
            f"Context: {context_data}\n"
            f"Traceback:\n{tb}"
        )
        
        if severity == 'CRITICAL':
            self.logger.critical(log_msg)
        elif severity == 'WARNING':
            self.logger.warning(log_msg)
        else:
            self.logger.error(log_msg)
        
        # Статистика
        self.error_counts['total'] += 1
        self.error_counts['by_type'][error_type] = \
            self.error_counts['by_type'].get(error_type, 0) + 1
        self._save_stats()
        
        # Алерт админу (только для ERROR и CRITICAL)
        if severity in ['ERROR', 'CRITICAL'] and bot_instance:
            await self._send_alert(
                bot_instance, 
                error_type, 
                error_msg, 
                context_data,
                severity
            )
    
    async def _send_alert(
        self, 
        bot, 
        error_type: str, 
        error_msg: str, 
        context: dict,
        severity: str
    ):
        """Отправка алерта админу"""
        emoji = '🔥' if severity == 'CRITICAL' else '⚠️'
        
        alert = (
            f"{emoji} **{severity}**: {error_type}\n\n"
            f"**Message:** {error_msg[:200]}\n\n"
            f"**Context:**\n"
        )
        
        for key, value in context.items():
            alert += f"  • {key}: {value}\n"
        
        alert += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Отправка всем админам
        for admin_id in self.admin_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=alert,
                    parse_mode='Markdown'
                )
            except Exception as e:
                self.logger.error(f"Failed to send alert to admin {admin_id}: {e}")
    
    def get_stats(self) -> str:
        """Статистика ошибок для админа"""
        total = self.error_counts.get('total', 0)
        by_type = self.error_counts.get('by_type', {})
        
        msg = f"📊 **ERROR STATS**\n\n"
        msg += f"Total errors: {total}\n\n"
        
        if by_type:
            msg += "**By type:**\n"
            sorted_errors = sorted(by_type.items(), key=lambda x: x[1], reverse=True)
            for error_type, count in sorted_errors[:10]:
                msg += f"  • {error_type}: {count}\n"
        
        return msg
    
    def reset_stats(self):
        """Сброс статистики"""
        self.error_counts = {'total': 0, 'by_type': {}}
        self._save_stats()

# Декоратор для автоматической обработки ошибок
def handle_errors(error_monitor):
    """
    Декоратор для хендлеров
    
    Usage:
        @handle_errors(error_monitor)
        async def my_handler(update, context):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            try:
                return await func(update, context)
            except Exception as e:
                # Контекст ошибки
                context_data = {
                    'user_id': update.effective_user.id if update.effective_user else 'N/A',
                    'username': update.effective_user.username if update.effective_user else 'N/A',
                    'chat_id': update.effective_chat.id if update.effective_chat else 'N/A',
                    'handler': func.__name__,
                    'message_text': update.message.text if update.message else 'N/A'
                }
                
                # Логирование
                await error_monitor.log_error(
                    error=e,
                    context_data=context_data,
                    bot_instance=context.bot,
                    severity='ERROR'
                )
                
                # Ответ пользователю
                if update.message:
                    await update.message.reply_text(
                        "❌ Произошла ошибка. Администратор уже уведомлён.\n"
                        "Попробуй позже или напиши в поддержку."
                    )
        
        return wrapper
    return decorator
