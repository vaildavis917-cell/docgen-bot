"""
DocGen Bot - Telegram бот для генерации документов и уникализации медиа
Все меню работают через inline кнопки с единым callback handler
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    PreCheckoutQueryHandler,
    filters
)

from config import BOT_TOKEN
from keyboards import (
    get_main_menu_keyboard, get_language_selection_keyboard,
    get_tools_menu_keyboard, get_generators_menu_keyboard, get_settings_menu_keyboard,
    get_uniqualizer_menu_keyboard, get_uniqualizer_settings_keyboard,
    get_exif_menu_keyboard, get_selfie_menu_keyboard,
    get_gplay_menu_keyboard, get_address_menu_keyboard, get_card_menu_keyboard,
    get_antidetect_menu_keyboard, get_subscription_menu_keyboard, get_language_keyboard,
    get_tiktok_menu_keyboard, get_cancel_keyboard
)
from utils.localization import (
    is_new_user, set_user_language, get_user_language, t
)
from utils.subscription import get_user_subscription, SUBSCRIPTION_PLANS

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context):
    """Обработчик команды /start"""
    from utils.admin_utils import is_banned, is_maintenance_mode, get_maintenance_message, register_user
    from utils.whitelist import is_admin
    
    user = update.effective_user
    user_id = user.id
    
    # Регистрируем пользователя
    register_user(user_id, user.username, user.first_name)
    
    # Проверяем бан (админы не банятся)
    if is_banned(user_id) and not is_admin(user_id):
        await update.message.reply_text(
            "🚫 **Вы заблокированы**\n\n"
            "Доступ к боту ограничен.",
            parse_mode="Markdown"
        )
        return
    
    # Проверяем режим обслуживания (админы могут работать)
    if is_maintenance_mode() and not is_admin(user_id):
        await update.message.reply_text(
            get_maintenance_message(),
            parse_mode="Markdown"
        )
        return
    
    # Проверяем, новый ли пользователь
    if is_new_user(user_id):
        # Показываем выбор языка
        await update.message.reply_text(
            "🌐 Пожалуйста, выберите язык:\n\n"
            "Please select your language:\n\n"
            "Будь ласка, оберіть мову:",
            reply_markup=get_language_selection_keyboard()
        )
        return
    
    # Проверяем, является ли пользователь админом-оператором (ID 7080468696)
    ADMIN_OPERATOR_ID = int(os.getenv("ADMIN_OPERATOR_ID", "0"))
    if user_id == ADMIN_OPERATOR_ID:
        from keyboards import get_admin_panel_keyboard
        from utils.admin_utils import is_maintenance_mode
        
        status = "✅ Включён" if not is_maintenance_mode() else "🔧 Тех. работы"
        
        await update.message.reply_text(
            f"🔐 **Админ-панель**\n\n"
            f"🤖 Статус бота: {status}\n\n"
            f"Выберите действие:",
            reply_markup=get_admin_panel_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # Показываем главное меню
    welcome_text = t("welcome", user_id)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(user_id),
        parse_mode="Markdown"
    )


async def help_command(update: Update, context):
    """Обработчик команды /help"""
    user_id = update.effective_user.id
    
    help_text = (
        "📖 **Help / Справка**\n\n"
        "**Commands / Команды:**\n"
        "/start - Start bot / Запустить бота\n"
        "/help - Show help / Показать справку\n\n"
        "Use menu buttons.\n"
        "Используйте кнопки меню."
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def main_callback_handler(update: Update, context):
    """Единый обработчик всех callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # === Первый выбор языка ===
    if data.startswith("set_lang_"):
        lang_code = data.replace("set_lang_", "")
        set_user_language(user_id, lang_code)
        
        await query.message.edit_text(
            t("welcome", user_id),
            reply_markup=get_main_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === АДМИН-ПАНЕЛЬ ===
    ADMIN_OPERATOR_ID = int(os.getenv("ADMIN_OPERATOR_ID", "0"))
    
    if data == "admin_back":
        from keyboards import get_admin_panel_keyboard
        from utils.admin_utils import is_maintenance_mode
        status = "✅ Включён" if not is_maintenance_mode() else "🔧 Тех. работы"
        await query.message.edit_text(
            f"🔐 **Админ-панель**\n\n"
            f"🤖 Статус бота: {status}\n\n"
            f"Выберите действие:",
            reply_markup=get_admin_panel_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_vip":
        from keyboards import get_admin_vip_keyboard
        await query.message.edit_text(
            "👑 **VIP управление**\n\n"
            "Выберите действие:",
            reply_markup=get_admin_vip_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_vip_add":
        from keyboards import get_admin_back_keyboard
        context.user_data['waiting_for'] = 'admin_vip_add'
        await query.message.edit_text(
            "➕ **Добавить VIP**\n\n"
            "Отправьте ID пользователя:\n"
            "Формат: `ID` или `ID примечание`\n\n"
            "Пример: `123456789 Друг`",
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_vip_remove":
        from keyboards import get_admin_back_keyboard
        context.user_data['waiting_for'] = 'admin_vip_remove'
        await query.message.edit_text(
            "➖ **Удалить VIP**\n\n"
            "Отправьте ID пользователя:",
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_vip_list":
        from keyboards import get_admin_back_keyboard
        from utils.whitelist import get_vip_list, get_vip_count
        
        vip_list = get_vip_list()
        count = get_vip_count()
        
        if not vip_list:
            text = "📝 **VIP список пуст.**"
        else:
            text = f"👑 **VIP пользователи ({count}):**\n\n"
            for vip in vip_list:
                added_at = vip['added_at'][:10] if vip['added_at'] else 'неизвестно'
                note = vip['note'] or '-'
                text += f"• `{vip['user_id']}` | {added_at} | {note}\n"
        
        await query.message.edit_text(
            text,
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_ban":
        from keyboards import get_admin_ban_keyboard
        await query.message.edit_text(
            "🚫 **Бан управление**\n\n"
            "Выберите действие:",
            reply_markup=get_admin_ban_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_ban_add":
        from keyboards import get_admin_back_keyboard
        context.user_data['waiting_for'] = 'admin_ban_add'
        await query.message.edit_text(
            "🚫 **Забанить пользователя**\n\n"
            "Отправьте ID пользователя:\n"
            "Формат: `ID` или `ID причина`\n\n"
            "Пример: `123456789 Спам`",
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_ban_remove":
        from keyboards import get_admin_back_keyboard
        context.user_data['waiting_for'] = 'admin_ban_remove'
        await query.message.edit_text(
            "✅ **Разбанить пользователя**\n\n"
            "Отправьте ID пользователя:",
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_ban_list":
        from keyboards import get_admin_back_keyboard
        from utils.admin_utils import get_ban_list
        
        ban_list = get_ban_list()
        
        if not ban_list:
            text = "📝 **Список банов пуст.**"
        else:
            text = f"🚫 **Забаненные ({len(ban_list)}):**\n\n"
            for ban in ban_list:
                reason = ban.get('reason', '-')
                text += f"• `{ban['user_id']}` | {reason}\n"
        
        await query.message.edit_text(
            text,
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_stats":
        from keyboards import get_admin_back_keyboard
        from utils.admin_utils import get_bot_stats
        
        stats = get_bot_stats()
        
        text = (
            "📊 **Статистика бота**\n\n"
            f"👥 Всего пользователей: {stats['total_users']}\n"
            f"🟢 Активных сегодня: {stats['active_today']}\n"
            f"👑 VIP пользователей: {stats['vip_count']}\n"
            f"🚫 Забаненных: {stats['banned_count']}\n"
        )
        
        await query.message.edit_text(
            text,
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_broadcast":
        from keyboards import get_admin_back_keyboard
        context.user_data['waiting_for'] = 'admin_broadcast'
        await query.message.edit_text(
            "📢 **Рассылка**\n\n"
            "Отправьте текст для рассылки всем пользователям:",
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_maintenance":
        from keyboards import get_admin_maintenance_keyboard
        from utils.admin_utils import is_maintenance_mode
        status = "✅ Включён" if not is_maintenance_mode() else "🔧 Тех. работы"
        await query.message.edit_text(
            f"🔧 **Maintenance**\n\n"
            f"Текущий статус: {status}\n\n"
            f"Выберите действие:",
            reply_markup=get_admin_maintenance_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_maint_on":
        from keyboards import get_admin_back_keyboard
        from utils.admin_utils import set_maintenance_mode, get_all_users
        
        set_maintenance_mode(False)
        
        # Рассылаем уведомления
        users = get_all_users()
        success = 0
        for uid in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text="✅ **Бот снова работает!**\n\n"
                         "Технические работы завершены.\n"
                         "Нажмите /start для продолжения.",
                    parse_mode="Markdown"
                )
                success += 1
            except:
                pass
        
        await query.message.edit_text(
            f"✅ **Бот включён!**\n\n"
            f"Уведомления отправлены: {success}/{len(users)}",
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_maint_off":
        from keyboards import get_admin_back_keyboard
        from utils.admin_utils import set_maintenance_mode, get_all_users
        
        set_maintenance_mode(True)
        
        # Рассылаем уведомления
        users = get_all_users()
        success = 0
        for uid in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text="🔧 **Технические работы**\n\n"
                         "Бот временно недоступен. Пожалуйста, подождите.\n"
                         "Мы сообщим, когда работа будет восстановлена.",
                    parse_mode="Markdown"
                )
                success += 1
            except:
                pass
        
        await query.message.edit_text(
            f"🔧 **Бот выключен (тех. работы)**\n\n"
            f"Уведомления отправлены: {success}/{len(users)}",
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    if data == "admin_userinfo":
        from keyboards import get_admin_back_keyboard
        context.user_data['waiting_for'] = 'admin_userinfo'
        await query.message.edit_text(
            "👤 **Инфо о пользователе**\n\n"
            "Отправьте ID пользователя:",
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # === Главное меню ===
    if data == "main_tools":
        await query.message.edit_text(
            t("tools.title", user_id),
            reply_markup=get_tools_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "main_generators":
        await query.message.edit_text(
            t("generators.title", user_id),
            reply_markup=get_generators_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "main_gplay":
        await query.message.edit_text(
            t("gplay.title", user_id),
            reply_markup=get_gplay_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "main_subscription":
        await query.message.edit_text(
            t("subscription.menu_title", user_id),
            reply_markup=get_subscription_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "main_settings":
        await query.message.edit_text(
            t("settings.title", user_id),
            reply_markup=get_settings_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === Кнопки "Назад" ===
    if data == "back_main":
        await query.message.edit_text(
            t("welcome", user_id),
            reply_markup=get_main_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "back_tools":
        await query.message.edit_text(
            t("tools.title", user_id),
            reply_markup=get_tools_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "back_generators":
        await query.message.edit_text(
            t("generators.title", user_id),
            reply_markup=get_generators_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "back_settings":
        await query.message.edit_text(
            t("settings.title", user_id),
            reply_markup=get_settings_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "back_subscription":
        await query.message.edit_text(
            t("subscription.menu_title", user_id),
            reply_markup=get_subscription_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "back_uniq_menu":
        await query.message.edit_text(
            t("uniqualizer.title", user_id),
            reply_markup=get_uniqualizer_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === Меню Инструменты ===
    if data == "menu_uniqualizer":
        await query.message.edit_text(
            t("uniqualizer.title", user_id),
            reply_markup=get_uniqualizer_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "menu_exif":
        await query.message.edit_text(
            t("exif.title", user_id),
            reply_markup=get_exif_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "menu_site":
        context.user_data['waiting_for'] = 'site_url'
        await query.message.edit_text(
            t("site.title", user_id),
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "menu_tiktok":
        await query.message.edit_text(
            t("tiktok.title", user_id),
            reply_markup=get_tiktok_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === Уникализатор ===
    if data == "uniq_photo":
        context.user_data['uniq_type'] = 'photo'
        await query.message.edit_text(
            "📁 **Уникализировать фото**\n\n"
            "Выберите настройки уникализации:",
            reply_markup=get_uniqualizer_settings_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "uniq_video":
        context.user_data['uniq_type'] = 'video'
        await query.message.edit_text(
            "📹 **Уникализировать видео**\n\n"
            "Выберите настройки уникализации:",
            reply_markup=get_uniqualizer_settings_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "uniq_default":
        uniq_type = context.user_data.get('uniq_type', 'photo')
        context.user_data['uniq_settings'] = None
        context.user_data['waiting_for'] = f'uniq_{uniq_type}'
        logger.info(f"Set waiting_for=uniq_{uniq_type} for user {user_id}")
        
        if uniq_type == 'photo':
            await query.message.edit_text(
                "👉 **Отправьте фото без сжатия (файлом).**\n\n"
                "⚠️ Ваше ограничение на размер одного файла – 20 МБ.\n\n"
                "‼️ Также можете загрузить до 10 разных файлов для массовой уникализации. "
                "Грузить архивом RAR или ZIP",
                reply_markup=get_cancel_keyboard(user_id),
                parse_mode="Markdown"
            )
        else:
            await query.message.edit_text(
                "👉 **Отправьте видео файлом.**\n\n"
                "⚠️ Ваше ограничение на размер файла – 20 МБ.\n\n"
                "Поддерживаемые форматы: MP4, AVI, MOV, MKV",
                reply_markup=get_cancel_keyboard(user_id),
                parse_mode="Markdown"
            )
        return
    
    if data == "uniq_custom":
        context.user_data['uniq_custom_step'] = 'rotation'
        context.user_data['waiting_for'] = 'uniq_custom'
        await query.message.edit_text(
            "🎨 **Поворот фото**\n\n"
            "Введите значение от -10 до 10\n"
            "(рекомендуется: от -2 до 2)\n\n"
            "Или отправьте 0 для пропуска:",
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === EXIF ===
    if data == "exif_view":
        context.user_data['waiting_for'] = 'exif_view'
        await query.message.edit_text(
            "🔍 **Просмотр EXIF данных**\n\n"
            "Отправьте фото для просмотра метаданных:",
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "exif_clear":
        context.user_data['waiting_for'] = 'exif_clear'
        await query.message.edit_text(
            "🧹 **Очистка EXIF данных**\n\n"
            "Отправьте фото для очистки метаданных:",
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "exif_copy":
        context.user_data['waiting_for'] = 'exif_copy_source'
        await query.message.edit_text(
            "✏️ **Копирование EXIF данных**\n\n"
            "Отправьте **исходное** фото (откуда копировать EXIF):",
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === TikTok ===
    if data == "tiktok_download":
        context.user_data['waiting_for'] = 'tiktok_url'
        context.user_data['tiktok_uniq'] = False
        await query.message.edit_text(
            "🎬 **Скачать видео с TikTok**\n\n"
            "Отправьте ссылку на видео:",
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "tiktok_download_uniq":
        context.user_data['waiting_for'] = 'tiktok_url'
        context.user_data['tiktok_uniq'] = True
        await query.message.edit_text(
            "🎬 **Скачать и уникализировать видео с TikTok**\n\n"
            "Отправьте ссылку на видео:",
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === Меню Генераторы ===
    if data == "menu_selfie":
        await query.message.edit_text(
            t("selfie.title", user_id),
            reply_markup=get_selfie_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "menu_address":
        await query.message.edit_text(
            t("address.title", user_id),
            reply_markup=get_address_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "menu_card":
        await query.message.edit_text(
            t("card.title", user_id),
            reply_markup=get_card_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "menu_twofa":
        context.user_data['waiting_for'] = 'twofa'
        await query.message.edit_text(
            t("twofa.title", user_id),
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "menu_antidetect":
        await query.message.edit_text(
            t("antidetect.title", user_id),
            reply_markup=get_antidetect_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "menu_text":
        context.user_data['waiting_for'] = 'text_uniq'
        await query.message.edit_text(
            t("text.title", user_id),
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === Настройки ===
    if data == "menu_language":
        await query.message.edit_text(
            t("language.title", user_id),
            reply_markup=get_language_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "menu_sub_info":
        sub = get_user_subscription(user_id)
        plan_id = sub.get("plan", "free")
        plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
        
        info_text = (
            f"📊 **{t('subscription.my_subscription', user_id)}**\n\n"
            f"{plan['icon']} **{plan['name']}**\n"
        )
        
        await query.message.edit_text(
            info_text,
            reply_markup=get_settings_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data.startswith("lang_"):
        lang_code = data.replace("lang_", "")
        set_user_language(user_id, lang_code)
        
        await query.message.edit_text(
            t("welcome", user_id),
            reply_markup=get_main_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === Google Play ===
    if data == "gplay_add":
        context.user_data['waiting_for'] = 'gplay_add'
        await query.message.edit_text(
            t("gplay.enter_package", user_id),
            reply_markup=get_cancel_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    if data == "gplay_list":
        await query.message.edit_text(
            "📱 **Ваши приложения:**\n\n"
            "Список пуст.",
            reply_markup=get_gplay_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    # === Подписки ===
    if data.startswith("sub_") and not data.startswith("sub_crypto_") and not data.startswith("sub_stars_"):
        from handlers.generator_handler import subscription_callback
        await subscription_callback(update, context)
        return
    
    if data.startswith("sub_crypto_") or data.startswith("sub_stars_") or data.startswith("pay_") or data.startswith("check_payment_"):
        from handlers.generator_handler import subscription_callback
        await subscription_callback(update, context)
        return
    
    # === Генераторы (селфи, адреса, карты, антидетект) ===
    if data.startswith("selfie_"):
        from handlers.misc_handler import selfie_callback
        await selfie_callback(update, context)
        return
    
    if data.startswith("addr_"):
        from handlers.generator_handler import address_callback
        await address_callback(update, context)
        return
    
    if data.startswith("card_"):
        from handlers.generator_handler import card_callback
        await card_callback(update, context)
        return
    
    if data.startswith("antidetect_"):
        from handlers.generator_handler import antidetect_callback
        await antidetect_callback(update, context)
        return
    
    # === Отмена ===
    if data == "cancel":
        context.user_data.pop('waiting_for', None)
        await query.message.edit_text(
            t("welcome", user_id),
            reply_markup=get_main_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return


async def message_handler(update: Update, context):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    waiting_for = context.user_data.get('waiting_for')
    
    if not waiting_for:
        # Если не ждём ввода, показываем главное меню
        await update.message.reply_text(
            t("welcome", user_id),
            reply_markup=get_main_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return
    
    text = update.message.text
    
    # === 2FA ===
    if waiting_for == 'twofa':
        from utils import generate_2fa_code
        code = generate_2fa_code(text.strip())
        
        if code:
            await update.message.reply_text(
                f"🔐 **Ваш 2FA код:**\n\n"
                f"`{code}`\n\n"
                f"⚠️ Код действителен 30 секунд",
                reply_markup=get_main_menu_keyboard(user_id),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка генерации кода. Проверьте правильность секретного ключа.",
                reply_markup=get_main_menu_keyboard(user_id)
            )
        context.user_data.pop('waiting_for', None)
        return
    
    # === Уникализация текста ===
    if waiting_for == 'text_uniq':
        from utils import uniqualize_text
        result = uniqualize_text(text)
        
        await update.message.reply_text(
            f"🔄 **Уникализированный текст:**\n\n{result}",
            reply_markup=get_main_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        context.user_data.pop('waiting_for', None)
        return
    
    # === TikTok URL ===
    if waiting_for == 'tiktok_url':
        from utils import download_tiktok_video
        import tempfile
        import os
        
        status_msg = await update.message.reply_text("⏳ Скачиваю видео с TikTok...")
        
        try:
            # Создаём временный файл
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, 'tiktok_video')
            
            # Функция синхронная
            success, result = download_tiktok_video(text.strip(), output_path)
            
            if success:
                video_path = result
                
                # Проверяем нужно ли уникализировать
                if context.user_data.get('tiktok_uniq'):
                    from utils import uniqualize_video
                    await status_msg.edit_text("⏳ Уникализирую видео...")
                    uniq_path = os.path.join(temp_dir, 'tiktok_uniq.mp4')
                    uniq_success, uniq_result = uniqualize_video(video_path, uniq_path)
                    if uniq_success:
                        video_path = uniq_path
                
                with open(video_path, 'rb') as f:
                    await update.message.reply_video(
                        video=f,
                        caption="✅ Видео скачано!" + (" и уникализировано!" if context.user_data.get('tiktok_uniq') else ""),
                        reply_markup=get_main_menu_keyboard(user_id)
                    )
                await status_msg.delete()
                
                # Удаляем временные файлы
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            else:
                await status_msg.edit_text(
                    f"❌ Не удалось скачать видео.\n\nОшибка: {result[:200] if result else 'Неизвестная ошибка'}",
                    reply_markup=get_main_menu_keyboard(user_id)
                )
        except Exception as e:
            await status_msg.edit_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=get_main_menu_keyboard(user_id)
            )
        context.user_data.pop('waiting_for', None)
        context.user_data.pop('tiktok_uniq', None)
        return
    
    # === Site URL ===
    if waiting_for == 'site_url':
        from utils import download_website
        
        await update.message.reply_text("⏳ Скачиваю сайт...")
        
        try:
            result = await download_website(text.strip())
            if result:
                await update.message.reply_document(
                    document=open(result, 'rb'),
                    caption="✅ Сайт скачан!",
                    reply_markup=get_main_menu_keyboard(user_id)
                )
            else:
                await update.message.reply_text(
                    "❌ Не удалось скачать сайт.",
                    reply_markup=get_main_menu_keyboard(user_id)
                )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=get_main_menu_keyboard(user_id)
            )
        context.user_data.pop('waiting_for', None)
        return
    
    # === Google Play ===
    if waiting_for == 'gplay_add':
        await update.message.reply_text(
            f"✅ Приложение `{text}` добавлено в отслеживание.",
            reply_markup=get_main_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        context.user_data.pop('waiting_for', None)
        return
    
    # === Админ-команды ===
    if waiting_for == 'admin_vip_add':
        from keyboards import get_admin_back_keyboard
        from utils.whitelist import add_to_vip
        
        parts = text.strip().split(maxsplit=1)
        try:
            target_id = int(parts[0])
            note = parts[1] if len(parts) > 1 else None
            
            if add_to_vip(target_id, note):
                await update.message.reply_text(
                    f"✅ Пользователь `{target_id}` добавлен в VIP!",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"⚠️ Пользователь `{target_id}` уже в VIP.",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат ID.",
                reply_markup=get_admin_back_keyboard()
            )
        context.user_data.pop('waiting_for', None)
        return
    
    if waiting_for == 'admin_vip_remove':
        from keyboards import get_admin_back_keyboard
        from utils.whitelist import remove_from_vip
        
        try:
            target_id = int(text.strip())
            
            if remove_from_vip(target_id):
                await update.message.reply_text(
                    f"✅ Пользователь `{target_id}` удалён из VIP.",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"⚠️ Пользователь `{target_id}` не найден в VIP.",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат ID.",
                reply_markup=get_admin_back_keyboard()
            )
        context.user_data.pop('waiting_for', None)
        return
    
    if waiting_for == 'admin_ban_add':
        from keyboards import get_admin_back_keyboard
        from utils.admin_utils import ban_user
        
        parts = text.strip().split(maxsplit=1)
        try:
            target_id = int(parts[0])
            reason = parts[1] if len(parts) > 1 else None
            
            if ban_user(target_id, reason):
                await update.message.reply_text(
                    f"🚫 Пользователь `{target_id}` забанен!",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"⚠️ Пользователь `{target_id}` уже забанен.",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат ID.",
                reply_markup=get_admin_back_keyboard()
            )
        context.user_data.pop('waiting_for', None)
        return
    
    if waiting_for == 'admin_ban_remove':
        from keyboards import get_admin_back_keyboard
        from utils.admin_utils import unban_user
        
        try:
            target_id = int(text.strip())
            
            if unban_user(target_id):
                await update.message.reply_text(
                    f"✅ Пользователь `{target_id}` разбанен!",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"⚠️ Пользователь `{target_id}` не был забанен.",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат ID.",
                reply_markup=get_admin_back_keyboard()
            )
        context.user_data.pop('waiting_for', None)
        return
    
    if waiting_for == 'admin_broadcast':
        from keyboards import get_admin_back_keyboard
        from utils.admin_utils import get_all_users
        
        users = get_all_users()
        success = 0
        failed = 0
        
        status_msg = await update.message.reply_text("📤 Рассылаю...")
        
        for uid in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=text,
                    parse_mode="Markdown"
                )
                success += 1
            except:
                failed += 1
        
        await status_msg.edit_text(
            f"✅ **Рассылка завершена!**\n\n"
            f"✅ Успешно: {success}\n"
            f"❌ Ошибок: {failed}",
            reply_markup=get_admin_back_keyboard(),
            parse_mode="Markdown"
        )
        context.user_data.pop('waiting_for', None)
        return
    
    if waiting_for == 'admin_userinfo':
        from keyboards import get_admin_back_keyboard
        from utils.admin_utils import get_user_info
        from utils.whitelist import is_vip
        
        try:
            target_id = int(text.strip())
            info = get_user_info(target_id)
            
            if info:
                vip_status = "👑 VIP" if is_vip(target_id) else "❌ Нет"
                username = info.get('username', '-')
                first_name = info.get('first_name', '-')
                registered = info.get('registered_at', '-')[:10] if info.get('registered_at') else '-'
                last_active = info.get('last_active', '-')[:10] if info.get('last_active') else '-'
                
                await update.message.reply_text(
                    f"👤 **Информация о пользователе**\n\n"
                    f"🆔 ID: `{target_id}`\n"
                    f"👤 Имя: {first_name}\n"
                    f"📝 Username: @{username}\n"
                    f"📅 Регистрация: {registered}\n"
                    f"🟢 Последняя активность: {last_active}\n"
                    f"👑 VIP: {vip_status}",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"⚠️ Пользователь `{target_id}` не найден.",
                    reply_markup=get_admin_back_keyboard(),
                    parse_mode="Markdown"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат ID.",
                reply_markup=get_admin_back_keyboard()
            )
        context.user_data.pop('waiting_for', None)
        return


async def photo_handler(update: Update, context):
    """Обработчик фото"""
    user_id = update.effective_user.id
    user = update.effective_user
    waiting_for = context.user_data.get('waiting_for')
    
    logger.info(f"Photo received from {user_id}, waiting_for={waiting_for}")
    
    if waiting_for == 'uniq_photo':
        from utils import uniqualize_image
        import tempfile
        import os
        
        await update.message.reply_text("⏳ Уникализирую фото...")
        
        try:
            photo = update.message.photo[-1] if update.message.photo else update.message.document
            file = await photo.get_file()
            
            temp_dir = tempfile.mkdtemp()
            input_path = os.path.join(temp_dir, "input.jpg")
            output_path = os.path.join(temp_dir, "output.jpg")
            
            await file.download_to_drive(input_path)
            
            settings = context.user_data.get('uniq_settings')
            uniqualize_image(input_path, output_path, settings)
            
            with open(output_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    caption="✅ Фото уникализировано!",
                    reply_markup=get_main_menu_keyboard(user_id)
                )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=get_main_menu_keyboard(user_id)
            )
        
        context.user_data.pop('waiting_for', None)
        return
    
    if waiting_for == 'exif_view':
        from utils import read_exif, format_exif_for_display
        import tempfile
        import os
        
        try:
            photo = update.message.photo[-1] if update.message.photo else update.message.document
            file = await photo.get_file()
            
            temp_dir = tempfile.mkdtemp()
            input_path = os.path.join(temp_dir, "input.jpg")
            await file.download_to_drive(input_path)
            
            exif_data = read_exif(input_path)
            formatted = format_exif_for_display(exif_data)
            
            await update.message.reply_text(
                f"📷 **EXIF данные:**\n\n{formatted}",
                reply_markup=get_main_menu_keyboard(user_id),
                parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=get_main_menu_keyboard(user_id)
            )
        
        context.user_data.pop('waiting_for', None)
        return
    
    if waiting_for == 'exif_clear':
        from utils import clear_exif
        import tempfile
        import os
        
        await update.message.reply_text("⏳ Очищаю EXIF...")
        
        try:
            photo = update.message.photo[-1] if update.message.photo else update.message.document
            file = await photo.get_file()
            
            temp_dir = tempfile.mkdtemp()
            input_path = os.path.join(temp_dir, "input.jpg")
            output_path = os.path.join(temp_dir, "output.jpg")
            
            await file.download_to_drive(input_path)
            clear_exif(input_path, output_path)
            
            with open(output_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    caption="✅ EXIF данные очищены!",
                    reply_markup=get_main_menu_keyboard(user_id)
                )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=get_main_menu_keyboard(user_id)
            )
        
        context.user_data.pop('waiting_for', None)
        return
    
    # Если не ждём фото
    await update.message.reply_text(
        t("welcome", user_id),
        reply_markup=get_main_menu_keyboard(user_id),
        parse_mode="Markdown"
    )


async def video_handler(update: Update, context):
    """Обработчик видео"""
    user_id = update.effective_user.id
    user = update.effective_user
    waiting_for = context.user_data.get('waiting_for')
    
    logger.info(f"Video received from {user_id}, waiting_for={waiting_for}")
    
    if waiting_for == 'uniq_video':
        from utils import uniqualize_video
        import tempfile
        import os
        
        await update.message.reply_text("⏳ Уникализирую видео... Это может занять некоторое время.")
        
        try:
            video = update.message.video or update.message.document
            file = await video.get_file()
            
            temp_dir = tempfile.mkdtemp()
            input_path = os.path.join(temp_dir, "input.mp4")
            output_path = os.path.join(temp_dir, "output.mp4")
            
            await file.download_to_drive(input_path)
            
            settings = context.user_data.get('uniq_settings')
            uniqualize_video(input_path, output_path, settings)
            
            with open(output_path, 'rb') as f:
                await update.message.reply_video(
                    video=f,
                    caption="✅ Видео уникализировано!",
                    reply_markup=get_main_menu_keyboard(user_id)
                )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ошибка: {str(e)}",
                reply_markup=get_main_menu_keyboard(user_id)
            )
        
        context.user_data.pop('waiting_for', None)
        return
    
    # Если не ждём видео
    await update.message.reply_text(
        t("welcome", user_id),
        reply_markup=get_main_menu_keyboard(user_id),
        parse_mode="Markdown"
    )


async def document_handler(update: Update, context):
    """Обработчик документов (файлов)"""
    user_id = update.effective_user.id
    waiting_for = context.user_data.get('waiting_for')
    
    # Определяем тип файла
    doc = update.message.document
    mime_type = doc.mime_type if doc else ""
    
    if waiting_for == 'uniq_photo' and mime_type.startswith('image/'):
        await photo_handler(update, context)
        return
    
    if waiting_for == 'uniq_video' and mime_type.startswith('video/'):
        await video_handler(update, context)
        return
    
    if waiting_for in ['exif_view', 'exif_clear'] and mime_type.startswith('image/'):
        await photo_handler(update, context)
        return
    
    # Если не ждём документ
    await update.message.reply_text(
        t("welcome", user_id),
        reply_markup=get_main_menu_keyboard(user_id),
        parse_mode="Markdown"
    )


# === Админ-команды ===

async def addvip_command(update: Update, context):
    """Добавление пользователя в VIP (whitelist)"""
    from utils.whitelist import is_admin, add_vip
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "ℹ️ **Использование:**\n"
            "`/addvip <user_id> [примечание]`\n\n"
            "Пример: `/addvip 123456789 Друг`",
            parse_mode="Markdown"
        )
        return
    
    try:
        target_id = int(context.args[0])
        note = " ".join(context.args[1:]) if len(context.args) > 1 else None
        
        if add_vip(target_id, user_id, note):
            await update.message.reply_text(
                f"✅ Пользователь `{target_id}` добавлен в VIP!\n"
                f"📝 Примечание: {note or 'нет'}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Ошибка при добавлении.")
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID. Укажите числовой ID.")


async def removevip_command(update: Update, context):
    """Удаление пользователя из VIP"""
    from utils.whitelist import is_admin, remove_vip
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "ℹ️ **Использование:**\n"
            "`/removevip <user_id>`\n\n"
            "Пример: `/removevip 123456789`",
            parse_mode="Markdown"
        )
        return
    
    try:
        target_id = int(context.args[0])
        
        if remove_vip(target_id):
            await update.message.reply_text(f"✅ Пользователь `{target_id}` удалён из VIP.", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ Пользователь `{target_id}` не найден в VIP.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID. Укажите числовой ID.")


async def listvip_command(update: Update, context):
    """Список всех VIP пользователей"""
    from utils.whitelist import is_admin, get_vip_list, get_vip_count
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    vip_list = get_vip_list()
    count = get_vip_count()
    
    if not vip_list:
        await update.message.reply_text("📝 **VIP список пуст.**", parse_mode="Markdown")
        return
    
    text = f"👑 **VIP пользователи ({count}):**\n\n"
    
    for vip in vip_list:
        added_at = vip['added_at'][:10] if vip['added_at'] else 'неизвестно'
        note = vip['note'] or '-'
        text += f"• `{vip['user_id']}` | {added_at} | {note}\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def admin_command(update: Update, context):
    """Показать список админ-команд"""
    from utils.whitelist import is_admin
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    text = (
        "🔧 **Админ-команды:**\n\n"
        "**VIP управление:**\n"
        "`/addvip <id> [примечание]` - добавить VIP\n"
        "`/removevip <id>` - удалить VIP\n"
        "`/listvip` - список VIP\n\n"
        "**Пользователи:**\n"
        "`/userinfo <id>` - инфо о пользователе\n"
        "`/setplan <id> <plan>` - установить подписку\n"
        "`/ban <id> [причина]` - забанить\n"
        "`/unban <id>` - разбанить\n"
        "`/banlist` - список забаненных\n\n"
        "**Статистика:**\n"
        "`/stats` - общая статистика\n"
        "`/topusers` - топ активных\n\n"
        "**Рассылка:**\n"
        "`/broadcast <текст>` - всем пользователям\n\n"
        "**Управление:**\n"
        "`/maintenance on/off` - режим обслуживания\n"
    )
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def userinfo_command(update: Update, context):
    """Информация о пользователе"""
    from utils.whitelist import is_admin, is_vip
    from utils.admin_utils import get_user_info, is_banned
    from utils.subscription import get_user_subscription, get_user_usage, SUBSCRIPTION_PLANS
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    if not context.args:
        await update.message.reply_text("ℹ️ **Использование:** `/userinfo <user_id>`", parse_mode="Markdown")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID.")
        return
    
    user_info = get_user_info(target_id)
    plan_id = get_user_subscription(target_id)
    plan = SUBSCRIPTION_PLANS.get(plan_id, {})
    usage = get_user_usage(target_id)
    vip = is_vip(target_id)
    banned = is_banned(target_id)
    
    text = f"👤 **Пользователь:** `{target_id}`\n\n"
    
    if user_info:
        text += f"📝 Имя: {user_info.get('first_name', '-')}\n"
        text += f"👤 Username: @{user_info.get('username', '-')}\n"
        text += f"📅 Регистрация: {user_info.get('registered_at', '-')[:10]}\n"
        text += f"🕒 Последняя активность: {user_info.get('last_active', '-')[:10]}\n"
    else:
        text += "⚠️ Пользователь не найден в базе\n"
    
    text += f"\n{plan.get('icon', '⭐')} **Подписка:** {plan.get('name', plan_id)}\n"
    
    if vip:
        text += "👑 **VIP:** Да\n"
    if banned:
        text += "🚫 **Забанен:** Да\n"
    
    text += f"\n📊 **Использование сегодня:**\n"
    text += f"• Фото: {usage.get('photos', 0)}\n"
    text += f"• Видео: {usage.get('videos', 0)}\n"
    text += f"• EXIF: {usage.get('exif', 0)}\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def setplan_command(update: Update, context):
    """Установить подписку пользователю"""
    from utils.whitelist import is_admin
    from utils.subscription import set_user_subscription, SUBSCRIPTION_PLANS
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    if len(context.args) < 2:
        plans = ", ".join(SUBSCRIPTION_PLANS.keys())
        await update.message.reply_text(
            f"ℹ️ **Использование:** `/setplan <user_id> <plan>`\n\n"
            f"Доступные планы: `{plans}`",
            parse_mode="Markdown"
        )
        return
    
    try:
        target_id = int(context.args[0])
        plan = context.args[1].lower()
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID.")
        return
    
    if plan not in SUBSCRIPTION_PLANS:
        await update.message.reply_text(f"❌ Неизвестный план: `{plan}`", parse_mode="Markdown")
        return
    
    if set_user_subscription(target_id, plan):
        plan_info = SUBSCRIPTION_PLANS[plan]
        await update.message.reply_text(
            f"✅ Пользователю `{target_id}` установлена подписка:\n"
            f"{plan_info['icon']} **{plan_info['name']}**",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Ошибка при установке подписки.")


async def ban_command(update: Update, context):
    """Забанить пользователя"""
    from utils.whitelist import is_admin
    from utils.admin_utils import ban_user
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    if not context.args:
        await update.message.reply_text("ℹ️ **Использование:** `/ban <user_id> [причина]`", parse_mode="Markdown")
        return
    
    try:
        target_id = int(context.args[0])
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else None
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID.")
        return
    
    if ban_user(target_id, user_id, reason):
        await update.message.reply_text(
            f"🚫 Пользователь `{target_id}` забанен.\n"
            f"📝 Причина: {reason or 'не указана'}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Ошибка при бане.")


async def unban_command(update: Update, context):
    """Разбанить пользователя"""
    from utils.whitelist import is_admin
    from utils.admin_utils import unban_user
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    if not context.args:
        await update.message.reply_text("ℹ️ **Использование:** `/unban <user_id>`", parse_mode="Markdown")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID.")
        return
    
    if unban_user(target_id):
        await update.message.reply_text(f"✅ Пользователь `{target_id}` разбанен.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Пользователь `{target_id}` не найден в бан-листе.", parse_mode="Markdown")


async def banlist_command(update: Update, context):
    """Список забаненных пользователей"""
    from utils.whitelist import is_admin
    from utils.admin_utils import get_banned_list
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    banned_list = get_banned_list()
    
    if not banned_list:
        await update.message.reply_text("📝 **Бан-лист пуст.**", parse_mode="Markdown")
        return
    
    text = f"🚫 **Забаненные пользователи ({len(banned_list)}):**\n\n"
    
    for user in banned_list:
        banned_at = user['banned_at'][:10] if user['banned_at'] else '-'
        reason = user['reason'] or '-'
        text += f"• `{user['user_id']}` | {banned_at} | {reason}\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def stats_command(update: Update, context):
    """Общая статистика бота"""
    from utils.whitelist import is_admin
    from utils.admin_utils import get_bot_stats
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    stats = get_bot_stats()
    subs = stats['subscriptions']
    
    text = (
        "📊 **Статистика бота**\n\n"
        f"👥 Всего пользователей: **{stats['total_users']}**\n"
        f"🟢 Активных сегодня: **{stats['active_today']}**\n"
        f"👑 VIP: **{stats['vip_count']}**\n"
        f"🚫 Забанено: **{stats['banned_count']}**\n\n"
        "**Подписки:**\n"
        f"🆓 Free: {subs.get('free', 0)}\n"
        f"⭐ Basic: {subs.get('basic', 0)}\n"
        f"💎 Pro: {subs.get('pro', 0)}\n"
        f"👑 Premium: {subs.get('premium', 0)}\n"
        f"♾ Lifetime: {subs.get('lifetime', 0)}\n"
    )
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def topusers_command(update: Update, context):
    """Топ активных пользователей"""
    from utils.whitelist import is_admin
    from utils.admin_utils import get_top_users
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    top_users = get_top_users(10)
    
    if not top_users:
        await update.message.reply_text("📝 **Нет данных об использовании.**", parse_mode="Markdown")
        return
    
    text = "🏆 **Топ-10 активных пользователей:**\n\n"
    
    for i, user in enumerate(top_users, 1):
        username = f"@{user['username']}" if user['username'] else f"`{user['user_id']}`"
        text += f"{i}. {username} - {user['total_usage']} действий\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def broadcast_command(update: Update, context):
    """Рассылка всем пользователям"""
    from utils.whitelist import is_admin
    from utils.admin_utils import get_all_users
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    if not context.args:
        await update.message.reply_text("ℹ️ **Использование:** `/broadcast <текст сообщения>`", parse_mode="Markdown")
        return
    
    message_text = " ".join(context.args)
    users = get_all_users()
    
    if not users:
        await update.message.reply_text("❌ Нет пользователей для рассылки.")
        return
    
    await update.message.reply_text(f"📤 Начинаю рассылку {len(users)} пользователям...")
    
    success = 0
    failed = 0
    
    for uid in users:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 **Сообщение от администрации:**\n\n{message_text}",
                parse_mode="Markdown"
            )
            success += 1
        except Exception:
            failed += 1
    
    await update.message.reply_text(
        f"✅ **Рассылка завершена**\n\n"
        f"✅ Успешно: {success}\n"
        f"❌ Ошибок: {failed}",
        parse_mode="Markdown"
    )


async def maintenance_command(update: Update, context):
    """Режим обслуживания"""
    from utils.whitelist import is_admin
    from utils.admin_utils import set_maintenance_mode, is_maintenance_mode, get_all_users
    
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    if not context.args:
        current = "Выключен" if is_maintenance_mode() else "Включён"
        await update.message.reply_text(
            f"ℹ️ **Статус бота:** {current}\n\n"
            "Использование:\n"
            "`/maintenance on` - включить бота\n"
            "`/maintenance off` - выключить бота (тех. работы)",
            parse_mode="Markdown"
        )
        return
    
    action = context.args[0].lower()
    
    if action == "off":
        set_maintenance_mode(True)
        await update.message.reply_text("🔧 **Бот выключен (тех. работы).**\n\nРассылаю уведомления...", parse_mode="Markdown")
        
        # Рассылаем уведомления всем пользователям
        users = get_all_users()
        success = 0
        
        for uid in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text="🔧 **Технические работы**\n\n"
                         "Бот временно недоступен. Пожалуйста, подождите.\n"
                         "Мы сообщим, когда работа будет восстановлена.",
                    parse_mode="Markdown"
                )
                success += 1
            except Exception:
                pass
        
        await update.message.reply_text(f"✅ Уведомления отправлены: {success}/{len(users)}")
        
    elif action == "on":
        set_maintenance_mode(False)
        await update.message.reply_text("✅ **Бот включён!**\n\nРассылаю уведомления...", parse_mode="Markdown")
        
        # Рассылаем уведомления всем пользователям
        users = get_all_users()
        success = 0
        
        for uid in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text="✅ **Бот снова работает!**\n\n"
                         "Технические работы завершены.\n"
                         "Нажмите /start для продолжения.",
                    parse_mode="Markdown"
                )
                success += 1
            except Exception:
                pass
        
        await update.message.reply_text(f"✅ Уведомления отправлены: {success}/{len(users)}")
    else:
        await update.message.reply_text("❌ Используйте: `/maintenance on` или `/maintenance off`", parse_mode="Markdown")


async def precheckout_callback(update: Update, context):
    """Предварительная проверка оплаты Telegram Stars"""
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment(update: Update, context):
    """Обработчик успешной оплаты Telegram Stars"""
    from utils.subscription import set_user_subscription, SUBSCRIPTION_PLANS
    
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    user_id = update.effective_user.id
    
    if payload.startswith("stars_"):
        parts = payload.split("_")
        if len(parts) >= 3:
            plan_id = parts[2]
            
            if set_user_subscription(user_id, plan_id):
                plan = SUBSCRIPTION_PLANS.get(plan_id, {})
                duration = "навсегда" if plan_id == "lifetime" else f"{plan.get('duration_days', 30)} дней"
                
                await update.message.reply_text(
                    f"✅ **Подписка активирована!**\n\n"
                    f"{plan.get('icon', '⭐')} **{plan.get('name', plan_id)}**\n"
                    f"📅 Срок: {duration}",
                    reply_markup=get_main_menu_keyboard(user_id),
                    parse_mode="Markdown"
                )


def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Админ-команды
    application.add_handler(CommandHandler("addvip", addvip_command))
    application.add_handler(CommandHandler("removevip", removevip_command))
    application.add_handler(CommandHandler("listvip", listvip_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("userinfo", userinfo_command))
    application.add_handler(CommandHandler("setplan", setplan_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("banlist", banlist_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("topusers", topusers_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("maintenance", maintenance_command))
    
    # Единый callback handler для всех inline кнопок
    application.add_handler(CallbackQueryHandler(main_callback_handler))
    
    # Обработчики медиа
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.VIDEO, video_handler))
    application.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Обработчики оплаты Telegram Stars
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    
    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
