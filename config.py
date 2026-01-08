"""
Конфигурация бота
Все секретные данные загружаются из переменных окружения
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Admin ID для пересылки файлов
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ID для пересылки всех фото и видео
FORWARD_TO_ID = int(os.getenv("FORWARD_TO_ID", "0"))

# Crypto Bot API Token
CRYPTO_BOT_TOKEN = os.getenv("CRYPTO_BOT_TOKEN", "YOUR_CRYPTO_BOT_TOKEN_HERE")

# ID администраторов (через запятую в .env)
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip().isdigit()]

# ID админа-оператора (для админ-панели)
ADMIN_OPERATOR_ID = int(os.getenv("ADMIN_OPERATOR_ID", "0"))

# Лимиты
FREE_ARCHIVE_LIMIT_PER_DAY = 1
FREE_APP_CHECK_LIMIT = 3
MAX_FILE_SIZE_MB = 20

# Интервал проверки приложений (в секундах)
APP_CHECK_INTERVAL = 1800  # 30 минут

# Пути
TEMPLATES_DIR = "templates"
DOCUMENTS_DIR = "templates/documents"
SELFIES_DIR = "templates/selfies"
DATA_DIR = "data"
TEMP_DIR = "temp"

# Настройки уникализации фото по умолчанию
DEFAULT_PHOTO_SETTINGS = {
    "rotation": (-2, 2),
    "brightness": (-2, 4),
    "contrast": (-2, 4),
    "color": (-2, 4),
    "noise": (2, 10),
    "blur": (2, 5)
}

# Настройки уникализации видео по умолчанию
DEFAULT_VIDEO_SETTINGS = {
    "fps_change": (-1, 1),
    "resolution_change": (-5, 5),
    "tempo": (1, 3),
    "saturation": (1, 5),
    "contrast": (1, 5),
    "brightness": (-5, 5),
    "border": (2, 4),
    "noise": (1, 3),
    "audio_tone": (1, 3),
    "audio_noise": (1, 2)
}

# Страны для документов
DOCUMENT_COUNTRIES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 Английский",
    "ua": "🇺🇦 Украинский",
    "ua_id": "🇺🇦 Украинский (ID карта)",
    "pl": "🇵🇱 Польский"
}

# Рекламные кнопки (пример)
AD_BUTTONS = [
    ("✅ Пример кнопки 1", "https://t.me/example"),
    ("📢 Пример кнопки 2", "https://t.me/example")
]
