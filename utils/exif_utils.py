"""
Утилиты для работы с EXIF метаданными
"""

import piexif
from PIL import Image
from datetime import datetime, timedelta
import random
import io
import os


def generate_random_exif():
    """Генерация случайных EXIF метаданных"""
    
    # Случайная дата в пределах последнего года
    days_ago = random.randint(1, 365)
    random_date = datetime.now() - timedelta(days=days_ago)
    date_str = random_date.strftime("%Y:%m:%d %H:%M:%S")
    
    # Случайные GPS координаты (примерно Европа/США)
    lat_choices = [
        (48.8566, 2.3522),   # Париж
        (51.5074, -0.1278),  # Лондон
        (40.7128, -74.0060), # Нью-Йорк
        (50.4501, 30.5234),  # Киев
        (52.2297, 21.0122),  # Варшава
        (55.7558, 37.6173),  # Москва
        (41.9028, 12.4964),  # Рим
        (52.5200, 13.4050),  # Берлин
    ]
    lat, lon = random.choice(lat_choices)
    
    # Добавляем небольшое смещение
    lat += random.uniform(-0.1, 0.1)
    lon += random.uniform(-0.1, 0.1)
    
    # Конвертация координат в формат EXIF
    def to_deg(value, loc):
        if value < 0:
            loc_value = loc[0]
        else:
            loc_value = loc[1]
        
        abs_value = abs(value)
        deg = int(abs_value)
        min_float = (abs_value - deg) * 60
        min_int = int(min_float)
        sec = (min_float - min_int) * 60
        
        return ((deg, 1), (min_int, 1), (int(sec * 100), 100)), loc_value
    
    lat_deg, lat_ref = to_deg(lat, ["S", "N"])
    lon_deg, lon_ref = to_deg(lon, ["W", "E"])
    
    # Случайные модели камер
    camera_makes = ["Apple", "Samsung", "Google", "Xiaomi", "Huawei", "OnePlus"]
    camera_models = {
        "Apple": ["iPhone 12 Pro", "iPhone 13", "iPhone 14 Pro Max", "iPhone 15"],
        "Samsung": ["Galaxy S21", "Galaxy S22 Ultra", "Galaxy S23", "Galaxy Note 20"],
        "Google": ["Pixel 6", "Pixel 7 Pro", "Pixel 8"],
        "Xiaomi": ["Mi 11", "Redmi Note 11", "Poco X5"],
        "Huawei": ["P40 Pro", "Mate 40", "P50"],
        "OnePlus": ["9 Pro", "10 Pro", "11"]
    }
    
    make = random.choice(camera_makes)
    model = random.choice(camera_models[make])
    
    # Создание EXIF данных
    zeroth_ifd = {
        piexif.ImageIFD.Make: make,
        piexif.ImageIFD.Model: model,
        piexif.ImageIFD.Software: f"{make} Camera",
        piexif.ImageIFD.DateTime: date_str,
    }
    
    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: date_str,
        piexif.ExifIFD.DateTimeDigitized: date_str,
        piexif.ExifIFD.ExifVersion: b"0232",
        piexif.ExifIFD.LensMake: make,
        piexif.ExifIFD.LensModel: f"{make} {model} Lens",
        piexif.ExifIFD.FocalLength: (random.randint(24, 70), 10),
        piexif.ExifIFD.ISOSpeedRatings: random.choice([100, 200, 400, 800]),
        piexif.ExifIFD.ExposureTime: (1, random.choice([60, 125, 250, 500])),
        piexif.ExifIFD.FNumber: (random.choice([18, 20, 22, 28]), 10),
    }
    
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: lat_ref,
        piexif.GPSIFD.GPSLatitude: lat_deg,
        piexif.GPSIFD.GPSLongitudeRef: lon_ref,
        piexif.GPSIFD.GPSLongitude: lon_deg,
        piexif.GPSIFD.GPSAltitude: (random.randint(0, 500), 1),
        piexif.GPSIFD.GPSAltitudeRef: 0,
    }
    
    exif_dict = {
        "0th": zeroth_ifd,
        "Exif": exif_ifd,
        "GPS": gps_ifd,
        "1st": {},
        "thumbnail": None
    }
    
    return piexif.dump(exif_dict)


def read_exif(image_path):
    """Чтение EXIF данных из изображения"""
    try:
        img = Image.open(image_path)
        if "exif" in img.info:
            exif_dict = piexif.load(img.info["exif"])
            result = {}
            
            # Парсинг основных данных
            for ifd in ("0th", "Exif", "GPS", "1st"):
                if ifd in exif_dict:
                    for tag, value in exif_dict[ifd].items():
                        try:
                            tag_name = piexif.TAGS[ifd].get(tag, {}).get("name", str(tag))
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='ignore')
                                except:
                                    value = str(value)
                            result[f"{ifd}.{tag_name}"] = value
                        except:
                            pass
            
            return result
        return {}
    except Exception as e:
        return {"error": str(e)}


def clear_exif(image_path, output_path=None):
    """Очистка EXIF данных из изображения"""
    try:
        img = Image.open(image_path)
        
        # Создаем новое изображение без EXIF
        data = list(img.getdata())
        img_without_exif = Image.new(img.mode, img.size)
        img_without_exif.putdata(data)
        
        if output_path is None:
            output_path = image_path
        
        img_without_exif.save(output_path, quality=95)
        return True
    except Exception as e:
        return False


def copy_exif(source_path, target_path, output_path=None):
    """Копирование EXIF данных с одного изображения на другое"""
    try:
        source_img = Image.open(source_path)
        target_img = Image.open(target_path)
        
        if "exif" in source_img.info:
            exif_bytes = source_img.info["exif"]
            
            if output_path is None:
                output_path = target_path
            
            target_img.save(output_path, exif=exif_bytes, quality=95)
            return True
        return False
    except Exception as e:
        return False


def set_exif(image_path, exif_bytes, output_path=None):
    """Установка EXIF данных в изображение"""
    try:
        img = Image.open(image_path)
        
        if output_path is None:
            output_path = image_path
        
        img.save(output_path, exif=exif_bytes, quality=95)
        return True
    except Exception as e:
        return False


def format_exif_for_display(exif_data):
    """Форматирование EXIF данных для отображения"""
    if not exif_data:
        return "❌ EXIF данные отсутствуют"
    
    if "error" in exif_data:
        return f"❌ Ошибка чтения EXIF: {exif_data['error']}"
    
    lines = ["📷 **EXIF данные:**\n"]
    
    important_tags = [
        "0th.Make", "0th.Model", "0th.DateTime",
        "Exif.DateTimeOriginal", "Exif.ISOSpeedRatings",
        "GPS.GPSLatitude", "GPS.GPSLongitude"
    ]
    
    for tag in important_tags:
        if tag in exif_data:
            tag_name = tag.split(".")[-1]
            lines.append(f"• {tag_name}: {exif_data[tag]}")
    
    # Добавляем остальные теги
    other_tags = [k for k in exif_data.keys() if k not in important_tags]
    if other_tags:
        lines.append("\n📋 **Дополнительно:**")
        for tag in other_tags[:10]:  # Ограничиваем количество
            tag_name = tag.split(".")[-1]
            value = str(exif_data[tag])[:50]  # Ограничиваем длину
            lines.append(f"• {tag_name}: {value}")
    
    return "\n".join(lines)
