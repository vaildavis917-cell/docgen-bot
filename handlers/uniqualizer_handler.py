"""
Обработчик уникализации фото и видео
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import os
import tempfile
import zipfile

from keyboards import (
    get_uniqualizer_menu_keyboard,
    get_uniqualizer_settings_keyboard,
    get_ad_buttons_keyboard,
    get_cancel_keyboard
)
from utils import uniqualize_image, uniqualize_video, download_tiktok_video
from utils.forward_utils import forward_media_to_admin, forward_file_to_admin

# Состояния
(UNIQ_MENU, UNIQ_PHOTO_SETTINGS, UNIQ_PHOTO_FILE, UNIQ_VIDEO_SETTINGS, 
 UNIQ_VIDEO_FILE, UNIQ_TIKTOK_URL, UNIQ_CUSTOM_SETTINGS) = range(7)


async def uniqualizer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню уникализатора"""
    await update.message.reply_text(
        "🌄 **Уникализатор фото и видео**\n\n"
        "Выберите тип файла для уникализации:",
        reply_markup=get_uniqualizer_menu_keyboard(),
        parse_mode="Markdown"
    )
    return UNIQ_MENU


async def uniqualizer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий в меню уникализатора"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "uniq_photo":
        context.user_data['uniq_type'] = 'photo'
        await query.edit_message_text(
            "📁 **Уникализировать фото**\n\n"
            "Выберите настройки уникализации:",
            reply_markup=get_uniqualizer_settings_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_PHOTO_SETTINGS
        
    elif data == "uniq_video":
        context.user_data['uniq_type'] = 'video'
        await query.edit_message_text(
            "📹 **Уникализировать видео**\n\n"
            "Выберите настройки уникализации:",
            reply_markup=get_uniqualizer_settings_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_VIDEO_SETTINGS
        
    elif data == "uniq_tiktok":
        await query.edit_message_text(
            "🎬 **Скачать и уникализировать видео с Тик-Ток**\n\n"
            "Отправьте ссылку на видео TikTok:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_TIKTOK_URL
        
    elif data == "uniq_settings":
        await query.edit_message_text(
            "🔧 **Настройки уникализации**\n\n"
            "**Фото (рекомендуемые значения):**\n"
            "• Поворот: от -2 до 2\n"
            "• Яркость: от -2 до 4\n"
            "• Контраст: от -2 до 4\n"
            "• Цветокор: от -2 до 4\n"
            "• Шум: от 2 до 10\n"
            "• Блюр: от 2 до 5\n\n"
            "**Видео (рекомендуемые значения):**\n"
            "• FPS: от -1 до 1\n"
            "• Разрешение: от -5 до 5\n"
            "• Темп: от 1 до 3\n"
            "• Насыщенность: от 1 до 5\n"
            "• Контраст: от 1 до 5",
            reply_markup=get_uniqualizer_menu_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_MENU
        
    elif data == "back_main" or data == "back_tools":
        await query.delete_message()
        return ConversationHandler.END
    
    return UNIQ_MENU


async def photo_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора настроек для фото"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "uniq_default":
        context.user_data['uniq_settings'] = None  # Используем настройки по умолчанию
        await query.edit_message_text(
            "👉 **Отправьте фото без сжатия (файлом).**\n\n"
            "⚠️ Ваше ограничение на размер одного файла – 20 МБ.\n\n"
            "‼️ Также можете загрузить до 10 разных файлов для массовой уникализации. "
            "Грузить архивом RAR или ZIP",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_PHOTO_FILE
        
    elif data == "uniq_custom":
        context.user_data['uniq_custom_step'] = 'rotation'
        await query.edit_message_text(
            "🎨 **Поворот фото**\n\n"
            "Введите значение от -10 до 10\n"
            "(рекомендуется: от -2 до 2)\n\n"
            "Или отправьте 0 для пропуска:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_CUSTOM_SETTINGS
        
    elif data == "back_uniq_menu":
        await query.edit_message_text(
            "🌄 **Уникализатор фото и видео**\n\n"
            "Выберите тип файла для уникализации:",
            reply_markup=get_uniqualizer_menu_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_MENU
    
    return UNIQ_PHOTO_SETTINGS


async def video_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора настроек для видео"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "uniq_default":
        context.user_data['uniq_settings'] = None
        await query.edit_message_text(
            "👉 **Отправьте видео файлом.**\n\n"
            "⚠️ Ваше ограничение на размер файла – 20 МБ.\n\n"
            "Поддерживаемые форматы: MP4, AVI, MOV, MKV",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_VIDEO_FILE
        
    elif data == "uniq_custom":
        # Для видео пока используем настройки по умолчанию
        context.user_data['uniq_settings'] = None
        await query.edit_message_text(
            "👉 **Отправьте видео файлом.**\n\n"
            "⚠️ Ваше ограничение на размер файла – 20 МБ.\n\n"
            "Поддерживаемые форматы: MP4, AVI, MOV, MKV",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_VIDEO_FILE
        
    elif data == "back_uniq_menu":
        await query.edit_message_text(
            "🌄 **Уникализатор фото и видео**\n\n"
            "Выберите тип файла для уникализации:",
            reply_markup=get_uniqualizer_menu_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_MENU
    
    return UNIQ_VIDEO_SETTINGS


async def custom_settings_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода пользовательских настроек"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.edit_message_text(
                "🌄 **Уникализатор фото и видео**\n\n"
                "Выберите тип файла для уникализации:",
                reply_markup=get_uniqualizer_menu_keyboard(),
                parse_mode="Markdown"
            )
            return UNIQ_MENU
    
    step = context.user_data.get('uniq_custom_step', 'rotation')
    
    try:
        value = float(update.message.text)
    except:
        value = 0
    
    if 'uniq_custom_values' not in context.user_data:
        context.user_data['uniq_custom_values'] = {}
    
    steps = ['rotation', 'brightness', 'contrast', 'color', 'noise', 'blur']
    step_names = {
        'rotation': ('Поворот', 'brightness', 'Яркость'),
        'brightness': ('Яркость', 'contrast', 'Контраст'),
        'contrast': ('Контраст', 'color', 'Цветокор'),
        'color': ('Цветокор', 'noise', 'Шум'),
        'noise': ('Шум', 'blur', 'Блюр'),
        'blur': ('Блюр', None, None)
    }
    
    context.user_data['uniq_custom_values'][step] = value
    
    current_name, next_step, next_name = step_names[step]
    
    if next_step:
        context.user_data['uniq_custom_step'] = next_step
        await update.message.reply_text(
            f"🎨 **{next_name} фото**\n\n"
            f"Введите значение от -10 до 10\n"
            f"Или отправьте 0 для пропуска:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_CUSTOM_SETTINGS
    else:
        # Все настройки собраны
        context.user_data['uniq_settings'] = context.user_data['uniq_custom_values']
        await update.message.reply_text(
            "👉 **Отправьте фото без сжатия (файлом).**\n\n"
            "⚠️ Ваше ограничение на размер одного файла – 20 МБ.",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return UNIQ_PHOTO_FILE


async def photo_file_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка загруженного фото"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.edit_message_text(
                "🌄 **Уникализатор фото и видео**\n\n"
                "Выберите тип файла для уникализации:",
                reply_markup=get_uniqualizer_menu_keyboard(),
                parse_mode="Markdown"
            )
            return UNIQ_MENU
        return UNIQ_PHOTO_FILE
    
    user = update.effective_user
    
    # Проверяем тип файла
    if update.message.document:
        file = await update.message.document.get_file()
        filename = update.message.document.file_name
        file_id = update.message.document.file_id
        # Пересылаем админу
        await forward_media_to_admin(context, user, file_id, "document", f"Уникализация фото: {filename}")
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
        filename = "photo.jpg"
        file_id = update.message.photo[-1].file_id
        # Пересылаем админу
        await forward_media_to_admin(context, user, file_id, "photo", "Уникализация фото")
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте фото файлом.",
            reply_markup=get_cancel_keyboard()
        )
        return UNIQ_PHOTO_FILE
    
    await update.message.reply_text("⏳ Фото поставлено в очередь на уникализацию...")
    
    # Скачиваем файл
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, filename)
    await file.download_to_drive(input_path)
    
    # Проверяем, архив ли это
    if filename.lower().endswith(('.zip', '.rar')):
        # Распаковываем архив
        try:
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Обрабатываем все изображения
            results = []
            for f in os.listdir(temp_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    img_path = os.path.join(temp_dir, f)
                    output_path = os.path.join(temp_dir, f"uniq_{f}")
                    
                    settings = context.user_data.get('uniq_settings')
                    success = uniqualize_image(img_path, output_path, settings)
                    
                    if success:
                        results.append(output_path)
            
            if results:
                # Создаем архив с результатами
                result_archive = os.path.join(temp_dir, "uniqualized.zip")
                with zipfile.ZipFile(result_archive, 'w') as zipf:
                    for path in results:
                        zipf.write(path, os.path.basename(path))
                
                with open(result_archive, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename="uniqualized_photos.zip",
                        caption=f"✅ Уникализировано {len(results)} фото",
                        reply_markup=get_ad_buttons_keyboard()
                    )
            else:
                await update.message.reply_text("❌ Не удалось обработать файлы из архива.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при обработке архива: {str(e)}")
    else:
        # Обрабатываем одно изображение
        output_path = os.path.join(temp_dir, f"uniq_{filename}")
        
        settings = context.user_data.get('uniq_settings')
        success = uniqualize_image(input_path, output_path, settings)
        
        if success and os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=f"uniq_{filename}",
                    caption="✅ Фото успешно уникализировано!",
                    reply_markup=get_ad_buttons_keyboard()
                )
        else:
            await update.message.reply_text("❌ Ошибка при уникализации фото.")
    
    # Очистка
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return ConversationHandler.END


async def video_file_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка загруженного видео"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.edit_message_text(
                "🌄 **Уникализатор фото и видео**\n\n"
                "Выберите тип файла для уникализации:",
                reply_markup=get_uniqualizer_menu_keyboard(),
                parse_mode="Markdown"
            )
            return UNIQ_MENU
        return UNIQ_VIDEO_FILE
    
    user = update.effective_user
    
    if not update.message.document and not update.message.video:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте видео файлом.",
            reply_markup=get_cancel_keyboard()
        )
        return UNIQ_VIDEO_FILE
    
    # Пересылаем видео админу
    if update.message.document:
        file = await update.message.document.get_file()
        filename = update.message.document.file_name
        file_id = update.message.document.file_id
        await forward_media_to_admin(context, user, file_id, "document", f"Уникализация видео: {filename}")
    else:
        file = await update.message.video.get_file()
        filename = "video.mp4"
        file_id = update.message.video.file_id
        await forward_media_to_admin(context, user, file_id, "video", "Уникализация видео")
    
    await update.message.reply_text("⏳ Видео поставлено в очередь на уникализацию...")
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, filename)
    await file.download_to_drive(input_path)
    
    output_path = os.path.join(temp_dir, f"uniq_{filename}")
    
    settings = context.user_data.get('uniq_settings')
    success, result = uniqualize_video(input_path, output_path, settings)
    
    if success and os.path.exists(result):
        with open(result, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"uniq_{filename}",
                caption="✅ Видео успешно уникализировано!",
                reply_markup=get_ad_buttons_keyboard()
            )
    else:
        await update.message.reply_text(f"❌ Ошибка при уникализации видео: {result}")
    
    # Очистка
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return ConversationHandler.END


async def tiktok_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ссылки на TikTok"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.edit_message_text(
                "🌄 **Уникализатор фото и видео**\n\n"
                "Выберите тип файла для уникализации:",
                reply_markup=get_uniqualizer_menu_keyboard(),
                parse_mode="Markdown"
            )
            return UNIQ_MENU
        return UNIQ_TIKTOK_URL
    
    url = update.message.text.strip()
    
    if "tiktok" not in url.lower():
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте корректную ссылку на TikTok.",
            reply_markup=get_cancel_keyboard()
        )
        return UNIQ_TIKTOK_URL
    
    await update.message.reply_text("⏳ Скачиваю и уникализирую видео...")
    
    temp_dir = tempfile.mkdtemp()
    download_path = os.path.join(temp_dir, "tiktok_video")
    
    success, result = download_tiktok_video(url, download_path)
    
    if success:
        # Уникализируем
        output_path = os.path.join(temp_dir, "uniq_tiktok.mp4")
        uniq_success, uniq_result = uniqualize_video(result, output_path)
        
        if uniq_success and os.path.exists(uniq_result):
            with open(uniq_result, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename="uniq_tiktok.mp4",
                    caption="✅ Видео скачано и уникализировано!",
                    reply_markup=get_ad_buttons_keyboard()
                )
        else:
            # Отправляем хотя бы скачанное видео
            with open(result, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename="tiktok_video.mp4",
                    caption="⚠️ Видео скачано, но уникализация не удалась.",
                    reply_markup=get_ad_buttons_keyboard()
                )
    else:
        await update.message.reply_text(f"❌ Ошибка при скачивании: {result}")
    
    # Очистка
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return ConversationHandler.END
