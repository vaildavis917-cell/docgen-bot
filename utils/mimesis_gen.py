"""
Генератор фейковых данных на базе Mimesis
Поддержка локалей: RU, EN, UK (UA)
"""

from mimesis import Person, Address, Finance, Payment, Datetime, Internet, Cryptographic, Text
from mimesis.locales import Locale
from mimesis.enums import Gender, Algorithm
import random

# Маппинг кодов языков на локали Mimesis
LOCALE_MAP = {
    'ru': Locale.RU,
    'en': Locale.EN,
    'ua': Locale.UK,  # Ukrainian
}

# Маппинг стран на локали
COUNTRY_LOCALE_MAP = {
    'us': Locale.EN,
    'uk': Locale.EN,
    'de': Locale.DE,
    'ru': Locale.RU,
    'ua': Locale.UK,
    'pl': Locale.PL,
    'fr': Locale.FR,
    'es': Locale.ES,
    'it': Locale.IT,
}


def get_locale(lang_code: str = 'ru') -> Locale:
    """Получить локаль Mimesis по коду языка"""
    return LOCALE_MAP.get(lang_code, Locale.EN)


def generate_person(lang_code: str = 'ru') -> dict:
    """Генерация данных персоны"""
    locale = get_locale(lang_code)
    person = Person(locale)
    dt = Datetime(locale)
    
    gender = random.choice([Gender.MALE, Gender.FEMALE])
    
    return {
        'first_name': person.first_name(gender=gender),
        'last_name': person.last_name(gender=gender),
        'full_name': person.full_name(gender=gender),
        'gender': person.gender(),
        'email': person.email(),
        'phone': person.telephone(),
        'birthday': dt.date(start=1970, end=2000),
        'age': random.randint(18, 65),
        'username': person.email().split('@')[0],
        'password': Cryptographic().token_urlsafe(12)[:12],
    }


def generate_address(country_code: str = 'us') -> dict:
    """Генерация адреса по стране"""
    locale = COUNTRY_LOCALE_MAP.get(country_code.lower(), Locale.EN)
    addr = Address(locale)
    
    result = {
        'country': addr.country(),
        'country_code': addr.country_code(),
        'city': addr.city(),
        'street': addr.street_name(),
        'address': addr.address(),
        'postal_code': addr.postal_code(),
        'state': addr.state() if hasattr(addr, 'state') else addr.region(),
    }
    
    # Координаты
    try:
        coords = addr.coordinates()
        result['latitude'] = coords['latitude']
        result['longitude'] = coords['longitude']
    except:
        result['latitude'] = round(random.uniform(-90, 90), 6)
        result['longitude'] = round(random.uniform(-180, 180), 6)
    
    return result


def generate_card(card_type: str = 'random') -> dict:
    """Генерация платёжной карты"""
    pay = Payment()
    
    # Выбор сети карты
    if card_type == 'random':
        card_type = random.choice(['visa', 'mastercard', 'amex', 'discover'])
    
    network_map = {
        'visa': 'Visa',
        'mastercard': 'MasterCard', 
        'amex': 'American Express',
        'discover': 'Discover',
    }
    
    return {
        'number': pay.credit_card_number(),
        'network': network_map.get(card_type, 'Visa'),
        'cvv': pay.cvv(),
        'expiration': pay.credit_card_expiration_date(),
        'holder': pay.credit_card_owner().get('owner', 'JOHN DOE'),
    }


def generate_company(lang_code: str = 'ru') -> dict:
    """Генерация данных компании"""
    locale = get_locale(lang_code)
    fin = Finance(locale)
    addr = Address(locale)
    internet = Internet()
    
    company_name = fin.company()
    
    return {
        'name': company_name,
        'type': fin.company_type(),
        'bank': fin.bank(),
        'address': addr.address(),
        'city': addr.city(),
        'phone': Person(locale).telephone(),
        'email': f"info@{internet.hostname()}",
        'website': f"https://{internet.hostname()}",
    }


def generate_internet(lang_code: str = 'ru') -> dict:
    """Генерация интернет-данных"""
    locale = get_locale(lang_code)
    internet = Internet()
    person = Person(locale)
    
    return {
        'email': person.email(),
        'username': person.email().split('@')[0],
        'password': Cryptographic().token_urlsafe(16)[:16],
        'ip_v4': internet.ip_v4(),
        'ip_v6': internet.ip_v6(),
        'mac': internet.mac_address(),
        'user_agent': internet.user_agent(),
        'hostname': internet.hostname(),
    }


def generate_crypto() -> dict:
    """Генерация криптографических данных"""
    crypto = Cryptographic()
    pay = Payment()
    
    return {
        'uuid': crypto.uuid(),
        'token': crypto.token_hex(32),
        'api_key': crypto.token_urlsafe(32),
        'hash_md5': crypto.hash(algorithm=Algorithm.MD5),
        'hash_sha256': crypto.hash(algorithm=Algorithm.SHA256),
        'bitcoin': pay.bitcoin_address(),
        'ethereum': pay.ethereum_address(),
        'mnemonic': crypto.mnemonic_phrase(),
    }


def generate_full_profile(lang_code: str = 'ru', country_code: str = None) -> dict:
    """Генерация полного профиля (всё вместе)"""
    if not country_code:
        country_code = {'ru': 'ru', 'en': 'us', 'ua': 'ua'}.get(lang_code, 'us')
    
    person = generate_person(lang_code)
    address = generate_address(country_code)
    card = generate_card('random')
    internet = generate_internet(lang_code)
    crypto = generate_crypto()
    
    return {
        'person': person,
        'address': address,
        'card': card,
        'internet': internet,
        'crypto': crypto,
    }


# === Форматирование для вывода в Telegram ===

def format_person(data: dict, lang_code: str = 'ru') -> str:
    """Форматирование персоны для Telegram"""
    labels = {
        'ru': {
            'title': '👤 Персона',
            'name': 'Имя',
            'gender': 'Пол',
            'email': 'Email',
            'phone': 'Телефон',
            'birthday': 'Дата рождения',
            'age': 'Возраст',
            'username': 'Username',
            'password': 'Пароль',
        },
        'en': {
            'title': '👤 Person',
            'name': 'Name',
            'gender': 'Gender',
            'email': 'Email',
            'phone': 'Phone',
            'birthday': 'Birthday',
            'age': 'Age',
            'username': 'Username',
            'password': 'Password',
        },
        'ua': {
            'title': '👤 Персона',
            'name': "Ім'я",
            'gender': 'Стать',
            'email': 'Email',
            'phone': 'Телефон',
            'birthday': 'Дата народження',
            'age': 'Вік',
            'username': 'Username',
            'password': 'Пароль',
        },
    }
    l = labels.get(lang_code, labels['en'])
    
    return f"""**{l['title']}**

👤 {l['name']}: `{data['full_name']}`
⚧ {l['gender']}: {data['gender']}
📧 {l['email']}: `{data['email']}`
📱 {l['phone']}: `{data['phone']}`
🎂 {l['birthday']}: `{data['birthday']}`
🔢 {l['age']}: {data['age']}
👤 {l['username']}: `{data['username']}`
🔐 {l['password']}: `{data['password']}`"""


def format_address(data: dict, lang_code: str = 'ru') -> str:
    """Форматирование адреса для Telegram"""
    labels = {
        'ru': {'title': '📍 Адрес', 'country': 'Страна', 'city': 'Город', 'street': 'Улица', 
               'address': 'Адрес', 'postal': 'Индекс', 'state': 'Регион', 'coords': 'Координаты'},
        'en': {'title': '📍 Address', 'country': 'Country', 'city': 'City', 'street': 'Street',
               'address': 'Address', 'postal': 'Postal Code', 'state': 'State', 'coords': 'Coordinates'},
        'ua': {'title': '📍 Адреса', 'country': 'Країна', 'city': 'Місто', 'street': 'Вулиця',
               'address': 'Адреса', 'postal': 'Індекс', 'state': 'Регіон', 'coords': 'Координати'},
    }
    l = labels.get(lang_code, labels['en'])
    
    return f"""**{l['title']}**

🌍 {l['country']}: {data['country']} ({data['country_code']})
🏙 {l['city']}: `{data['city']}`
🏠 {l['address']}: `{data['address']}`
📮 {l['postal']}: `{data['postal_code']}`
📍 {l['coords']}: `{data.get('latitude', 0)}, {data.get('longitude', 0)}`"""


def format_card(data: dict, lang_code: str = 'ru') -> str:
    """Форматирование карты для Telegram"""
    labels = {
        'ru': {'title': '💳 Карта', 'number': 'Номер', 'network': 'Сеть', 'cvv': 'CVV', 
               'exp': 'Срок', 'holder': 'Владелец'},
        'en': {'title': '💳 Card', 'number': 'Number', 'network': 'Network', 'cvv': 'CVV',
               'exp': 'Expiration', 'holder': 'Holder'},
        'ua': {'title': '💳 Картка', 'number': 'Номер', 'network': 'Мережа', 'cvv': 'CVV',
               'exp': 'Термін', 'holder': 'Власник'},
    }
    l = labels.get(lang_code, labels['en'])
    
    return f"""**{l['title']}**

💳 {l['network']}: {data['network']}
🔢 {l['number']}: `{data['number']}`
🔐 {l['cvv']}: `{data['cvv']}`
📅 {l['exp']}: `{data['expiration']}`
👤 {l['holder']}: `{data['holder']}`"""


def format_company(data: dict, lang_code: str = 'ru') -> str:
    """Форматирование компании для Telegram"""
    labels = {
        'ru': {'title': '🏢 Компания', 'name': 'Название', 'type': 'Тип', 'bank': 'Банк',
               'address': 'Адрес', 'phone': 'Телефон', 'email': 'Email', 'website': 'Сайт'},
        'en': {'title': '🏢 Company', 'name': 'Name', 'type': 'Type', 'bank': 'Bank',
               'address': 'Address', 'phone': 'Phone', 'email': 'Email', 'website': 'Website'},
        'ua': {'title': '🏢 Компанія', 'name': 'Назва', 'type': 'Тип', 'bank': 'Банк',
               'address': 'Адреса', 'phone': 'Телефон', 'email': 'Email', 'website': 'Сайт'},
    }
    l = labels.get(lang_code, labels['en'])
    
    return f"""**{l['title']}**

🏢 {l['name']}: `{data['name']}`
📋 {l['type']}: {data['type']}
🏦 {l['bank']}: {data['bank']}
📍 {l['address']}: `{data['address']}`
📱 {l['phone']}: `{data['phone']}`
📧 {l['email']}: `{data['email']}`
🌐 {l['website']}: `{data['website']}`"""


def format_internet(data: dict, lang_code: str = 'ru') -> str:
    """Форматирование интернет-данных для Telegram"""
    labels = {
        'ru': {'title': '💻 Интернет'},
        'en': {'title': '💻 Internet'},
        'ua': {'title': '💻 Інтернет'},
    }
    l = labels.get(lang_code, labels['en'])
    
    return f"""**{l['title']}**

📧 Email: `{data['email']}`
👤 Username: `{data['username']}`
🔐 Password: `{data['password']}`
🌐 IPv4: `{data['ip_v4']}`
🌐 IPv6: `{data['ip_v6']}`
📡 MAC: `{data['mac']}`
🖥 User-Agent: `{data['user_agent'][:50]}...`"""


def format_crypto(data: dict, lang_code: str = 'ru') -> str:
    """Форматирование криптоданных для Telegram"""
    labels = {
        'ru': {'title': '🔐 Крипто'},
        'en': {'title': '🔐 Crypto'},
        'ua': {'title': '🔐 Крипто'},
    }
    l = labels.get(lang_code, labels['en'])
    
    return f"""**{l['title']}**

🆔 UUID: `{data['uuid']}`
🔑 Token: `{data['token'][:32]}...`
🔐 API Key: `{data['api_key'][:32]}...`
#️⃣ MD5: `{data['hash_md5']}`
#️⃣ SHA256: `{data['hash_sha256'][:32]}...`
₿ Bitcoin: `{data['bitcoin']}`
Ξ Ethereum: `{data['ethereum']}`
📝 Mnemonic: `{data['mnemonic'][:50]}...`"""


def format_full_profile(data: dict, lang_code: str = 'ru') -> str:
    """Форматирование полного профиля для Telegram"""
    labels = {
        'ru': {'title': '📦 Полный профиль'},
        'en': {'title': '📦 Full Profile'},
        'ua': {'title': '📦 Повний профіль'},
    }
    l = labels.get(lang_code, labels['en'])
    
    parts = [
        f"**{l['title']}**\n",
        format_person(data['person'], lang_code),
        "\n" + "─" * 20 + "\n",
        format_address(data['address'], lang_code),
        "\n" + "─" * 20 + "\n",
        format_card(data['card'], lang_code),
    ]
    
    return "".join(parts)
