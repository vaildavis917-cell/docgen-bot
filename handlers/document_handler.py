"""
Обработчик генерации документов
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import os
import tempfile

from keyboards import (
    get_document_menu_keyboard,
    get_country_keyboard,
    get_gender_keyboard,
    get_skip_keyboard,
    get_ad_buttons_keyboard,
    get_main_menu_keyboard
)
from utils import create_document_image, generate_random_person, generate_random_exif, set_exif
from utils.forward_utils import forward_media_to_admin, forward_file_to_admin

# Состояния для ConversationHandler
(DOC_MENU, DOC_COUNTRY, DOC_FIRST_NAME, DOC_LAST_NAME, DOC_MIDDLE_NAME,
 DOC_GENDER, DOC_BIRTH_DATE, DOC_PHOTO, DOC_SCALE) = range(9)


async def document_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню генерации документов"""
    await update.message.reply_text(
        "🆔 **Сгенерировать документ**\n\n"
        "Выберите режим генерации:",
        reply_markup=get_document_menu_keyboard(),
        parse_mode="Markdown"
    )
    return DOC_MENU


async def document_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий в меню документов"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "doc_custom":
        # Свой вариант
        context.user_data['doc_mode'] = 'custom'
        context.user_data['doc_add_exif'] = True
        await query.edit_message_text(
            "🎊 **Свой вариант (автозамена метаданных)**\n\n"
            "Выберите страну/тип документа:",
            reply_markup=get_country_keyboard(),
            parse_mode="Markdown"
        )
        return DOC_COUNTRY
        
    elif data == "doc_random_exif":
        # Рандом с EXIF
        context.user_data['doc_mode'] = 'random'
        context.user_data['doc_add_exif'] = True
        await query.edit_message_text(
            "✅ **Рандом (автозамена метаданных)**\n\n"
            "Выберите страну/тип документа:",
            reply_markup=get_country_keyboard(),
            parse_mode="Markdown"
        )
        return DOC_COUNTRY
        
    elif data == "doc_random_no_exif":
        # Рандом без EXIF
        context.user_data['doc_mode'] = 'random'
        context.user_data['doc_add_exif'] = False
        await query.edit_message_text(
            "❌ **Рандом (без метаданных)**\n\n"
            "Выберите страну/тип документа:",
            reply_markup=get_country_keyboard(),
            parse_mode="Markdown"
        )
        return DOC_COUNTRY
        
    elif data == "doc_settings":
        await query.edit_message_text(
            "🔧 **Настройки генерации**\n\n"
            "Здесь будут настройки генерации документов.",
            reply_markup=get_document_menu_keyboard(),
            parse_mode="Markdown"
        )
        return DOC_MENU
        
    elif data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    return DOC_MENU


async def country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора страны"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_doc_menu":
        await query.edit_message_text(
            "🆔 **Сгенерировать документ**\n\n"
            "Выберите режим генерации:",
            reply_markup=get_document_menu_keyboard(),
            parse_mode="Markdown"
        )
        return DOC_MENU
    
    if data == "country_private":
        await query.edit_message_text(
            "🔒 **Приватные шаблоны**\n\n"
            "Для доступа к приватным шаблонам необходима подписка.\n"
            "Свяжитесь с администратором.",
            reply_markup=get_country_keyboard(),
            parse_mode="Markdown"
        )
        return DOC_COUNTRY
    
    if data == "country_skip":
        context.user_data['doc_country'] = 'en'  # По умолчанию английский
    else:
        country = data.replace("country_", "")
        context.user_data['doc_country'] = country
    
    # Если режим рандом - сразу генерируем
    if context.user_data.get('doc_mode') == 'random':
        return await generate_random_document(update, context)
    
    # Иначе запрашиваем данные
    await query.edit_message_text(
        "📝 **Введите данные**\n\n"
        "Отправьте ваше **имя**:",
        reply_markup=get_skip_keyboard("first_name"),
        parse_mode="Markdown"
    )
    return DOC_FIRST_NAME


async def first_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение имени"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "first_name_skip":
            context.user_data['doc_first_name'] = None
        await query.edit_message_text(
            "📝 Отправьте вашу **фамилию**:",
            reply_markup=get_skip_keyboard("last_name"),
            parse_mode="Markdown"
        )
    else:
        context.user_data['doc_first_name'] = update.message.text
        await update.message.reply_text(
            "📝 Отправьте вашу **фамилию**:",
            reply_markup=get_skip_keyboard("last_name"),
            parse_mode="Markdown"
        )
    return DOC_LAST_NAME


async def last_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение фамилии"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "last_name_skip":
            context.user_data['doc_last_name'] = None
        await query.edit_message_text(
            "📝 Отправьте ваше **отчество**:",
            reply_markup=get_skip_keyboard("middle_name"),
            parse_mode="Markdown"
        )
    else:
        context.user_data['doc_last_name'] = update.message.text
        await update.message.reply_text(
            "📝 Отправьте ваше **отчество**:",
            reply_markup=get_skip_keyboard("middle_name"),
            parse_mode="Markdown"
        )
    return DOC_MIDDLE_NAME


async def middle_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение отчества"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "middle_name_skip":
            context.user_data['doc_middle_name'] = None
        await query.edit_message_text(
            "👤 Выберите **пол**:",
            reply_markup=get_gender_keyboard(),
            parse_mode="Markdown"
        )
    else:
        context.user_data['doc_middle_name'] = update.message.text
        await update.message.reply_text(
            "👤 Выберите **пол**:",
            reply_markup=get_gender_keyboard(),
            parse_mode="Markdown"
        )
    return DOC_GENDER


async def gender_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора пола"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "gender_male":
        context.user_data['doc_gender'] = "М"
    elif data == "gender_female":
        context.user_data['doc_gender'] = "Ж"
    else:
        context.user_data['doc_gender'] = None
    
    await query.edit_message_text(
        "📅 Отправьте вашу **дату рождения** (ДД.ММ.ГГГГ):",
        reply_markup=get_skip_keyboard("birth_date"),
        parse_mode="Markdown"
    )
    return DOC_BIRTH_DATE


async def birth_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение даты рождения"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "birth_date_skip":
            context.user_data['doc_birth_date'] = None
        await query.edit_message_text(
            "📷 Отправьте **фото без сжатия** (файлом, до 20 МБ):",
            reply_markup=get_skip_keyboard("photo"),
            parse_mode="Markdown"
        )
    else:
        context.user_data['doc_birth_date'] = update.message.text
        await update.message.reply_text(
            "📷 Отправьте **фото без сжатия** (файлом, до 20 МБ):",
            reply_markup=get_skip_keyboard("photo"),
            parse_mode="Markdown"
        )
    return DOC_PHOTO


async def photo_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение фото"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "photo_skip":
            context.user_data['doc_photo_path'] = None
        await query.edit_message_text(
            "🔍 Во сколько раз **увеличить фото**? (2 или 4, не больше 5):",
            reply_markup=get_skip_keyboard("scale"),
            parse_mode="Markdown"
        )
        return DOC_SCALE
    
    user = update.effective_user
    
    # Получаем фото
    if update.message.document:
        file = await update.message.document.get_file()
        file_id = update.message.document.file_id
        # Пересылаем админу
        await forward_media_to_admin(context, user, file_id, "document", "Фото для документа")
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
        file_id = update.message.photo[-1].file_id
        # Пересылаем админу
        await forward_media_to_admin(context, user, file_id, "photo", "Фото для документа")
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте фото файлом.",
            reply_markup=get_skip_keyboard("photo")
        )
        return DOC_PHOTO
    
    # Сохраняем фото
    temp_dir = tempfile.mkdtemp()
    photo_path = os.path.join(temp_dir, "user_photo.jpg")
    await file.download_to_drive(photo_path)
    context.user_data['doc_photo_path'] = photo_path
    
    await update.message.reply_text(
        "🔍 Во сколько раз **увеличить фото**? (2 или 4, не больше 5):",
        reply_markup=get_skip_keyboard("scale"),
        parse_mode="Markdown"
    )
    return DOC_SCALE


async def scale_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение масштаба и генерация документа"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        context.user_data['doc_scale'] = 1
        await query.edit_message_text("⏳ Фото поставлено в очередь на генерацию...")
    else:
        try:
            scale = int(update.message.text)
            if scale > 5:
                scale = 5
            context.user_data['doc_scale'] = scale
        except:
            context.user_data['doc_scale'] = 1
        await update.message.reply_text("⏳ Фото поставлено в очередь на генерацию...")
    
    return await generate_custom_document(update, context)


async def generate_random_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация документа со случайными данными"""
    query = update.callback_query
    
    await query.edit_message_text("⏳ Фото поставлено в очередь на генерацию...")
    
    country = context.user_data.get('doc_country', 'en')
    add_exif = context.user_data.get('doc_add_exif', True)
    
    # Генерируем случайные данные
    person = generate_random_person(country)
    
    user_data = {
        "first_name": person['first_name'],
        "last_name": person['last_name'],
        "middle_name": person.get('middle_name', ''),
        "birth_date": person['birth_date'],
        "gender": person['gender'],
        "photo_path": None
    }
    
    # Создаем документ
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "document.jpg")
    
    success = create_document_image(country, user_data, output_path)
    
    if success and os.path.exists(output_path):
        # Добавляем EXIF если нужно
        if not add_exif:
            from utils import clear_exif
            clear_exif(output_path)
        
        # Отправляем документ
        await query.message.reply_text(
            "⚠️ **ПРЕДУПРЕЖДЕНИЕ:** Генерируемые изображения не являются документами "
            "и не могут быть использованы в жизни. Данный сервис носит шуточный характер."
        )
        
        with open(output_path, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename=f"document_{country}.jpg",
                reply_markup=get_ad_buttons_keyboard()
            )
        
        # Очистка
        os.remove(output_path)
    else:
        await query.message.reply_text("❌ Ошибка при генерации документа.")
    
    return ConversationHandler.END


async def generate_custom_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация документа с пользовательскими данными"""
    country = context.user_data.get('doc_country', 'en')
    add_exif = context.user_data.get('doc_add_exif', True)
    
    # Собираем данные
    person = generate_random_person(country)  # Для заполнения пропущенных полей
    
    user_data = {
        "first_name": context.user_data.get('doc_first_name') or person['first_name'],
        "last_name": context.user_data.get('doc_last_name') or person['last_name'],
        "middle_name": context.user_data.get('doc_middle_name') or person.get('middle_name', ''),
        "birth_date": context.user_data.get('doc_birth_date') or person['birth_date'],
        "gender": context.user_data.get('doc_gender') or person['gender'],
        "photo_path": context.user_data.get('doc_photo_path')
    }
    
    # Создаем документ
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "document.jpg")
    
    success = create_document_image(country, user_data, output_path)
    
    chat_id = update.effective_chat.id
    
    if success and os.path.exists(output_path):
        # Добавляем EXIF если нужно
        if not add_exif:
            from utils import clear_exif
            clear_exif(output_path)
        
        # Отправляем документ
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ **ПРЕДУПРЕЖДЕНИЕ:** Генерируемые изображения не являются документами "
                 "и не могут быть использованы в жизни. Данный сервис носит шуточный характер.",
            parse_mode="Markdown"
        )
        
        with open(output_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=chat_id,
                document=f,
                filename=f"document_{country}.jpg",
                reply_markup=get_ad_buttons_keyboard()
            )
        
        # Очистка
        os.remove(output_path)
        if context.user_data.get('doc_photo_path'):
            try:
                os.remove(context.user_data['doc_photo_path'])
            except:
                pass
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Ошибка при генерации документа."
        )
    
    # Очищаем данные
    for key in list(context.user_data.keys()):
        if key.startswith('doc_'):
            del context.user_data[key]
    
    return ConversationHandler.END
