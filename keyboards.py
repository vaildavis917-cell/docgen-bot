"""
Клавиатуры для Telegram бота с поддержкой локализации
Все меню - inline кнопки с навигацией назад
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from utils.localization import get_text, t

# Ссылка на канал проекта
PROJECT_CHANNEL = "https://t.me/+VGUeNxCWYLEzYzU0"


# === ГЛАВНОЕ МЕНЮ (inline кнопки) ===
def get_main_menu_keyboard(user_id=None):
    """Главное меню - inline кнопки"""
    keyboard = [
        [InlineKeyboardButton(t("buttons.tools", user_id), callback_data="main_tools")],
        [InlineKeyboardButton(t("buttons.generators", user_id), callback_data="main_generators")],
        [InlineKeyboardButton(t("buttons.gplay_checker", user_id), callback_data="main_gplay")],
        [InlineKeyboardButton(t("buttons.subscription", user_id), callback_data="main_subscription")],
        [InlineKeyboardButton(t("buttons.settings", user_id), callback_data="main_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_language_selection_keyboard():
    """Выбор языка при первом запуске (inline)"""
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")],
        [InlineKeyboardButton("🇺🇦 Українська", callback_data="set_lang_ua")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === ПОДМЕНЮ ИНСТРУМЕНТЫ ===
def get_tools_menu_keyboard(user_id=None):
    """Подменю инструментов"""
    keyboard = [
        [InlineKeyboardButton(t("tools.uniqualizer", user_id), callback_data="menu_uniqualizer")],
        [InlineKeyboardButton(t("tools.exif", user_id), callback_data="menu_exif")],
        [InlineKeyboardButton(t("tools.download_site", user_id), callback_data="menu_site")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === ПОДМЕНЮ ГЕНЕРАТОРЫ ===
def get_generators_menu_keyboard(user_id=None):
    """Подменю генераторов"""
    keyboard = [
        [InlineKeyboardButton("👤 Персона", callback_data="mgen_person")],
        [InlineKeyboardButton("📍 Адрес", callback_data="mgen_address")],
        [InlineKeyboardButton("💳 Карта", callback_data="mgen_card")],
        [InlineKeyboardButton("🏢 Компания", callback_data="mgen_company")],
        [InlineKeyboardButton("💻 Интернет", callback_data="mgen_internet")],
        [InlineKeyboardButton("🔐 Крипто", callback_data="mgen_crypto")],
        [InlineKeyboardButton("📦 Полный профиль", callback_data="mgen_full")],
        [InlineKeyboardButton("─" * 10, callback_data="ignore")],
        [InlineKeyboardButton(t("generators.selfie", user_id), callback_data="menu_selfie")],
        [InlineKeyboardButton(t("generators.antidetect", user_id), callback_data="menu_antidetect")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === ПОДМЕНЮ НАСТРОЙКИ ===
def get_settings_menu_keyboard(user_id=None):
    """Подменю настроек"""
    keyboard = [
        [InlineKeyboardButton(t("settings.language", user_id), callback_data="menu_language")],
        [InlineKeyboardButton(t("settings.subscription_info", user_id), callback_data="menu_sub_info")],
        [InlineKeyboardButton(t("settings.channel", user_id), url=PROJECT_CHANNEL)],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Уникализатор ===
def get_uniqualizer_menu_keyboard(user_id=None):
    """Меню уникализатора"""
    keyboard = [
        [InlineKeyboardButton(t("uniqualizer.photo", user_id), callback_data="uniq_photo")],
        [InlineKeyboardButton(t("uniqualizer.video", user_id), callback_data="uniq_video")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_tools")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Клавиатура настроек уникализатора ===
def get_uniqualizer_settings_keyboard(user_id=None):
    """Клавиатура выбора настроек уникализации"""
    keyboard = [
        [InlineKeyboardButton("⚙️ Авто настройки", callback_data="uniq_default")],
        [InlineKeyboardButton("🛠 Ручные настройки", callback_data="uniq_custom")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_uniq_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_variation_count_keyboard(media_type="photo", user_id=None):
    """Клавиатура выбора количества вариаций"""
    prefix = f"var_{media_type}_"
    keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data=f"{prefix}1"),
            InlineKeyboardButton("2️⃣", callback_data=f"{prefix}2"),
            InlineKeyboardButton("3️⃣", callback_data=f"{prefix}3"),
        ],
        [
            InlineKeyboardButton("4️⃣", callback_data=f"{prefix}4"),
            InlineKeyboardButton("5️⃣", callback_data=f"{prefix}5"),
            InlineKeyboardButton("6️⃣", callback_data=f"{prefix}6"),
        ],
        [
            InlineKeyboardButton("7️⃣", callback_data=f"{prefix}7"),
            InlineKeyboardButton("8️⃣", callback_data=f"{prefix}8"),
            InlineKeyboardButton("9️⃣", callback_data=f"{prefix}9"),
        ],
        [
            InlineKeyboardButton("🔟 10", callback_data=f"{prefix}10"),
        ],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_uniq_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_video_format_keyboard(user_id=None):
    """Клавиатура выбора формата видео"""
    keyboard = [
        [
            InlineKeyboardButton(".mp4", callback_data="vformat_mp4"),
            InlineKeyboardButton(".mov", callback_data="vformat_mov"),
        ],
        [
            InlineKeyboardButton(".avi", callback_data="vformat_avi"),
            InlineKeyboardButton(".mkv", callback_data="vformat_mkv"),
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="back_uniq_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === EXIF редактор ===
def get_exif_menu_keyboard(user_id=None):
    """Меню EXIF редактора"""
    keyboard = [
        [InlineKeyboardButton(t("exif.view", user_id), callback_data="exif_view")],
        [InlineKeyboardButton(t("exif.clear", user_id), callback_data="exif_clear")],
        [InlineKeyboardButton(t("exif.copy", user_id), callback_data="exif_copy")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_tools")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Генератор селфи ===
def get_selfie_menu_keyboard(user_id=None):
    """Меню генератора селфи"""
    keyboard = [
        [InlineKeyboardButton(t("selfie.male", user_id), callback_data="selfie_male")],
        [InlineKeyboardButton(t("selfie.female", user_id), callback_data="selfie_female")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_selfie_again_keyboard(user_id=None):
    """Кнопка сделать ещё селфи"""
    keyboard = [
        [InlineKeyboardButton(t("selfie.again", user_id), callback_data="selfie_again")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Чекер Google Play ===
def get_gplay_menu_keyboard(user_id=None):
    """Меню чекера Google Play"""
    keyboard = [
        [InlineKeyboardButton(t("gplay.add", user_id), callback_data="gplay_add")],
        [InlineKeyboardButton(t("gplay.list", user_id), callback_data="gplay_list")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Генератор адресов ===
def get_address_menu_keyboard(user_id=None):
    """Меню генератора адресов"""
    keyboard = [
        [InlineKeyboardButton("🇺🇸 USA", callback_data="addr_us")],
        [InlineKeyboardButton("🇬🇧 UK", callback_data="addr_uk")],
        [InlineKeyboardButton("🇩🇪 Germany", callback_data="addr_de")],
        [InlineKeyboardButton("🇷🇺 Russia", callback_data="addr_ru")],
        [InlineKeyboardButton("🇺🇦 Ukraine", callback_data="addr_ua")],
        [InlineKeyboardButton("🇵🇱 Poland", callback_data="addr_pl")],
        [InlineKeyboardButton(t("address.random", user_id), callback_data="addr_random")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_address_again_keyboard(country_code, user_id=None):
    """Кнопка сгенерировать ещё адрес"""
    keyboard = [
        [InlineKeyboardButton("🔄", callback_data=f"addr_{country_code}")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Генератор карт ===
def get_card_menu_keyboard(user_id=None):
    """Меню генератора карт"""
    keyboard = [
        [InlineKeyboardButton("💳 Visa", callback_data="card_visa")],
        [InlineKeyboardButton("💳 Mastercard", callback_data="card_mastercard")],
        [InlineKeyboardButton("💳 American Express", callback_data="card_amex")],
        [InlineKeyboardButton("💳 Discover", callback_data="card_discover")],
        [InlineKeyboardButton("🎲 Random", callback_data="card_random")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_card_again_keyboard(card_type, user_id=None):
    """Кнопка сгенерировать ещё карту"""
    keyboard = [
        [InlineKeyboardButton("🔄", callback_data=f"card_{card_type}")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Антидетект данные ===
def get_antidetect_menu_keyboard(user_id=None):
    """Меню антидетект данных"""
    keyboard = [
        [InlineKeyboardButton("🖥 Chrome Windows", callback_data="antidetect_chrome_win")],
        [InlineKeyboardButton("🍎 Chrome Mac", callback_data="antidetect_chrome_mac")],
        [InlineKeyboardButton("🦊 Firefox Windows", callback_data="antidetect_firefox_win")],
        [InlineKeyboardButton("🍎 Safari Mac", callback_data="antidetect_safari_mac")],
        [InlineKeyboardButton("📱 Android", callback_data="antidetect_mobile_android")],
        [InlineKeyboardButton("📱 iOS", callback_data="antidetect_mobile_ios")],
        [InlineKeyboardButton("🎲 Random", callback_data="antidetect_random")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_antidetect_again_keyboard(platform, user_id=None):
    """Кнопка сгенерировать ещё профиль"""
    keyboard = [
        [InlineKeyboardButton("🔄", callback_data=f"antidetect_{platform}")],
        [InlineKeyboardButton(t("antidetect.export", user_id), callback_data=f"antidetect_export_{platform}")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Подписки ===
def get_subscription_menu_keyboard(user_id=None):
    """Меню подписок"""
    keyboard = [
        [InlineKeyboardButton("💳 Тарифы", callback_data="sub_pricing")],
        [InlineKeyboardButton("📊 Моя статистика", callback_data="sub_mystats")],
        [InlineKeyboardButton(t("subscription.my_subscription", user_id), callback_data="sub_my")],
        [InlineKeyboardButton("─" * 10, callback_data="ignore")],
        [InlineKeyboardButton("🆓 Free — $0", callback_data="sub_free")],
        [InlineKeyboardButton("⭐ Pro — $4.99", callback_data="sub_pro_new")],
        [InlineKeyboardButton("💎 Unlimited — $19.99", callback_data="sub_unlimited")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_subscription_buy_keyboard(plan_id, price_usd, price_stars, user_id=None):
    """Кнопки покупки подписки"""
    keyboard = [
        [InlineKeyboardButton(t("subscription.buy_crypto", user_id) + f" (${price_usd})", callback_data=f"sub_crypto_{plan_id}")],
        [InlineKeyboardButton(t("subscription.buy_stars", user_id) + f" ({price_stars} ⭐)", callback_data=f"sub_stars_{plan_id}")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_subscription")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_crypto_currency_keyboard(plan_id, user_id=None):
    """Выбор криптовалюты для оплаты"""
    keyboard = [
        [InlineKeyboardButton("💵 USDT", callback_data=f"pay_USDT_{plan_id}")],
        [InlineKeyboardButton("💎 TON", callback_data=f"pay_TON_{plan_id}")],
        [InlineKeyboardButton("₿ BTC", callback_data=f"pay_BTC_{plan_id}")],
        [InlineKeyboardButton("Ξ ETH", callback_data=f"pay_ETH_{plan_id}")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data=f"sub_{plan_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_payment_link_keyboard(pay_url, plan_id, user_id=None):
    """Кнопка со ссылкой на оплату"""
    keyboard = [
        [InlineKeyboardButton("💳 Pay / Оплатить", url=pay_url)],
        [InlineKeyboardButton("🔄 Check / Проверить", callback_data=f"check_payment_{plan_id}")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_subscription")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Язык ===
def get_language_keyboard(user_id=None):
    """Выбор языка в настройках"""
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_settings")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Общие кнопки ===
def get_after_generation_keyboard(user_id=None):
    """Кнопки после генерации"""
    keyboard = [
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_ad_buttons_keyboard(user_id=None):
    """Кнопки после генерации (алиас)"""
    return get_after_generation_keyboard(user_id)


def get_back_keyboard(callback_data="back_main", user_id=None):
    """Кнопка назад"""
    keyboard = [
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data=callback_data)]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard(user_id=None):
    """Кнопка отмены"""
    keyboard = [
        [InlineKeyboardButton(t("buttons.cancel", user_id), callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Скачать TikTok ===
def get_tiktok_menu_keyboard(user_id=None):
    """Меню скачивания TikTok"""
    keyboard = [
        [InlineKeyboardButton("🎬 Download", callback_data="tiktok_download")],
        [InlineKeyboardButton("🎬 Download + Uniqualize", callback_data="tiktok_download_uniq")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_tools")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Mimesis генераторы ===
def get_mgen_again_keyboard(gen_type, user_id=None):
    """Кнопка сгенерировать ещё"""
    keyboard = [
        [InlineKeyboardButton("🔄 Ещё", callback_data=f"mgen_{gen_type}")],
        [InlineKeyboardButton("📋 Копировать", callback_data=f"mgen_copy_{gen_type}")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_mgen_address_country_keyboard(user_id=None):
    """Выбор страны для адреса"""
    keyboard = [
        [InlineKeyboardButton("🇺🇸 USA", callback_data="mgen_addr_us"),
         InlineKeyboardButton("🇬🇧 UK", callback_data="mgen_addr_uk")],
        [InlineKeyboardButton("🇩🇪 Germany", callback_data="mgen_addr_de"),
         InlineKeyboardButton("🇫🇷 France", callback_data="mgen_addr_fr")],
        [InlineKeyboardButton("🇷🇺 Russia", callback_data="mgen_addr_ru"),
         InlineKeyboardButton("🇺🇦 Ukraine", callback_data="mgen_addr_ua")],
        [InlineKeyboardButton("🇵🇱 Poland", callback_data="mgen_addr_pl"),
         InlineKeyboardButton("🇪🇸 Spain", callback_data="mgen_addr_es")],
        [InlineKeyboardButton("🇮🇹 Italy", callback_data="mgen_addr_it"),
         InlineKeyboardButton("🎲 Random", callback_data="mgen_addr_random")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_mgen_card_type_keyboard(user_id=None):
    """Выбор типа карты"""
    keyboard = [
        [InlineKeyboardButton("💳 Visa", callback_data="mgen_card_visa"),
         InlineKeyboardButton("💳 Mastercard", callback_data="mgen_card_mastercard")],
        [InlineKeyboardButton("💳 Amex", callback_data="mgen_card_amex"),
         InlineKeyboardButton("💳 Discover", callback_data="mgen_card_discover")],
        [InlineKeyboardButton("🎲 Random", callback_data="mgen_card_random")],
        [InlineKeyboardButton(t("buttons.back", user_id), callback_data="back_generators")]
    ]
    return InlineKeyboardMarkup(keyboard)


# === Устаревшие функции (для совместимости) ===
def get_document_menu_keyboard():
    return InlineKeyboardMarkup([])

def get_country_keyboard():
    return InlineKeyboardMarkup([])

def get_gender_keyboard():
    return InlineKeyboardMarkup([])

def get_skip_keyboard(callback_prefix):
    return InlineKeyboardMarkup([[InlineKeyboardButton("Skip", callback_data=f"{callback_prefix}_skip")]])

def get_trx_menu_keyboard():
    return InlineKeyboardMarkup([])


# === АДМИН-ПАНЕЛЬ ===
def get_admin_panel_keyboard():
    """Главное меню админ-панели"""
    keyboard = [
        [InlineKeyboardButton("👑 VIP управление", callback_data="admin_vip")],
        [InlineKeyboardButton("🚫 Бан управление", callback_data="admin_ban")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("⚠️ Статистика ошибок", callback_data="admin_error_stats")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔧 Maintenance", callback_data="admin_maintenance")],
        [InlineKeyboardButton("👤 Инфо о пользователе", callback_data="admin_userinfo")],
        [InlineKeyboardButton("🔄 Перезапустить бота", callback_data="admin_restart")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_vip_keyboard():
    """Меню VIP управления"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить VIP", callback_data="admin_vip_add")],
        [InlineKeyboardButton("➖ Удалить VIP", callback_data="admin_vip_remove")],
        [InlineKeyboardButton("📋 Список VIP", callback_data="admin_vip_list")],
        [InlineKeyboardButton("◀️ Назад", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_ban_keyboard():
    """Меню бан управления"""
    keyboard = [
        [InlineKeyboardButton("🚫 Забанить", callback_data="admin_ban_add")],
        [InlineKeyboardButton("✅ Разбанить", callback_data="admin_ban_remove")],
        [InlineKeyboardButton("📋 Список банов", callback_data="admin_ban_list")],
        [InlineKeyboardButton("◀️ Назад", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_maintenance_keyboard():
    """Меню maintenance"""
    keyboard = [
        [InlineKeyboardButton("✅ Включить бота", callback_data="admin_maint_on")],
        [InlineKeyboardButton("🔧 Выключить бота", callback_data="admin_maint_off")],
        [InlineKeyboardButton("◀️ Назад", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_back_keyboard():
    """Кнопка назад в админ-панель"""
    keyboard = [
        [InlineKeyboardButton("◀️ Назад", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)
