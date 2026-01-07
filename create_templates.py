"""
Скрипт для создания базовых шаблонов документов
"""

from PIL import Image, ImageDraw, ImageFont
import os

TEMPLATES_DIR = "/home/ubuntu/docgen_bot/templates"

def create_template(country, width=800, height=500):
    """Создание базового шаблона документа"""
    
    # Цвета для разных стран
    colors = {
        "ru": {"bg": "#f5f5dc", "border": "#8b0000", "text": "#000000"},
        "en": {"bg": "#f0f8ff", "border": "#00008b", "text": "#000000"},
        "ua": {"bg": "#fffacd", "border": "#0057b7", "text": "#000000"},
        "ua_id": {"bg": "#e6f3ff", "border": "#0057b7", "text": "#000000"},
        "pl": {"bg": "#fff0f5", "border": "#dc143c", "text": "#000000"},
    }
    
    titles = {
        "ru": "ПАСПОРТ ГРАЖДАНИНА",
        "en": "IDENTITY CARD",
        "ua": "ПАСПОРТ ГРОМАДЯНИНА",
        "ua_id": "ID-КАРТКА ГРОМАДЯНИНА",
        "pl": "DOWÓD OSOBISTY",
    }
    
    color = colors.get(country, colors["en"])
    title = titles.get(country, "IDENTITY CARD")
    
    # Создаем изображение
    img = Image.new('RGB', (width, height), color['bg'])
    draw = ImageDraw.Draw(img)
    
    # Рамка
    draw.rectangle([5, 5, width-5, height-5], outline=color['border'], width=3)
    draw.rectangle([15, 15, width-15, height-15], outline=color['border'], width=1)
    
    # Заголовок
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Заголовок по центру
    bbox = draw.textbbox((0, 0), title, font=font_title)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, 30), title, fill=color['border'], font=font_title)
    
    # Область для фото
    photo_x, photo_y = 50, 100
    photo_w, photo_h = 150, 200
    draw.rectangle([photo_x, photo_y, photo_x + photo_w, photo_y + photo_h], 
                   outline=color['border'], width=2)
    draw.text((photo_x + 50, photo_y + 90), "ФОТО", fill="#888888", font=font_text)
    
    # Поля для данных
    fields_x = 230
    fields = [
        ("{{LAST_NAME}}", 100),
        ("{{FIRST_NAME}}", 140),
        ("{{MIDDLE_NAME}}", 180),
        ("{{BIRTH_DATE}}", 220),
        ("{{GENDER}}", 260),
    ]
    
    labels = {
        "ru": ["Фамилия:", "Имя:", "Отчество:", "Дата рождения:", "Пол:"],
        "en": ["Surname:", "Name:", "Middle name:", "Date of birth:", "Sex:"],
        "ua": ["Прізвище:", "Ім'я:", "По батькові:", "Дата народження:", "Стать:"],
        "ua_id": ["Прізвище:", "Ім'я:", "По батькові:", "Дата народження:", "Стать:"],
        "pl": ["Nazwisko:", "Imię:", "Drugie imię:", "Data urodzenia:", "Płeć:"],
    }
    
    country_labels = labels.get(country, labels["en"])
    
    for i, (placeholder, y) in enumerate(fields):
        if i < len(country_labels):
            draw.text((fields_x, y), country_labels[i], fill=color['text'], font=font_text)
            draw.text((fields_x + 150, y), placeholder, fill=color['border'], font=font_text)
    
    # Сохраняем шаблон
    output_dir = os.path.join(TEMPLATES_DIR, country)
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "template.png")
    img.save(output_path, "PNG")
    print(f"✓ Создан шаблон: {output_path}")
    
    return output_path


def create_bm_template(country="ua"):
    """Создание шаблона для верификации БМ"""
    
    width, height = 800, 600
    
    # Создаем изображение
    img = Image.new('RGB', (width, height), '#ffffff')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Заголовок
    if country == "ua":
        title = "ВИПИСКА З ЄДИНОГО ДЕРЖАВНОГО РЕЄСТРУ"
    else:
        title = "BUSINESS REGISTRATION CERTIFICATE"
    
    bbox = draw.textbbox((0, 0), title, font=font_title)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, 30), title, fill='#000080', font=font_title)
    
    # Рамка
    draw.rectangle([20, 70, width-20, height-20], outline='#000080', width=2)
    
    # Поля
    fields = [
        ("Найменування:", "{{COMPANY_NAME}}", 100),
        ("Код ЄДРПОУ:", "{{REG_NUMBER}}", 140),
        ("Адреса:", "{{ADDRESS}}", 180),
        ("Місто:", "{{CITY}}", 220),
        ("Область:", "{{REGION}}", 260),
        ("Поштовий індекс:", "{{POSTAL}}", 300),
        ("Телефон:", "{{PHONE}}", 340),
    ]
    
    for label, placeholder, y in fields:
        draw.text((40, y), label, fill='#000000', font=font_text)
        draw.text((200, y), placeholder, fill='#000080', font=font_text)
    
    # Печать (круг)
    stamp_x, stamp_y = 550, 400
    draw.ellipse([stamp_x, stamp_y, stamp_x+120, stamp_y+120], outline='#0000aa', width=2)
    draw.text((stamp_x+30, stamp_y+50), "ПЕЧАТКА", fill='#0000aa', font=font_text)
    
    # Сохраняем
    output_dir = os.path.join(TEMPLATES_DIR, "bm")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"bm_{country}.png")
    img.save(output_path, "PNG")
    print(f"✓ Создан шаблон БМ: {output_path}")
    
    return output_path


def create_tiktok_template():
    """Создание шаблона для верификации TikTok"""
    
    width, height = 800, 600
    
    img = Image.new('RGB', (width, height), '#ffffff')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    title = "BUSINESS VERIFICATION DOCUMENT"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, 30), title, fill='#000000', font=font_title)
    
    # Рамка
    draw.rectangle([20, 70, width-20, height-20], outline='#333333', width=2)
    
    # Поля
    fields = [
        ("Legal Company Name:", "{{COMPANY_NAME}}", 100),
        ("Country/Region:", "{{COUNTRY}}", 140),
        ("Address:", "{{ADDRESS}}", 180),
        ("City:", "{{CITY}}", 220),
        ("State/Province:", "{{REGION}}", 260),
        ("Postal Code:", "{{POSTAL}}", 300),
        ("License Number:", "{{LICENSE}}", 340),
    ]
    
    for label, placeholder, y in fields:
        draw.text((40, y), label, fill='#000000', font=font_text)
        draw.text((220, y), placeholder, fill='#333333', font=font_text)
    
    # Сохраняем
    output_dir = os.path.join(TEMPLATES_DIR, "tiktok")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "tiktok_verif.png")
    img.save(output_path, "PNG")
    print(f"✓ Создан шаблон TikTok: {output_path}")
    
    return output_path


if __name__ == "__main__":
    print("Создание шаблонов документов...")
    
    # Создаем шаблоны для разных стран
    for country in ["ru", "en", "ua", "ua_id", "pl"]:
        create_template(country)
    
    # Создаем шаблоны для верификации
    create_bm_template("ua")
    create_bm_template("en")
    create_tiktok_template()
    
    print("\n✅ Все шаблоны созданы!")
