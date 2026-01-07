"""
Обработчики генераторов:
- Генератор адресов
- Генератор карт
- Антидетект данные
- Подписки (Crypto Bot)
"""

import os
import json
import tempfile
import random
import asyncio
from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes, ConversationHandler

from keyboards import (
    get_address_menu_keyboard,
    get_address_again_keyboard,
    get_card_menu_keyboard,
    get_card_again_keyboard,
    get_antidetect_menu_keyboard,
    get_antidetect_again_keyboard,
    get_subscription_menu_keyboard,
    get_subscription_buy_keyboard,
    get_crypto_currency_keyboard,
    get_payment_link_keyboard,
    get_main_menu_keyboard,
    get_cancel_keyboard,
    get_after_generation_keyboard,
    PROJECT_CHANNEL
)

from utils.generators import (
    generate_address,
    format_address,
    generate_card,
    format_card,
    format_card_number,
    generate_antidetect_profile,
    format_antidetect_profile,
    export_antidetect_profile,
    ADDRESS_DATA,
    CARD_BINS
)

from utils.subscription import (
    get_user_subscription,
    set_user_subscription,
    get_user_limits,
    check_limit,
    increment_usage,
    format_subscription_info,
    format_plans_list,
    get_plan_details,
    get_plan_stars_price,
    SUBSCRIPTION_PLANS
)

from utils.crypto_pay import (
    create_subscription_invoice,
    check_invoice,
    get_invoice_pay_url,
    get_invoice_status,
    parse_invoice_payload,
    format_crypto_payment_info,
    SUBSCRIPTION_PRICES_USD
)

# Состояния
(ADDRESS_MENU, CARD_MENU, ANTIDETECT_MENU, SUBSCRIPTION_MENU) = range(100, 104)


# === Генератор адресов ===
async def address_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню генератора адресов"""
    await update.message.reply_text(
        "🏠 **Генератор адресов**\n\n"
        "Выберите страну для генерации случайного адреса:",
        reply_markup=get_address_menu_keyboard(),
        parse_mode="Markdown"
    )
    return ADDRESS_MENU


async def address_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора страны для адреса"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    if data == "back_addr_menu":
        await query.edit_message_text(
            "🏠 **Генератор адресов**\n\n"
            "Выберите страну для генерации случайного адреса:",
            reply_markup=get_address_menu_keyboard(),
            parse_mode="Markdown"
        )
        return ADDRESS_MENU
    
    # Переход к подписке
    if data == "show_subscription":
        text = format_plans_list()
        text += "\n\nВыберите тариф для просмотра деталей:"
        await query.edit_message_text(
            text,
            reply_markup=get_subscription_menu_keyboard(),
            parse_mode="Markdown"
        )
        return SUBSCRIPTION_MENU
    
    # Проверяем лимиты
    can_use, used, limit = check_limit(user_id, "addresses")
    if not can_use:
        await query.edit_message_text(
            f"❌ **Достигнут дневной лимит**\n\n"
            f"Использовано: {used}/{limit} адресов\n\n"
            f"Для увеличения лимита приобретите подписку.",
            reply_markup=get_after_generation_keyboard(),
            parse_mode="Markdown"
        )
        return ADDRESS_MENU
    
    # Генерация адреса
    if data.startswith("addr_"):
        country_code = data.replace("addr_", "").replace("copy_", "")
        
        if country_code == "random":
            country_code = random.choice(list(ADDRESS_DATA.keys()))
        
        if country_code in ADDRESS_DATA:
            address = generate_address(country_code)
            context.user_data['last_address'] = address
            
            # Увеличиваем счётчик
            increment_usage(user_id, "addresses")
            
            text = format_address(address)
            
            await query.edit_message_text(
                text,
                reply_markup=get_address_again_keyboard(country_code),
                parse_mode="Markdown"
            )
    
    return ADDRESS_MENU


# === Генератор карт ===
async def card_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню генератора карт"""
    await update.message.reply_text(
        "💳 **Генератор тестовых карт**\n\n"
        "⚠️ **Внимание:** Генерируются тестовые номера карт "
        "для разработки и тестирования. Они не являются реальными "
        "платёжными средствами.\n\n"
        "Выберите тип карты:",
        reply_markup=get_card_menu_keyboard(),
        parse_mode="Markdown"
    )
    return CARD_MENU


async def card_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора типа карты"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    if data == "back_card_menu":
        await query.edit_message_text(
            "💳 **Генератор тестовых карт**\n\n"
            "⚠️ **Внимание:** Генерируются тестовые номера карт "
            "для разработки и тестирования.\n\n"
            "Выберите тип карты:",
            reply_markup=get_card_menu_keyboard(),
            parse_mode="Markdown"
        )
        return CARD_MENU
    
    # Переход к подписке
    if data == "show_subscription":
        text = format_plans_list()
        text += "\n\nВыберите тариф для просмотра деталей:"
        await query.edit_message_text(
            text,
            reply_markup=get_subscription_menu_keyboard(),
            parse_mode="Markdown"
        )
        return SUBSCRIPTION_MENU
    
    # Проверяем лимиты
    can_use, used, limit = check_limit(user_id, "cards")
    if not can_use:
        await query.edit_message_text(
            f"❌ **Достигнут дневной лимит**\n\n"
            f"Использовано: {used}/{limit} карт\n\n"
            f"Для увеличения лимита приобретите подписку.",
            reply_markup=get_after_generation_keyboard(),
            parse_mode="Markdown"
        )
        return CARD_MENU
    
    # Генерация карты
    if data.startswith("card_"):
        card_type = data.replace("card_", "").replace("copy_", "")
        
        if card_type == "random":
            card_type = random.choice(list(CARD_BINS.keys()))
        
        if card_type in CARD_BINS:
            card = generate_card(card_type)
            context.user_data['last_card'] = card
            
            # Увеличиваем счётчик
            increment_usage(user_id, "cards")
            
            text = format_card(card)
            
            await query.edit_message_text(
                text,
                reply_markup=get_card_again_keyboard(card_type),
                parse_mode="Markdown"
            )
    
    return CARD_MENU


# === Антидетект данные ===
async def antidetect_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню антидетект данных"""
    await update.message.reply_text(
        "🤖 **Генератор антидетект данных**\n\n"
        "Генерация уникальных fingerprint профилей:\n"
        "• User-Agent\n"
        "• Screen resolution\n"
        "• WebGL fingerprint\n"
        "• Canvas fingerprint\n"
        "• Timezone, language\n"
        "• И многое другое\n\n"
        "Выберите платформу:",
        reply_markup=get_antidetect_menu_keyboard(),
        parse_mode="Markdown"
    )
    return ANTIDETECT_MENU


async def antidetect_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора платформы антидетекта"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    if data == "back_antidetect_menu":
        await query.edit_message_text(
            "🤖 **Генератор антидетект данных**\n\n"
            "Выберите платформу:",
            reply_markup=get_antidetect_menu_keyboard(),
            parse_mode="Markdown"
        )
        return ANTIDETECT_MENU
    
    # Переход к подписке
    if data == "show_subscription":
        text = format_plans_list()
        text += "\n\nВыберите тариф для просмотра деталей:"
        await query.edit_message_text(
            text,
            reply_markup=get_subscription_menu_keyboard(),
            parse_mode="Markdown"
        )
        return SUBSCRIPTION_MENU
    
    # Проверяем лимиты
    can_use, used, limit = check_limit(user_id, "antidetect")
    if not can_use:
        await query.edit_message_text(
            f"❌ **Достигнут дневной лимит**\n\n"
            f"Использовано: {used}/{limit} профилей\n\n"
            f"Для увеличения лимита приобретите подписку.",
            reply_markup=get_after_generation_keyboard(),
            parse_mode="Markdown"
        )
        return ANTIDETECT_MENU
    
    # Экспорт в JSON
    if data.startswith("antidetect_export_"):
        profile = context.user_data.get('last_antidetect_profile')
        if profile:
            # Создаём временный файл
            temp_dir = tempfile.mkdtemp()
            json_path = os.path.join(temp_dir, f"antidetect_profile_{profile['session_id'][:8]}.json")
            
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(export_antidetect_profile(profile))
            
            with open(json_path, 'rb') as f:
                await query.message.reply_document(
                    document=f,
                    filename=f"antidetect_profile.json",
                    caption="📄 Антидетект профиль в формате JSON",
                    reply_markup=get_after_generation_keyboard()
                )
            
            os.remove(json_path)
            os.rmdir(temp_dir)
        else:
            await query.answer("Сначала сгенерируйте профиль", show_alert=True)
        return ANTIDETECT_MENU
    
    # Генерация профиля
    if data.startswith("antidetect_"):
        platform = data.replace("antidetect_", "")
        
        if platform == "random":
            platforms = ["chrome_win", "chrome_mac", "firefox_win", "safari_mac", "mobile_android", "mobile_ios"]
            platform = random.choice(platforms)
        
        profile = generate_antidetect_profile(platform)
        context.user_data['last_antidetect_profile'] = profile
        
        # Увеличиваем счётчик
        increment_usage(user_id, "antidetect")
        
        text = format_antidetect_profile(profile)
        
        await query.edit_message_text(
            text,
            reply_markup=get_antidetect_again_keyboard(platform),
            parse_mode="Markdown"
        )
    
    return ANTIDETECT_MENU


# === Подписки (Crypto Bot) ===
async def subscription_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню подписок"""
    user_id = update.effective_user.id
    
    text = format_plans_list()
    text += "\n\nВыберите тариф для просмотра деталей:"
    
    await update.message.reply_text(
        text,
        reply_markup=get_subscription_menu_keyboard(),
        parse_mode="Markdown"
    )
    return SUBSCRIPTION_MENU


async def subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка меню подписок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "back_main":
        await query.delete_message()
        return ConversationHandler.END
    
    if data == "back_sub_menu":
        text = format_plans_list()
        text += "\n\nВыберите тариф для просмотра деталей:"
        
        await query.edit_message_text(
            text,
            reply_markup=get_subscription_menu_keyboard(),
            parse_mode="Markdown"
        )
        return SUBSCRIPTION_MENU
    
    # Просмотр своей подписки
    if data == "sub_my":
        text = format_subscription_info(user_id)
        await query.edit_message_text(
            text,
            reply_markup=get_subscription_menu_keyboard(),
            parse_mode="Markdown"
        )
        return SUBSCRIPTION_MENU
    
    # Просмотр деталей тарифа
    if data.startswith("sub_") and not data.startswith("sub_crypto_") and not data.startswith("sub_stars_"):
        plan_id = data.replace("sub_", "")
        if plan_id in SUBSCRIPTION_PLANS:
            text = get_plan_details(plan_id)
            
            if plan_id != "free":
                price_usd = SUBSCRIPTION_PRICES_USD.get(plan_id, 0)
                price_stars = get_plan_stars_price(plan_id)
                await query.edit_message_text(
                    text,
                    reply_markup=get_subscription_buy_keyboard(plan_id, price_usd, price_stars),
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    text,
                    reply_markup=get_subscription_menu_keyboard(),
                    parse_mode="Markdown"
                )
        return SUBSCRIPTION_MENU
    
    # Оплата через Telegram Stars
    if data.startswith("sub_stars_"):
        plan_id = data.replace("sub_stars_", "")
        if plan_id in SUBSCRIPTION_PLANS:
            price_stars = get_plan_stars_price(plan_id)
            plan = SUBSCRIPTION_PLANS[plan_id]
            
            # Создаём инвойс для Telegram Stars
            try:
                # Определяем описание в зависимости от типа подписки
                if plan_id == 'lifetime':
                    invoice_desc = f"Subscription {plan['name']} FOREVER. Unlimited access to all features."
                else:
                    invoice_desc = f"Subscription {plan['name']} for 30 days. Extended limits and features."
                
                await query.message.reply_invoice(
                    title=f"Subscription {plan['name']}",
                    description=invoice_desc,
                    payload=f"stars_{user_id}_{plan_id}",
                    currency="XTR",  # Telegram Stars
                    prices=[LabeledPrice(label=f"Subscription {plan['name']}", amount=price_stars)],
                    provider_token="",  # Пустой для Stars
                )
                await query.edit_message_text(
                    f"⭐ **Оплата Telegram Stars**\n\n"
                    f"Нажмите кнопку оплаты в сообщении выше.\n"
                    f"После успешной оплаты подписка активируется автоматически.",
                    reply_markup=get_subscription_menu_keyboard(),
                    parse_mode="Markdown"
                )
            except Exception as e:
                await query.edit_message_text(
                    f"❌ **Ошибка создания счёта**\n\n"
                    f"Telegram Stars могут быть недоступны для этого бота.\n"
                    f"Попробуйте оплатить криптовалютой.",
                    reply_markup=get_subscription_menu_keyboard(),
                    parse_mode="Markdown"
                )
        return SUBSCRIPTION_MENU
    
    # Выбор криптовалюты для оплаты
    if data.startswith("sub_crypto_"):
        plan_id = data.replace("sub_crypto_", "")
        if plan_id in SUBSCRIPTION_PLANS:
            text = format_crypto_payment_info(plan_id)
            await query.edit_message_text(
                text,
                reply_markup=get_crypto_currency_keyboard(plan_id),
                parse_mode="Markdown"
            )
        return SUBSCRIPTION_MENU
    
    # Создание инвойса для оплаты
    if data.startswith("pay_"):
        parts = data.split("_")
        if len(parts) >= 3:
            asset = parts[1]  # USDT, TON, BTC, etc.
            plan_id = parts[2]  # basic, pro, unlimited
            
            await query.edit_message_text(
                "⏳ Создаю счёт для оплаты...",
                parse_mode="Markdown"
            )
            
            # Создаём инвойс через Crypto Bot
            invoice = await create_subscription_invoice(user_id, plan_id, asset)
            
            if invoice:
                pay_url = get_invoice_pay_url(invoice)
                invoice_id = invoice.get("invoice_id")
                
                # Сохраняем invoice_id для проверки
                context.user_data['pending_invoice'] = {
                    'invoice_id': invoice_id,
                    'plan_id': plan_id,
                    'user_id': user_id
                }
                
                plan_names = {
                    "basic": "Basic",
                    "pro": "Professional",
                    "premium": "Premium",
                    "lifetime": "Lifetime"
                }
                
                await query.edit_message_text(
                    f"💎 **Оплата подписки {plan_names.get(plan_id)}**\n\n"
                    f"💰 **Сумма:** {invoice.get('amount')} {asset}\n"
                    f"📅 **Срок:** {'FOREVER' if plan_id == 'lifetime' else '30 дней'}\n\n"
                    f"Нажмите кнопку ниже для оплаты через @CryptoBot.\n"
                    f"После оплаты нажмите «Проверить оплату».",
                    reply_markup=get_payment_link_keyboard(pay_url, plan_id),
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    "❌ Ошибка создания счёта. Попробуйте позже или выберите другую валюту.",
                    reply_markup=get_crypto_currency_keyboard(plan_id),
                    parse_mode="Markdown"
                )
        return SUBSCRIPTION_MENU
    
    # Проверка оплаты
    if data.startswith("check_payment_"):
        pending = context.user_data.get('pending_invoice')
        
        if pending:
            invoice_id = pending.get('invoice_id')
            plan_id = pending.get('plan_id')
            
            await query.edit_message_text(
                "🔄 Проверяю оплату...",
                parse_mode="Markdown"
            )
            
            # Проверяем статус инвойса
            invoice = await check_invoice(invoice_id)
            
            if invoice:
                status = get_invoice_status(invoice)
                
                if status == "paid":
                    # Активируем подписку
                    if set_user_subscription(user_id, plan_id):
                        plan = SUBSCRIPTION_PLANS.get(plan_id, {})
                        
                        # Очищаем pending invoice
                        context.user_data.pop('pending_invoice', None)
                        
                        # Определяем срок подписки
                        duration = plan.get('duration_days', 30)
                        if duration == -1:
                            duration_text = "FOREVER ♾"
                        else:
                            duration_text = f"{duration} days"
                        
                        await query.edit_message_text(
                            f"✅ **Subscription activated!**\n\n"
                            f"{plan.get('icon', '⭐')} **{plan.get('name', plan_id)}**\n"
                            f"📅 Duration: {duration_text}\n\n"
                            f"Thank you for your purchase! Extended limits are now available.\n\n"
                            f"📢 Project channel: {PROJECT_CHANNEL}",
                            reply_markup=get_subscription_menu_keyboard(),
                            parse_mode="Markdown"
                        )
                    else:
                        await query.edit_message_text(
                            "❌ Ошибка активации подписки. Обратитесь в поддержку.",
                            reply_markup=get_subscription_menu_keyboard(),
                            parse_mode="Markdown"
                        )
                elif status == "active":
                    pay_url = get_invoice_pay_url(invoice)
                    await query.edit_message_text(
                        "⏳ **Оплата ещё не получена**\n\n"
                        "Пожалуйста, оплатите счёт и нажмите «Проверить оплату» снова.",
                        reply_markup=get_payment_link_keyboard(pay_url, plan_id),
                        parse_mode="Markdown"
                    )
                elif status == "expired":
                    await query.edit_message_text(
                        "❌ **Счёт истёк**\n\n"
                        "Пожалуйста, создайте новый счёт для оплаты.",
                        reply_markup=get_subscription_menu_keyboard(),
                        parse_mode="Markdown"
                    )
                else:
                    await query.edit_message_text(
                        f"⚠️ Статус счёта: {status}\n\nПопробуйте позже.",
                        reply_markup=get_subscription_menu_keyboard(),
                        parse_mode="Markdown"
                    )
            else:
                await query.edit_message_text(
                    "❌ Не удалось проверить статус оплаты. Попробуйте позже.",
                    reply_markup=get_subscription_menu_keyboard(),
                    parse_mode="Markdown"
                )
        else:
            await query.edit_message_text(
                "❌ Нет активного счёта для проверки.",
                reply_markup=get_subscription_menu_keyboard(),
                parse_mode="Markdown"
            )
        return SUBSCRIPTION_MENU
    
    return SUBSCRIPTION_MENU


# === Обновлённая информация о подписке ===
async def subscription_info_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о подписке (обновлённая версия)"""
    user_id = update.effective_user.id
    text = format_subscription_info(user_id)
    
    await update.message.reply_text(
        text,
        reply_markup=get_subscription_menu_keyboard(),
        parse_mode="Markdown"
    )
    return SUBSCRIPTION_MENU
