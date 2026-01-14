"""
Обработчик Mimesis генераторов для Telegram бота
Генерация фейковых данных: персона, адрес, карта, компания, интернет, крипто
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.localization import get_user_language
from utils.mimesis_gen import (
    generate_person, generate_address, generate_card, generate_company,
    generate_internet, generate_crypto, generate_full_profile,
    format_person, format_address, format_card, format_company,
    format_internet, format_crypto, format_full_profile
)
from keyboards import (
    get_mgen_again_keyboard, get_mgen_address_country_keyboard,
    get_mgen_card_type_keyboard, get_generators_menu_keyboard
)

logger = logging.getLogger(__name__)


async def safe_edit_text(query, text, reply_markup=None, parse_mode=None):
    """Безопасное редактирование сообщения"""
    try:
        await query.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except Exception as e:
        error_str = str(e).lower()
        if "message is not modified" in error_str or "no text" in error_str:
            pass
        else:
            logger.warning(f"Failed to edit message: {e}")


async def mimesis_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback для Mimesis генераторов"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    lang_code = get_user_language(user_id)
    
    # === Меню выбора ===
    
    # Персона - сразу генерируем
    if data == "mgen_person":
        person_data = generate_person(lang_code)
        text = format_person(person_data, lang_code)
        # Сохраняем для копирования
        context.user_data['last_mgen'] = person_data
        context.user_data['last_mgen_type'] = 'person'
        await safe_edit_text(query, text, 
                           reply_markup=get_mgen_again_keyboard('person', user_id),
                           parse_mode="Markdown")
        return
    
    # Адрес - показываем выбор страны
    if data == "mgen_address":
        await safe_edit_text(query, 
            "📍 **Выберите страну:**" if lang_code == 'ru' else "📍 **Select country:**",
            reply_markup=get_mgen_address_country_keyboard(user_id),
            parse_mode="Markdown")
        return
    
    # Адрес по стране
    if data.startswith("mgen_addr_"):
        country = data.replace("mgen_addr_", "")
        if country == "random":
            import random
            country = random.choice(['us', 'uk', 'de', 'ru', 'ua', 'pl', 'fr', 'es', 'it'])
        
        addr_data = generate_address(country)
        text = format_address(addr_data, lang_code)
        context.user_data['last_mgen'] = addr_data
        context.user_data['last_mgen_type'] = 'address'
        context.user_data['last_mgen_country'] = country
        await safe_edit_text(query, text,
                           reply_markup=get_mgen_again_keyboard(f'addr_{country}', user_id),
                           parse_mode="Markdown")
        return
    
    # Карта - показываем выбор типа
    if data == "mgen_card":
        await safe_edit_text(query,
            "💳 **Выберите тип карты:**" if lang_code == 'ru' else "💳 **Select card type:**",
            reply_markup=get_mgen_card_type_keyboard(user_id),
            parse_mode="Markdown")
        return
    
    # Карта по типу
    if data.startswith("mgen_card_"):
        card_type = data.replace("mgen_card_", "")
        card_data = generate_card(card_type)
        text = format_card(card_data, lang_code)
        context.user_data['last_mgen'] = card_data
        context.user_data['last_mgen_type'] = 'card'
        await safe_edit_text(query, text,
                           reply_markup=get_mgen_again_keyboard(f'card_{card_type}', user_id),
                           parse_mode="Markdown")
        return
    
    # Компания
    if data == "mgen_company":
        company_data = generate_company(lang_code)
        text = format_company(company_data, lang_code)
        context.user_data['last_mgen'] = company_data
        context.user_data['last_mgen_type'] = 'company'
        await safe_edit_text(query, text,
                           reply_markup=get_mgen_again_keyboard('company', user_id),
                           parse_mode="Markdown")
        return
    
    # Интернет
    if data == "mgen_internet":
        internet_data = generate_internet(lang_code)
        text = format_internet(internet_data, lang_code)
        context.user_data['last_mgen'] = internet_data
        context.user_data['last_mgen_type'] = 'internet'
        await safe_edit_text(query, text,
                           reply_markup=get_mgen_again_keyboard('internet', user_id),
                           parse_mode="Markdown")
        return
    
    # Крипто
    if data == "mgen_crypto":
        crypto_data = generate_crypto()
        text = format_crypto(crypto_data, lang_code)
        context.user_data['last_mgen'] = crypto_data
        context.user_data['last_mgen_type'] = 'crypto'
        await safe_edit_text(query, text,
                           reply_markup=get_mgen_again_keyboard('crypto', user_id),
                           parse_mode="Markdown")
        return
    
    # Полный профиль
    if data == "mgen_full":
        full_data = generate_full_profile(lang_code)
        text = format_full_profile(full_data, lang_code)
        context.user_data['last_mgen'] = full_data
        context.user_data['last_mgen_type'] = 'full'
        await safe_edit_text(query, text,
                           reply_markup=get_mgen_again_keyboard('full', user_id),
                           parse_mode="Markdown")
        return
    
    # === Копирование ===
    if data.startswith("mgen_copy_"):
        gen_type = data.replace("mgen_copy_", "")
        last_data = context.user_data.get('last_mgen', {})
        
        if not last_data:
            await query.answer("❌ Нет данных для копирования", show_alert=True)
            return
        
        # Форматируем для копирования (без Markdown)
        copy_text = format_for_copy(last_data, gen_type)
        
        # Отправляем как отдельное сообщение для удобного копирования
        await query.message.reply_text(
            f"📋 **Скопируйте:**\n\n```\n{copy_text}\n```",
            parse_mode="Markdown"
        )
        await query.answer("✅ Готово!")
        return
    
    # Игнорируем разделитель
    if data == "ignore":
        await query.answer()
        return


def format_for_copy(data: dict, gen_type: str) -> str:
    """Форматирование данных для копирования"""
    if gen_type == 'person' or gen_type.startswith('person'):
        return f"""Name: {data.get('full_name', '')}
Email: {data.get('email', '')}
Phone: {data.get('phone', '')}
Birthday: {data.get('birthday', '')}
Username: {data.get('username', '')}
Password: {data.get('password', '')}"""
    
    elif 'addr' in gen_type or gen_type == 'address':
        return f"""Country: {data.get('country', '')}
City: {data.get('city', '')}
Address: {data.get('address', '')}
Postal: {data.get('postal_code', '')}
Coords: {data.get('latitude', '')}, {data.get('longitude', '')}"""
    
    elif 'card' in gen_type:
        return f"""Network: {data.get('network', '')}
Number: {data.get('number', '')}
CVV: {data.get('cvv', '')}
Exp: {data.get('expiration', '')}
Holder: {data.get('holder', '')}"""
    
    elif gen_type == 'company':
        return f"""Name: {data.get('name', '')}
Type: {data.get('type', '')}
Bank: {data.get('bank', '')}
Address: {data.get('address', '')}
Phone: {data.get('phone', '')}
Email: {data.get('email', '')}
Website: {data.get('website', '')}"""
    
    elif gen_type == 'internet':
        return f"""Email: {data.get('email', '')}
Username: {data.get('username', '')}
Password: {data.get('password', '')}
IPv4: {data.get('ip_v4', '')}
IPv6: {data.get('ip_v6', '')}
MAC: {data.get('mac', '')}"""
    
    elif gen_type == 'crypto':
        return f"""UUID: {data.get('uuid', '')}
Token: {data.get('token', '')}
API Key: {data.get('api_key', '')}
Bitcoin: {data.get('bitcoin', '')}
Ethereum: {data.get('ethereum', '')}"""
    
    elif gen_type == 'full':
        person = data.get('person', {})
        address = data.get('address', {})
        card = data.get('card', {})
        return f"""=== PERSON ===
Name: {person.get('full_name', '')}
Email: {person.get('email', '')}
Phone: {person.get('phone', '')}
Birthday: {person.get('birthday', '')}

=== ADDRESS ===
Country: {address.get('country', '')}
City: {address.get('city', '')}
Address: {address.get('address', '')}
Postal: {address.get('postal_code', '')}

=== CARD ===
Number: {card.get('number', '')}
CVV: {card.get('cvv', '')}
Exp: {card.get('expiration', '')}
Holder: {card.get('holder', '')}"""
    
    return str(data)
