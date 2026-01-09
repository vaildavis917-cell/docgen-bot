"""
Обработчики дополнительных функций:
- Генератор 2FA
- Генератор селфи
- Чекер Google Play
- Скачать сайт
- Скачать TikTok
- Уникализация текста
- Верификация БМ/TikTok
- Экономия TRX
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import os
import tempfile
import random
import requests
from PIL import Image

from keyboards import (
    get_selfie_menu_keyboard,
    get_selfie_again_keyboard,
    get_gplay_menu_keyboard,
    get_tiktok_menu_keyboard,
    get_trx_menu_keyboard,
    get_ad_buttons_keyboard,
    get_cancel_keyboard,
    get_language_keyboard,
    get_main_menu_keyboard
)
from utils import (
    generate_2fa_code,
    generate_company_data,
    check_google_play_app,
    download_website,
    download_tiktok_video,
    uniqualize_text,
    extract_package_name,
    create_document_image,
    generate_random_person
)

# Состояния
(TWOFA_INPUT, SELFIE_MENU, GPLAY_MENU, GPLAY_ADD, TIKTOK_MENU, TIKTOK_URL,
 SITE_URL, TEXT_INPUT, VERIF_BM, VERIF_TT, TRX_MENU, LANG_MENU) = range(12)


# === Генератор 2FA ===
async def twofa_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало генерации 2FA"""
    await update.message.reply_text(
        "⚙️ **Генератор 2FA**\n\n"
        "Введите Ваш код 2FA:\n"
        "(пример: EPU2AAKVZ742QLNIVPPUSGLHQIHDFQHD)",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    return TWOFA_INPUT


async def twofa_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация 2FA кода"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.delete_message()
            return ConversationHandler.END
        return TWOFA_INPUT
    
    secret = update.message.text.strip()
    
    await update.message.reply_text("⏳ 2FA код поставлен в очередь на генерацию...")
    
    code = generate_2fa_code(secret)
    
    if code:
        await update.message.reply_text(
            f"🔐 **Ваш 2FA код:**\n\n"
            f"`{code}`\n\n"
            f"⚠️ Код действителен 30 секунд",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ Ошибка генерации кода. Проверьте правильность секретного ключа."
        )
    
    return ConversationHandler.END


# === Генератор селфи ===
async def selfie_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню генератора селфи"""
    await update.message.reply_text(
        "👥 **Генератор селфи**\n\n"
        "Выберите пол:",
        reply_markup=get_selfie_menu_keyboard(),
        parse_mode="Markdown"
    )
    return SELFIE_MENU


async def selfie_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора селфи"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    if data == "back_generators":
        from keyboards import get_generators_menu_keyboard
        await query.edit_message_text(
            "🛠 **Генераторы**\n\nВыберите тип генерации:",
            reply_markup=get_generators_menu_keyboard(),
            parse_mode="Markdown"
        )
        return SELFIE_MENU
    
    if data in ["selfie_male", "selfie_female", "selfie_again"]:
        gender = "male" if data == "selfie_male" else "female"
        if data == "selfie_again":
            gender = context.user_data.get('selfie_gender', 'male')
        
        context.user_data['selfie_gender'] = gender
        
        await query.edit_message_text("⏳ Селфи в очереди на генерацию...")
        
        # Генерируем селфи через AI API
        try:
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, "selfie.jpg")
            
            # Получаем AI-сгенерированное лицо
            success = False
            
            # Метод 1: fakeface.rest API (с фильтром возраста - ТОЛЬКО взрослые 25-50 лет)
            try:
                gender_param = "male" if gender == "male" else "female"
                response = requests.get(
                    f"https://fakeface.rest/face/json?gender={gender_param}&minimum_age=25&maximum_age=50",
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    timeout=15
                )
                if response.status_code == 200:
                    data_json = response.json()
                    if 'image_url' in data_json:
                        img_response = requests.get(data_json['image_url'], timeout=15)
                        if img_response.status_code == 200:
                            with open(output_path, 'wb') as f:
                                f.write(img_response.content)
                            success = True
            except Exception as e:
                pass
            
            # Метод 2: thispersondoesnotexist.com (резервный - без фильтра возраста)
            if not success:
                try:
                    response = requests.get(
                        "https://thispersondoesnotexist.com",
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        },
                        timeout=15
                    )
                    if response.status_code == 200 and len(response.content) > 10000:
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        success = True
                except Exception as e:
                    pass
            
            if success and os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    await query.message.reply_photo(
                        photo=f,
                        caption=f"👤 {'Мужское' if gender == 'male' else 'Женское'} фото\n\n"
                                f"🤖 Сгенерировано AI",
                        reply_markup=get_selfie_again_keyboard()
                    )
                
                # Очистка
                os.remove(output_path)
            else:
                await query.message.reply_text(
                    "❌ Не удалось сгенерировать селфи. Попробуйте ещё раз.",
                    reply_markup=get_selfie_menu_keyboard()
                )
            
            # Очистка временной директории
            try:
                os.rmdir(temp_dir)
            except:
                pass
            
        except Exception as e:
            await query.message.reply_text(
                f"❌ Ошибка генерации селфи. Попробуйте позже.",
                reply_markup=get_selfie_menu_keyboard()
            )
        
        return SELFIE_MENU
    
    return SELFIE_MENU


# === Чекер Google Play ===
async def gplay_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню чекера Google Play"""
    await update.message.reply_text(
        "✅ **Чекер приложений Google Play**\n\n"
        "Привет 👋 Я буду чекером твоих приложений.\n"
        "Если приложение улетит в бан, я отправлю тебе оповещение 🔔\n\n"
        "Отправь мне ссылку в формате `com.google.android.youtube`,\n"
        "чтобы начать слежку 👁\n\n"
        "• чекаю в бане или активное приложение каждые 30 минут\n"
        "• Бесплатно максимальный лимит одновременно на чек прил = 3 шт",
        reply_markup=get_gplay_menu_keyboard(),
        parse_mode="Markdown"
    )
    return GPLAY_MENU


async def gplay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка меню Google Play"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    if data == "gplay_add":
        await query.edit_message_text(
            "💎 **Добавить приложение**\n\n"
            "Отправьте package name приложения:\n"
            "(например: `com.google.android.youtube`)",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return GPLAY_ADD
    
    if data == "gplay_list":
        apps = context.user_data.get('gplay_apps', [])
        if apps:
            text = "📱 **Ваши приложения:**\n\n"
            for app in apps:
                text += f"• `{app}`\n"
        else:
            text = "📱 У вас пока нет отслеживаемых приложений."
        
        await query.edit_message_text(
            text,
            reply_markup=get_gplay_menu_keyboard(),
            parse_mode="Markdown"
        )
        return GPLAY_MENU
    
    return GPLAY_MENU


async def gplay_add_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление приложения для отслеживания"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.edit_message_text(
                "✅ **Чекер приложений Google Play**",
                reply_markup=get_gplay_menu_keyboard()
            )
            return GPLAY_MENU
        return GPLAY_ADD
    
    package = extract_package_name(update.message.text)
    
    await update.message.reply_text("⏳ Проверяю приложение...")
    
    # Проверяем приложение
    exists, message = check_google_play_app(package)
    
    if exists:
        # Добавляем в список
        if 'gplay_apps' not in context.user_data:
            context.user_data['gplay_apps'] = []
        
        if len(context.user_data['gplay_apps']) >= 3:
            await update.message.reply_text(
                "❌ Достигнут лимит в 3 приложения.\n"
                "Для увеличения лимита приобретите подписку.",
                reply_markup=get_gplay_menu_keyboard()
            )
        elif package in context.user_data['gplay_apps']:
            await update.message.reply_text(
                "⚠️ Это приложение уже отслеживается.",
                reply_markup=get_gplay_menu_keyboard()
            )
        else:
            context.user_data['gplay_apps'].append(package)
            await update.message.reply_text(
                f"✅ Приложение `{package}` добавлено в отслеживание!\n\n"
                f"Статус: {message}",
                reply_markup=get_gplay_menu_keyboard(),
                parse_mode="Markdown"
            )
    elif exists is False:
        await update.message.reply_text(
            f"⚠️ {message}\n\n"
            f"Приложение не добавлено.",
            reply_markup=get_gplay_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            f"❌ {message}",
            reply_markup=get_gplay_menu_keyboard()
        )
    
    return GPLAY_MENU


# === Скачать TikTok ===
async def tiktok_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню скачивания TikTok"""
    await update.message.reply_text(
        "🎵 **Скачать креатив Тик-Ток**\n\n"
        "Выберите операцию:",
        reply_markup=get_tiktok_menu_keyboard(),
        parse_mode="Markdown"
    )
    return TIKTOK_MENU


async def tiktok_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка меню TikTok"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    if data == "tiktok_download":
        context.user_data['tiktok_uniq'] = False
        await query.edit_message_text(
            "🎬 **Скачать видео**\n\n"
            "Отправьте ссылку на видео TikTok:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return TIKTOK_URL
    
    if data == "tiktok_download_uniq":
        context.user_data['tiktok_uniq'] = True
        await query.edit_message_text(
            "🎬 **Скачать и уникализировать**\n\n"
            "Отправьте ссылку на видео TikTok:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return TIKTOK_URL
    
    return TIKTOK_MENU


async def tiktok_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скачивание видео TikTok"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.edit_message_text(
                "🎵 **Скачать креатив Тик-Ток**",
                reply_markup=get_tiktok_menu_keyboard()
            )
            return TIKTOK_MENU
        return TIKTOK_URL
    
    url = update.message.text.strip()
    
    if "tiktok" not in url.lower():
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте корректную ссылку на TikTok.",
            reply_markup=get_cancel_keyboard()
        )
        return TIKTOK_URL
    
    await update.message.reply_text("⏳ Скачиваю видео...")
    
    temp_dir = tempfile.mkdtemp()
    download_path = os.path.join(temp_dir, "tiktok_video")
    
    success, result = download_tiktok_video(url, download_path)
    
    if success:
        should_uniq = context.user_data.get('tiktok_uniq', False)
        
        if should_uniq:
            from utils import uniqualize_video
            output_path = os.path.join(temp_dir, "uniq_tiktok.mp4")
            uniq_success, uniq_result = uniqualize_video(result, output_path)
            
            if uniq_success:
                result = uniq_result
        
        with open(result, 'rb') as f:
            caption = "✅ Видео скачано"
            if should_uniq:
                caption += " и уникализировано"
            caption += "!"
            
            await update.message.reply_document(
                document=f,
                filename="tiktok_video.mp4",
                caption=caption,
                reply_markup=get_ad_buttons_keyboard()
            )
    else:
        await update.message.reply_text(f"❌ Ошибка: {result}")
    
    # Очистка
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return ConversationHandler.END


# === Скачать сайт ===
async def site_download_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало скачивания сайта"""
    await update.message.reply_text(
        "📥 **Скачать сайт**\n\n"
        "Отправьте ссылку на сайт:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    return SITE_URL


async def site_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скачивание сайта"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.delete_message()
            return ConversationHandler.END
        return SITE_URL
    
    url = update.message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    await update.message.reply_text("⏳ Сайт поставлен в очередь на скачивание...")
    
    temp_dir = tempfile.mkdtemp()
    output_dir = os.path.join(temp_dir, "site")
    
    success, result = download_website(url, output_dir)
    
    if success and os.path.exists(result):
        with open(result, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename="website.zip",
                caption="✅ Сайт успешно скачан!",
                reply_markup=get_ad_buttons_keyboard()
            )
    else:
        await update.message.reply_text(f"❌ Ошибка: {result}")
    
    # Очистка
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return ConversationHandler.END


# === Уникализация текста ===
async def text_uniq_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало уникализации текста"""
    await update.message.reply_text(
        "🔄 **Уникализация текста**\n\n"
        "Отправьте текст для уникализации:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    return TEXT_INPUT


async def text_uniq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Уникализация текста"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel":
            await query.delete_message()
            return ConversationHandler.END
        return TEXT_INPUT
    
    text = update.message.text
    
    await update.message.reply_text("⏳ Уникализирую текст...")
    
    result = uniqualize_text(text)
    
    await update.message.reply_text(
        f"✅ **Уникализированный текст:**\n\n{result}",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END


# === Верификация БМ ===
async def verif_bm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация верификации БМ"""
    await update.message.reply_text("⏳ Поставлен в очередь на генерацию...")
    
    # Генерируем данные компании
    company = generate_company_data("ua")
    
    # Создаем изображение документа
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "bm_verification.jpg")
    
    # Создаем простой документ
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
        font_bold = font
    
    # Заголовок
    draw.text((50, 30), "ВИПИСКА З ЄДИНОГО ДЕРЖАВНОГО РЕЄСТРУ", fill=(0, 0, 100), font=font_bold)
    
    # Данные
    y = 100
    fields = [
        ("Юридична назва компанії:", company['company_name']),
        ("Країна або регіон:", "Україна"),
        ("Адреса:", company['address']),
        ("Місто:", company['city']),
        ("Область:", company['region']),
        ("Поштовий індекс:", company['postal_code']),
        ("Номер ліцензії:", company['license_number']),
        ("Телефон:", company['phone'])
    ]
    
    for label, value in fields:
        draw.text((50, y), label, fill=(100, 100, 100), font=font)
        draw.text((300, y), value, fill=(0, 0, 0), font=font)
        y += 40
    
    # Рамка
    draw.rectangle([(20, 20), (780, 580)], outline=(0, 0, 100), width=2)
    
    img.save(output_path, quality=95)
    
    # Отправляем
    await update.message.reply_text(
        "⚠️ **ПРЕДУПРЕЖДЕНИЕ:** Генерируемые изображения не являются документами "
        "и не могут быть использованы в жизни. Данный сервис носит шуточный характер.",
        parse_mode="Markdown"
    )
    
    with open(output_path, 'rb') as f:
        await update.message.reply_document(
            document=f,
            filename="bm_verification.jpg"
        )
    
    # Отправляем данные текстом
    text = (
        f"📋 **Данные компании:**\n\n"
        f"• Юридична назва компанії: {company['company_name']}\n"
        f"• Країна або регіон: Україна\n"
        f"• Адреса: {company['address']}\n"
        f"• Місто: {company['city']}\n"
        f"• Область: {company['region']}\n"
        f"• Поштовий індекс: {company['postal_code']}\n"
        f"• Номер ліцензії: {company['license_number']}\n"
        f"• Телефон: {company['phone']}"
    )
    
    await update.message.reply_text(
        text,
        reply_markup=get_ad_buttons_keyboard(),
        parse_mode="Markdown"
    )
    
    # Очистка
    os.remove(output_path)
    os.rmdir(temp_dir)
    
    return ConversationHandler.END


# === Верификация TikTok ===
async def verif_tt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация верификации TikTok"""
    await update.message.reply_text("⏳ Поставлен в очередь на генерацию...")
    
    # Генерируем данные компании (США)
    company = generate_company_data("en")
    
    # Создаем изображение
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "tt_verification.jpg")
    
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
        font_bold = font
    
    # Заголовок
    draw.text((50, 30), "BUSINESS REGISTRATION CERTIFICATE", fill=(0, 0, 100), font=font_bold)
    
    # Данные
    y = 100
    fields = [
        ("Company Name:", company['company_name']),
        ("Country:", "United States"),
        ("Address:", company['address']),
        ("City:", company['city']),
        ("State:", company['region']),
        ("Postal Code:", company['postal_code']),
        ("License Number:", company['license_number']),
        ("Phone:", company['phone'])
    ]
    
    for label, value in fields:
        draw.text((50, y), label, fill=(100, 100, 100), font=font)
        draw.text((250, y), value, fill=(0, 0, 0), font=font)
        y += 40
    
    draw.rectangle([(20, 20), (780, 580)], outline=(0, 0, 100), width=2)
    
    img.save(output_path, quality=95)
    
    await update.message.reply_text(
        "⚠️ **ПРЕДУПРЕЖДЕНИЕ:** Генерируемые изображения не являются документами "
        "и не могут быть использованы в жизни. Данный сервис носит шуточный характер.",
        parse_mode="Markdown"
    )
    
    with open(output_path, 'rb') as f:
        await update.message.reply_document(
            document=f,
            filename="tt_verification.jpg"
        )
    
    text = (
        f"📋 **Company Data:**\n\n"
        f"• Company Name: {company['company_name']}\n"
        f"• Country: United States\n"
        f"• Address: {company['address']}\n"
        f"• City: {company['city']}\n"
        f"• State: {company['region']}\n"
        f"• Postal Code: {company['postal_code']}\n"
        f"• License Number: {company['license_number']}\n"
        f"• Phone: {company['phone']}"
    )
    
    await update.message.reply_text(
        text,
        reply_markup=get_ad_buttons_keyboard(),
        parse_mode="Markdown"
    )
    
    os.remove(output_path)
    os.rmdir(temp_dir)
    
    return ConversationHandler.END


# === Экономия TRX ===
async def trx_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню экономии TRX"""
    balance = context.user_data.get('trx_balance', 0.0)
    
    await update.message.reply_text(
        "👋 **Аптека Арбитражника** поможет сэкономить тебе TRX для переводов в USDT trc20\n\n"
        "**Все очень просто:**\n"
        "1. Добавьте кошелек в разделе Кошельки\n"
        "2. Пополните TRX раздел - Пополнить баланс\n"
        "3. Купить энергию - раздел Купить энергию\n"
        "4. Выбрать кошелек и количество энергии\n\n"
        "Энергия арендуется ровно на 1 час.\n\n"
        "⚠️ **Аренда энергии на 1 час:**\n"
        "• Если у получателя есть USDT - нужно 65 000⚡️ (стоимость: 2.9 TRX)\n"
        "• Если у получателя нет USDT - нужно 131 000⚡️ (стоимость: 6.0 TRX)\n\n"
        f"┌ 💰 **Ваш баланс:**\n"
        f"└ {balance:.3f} TRX",
        reply_markup=get_trx_menu_keyboard(),
        parse_mode="Markdown"
    )
    return TRX_MENU


async def trx_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка меню TRX"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    if data == "trx_wallets":
        wallets = context.user_data.get('trx_wallets', [])
        if wallets:
            text = "💼 **Ваши кошельки:**\n\n"
            for w in wallets:
                text += f"• `{w}`\n"
        else:
            text = "💼 У вас пока нет добавленных кошельков.\n\nДля добавления отправьте адрес TRON кошелька."
        
        await query.edit_message_text(
            text,
            reply_markup=get_trx_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "trx_deposit":
        await query.edit_message_text(
            "💰 **Пополнение баланса**\n\n"
            "Для пополнения отправьте TRX на адрес:\n"
            "`TXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`\n\n"
            "После отправки баланс обновится автоматически.",
            reply_markup=get_trx_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "trx_buy_energy":
        await query.edit_message_text(
            "⚡ **Купить энергию**\n\n"
            "Для покупки энергии сначала:\n"
            "1. Добавьте кошелек\n"
            "2. Пополните баланс\n\n"
            "Затем выберите количество энергии.",
            reply_markup=get_trx_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "trx_history":
        await query.edit_message_text(
            "📊 **История операций**\n\n"
            "История пуста.",
            reply_markup=get_trx_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    return TRX_MENU


# === Язык ===
async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора языка"""
    await update.message.reply_text(
        "🌐 **Изменить язык**\n\n"
        "Выберите язык интерфейса:",
        reply_markup=get_language_keyboard(),
        parse_mode="Markdown"
    )
    return LANG_MENU


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора языка"""
    from utils.localization import set_user_language, AVAILABLE_LANGUAGES
    
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    lang_map = {
        "lang_ru": "ru",
        "lang_en": "en",
        "lang_ua": "ua"
    }
    
    if data in lang_map:
        lang_code = lang_map[data]
        set_user_language(user_id, lang_code)
        context.user_data['language'] = lang_code
        
        lang_name = AVAILABLE_LANGUAGES.get(lang_code, lang_code)
        
        await query.edit_message_text(
            f"✅ Язык изменён на: {lang_name}\n\n"
            f"✅ Language changed to: {lang_name}",
            reply_markup=get_language_keyboard()
        )
    
    return LANG_MENU


# === Инфо о подписке ===
async def subscription_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о подписке"""
    await update.message.reply_text(
        "👆 **Информация о подписке**\n\n"
        "📊 **Ваш статус:** Бесплатный\n\n"
        "**Лимиты бесплатной версии:**\n"
        "• Архивов в сутки: 1\n"
        "• Приложений для чекера: 3\n"
        "• Размер файла: 20 МБ\n\n"
        "**Премиум подписка снимает все ограничения!**\n\n"
        "Для приобретения подписки свяжитесь с администратором.",
        parse_mode="Markdown"
    )
