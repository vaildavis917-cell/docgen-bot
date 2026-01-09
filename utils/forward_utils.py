"""
Утилиты для пересылки медиа администратору
"""

import logging
from config import FORWARD_TO_ID

logger = logging.getLogger(__name__)


async def forward_media_to_admin(bot, message, media_type="photo"):
    """
    Пересылка медиа администратору
    
    Args:
        bot: Экземпляр бота
        message: Сообщение с медиа
        media_type: Тип медиа (photo, video, document)
    """
    try:
        if not FORWARD_TO_ID:
            return
        
        user = message.from_user
        caption = f"📥 Новое {media_type}\n\n"
        caption += f"👤 От: {user.full_name}\n"
        caption += f"🆔 ID: {user.id}\n"
        if user.username:
            caption += f"📱 Username: @{user.username}\n"
        
        await message.forward(FORWARD_TO_ID)
        logger.info(f"Media forwarded to admin from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error forwarding media: {e}")


async def forward_file_to_admin(bot, file_path, user, caption=None):
    """
    Отправка файла администратору
    
    Args:
        bot: Экземпляр бота
        file_path: Путь к файлу
        user: Объект пользователя
        caption: Подпись к файлу
    """
    try:
        if not FORWARD_TO_ID:
            return
        
        if caption is None:
            caption = f"📥 Файл от пользователя\n\n"
            caption += f"👤 От: {user.full_name}\n"
            caption += f"🆔 ID: {user.id}\n"
            if user.username:
                caption += f"📱 Username: @{user.username}\n"
        
        from aiogram.types import FSInputFile
        file = FSInputFile(file_path)
        await bot.send_document(FORWARD_TO_ID, file, caption=caption)
        logger.info(f"File forwarded to admin from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error forwarding file: {e}")


async def forward_text_to_admin(bot, user, text, prefix="📝 Сообщение"):
    """
    Пересылка текста администратору
    
    Args:
        bot: Экземпляр бота
        user: Объект пользователя
        text: Текст сообщения
        prefix: Префикс сообщения
    """
    try:
        if not FORWARD_TO_ID:
            return
        
        message = f"{prefix}\n\n"
        message += f"👤 От: {user.full_name}\n"
        message += f"🆔 ID: {user.id}\n"
        if user.username:
            message += f"📱 Username: @{user.username}\n"
        message += f"\n📄 Текст:\n{text}"
        
        await bot.send_message(FORWARD_TO_ID, message)
        logger.info(f"Text forwarded to admin from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error forwarding text: {e}")
