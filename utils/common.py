"""
Общие утилиты
"""

import pyotp
import requests
import subprocess
import os
import zipfile
import random
from faker import Faker
from datetime import datetime


def generate_2fa_code(secret):
    """Генерация 2FA кода из секретного ключа"""
    try:
        # Очищаем секрет от пробелов
        secret = secret.replace(" ", "").upper()
        totp = pyotp.TOTP(secret)
        return totp.now()
    except Exception as e:
        return None


def generate_random_person(country="en"):
    """Генерация случайных данных человека"""
    locale_map = {
        "ru": "ru_RU",
        "en": "en_GB",
        "ua": "uk_UA",
        "ua_id": "uk_UA",
        "pl": "pl_PL"
    }
    
    locale = locale_map.get(country, "en_US")
    fake = Faker(locale)
    
    gender = random.choice(["male", "female"])
    
    if gender == "male":
        first_name = fake.first_name_male()
        if country in ["ru", "ua", "ua_id"]:
            middle_name = fake.middle_name_male() if hasattr(fake, 'middle_name_male') else ""
        else:
            middle_name = ""
    else:
        first_name = fake.first_name_female()
        if country in ["ru", "ua", "ua_id"]:
            middle_name = fake.middle_name_female() if hasattr(fake, 'middle_name_female') else ""
        else:
            middle_name = ""
    
    # Генерируем дату рождения (18-60 лет)
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=60)
    
    return {
        "first_name": first_name,
        "last_name": fake.last_name(),
        "middle_name": middle_name,
        "birth_date": birth_date.strftime("%d.%m.%Y"),
        "gender": "М" if gender == "male" else "Ж",
        "gender_en": "M" if gender == "male" else "F"
    }


def generate_company_data(country="ua"):
    """Генерация данных компании для верификации"""
    locale_map = {
        "ru": "ru_RU",
        "en": "en_US",
        "ua": "uk_UA",
        "pl": "pl_PL"
    }
    
    locale = locale_map.get(country, "en_US")
    fake = Faker(locale)
    
    # Генерируем данные компании
    company_name = fake.company()
    
    # Адрес
    street = fake.street_address()
    city = fake.city()
    
    # Код региона/штата
    if country == "ua":
        region = fake.region() if hasattr(fake, 'region') else city
        postal = fake.postcode()
        phone = f"+38 {fake.msisdn()[3:6]} {fake.msisdn()[6:9]}-{fake.msisdn()[9:11]}-{fake.msisdn()[11:13]}"
        license_num = f"{random.randint(10000000, 99999999)}"
    elif country == "en":
        region = fake.state() if hasattr(fake, 'state') else ""
        postal = fake.postcode()
        phone = fake.phone_number()
        license_num = f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"
    else:
        region = fake.administrative_unit() if hasattr(fake, 'administrative_unit') else ""
        postal = fake.postcode()
        phone = fake.phone_number()
        license_num = f"{random.randint(10000000, 99999999)}"
    
    return {
        "company_name": company_name,
        "country": country.upper(),
        "address": street,
        "city": city,
        "region": region,
        "postal_code": postal,
        "phone": phone,
        "license_number": license_num,
        "registration_number": f"{random.randint(10000000, 99999999)}"
    }


def check_google_play_app(package_name):
    """Проверка наличия приложения в Google Play"""
    try:
        url = f"https://play.google.com/store/apps/details?id={package_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "Приложение доступно в Google Play"
        elif response.status_code == 404:
            return False, "Приложение не найдено в Google Play"
        else:
            return None, f"Не удалось проверить (код: {response.status_code})"
            
    except requests.Timeout:
        return None, "Превышено время ожидания"
    except Exception as e:
        return None, str(e)


def download_website(url, output_dir):
    """Скачивание сайта с помощью wget"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            'wget',
            '--recursive',
            '--level=2',
            '--page-requisites',
            '--convert-links',
            '--no-parent',
            '--directory-prefix=' + output_dir,
            '--timeout=30',
            '--tries=2',
            '--quiet',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Создаем архив
        archive_path = output_dir + '.zip'
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
        
        return True, archive_path
        
    except subprocess.TimeoutExpired:
        return False, "Превышено время скачивания"
    except Exception as e:
        return False, str(e)


def uniqualize_text(text):
    """Уникализация текста (простой рерайт)"""
    # Простая замена синонимов
    synonyms = {
        "хороший": ["отличный", "превосходный", "замечательный", "прекрасный"],
        "плохой": ["ужасный", "отвратительный", "скверный", "негодный"],
        "большой": ["огромный", "крупный", "значительный", "масштабный"],
        "маленький": ["небольшой", "крохотный", "миниатюрный", "компактный"],
        "быстро": ["стремительно", "оперативно", "скоро", "моментально"],
        "медленно": ["неспешно", "постепенно", "неторопливо"],
        "делать": ["выполнять", "осуществлять", "производить", "совершать"],
        "говорить": ["сказать", "произнести", "заявить", "утверждать"],
        "думать": ["полагать", "считать", "размышлять", "рассуждать"],
        "хотеть": ["желать", "стремиться", "намереваться"],
        "можно": ["возможно", "допустимо", "разрешено"],
        "нужно": ["необходимо", "требуется", "следует"],
        "очень": ["весьма", "крайне", "чрезвычайно", "довольно"],
        "также": ["кроме того", "помимо этого", "вдобавок"],
        "поэтому": ["следовательно", "таким образом", "в связи с этим"],
        "однако": ["тем не менее", "впрочем", "вместе с тем"],
        "good": ["great", "excellent", "wonderful", "fantastic"],
        "bad": ["terrible", "awful", "poor", "horrible"],
        "big": ["large", "huge", "enormous", "massive"],
        "small": ["tiny", "little", "compact", "miniature"],
        "fast": ["quick", "rapid", "swift", "speedy"],
        "slow": ["gradual", "unhurried", "leisurely"],
        "make": ["create", "produce", "generate", "develop"],
        "say": ["state", "declare", "mention", "express"],
        "think": ["believe", "consider", "assume", "suppose"],
        "want": ["desire", "wish", "aim", "intend"],
        "very": ["extremely", "highly", "incredibly", "remarkably"],
        "also": ["additionally", "furthermore", "moreover"],
        "so": ["therefore", "thus", "consequently", "hence"],
        "but": ["however", "nevertheless", "yet", "although"]
    }
    
    result = text
    for word, replacements in synonyms.items():
        if word.lower() in result.lower():
            replacement = random.choice(replacements)
            # Сохраняем регистр
            if word[0].isupper():
                replacement = replacement.capitalize()
            result = result.replace(word, replacement, 1)
    
    # Добавляем небольшие изменения в пунктуацию
    result = result.replace(" - ", " — ")
    result = result.replace("...", "…")
    
    return result


def extract_package_name(url_or_package):
    """Извлечение package name из URL Google Play или строки"""
    if "play.google.com" in url_or_package:
        # Извлекаем из URL
        if "id=" in url_or_package:
            package = url_or_package.split("id=")[1].split("&")[0]
            return package
    return url_or_package.strip()


def format_file_size(size_bytes):
    """Форматирование размера файла"""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} ТБ"


# === Асинхронные обёртки для многопользовательского режима ===
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Пул потоков для сетевых операций
_network_executor = ThreadPoolExecutor(max_workers=15, thread_name_prefix='network_')


async def download_website_async(url, output_dir):
    """Асинхронное скачивание сайта"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _network_executor,
        download_website,
        url,
        output_dir
    )


async def check_google_play_app_async(package_name):
    """Асинхронная проверка приложения Google Play"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _network_executor,
        check_google_play_app,
        package_name
    )


async def uniqualize_text_async(text):
    """Асинхронная уникализация текста"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _network_executor,
        uniqualize_text,
        text
    )
