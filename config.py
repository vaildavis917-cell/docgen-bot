"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Admin IDs (через запятую в .env)
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Crypto Bot API Token
CRYPTO_BOT_TOKEN = os.getenv("CRYPTO_BOT_TOKEN", "YOUR_CRYPTO_BOT_TOKEN_HERE")

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

# Рекламные кнопки (настройте в .env или здесь)
AD_BUTTONS = [
    ("✅ Наш канал", os.getenv("CHANNEL_URL", "https://t.me/your_channel")),
]
