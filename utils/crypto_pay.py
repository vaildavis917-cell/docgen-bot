"""
Интеграция с Crypto Bot (Crypto Pay API)
Документация: https://help.crypt.bot/crypto-pay-api
"""

import aiohttp
import hashlib
import hmac
from typing import Optional, Dict, Any, List
from datetime import datetime

from config import CRYPTO_BOT_TOKEN

# Crypto Bot API настройки
CRYPTO_BOT_API_TOKEN = CRYPTO_BOT_TOKEN
CRYPTO_BOT_API_URL = "https://pay.crypt.bot/api"

# Поддерживаемые криптовалюты
SUPPORTED_ASSETS = ["USDT", "TON", "BTC", "ETH", "LTC", "BNB", "TRX", "USDC"]

# Цены подписок в USD (обновлённые)
SUBSCRIPTION_PRICES_USD = {
    "basic": 15.0,      # 150 Stars
    "pro": 20.0,        # 200 Stars
    "premium": 30.0,    # 300 Stars
    "lifetime": 200.0   # 2000 Stars (пожизненная)
}


async def crypto_api_request(method: str, params: Dict = None) -> Dict:
    """Выполнение запроса к Crypto Bot API"""
    headers = {
        "Crypto-Pay-API-Token": CRYPTO_BOT_API_TOKEN
    }
    
    url = f"{CRYPTO_BOT_API_URL}/{method}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            return data


async def get_me() -> Dict:
    """Получение информации о приложении"""
    return await crypto_api_request("getMe")


async def get_balance() -> List[Dict]:
    """Получение баланса приложения"""
    result = await crypto_api_request("getBalance")
    if result.get("ok"):
        return result.get("result", [])
    return []


async def get_exchange_rates() -> List[Dict]:
    """Получение курсов обмена"""
    result = await crypto_api_request("getExchangeRates")
    if result.get("ok"):
        return result.get("result", [])
    return []


async def get_currencies() -> List[Dict]:
    """Получение списка поддерживаемых валют"""
    result = await crypto_api_request("getCurrencies")
    if result.get("ok"):
        return result.get("result", [])
    return []


async def create_invoice(
    amount: float,
    asset: str = "USDT",
    description: str = "",
    payload: str = "",
    paid_btn_name: str = "callback",
    paid_btn_url: str = "",
    expires_in: int = 3600  # 1 час
) -> Optional[Dict]:
    """
    Создание инвойса для оплаты
    
    Args:
        amount: Сумма в выбранной криптовалюте
        asset: Криптовалюта (USDT, TON, BTC, ETH, LTC, BNB, TRX, USDC)
        description: Описание платежа
        payload: Данные для идентификации (до 1024 символов)
        paid_btn_name: Тип кнопки после оплаты (callback, openUrl, openBot)
        paid_btn_url: URL для кнопки
        expires_in: Время жизни инвойса в секундах
    
    Returns:
        Данные инвойса или None при ошибке
    """
    params = {
        "asset": asset,
        "amount": str(amount),
        "description": description[:1024] if description else "",
        "payload": payload[:1024] if payload else "",
        "expires_in": expires_in
    }
    
    if paid_btn_name and paid_btn_url:
        params["paid_btn_name"] = paid_btn_name
        params["paid_btn_url"] = paid_btn_url
    
    result = await crypto_api_request("createInvoice", params)
    
    if result.get("ok"):
        return result.get("result")
    return None


async def get_invoices(
    asset: str = None,
    invoice_ids: List[int] = None,
    status: str = None,
    offset: int = 0,
    count: int = 100
) -> List[Dict]:
    """
    Получение списка инвойсов
    
    Args:
        asset: Фильтр по криптовалюте
        invoice_ids: Список ID инвойсов
        status: Фильтр по статусу (active, paid, expired)
        offset: Смещение
        count: Количество (макс. 1000)
    """
    params = {
        "offset": offset,
        "count": min(count, 1000)
    }
    
    if asset:
        params["asset"] = asset
    if invoice_ids:
        params["invoice_ids"] = ",".join(map(str, invoice_ids))
    if status:
        params["status"] = status
    
    result = await crypto_api_request("getInvoices", params)
    
    if result.get("ok"):
        return result.get("result", {}).get("items", [])
    return []


async def check_invoice(invoice_id: int) -> Optional[Dict]:
    """Проверка статуса инвойса"""
    invoices = await get_invoices(invoice_ids=[invoice_id])
    if invoices:
        return invoices[0]
    return None


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Проверка подписи вебхука"""
    secret = hashlib.sha256(CRYPTO_BOT_API_TOKEN.encode()).digest()
    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


async def create_subscription_invoice(
    user_id: int,
    plan_id: str,
    asset: str = "USDT"
) -> Optional[Dict]:
    """
    Создание инвойса для оплаты подписки
    
    Args:
        user_id: ID пользователя Telegram
        plan_id: ID тарифного плана (basic, pro, premium, lifetime)
        asset: Криптовалюта для оплаты
    
    Returns:
        Данные инвойса с pay_url или None
    """
    if plan_id not in SUBSCRIPTION_PRICES_USD:
        return None
    
    price_usd = SUBSCRIPTION_PRICES_USD[plan_id]
    
    # Для USDT цена = USD
    # Для других валют нужно конвертировать через курсы
    if asset == "USDT":
        amount = price_usd
    elif asset == "USDC":
        amount = price_usd
    else:
        # Получаем курс и конвертируем
        rates = await get_exchange_rates()
        rate = None
        for r in rates:
            if r.get("source") == asset and r.get("target") == "USD":
                rate = float(r.get("rate", 0))
                break
        
        if rate and rate > 0:
            amount = price_usd / rate
        else:
            # Если курс не найден, используем USDT
            asset = "USDT"
            amount = price_usd
    
    # Округляем до разумного количества знаков
    if asset in ["BTC", "ETH", "LTC", "BNB"]:
        amount = round(amount, 8)
    else:
        amount = round(amount, 2)
    
    plan_names = {
        "basic": "Basic",
        "pro": "Professional",
        "premium": "Premium",
        "lifetime": "Lifetime"
    }
    
    # Определяем срок подписки
    if plan_id == "lifetime":
        description = f"Подписка {plan_names.get(plan_id, plan_id)} (пожизненная)"
    else:
        description = f"Подписка {plan_names.get(plan_id, plan_id)} на 30 дней"
    
    payload = f"sub_{plan_id}_{user_id}_{datetime.now().timestamp()}"
    
    invoice = await create_invoice(
        amount=amount,
        asset=asset,
        description=description,
        payload=payload,
        expires_in=3600  # 1 час на оплату
    )
    
    return invoice


def get_invoice_pay_url(invoice: Dict) -> str:
    """Получение ссылки на оплату из инвойса"""
    return invoice.get("pay_url", "") if invoice else ""


def get_invoice_status(invoice: Dict) -> str:
    """Получение статуса инвойса"""
    return invoice.get("status", "unknown") if invoice else "unknown"


def parse_invoice_payload(payload: str) -> Dict:
    """
    Парсинг payload инвойса
    Формат: sub_planid_userid_timestamp
    """
    try:
        parts = payload.split("_")
        if len(parts) >= 3 and parts[0] == "sub":
            return {
                "type": "subscription",
                "plan_id": parts[1],
                "user_id": int(parts[2]),
                "timestamp": float(parts[3]) if len(parts) > 3 else 0
            }
    except:
        pass
    return {}


# Форматирование для отображения
def format_crypto_payment_info(plan_id: str) -> str:
    """Форматирование информации об оплате криптой"""
    if plan_id not in SUBSCRIPTION_PRICES_USD:
        return "Тариф не найден"
    
    price = SUBSCRIPTION_PRICES_USD[plan_id]
    plan_names = {
        "basic": "Basic",
        "pro": "Professional", 
        "premium": "Premium",
        "lifetime": "Lifetime"
    }
    
    text = f"💎 **Оплата подписки {plan_names.get(plan_id)}**\n\n"
    text += f"💰 **Стоимость:** ${price}\n"
    
    if plan_id == "lifetime":
        text += f"📅 **Срок:** Пожизненно\n\n"
    else:
        text += f"📅 **Срок:** 30 дней\n\n"
    
    text += "**Доступные криптовалюты:**\n"
    text += "• USDT (TRC-20, ERC-20)\n"
    text += "• TON\n"
    text += "• BTC\n"
    text += "• ETH\n"
    text += "• LTC\n\n"
    text += "Выберите валюту для оплаты:"
    
    return text
