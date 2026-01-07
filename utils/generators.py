"""
Генераторы данных:
- Адреса
- Карты
- Антидетект данные
"""

import random
import string
import hashlib
import uuid
import json
from datetime import datetime, timedelta


# === ГЕНЕРАТОР АДРЕСОВ ===

# Базы данных адресов по странам
ADDRESS_DATA = {
    "us": {
        "country": "США",
        "flag": "🇺🇸",
        "cities": [
            {"city": "New York", "state": "NY", "zip_format": "100##"},
            {"city": "Los Angeles", "state": "CA", "zip_format": "900##"},
            {"city": "Chicago", "state": "IL", "zip_format": "606##"},
            {"city": "Houston", "state": "TX", "zip_format": "770##"},
            {"city": "Phoenix", "state": "AZ", "zip_format": "850##"},
            {"city": "Philadelphia", "state": "PA", "zip_format": "191##"},
            {"city": "San Antonio", "state": "TX", "zip_format": "782##"},
            {"city": "San Diego", "state": "CA", "zip_format": "921##"},
            {"city": "Dallas", "state": "TX", "zip_format": "752##"},
            {"city": "San Jose", "state": "CA", "zip_format": "951##"},
        ],
        "streets": ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St", "Washington Blvd", "Park Ave", "Lake Dr", "Hill Rd", "River St", "Forest Ave", "Sunset Blvd", "Broadway", "Market St"],
        "phone_format": "+1 (###) ###-####"
    },
    "uk": {
        "country": "Великобритания",
        "flag": "🇬🇧",
        "cities": [
            {"city": "London", "state": "England", "zip_format": "SW1A #AA"},
            {"city": "Manchester", "state": "England", "zip_format": "M1 #AA"},
            {"city": "Birmingham", "state": "England", "zip_format": "B1 #AA"},
            {"city": "Liverpool", "state": "England", "zip_format": "L1 #AA"},
            {"city": "Edinburgh", "state": "Scotland", "zip_format": "EH1 #AA"},
            {"city": "Glasgow", "state": "Scotland", "zip_format": "G1 #AA"},
            {"city": "Bristol", "state": "England", "zip_format": "BS1 #AA"},
            {"city": "Leeds", "state": "England", "zip_format": "LS1 #AA"},
        ],
        "streets": ["High Street", "Church Road", "Station Road", "Main Street", "Park Road", "London Road", "Victoria Street", "Green Lane", "Manor Road", "Kings Road"],
        "phone_format": "+44 ## #### ####"
    },
    "de": {
        "country": "Германия",
        "flag": "🇩🇪",
        "cities": [
            {"city": "Berlin", "state": "Berlin", "zip_format": "10###"},
            {"city": "Hamburg", "state": "Hamburg", "zip_format": "20###"},
            {"city": "München", "state": "Bayern", "zip_format": "80###"},
            {"city": "Köln", "state": "NRW", "zip_format": "50###"},
            {"city": "Frankfurt", "state": "Hessen", "zip_format": "60###"},
            {"city": "Stuttgart", "state": "BW", "zip_format": "70###"},
            {"city": "Düsseldorf", "state": "NRW", "zip_format": "40###"},
        ],
        "streets": ["Hauptstraße", "Bahnhofstraße", "Schulstraße", "Gartenstraße", "Dorfstraße", "Bergstraße", "Kirchstraße", "Waldstraße", "Ringstraße", "Lindenstraße"],
        "phone_format": "+49 ### #######"
    },
    "ua": {
        "country": "Украина",
        "flag": "🇺🇦",
        "cities": [
            {"city": "Київ", "state": "Київська обл.", "zip_format": "01###"},
            {"city": "Харків", "state": "Харківська обл.", "zip_format": "61###"},
            {"city": "Одеса", "state": "Одеська обл.", "zip_format": "65###"},
            {"city": "Дніпро", "state": "Дніпропетровська обл.", "zip_format": "49###"},
            {"city": "Львів", "state": "Львівська обл.", "zip_format": "79###"},
            {"city": "Запоріжжя", "state": "Запорізька обл.", "zip_format": "69###"},
        ],
        "streets": ["вул. Шевченка", "вул. Лесі Українки", "вул. Франка", "вул. Грушевського", "вул. Соборна", "вул. Центральна", "вул. Незалежності", "просп. Миру", "вул. Садова"],
        "phone_format": "+380 ## ### ## ##"
    },
    "ru": {
        "country": "Россия",
        "flag": "🇷🇺",
        "cities": [
            {"city": "Москва", "state": "Московская обл.", "zip_format": "1#####"},
            {"city": "Санкт-Петербург", "state": "Ленинградская обл.", "zip_format": "19####"},
            {"city": "Новосибирск", "state": "Новосибирская обл.", "zip_format": "63####"},
            {"city": "Екатеринбург", "state": "Свердловская обл.", "zip_format": "62####"},
            {"city": "Казань", "state": "Татарстан", "zip_format": "42####"},
            {"city": "Нижний Новгород", "state": "Нижегородская обл.", "zip_format": "60####"},
        ],
        "streets": ["ул. Ленина", "ул. Мира", "ул. Советская", "ул. Пушкина", "ул. Гагарина", "ул. Кирова", "просп. Победы", "ул. Центральная", "ул. Садовая"],
        "phone_format": "+7 (###) ###-##-##"
    },
    "pl": {
        "country": "Польша",
        "flag": "🇵🇱",
        "cities": [
            {"city": "Warszawa", "state": "Mazowieckie", "zip_format": "00-###"},
            {"city": "Kraków", "state": "Małopolskie", "zip_format": "30-###"},
            {"city": "Łódź", "state": "Łódzkie", "zip_format": "90-###"},
            {"city": "Wrocław", "state": "Dolnośląskie", "zip_format": "50-###"},
            {"city": "Poznań", "state": "Wielkopolskie", "zip_format": "60-###"},
            {"city": "Gdańsk", "state": "Pomorskie", "zip_format": "80-###"},
        ],
        "streets": ["ul. Główna", "ul. Kościelna", "ul. Szkolna", "ul. Ogrodowa", "ul. Polna", "ul. Leśna", "ul. Krótka", "ul. Parkowa", "ul. Słoneczna"],
        "phone_format": "+48 ### ### ###"
    }
}

FIRST_NAMES_MALE = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Alexander", "Daniel", "Matthew", "Anthony", "Mark"]
FIRST_NAMES_FEMALE = ["Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]


def generate_phone(format_str):
    """Генерация номера телефона по формату"""
    result = ""
    for char in format_str:
        if char == "#":
            result += str(random.randint(0, 9))
        else:
            result += char
    return result


def generate_zip(format_str):
    """Генерация почтового индекса по формату"""
    result = ""
    for char in format_str:
        if char == "#":
            result += str(random.randint(0, 9))
        elif char == "A":
            result += random.choice(string.ascii_uppercase)
        else:
            result += char
    return result


def generate_address(country_code="us"):
    """Генерация случайного адреса"""
    if country_code not in ADDRESS_DATA:
        country_code = "us"
    
    data = ADDRESS_DATA[country_code]
    city_data = random.choice(data["cities"])
    street = random.choice(data["streets"])
    house_num = random.randint(1, 999)
    apt = random.randint(1, 200) if random.random() > 0.5 else None
    
    # Генерация имени
    gender = random.choice(["male", "female"])
    first_name = random.choice(FIRST_NAMES_MALE if gender == "male" else FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)
    
    address = {
        "country": data["country"],
        "flag": data["flag"],
        "city": city_data["city"],
        "state": city_data["state"],
        "zip": generate_zip(city_data["zip_format"]),
        "street": f"{house_num} {street}",
        "apartment": f"Apt {apt}" if apt else None,
        "phone": generate_phone(data["phone_format"]),
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "email": f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{'gmail.com' if random.random() > 0.5 else 'outlook.com'}"
    }
    
    return address


def format_address(addr):
    """Форматирование адреса для отображения"""
    text = f"{addr['flag']} **{addr['country']}**\n\n"
    text += f"👤 **Имя:** {addr['full_name']}\n"
    text += f"📧 **Email:** `{addr['email']}`\n"
    text += f"📱 **Телефон:** `{addr['phone']}`\n\n"
    text += f"🏠 **Адрес:**\n"
    text += f"   {addr['street']}\n"
    if addr['apartment']:
        text += f"   {addr['apartment']}\n"
    text += f"   {addr['city']}, {addr['state']} {addr['zip']}\n"
    text += f"   {addr['country']}"
    return text


# === ГЕНЕРАТОР КАРТ ===

CARD_BINS = {
    "visa": {
        "name": "Visa",
        "icon": "💳",
        "bins": ["4", "4532", "4556", "4916", "4539", "4485", "4716"],
        "length": 16,
        "cvv_length": 3
    },
    "mastercard": {
        "name": "Mastercard",
        "icon": "💳",
        "bins": ["51", "52", "53", "54", "55", "2221", "2720"],
        "length": 16,
        "cvv_length": 3
    },
    "amex": {
        "name": "American Express",
        "icon": "💳",
        "bins": ["34", "37"],
        "length": 15,
        "cvv_length": 4
    },
    "discover": {
        "name": "Discover",
        "icon": "💳",
        "bins": ["6011", "644", "645", "646", "647", "648", "649", "65"],
        "length": 16,
        "cvv_length": 3
    }
}


def luhn_checksum(card_number):
    """Вычисление контрольной суммы по алгоритму Луна"""
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    
    return checksum % 10


def generate_card_number(card_type="visa"):
    """Генерация номера карты с валидной контрольной суммой"""
    if card_type not in CARD_BINS:
        card_type = "visa"
    
    card_data = CARD_BINS[card_type]
    bin_prefix = random.choice(card_data["bins"])
    length = card_data["length"]
    
    # Генерируем номер без последней цифры
    remaining_length = length - len(bin_prefix) - 1
    number = bin_prefix + ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
    
    # Вычисляем контрольную цифру
    checksum = luhn_checksum(int(number + '0'))
    check_digit = (10 - checksum) % 10
    
    return number + str(check_digit)


def generate_card(card_type="visa"):
    """Генерация полных данных карты"""
    if card_type not in CARD_BINS:
        card_type = "visa"
    
    card_data = CARD_BINS[card_type]
    
    # Генерация даты истечения (1-5 лет вперёд)
    exp_month = random.randint(1, 12)
    exp_year = datetime.now().year + random.randint(1, 5)
    
    # Генерация CVV
    cvv = ''.join([str(random.randint(0, 9)) for _ in range(card_data["cvv_length"])])
    
    # Генерация имени держателя
    first_name = random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)
    
    card = {
        "type": card_type,
        "type_name": card_data["name"],
        "icon": card_data["icon"],
        "number": generate_card_number(card_type),
        "exp_month": f"{exp_month:02d}",
        "exp_year": str(exp_year),
        "exp_short": f"{exp_month:02d}/{str(exp_year)[-2:]}",
        "cvv": cvv,
        "holder": f"{first_name.upper()} {last_name.upper()}"
    }
    
    return card


def format_card_number(number):
    """Форматирование номера карты с пробелами"""
    if len(number) == 15:  # Amex
        return f"{number[:4]} {number[4:10]} {number[10:]}"
    else:
        return ' '.join([number[i:i+4] for i in range(0, len(number), 4)])


def format_card(card):
    """Форматирование карты для отображения"""
    text = f"{card['icon']} **{card['type_name']}**\n\n"
    text += f"💳 **Номер:** `{format_card_number(card['number'])}`\n"
    text += f"📅 **Срок:** `{card['exp_short']}`\n"
    text += f"🔐 **CVV:** `{card['cvv']}`\n"
    text += f"👤 **Держатель:** `{card['holder']}`\n\n"
    text += f"⚠️ _Тестовые данные для разработки_"
    return text


# === ГЕНЕРАТОР АНТИДЕТЕКТ ДАННЫХ ===

USER_AGENTS = {
    "chrome_win": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ],
    "chrome_mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ],
    "firefox_win": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    ],
    "safari_mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ],
    "mobile_android": [
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    ],
    "mobile_ios": [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    ]
}

SCREEN_RESOLUTIONS = [
    {"width": 1920, "height": 1080, "name": "Full HD"},
    {"width": 2560, "height": 1440, "name": "2K QHD"},
    {"width": 3840, "height": 2160, "name": "4K UHD"},
    {"width": 1366, "height": 768, "name": "HD"},
    {"width": 1536, "height": 864, "name": "HD+"},
    {"width": 1440, "height": 900, "name": "WXGA+"},
    {"width": 1680, "height": 1050, "name": "WSXGA+"},
]

TIMEZONES = [
    {"name": "America/New_York", "offset": -5},
    {"name": "America/Los_Angeles", "offset": -8},
    {"name": "America/Chicago", "offset": -6},
    {"name": "Europe/London", "offset": 0},
    {"name": "Europe/Paris", "offset": 1},
    {"name": "Europe/Berlin", "offset": 1},
    {"name": "Europe/Moscow", "offset": 3},
    {"name": "Europe/Kiev", "offset": 2},
    {"name": "Asia/Tokyo", "offset": 9},
    {"name": "Asia/Shanghai", "offset": 8},
]

LANGUAGES = ["en-US", "en-GB", "de-DE", "fr-FR", "es-ES", "it-IT", "ru-RU", "uk-UA", "pl-PL", "ja-JP", "zh-CN"]

WEBGL_VENDORS = ["Google Inc. (NVIDIA)", "Google Inc. (Intel)", "Google Inc. (AMD)", "Intel Inc.", "NVIDIA Corporation"]
WEBGL_RENDERERS = [
    "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)",
]


def generate_fingerprint():
    """Генерация уникального fingerprint"""
    # Canvas fingerprint
    canvas_hash = hashlib.md5(str(random.random()).encode()).hexdigest()
    
    # WebGL fingerprint
    webgl_hash = hashlib.md5(str(random.random()).encode()).hexdigest()
    
    # Audio fingerprint
    audio_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:16]
    
    return {
        "canvas": canvas_hash,
        "webgl": webgl_hash,
        "audio": audio_hash
    }


def generate_antidetect_profile(platform="chrome_win"):
    """Генерация полного антидетект профиля"""
    if platform not in USER_AGENTS:
        platform = "chrome_win"
    
    user_agent = random.choice(USER_AGENTS[platform])
    screen = random.choice(SCREEN_RESOLUTIONS)
    timezone = random.choice(TIMEZONES)
    language = random.choice(LANGUAGES)
    fingerprint = generate_fingerprint()
    
    profile = {
        "user_agent": user_agent,
        "platform": platform,
        "screen": screen,
        "timezone": timezone,
        "language": language,
        "languages": [language, language.split("-")[0]],
        "webgl_vendor": random.choice(WEBGL_VENDORS),
        "webgl_renderer": random.choice(WEBGL_RENDERERS),
        "fingerprint": fingerprint,
        "hardware_concurrency": random.choice([4, 8, 12, 16]),
        "device_memory": random.choice([4, 8, 16, 32]),
        "do_not_track": random.choice(["1", None]),
        "cookies_enabled": True,
        "java_enabled": False,
        "pdf_viewer_enabled": True,
        "plugins_count": random.randint(3, 7),
        "color_depth": 24,
        "pixel_ratio": random.choice([1, 1.25, 1.5, 2]),
        "session_id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat()
    }
    
    return profile


def format_antidetect_profile(profile):
    """Форматирование профиля для отображения"""
    text = "🤖 **Антидетект профиль**\n\n"
    
    text += "📱 **User-Agent:**\n"
    text += f"`{profile['user_agent']}`\n\n"
    
    text += f"🖥 **Экран:** {profile['screen']['width']}x{profile['screen']['height']} ({profile['screen']['name']})\n"
    text += f"🌍 **Timezone:** {profile['timezone']['name']} (UTC{profile['timezone']['offset']:+d})\n"
    text += f"🗣 **Язык:** {profile['language']}\n\n"
    
    text += "🎮 **WebGL:**\n"
    text += f"   Vendor: `{profile['webgl_vendor']}`\n"
    text += f"   Renderer: `{profile['webgl_renderer'][:50]}...`\n\n"
    
    text += "🔑 **Fingerprints:**\n"
    text += f"   Canvas: `{profile['fingerprint']['canvas'][:16]}...`\n"
    text += f"   WebGL: `{profile['fingerprint']['webgl'][:16]}...`\n"
    text += f"   Audio: `{profile['fingerprint']['audio']}`\n\n"
    
    text += f"⚙️ **Hardware:**\n"
    text += f"   CPU Cores: {profile['hardware_concurrency']}\n"
    text += f"   RAM: {profile['device_memory']} GB\n"
    text += f"   Pixel Ratio: {profile['pixel_ratio']}\n\n"
    
    text += f"🆔 **Session ID:** `{profile['session_id'][:8]}...`"
    
    return text


def export_antidetect_profile(profile):
    """Экспорт профиля в JSON"""
    return json.dumps(profile, indent=2, ensure_ascii=False)
