"""
Утилиты для уникализации изображений
"""

from PIL import Image, ImageEnhance, ImageFilter
import random
import numpy as np
import io
import os
from .exif_utils import generate_random_exif, set_exif


def uniqualize_image(image_path, output_path, settings=None, add_exif=True):
    """
    Уникализация изображения с заданными настройками
    
    settings = {
        "rotation": float,      # -10 до 10
        "brightness": float,    # -10 до 10
        "contrast": float,      # -10 до 10
        "color": float,         # -10 до 10
        "noise": float,         # 0 до 10
        "blur": float           # 0 до 10
    }
    """
    try:
        img = Image.open(image_path)
        
        # Конвертируем в RGB если нужно
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Применяем настройки или используем случайные
        if settings is None:
            settings = {
                "rotation": random.uniform(-2, 2),
                "brightness": random.uniform(-0.1, 0.2),
                "contrast": random.uniform(-0.1, 0.2),
                "color": random.uniform(-0.1, 0.2),
                "noise": random.uniform(2, 5),
                "blur": random.uniform(0.5, 1.5)
            }
        
        # Поворот
        if "rotation" in settings and settings["rotation"] != 0:
            rotation = settings["rotation"]
            if isinstance(rotation, tuple):
                rotation = random.uniform(rotation[0], rotation[1])
            img = img.rotate(rotation, expand=False, fillcolor=(255, 255, 255))
        
        # Яркость (конвертируем из -10..10 в 0.5..1.5)
        if "brightness" in settings:
            brightness = settings["brightness"]
            if isinstance(brightness, tuple):
                brightness = random.uniform(brightness[0], brightness[1])
            # Нормализуем значение
            brightness_factor = 1 + (brightness / 20)  # -10 -> 0.5, 0 -> 1, 10 -> 1.5
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness_factor)
        
        # Контраст
        if "contrast" in settings:
            contrast = settings["contrast"]
            if isinstance(contrast, tuple):
                contrast = random.uniform(contrast[0], contrast[1])
            contrast_factor = 1 + (contrast / 20)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_factor)
        
        # Цветокоррекция
        if "color" in settings:
            color = settings["color"]
            if isinstance(color, tuple):
                color = random.uniform(color[0], color[1])
            color_factor = 1 + (color / 20)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(color_factor)
        
        # Шум
        if "noise" in settings and settings["noise"] > 0:
            noise_level = settings["noise"]
            if isinstance(noise_level, tuple):
                noise_level = random.uniform(noise_level[0], noise_level[1])
            
            img_array = np.array(img)
            noise = np.random.normal(0, noise_level, img_array.shape)
            noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(noisy_img)
        
        # Блюр
        if "blur" in settings and settings["blur"] > 0:
            blur_level = settings["blur"]
            if isinstance(blur_level, tuple):
                blur_level = random.uniform(blur_level[0], blur_level[1])
            blur_radius = blur_level / 5  # Нормализуем
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # Небольшое изменение размера для уникальности хеша
        width, height = img.size
        new_width = width + random.randint(-2, 2)
        new_height = height + random.randint(-2, 2)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Сохраняем
        img.save(output_path, "JPEG", quality=random.randint(90, 95))
        
        # Добавляем EXIF если нужно
        if add_exif:
            exif_bytes = generate_random_exif()
            set_exif(output_path, exif_bytes, output_path)
        
        return True
    except Exception as e:
        print(f"Error uniqualizing image: {e}")
        return False


def resize_image(image_path, output_path, scale_factor):
    """Изменение размера изображения"""
    try:
        img = Image.open(image_path)
        width, height = img.size
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        img.save(output_path, quality=95)
        return True
    except Exception as e:
        return False


def overlay_photo_on_template(template_path, photo_path, output_path, 
                              photo_position, photo_size, text_data=None):
    """
    Наложение фото на шаблон документа
    
    photo_position: (x, y) - позиция левого верхнего угла фото
    photo_size: (width, height) - размер фото
    text_data: список словарей с текстом и позициями
    """
    try:
        from PIL import ImageDraw, ImageFont
        
        template = Image.open(template_path)
        photo = Image.open(photo_path)
        
        # Изменяем размер фото
        photo = photo.resize(photo_size, Image.LANCZOS)
        
        # Накладываем фото на шаблон
        template.paste(photo, photo_position)
        
        # Добавляем текст если есть
        if text_data:
            draw = ImageDraw.Draw(template)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            for item in text_data:
                text = item.get("text", "")
                position = item.get("position", (0, 0))
                color = item.get("color", (0, 0, 0))
                draw.text(position, text, fill=color, font=font)
        
        template.save(output_path, quality=95)
        return True
    except Exception as e:
        print(f"Error overlaying photo: {e}")
        return False


def create_document_image(template_type, user_data, output_path):
    """
    Создание изображения документа на основе шаблона
    
    user_data = {
        "first_name": str,
        "last_name": str,
        "middle_name": str,
        "birth_date": str,
        "gender": str,
        "photo_path": str (optional)
    }
    """
    from PIL import ImageDraw, ImageFont
    from faker import Faker
    
    # Создаем базовое изображение документа
    # Размеры типичной ID-карты
    width, height = 856, 540
    
    # Цвета фона в зависимости от типа
    bg_colors = {
        "ru": (240, 240, 245),
        "en": (245, 245, 240),
        "ua": (240, 245, 240),
        "ua_id": (235, 240, 250),
        "pl": (245, 240, 240)
    }
    
    bg_color = bg_colors.get(template_type, (245, 245, 245))
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Загружаем шрифт
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Заголовки в зависимости от страны
    headers = {
        "ru": "РОССИЙСКАЯ ФЕДЕРАЦИЯ\nУДОСТОВЕРЕНИЕ ЛИЧНОСТИ",
        "en": "UNITED KINGDOM\nIDENTITY CARD",
        "ua": "УКРАЇНА\nПОСВІДЧЕННЯ ОСОБИ",
        "ua_id": "УКРАЇНА\nID КАРТКА",
        "pl": "RZECZPOSPOLITA POLSKA\nDOWÓD OSOBISTY"
    }
    
    field_labels = {
        "ru": {"name": "Имя", "surname": "Фамилия", "birth": "Дата рождения", "gender": "Пол"},
        "en": {"name": "Name", "surname": "Surname", "birth": "Date of Birth", "gender": "Gender"},
        "ua": {"name": "Ім'я", "surname": "Прізвище", "birth": "Дата народження", "gender": "Стать"},
        "ua_id": {"name": "Ім'я", "surname": "Прізвище", "birth": "Дата народження", "gender": "Стать"},
        "pl": {"name": "Imię", "surname": "Nazwisko", "birth": "Data urodzenia", "gender": "Płeć"}
    }
    
    # Рисуем рамку
    draw.rectangle([(10, 10), (width-10, height-10)], outline=(100, 100, 100), width=2)
    
    # Заголовок
    header = headers.get(template_type, "IDENTITY DOCUMENT")
    draw.multiline_text((width//2, 30), header, fill=(0, 0, 100), font=font_large, anchor="ma", align="center")
    
    # Область для фото
    photo_x, photo_y = 30, 100
    photo_w, photo_h = 200, 250
    draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], 
                   outline=(150, 150, 150), width=1)
    
    # Если есть фото пользователя, накладываем его
    if user_data.get("photo_path") and os.path.exists(user_data["photo_path"]):
        try:
            user_photo = Image.open(user_data["photo_path"])
            user_photo = user_photo.resize((photo_w, photo_h), Image.LANCZOS)
            img.paste(user_photo, (photo_x, photo_y))
        except:
            draw.text((photo_x + 50, photo_y + 100), "PHOTO", fill=(150, 150, 150), font=font_medium)
    else:
        draw.text((photo_x + 50, photo_y + 100), "PHOTO", fill=(150, 150, 150), font=font_medium)
    
    # Данные
    labels = field_labels.get(template_type, field_labels["en"])
    data_x = 260
    data_y = 120
    line_height = 50
    
    # Фамилия
    draw.text((data_x, data_y), labels["surname"], fill=(100, 100, 100), font=font_small)
    draw.text((data_x, data_y + 18), user_data.get("last_name", "UNKNOWN"), fill=(0, 0, 0), font=font_medium)
    
    # Имя
    data_y += line_height
    draw.text((data_x, data_y), labels["name"], fill=(100, 100, 100), font=font_small)
    name = user_data.get("first_name", "UNKNOWN")
    if user_data.get("middle_name"):
        name += " " + user_data["middle_name"]
    draw.text((data_x, data_y + 18), name, fill=(0, 0, 0), font=font_medium)
    
    # Дата рождения
    data_y += line_height
    draw.text((data_x, data_y), labels["birth"], fill=(100, 100, 100), font=font_small)
    draw.text((data_x, data_y + 18), user_data.get("birth_date", "01.01.1990"), fill=(0, 0, 0), font=font_medium)
    
    # Пол
    data_y += line_height
    draw.text((data_x, data_y), labels["gender"], fill=(100, 100, 100), font=font_small)
    gender = user_data.get("gender", "M")
    draw.text((data_x, data_y + 18), gender, fill=(0, 0, 0), font=font_medium)
    
    # Номер документа (случайный)
    doc_number = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    draw.text((data_x, data_y + line_height + 20), f"№ {doc_number}", fill=(0, 0, 100), font=font_medium)
    
    # MRZ зона внизу
    mrz_y = height - 80
    draw.rectangle([(20, mrz_y), (width-20, height-20)], fill=(230, 230, 230))
    
    # Генерируем MRZ-подобный текст
    mrz_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
    mrz_line1 = ''.join(random.choices(mrz_chars, k=44))
    mrz_line2 = ''.join(random.choices(mrz_chars, k=44))
    
    try:
        mrz_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
    except:
        mrz_font = font_small
    
    draw.text((30, mrz_y + 10), mrz_line1, fill=(0, 0, 0), font=mrz_font)
    draw.text((30, mrz_y + 30), mrz_line2, fill=(0, 0, 0), font=mrz_font)
    
    # Сохраняем
    img.save(output_path, "JPEG", quality=95)
    
    # Добавляем EXIF
    exif_bytes = generate_random_exif()
    set_exif(output_path, exif_bytes, output_path)
    
    return True
