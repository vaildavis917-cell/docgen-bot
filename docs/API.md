# DocGen Bot — API Documentation

Документация по внутренним модулям бота.

## Содержание

1. [Database](#database)
2. [Subscription Manager](#subscription-manager)
3. [Rate Limiter](#rate-limiter)
4. [Error Monitor](#error-monitor)
5. [Mimesis Generator](#mimesis-generator)
6. [CryptoPay Webhook](#cryptopay-webhook)

---

## Database

**Файл:** `utils/database.py`

SQLite база данных для хранения пользователей, подписок и генераций.

### Класс Database

```python
from utils.database import Database

db = Database(db_path='data/bot.db')
```

### Таблицы

| Таблица | Описание |
|---------|----------|
| `users` | Пользователи бота |
| `subscriptions` | Подписки пользователей |
| `generations` | История генераций |

### Методы

#### get_connection()

Контекстный менеджер для получения соединения с БД.

```python
with db.get_connection() as conn:
    cursor = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
```

### Схема таблиц

```sql
-- users
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    is_banned BOOLEAN DEFAULT 0
);

-- subscriptions
CREATE TABLE subscriptions (
    user_id INTEGER PRIMARY KEY,
    plan TEXT DEFAULT 'free',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    generations_used INTEGER DEFAULT 0,
    invoice_id TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- generations
CREATE TABLE generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

## Subscription Manager

**Файл:** `utils/subscription_manager.py`

Управление подписками пользователей.

### Класс SubscriptionManager

```python
from utils.subscription_manager import SubscriptionManager

sub_manager = SubscriptionManager(data_dir='data')
```

### Тарифные планы

| План | Лимит | Период |
|------|-------|--------|
| `free` | 5 генераций | день |
| `pro` | 500 генераций | месяц |
| `unlimited` | ∞ | месяц |

### Методы

#### can_generate(user_id: int) -> tuple[bool, str]

Проверяет, может ли пользователь генерировать.

```python
can, reason = sub_manager.can_generate(user_id)
if not can:
    await update.message.reply_text(reason)
    return
```

**Возвращает:**
- `(True, "")` — можно генерировать
- `(False, "Лимит исчерпан...")` — нельзя, причина

#### increment_usage(user_id: int)

Увеличивает счётчик генераций.

```python
sub_manager.increment_usage(user_id)
```

#### upgrade_subscription(user_id: int, plan: str, invoice_id: str = None)

Обновляет подписку пользователя.

```python
sub_manager.upgrade_subscription(
    user_id=123456789,
    plan='pro',
    invoice_id='INV-12345'
)
```

#### get_subscription(user_id: int) -> dict

Возвращает информацию о подписке.

```python
sub = sub_manager.get_subscription(user_id)
# {'plan': 'free', 'generations_used': 3, 'limit': 5, 'end_date': None}
```

#### get_usage_info(user_id: int) -> str

Возвращает форматированную строку с информацией об использовании.

```python
info = sub_manager.get_usage_info(user_id)
# "📊 Ваша подписка: Free\n📈 Использовано: 3/5 сегодня"
```

#### get_pricing_message() -> str

Возвращает сообщение с тарифами.

```python
pricing = sub_manager.get_pricing_message()
```

#### cleanup_old_usage()

Очищает старые записи использования (для daily job).

```python
sub_manager.cleanup_old_usage()
```

---

## Rate Limiter

**Файл:** `utils/rate_limiter.py`

Защита от флуда с адаптивными лимитами.

### Класс RateLimiter

```python
from utils.rate_limiter import RateLimiter

rate_limiter = RateLimiter()
```

### Методы

#### check_rate_limit(user_id: int, plan: str = 'free') -> tuple[bool, int]

Проверяет rate limit для пользователя.

```python
allowed, wait_time = rate_limiter.check_rate_limit(user_id, plan='pro')
if not allowed:
    await update.message.reply_text(f"Подождите {wait_time} секунд")
    return
```

**Возвращает:**
- `(True, 0)` — разрешено
- `(False, seconds)` — заблокировано, ждать N секунд

#### reset_user(user_id: int)

Сбрасывает лимиты для пользователя (админ команда).

```python
rate_limiter.reset_user(user_id)
```

### Декоратор rate_limit

```python
from utils.rate_limiter import rate_limit

@rate_limit(sub_manager)
async def generate_handler(update, context):
    # Автоматическая проверка rate limit
    pass
```

### Лимиты по планам

| План | Запросов/мин | Cooldown |
|------|--------------|----------|
| `free` | 10 | 3 сек |
| `pro` | 30 | 1 сек |
| `unlimited` | 60 | 0.5 сек |

---

## Error Monitor

**Файл:** `utils/error_monitor.py`

Мониторинг ошибок с уведомлениями админу.

### Класс ErrorMonitor

```python
from utils.error_monitor import ErrorMonitor

error_monitor = ErrorMonitor(
    admin_ids=[123456789],
    log_dir='logs'
)
```

### Методы

#### log_error(error: Exception, context: dict = None)

Логирует ошибку и отправляет алерт админу.

```python
try:
    # код
except Exception as e:
    await error_monitor.log_error(e, {
        'user_id': user_id,
        'action': 'generate_card'
    })
```

#### get_stats() -> str

Возвращает статистику ошибок.

```python
stats = error_monitor.get_stats()
# "📊 Статистика ошибок:\n- Всего: 15\n- Сегодня: 3\n..."
```

### Декоратор handle_errors

```python
from utils.error_monitor import handle_errors

@handle_errors(error_monitor)
async def some_handler(update, context):
    # Ошибки автоматически логируются
    pass
```

### Формат логов

Логи сохраняются в `logs/bot_YYYYMMDD.log`:

```
2026-01-14 12:30:45 ERROR [generate_card] user_id=123456789: ValueError: Invalid card type
2026-01-14 12:30:45 ERROR Traceback: ...
```

---

## Mimesis Generator

**Файл:** `utils/mimesis_gen.py`

Генерация фейковых данных.

### Функции

#### generate_person(locale: str = 'ru') -> dict

Генерирует данные персоны.

```python
from utils.mimesis_gen import generate_person

person = generate_person('ru')
# {
#     'name': 'Иван Петров',
#     'email': 'ivan.petrov@mail.ru',
#     'phone': '+7 (999) 123-45-67',
#     'birthday': '1990-05-15',
#     'password': 'xK9#mP2$nL'
# }
```

#### generate_address(country: str = 'US') -> dict

Генерирует адрес.

```python
from utils.mimesis_gen import generate_address

address = generate_address('RU')
# {
#     'street': 'ул. Ленина, 15',
#     'city': 'Москва',
#     'state': 'Московская область',
#     'postal_code': '123456',
#     'country': 'Россия'
# }
```

#### generate_card(card_type: str = 'visa') -> dict

Генерирует данные банковской карты.

```python
from utils.mimesis_gen import generate_card

card = generate_card('visa')
# {
#     'number': '4532 1234 5678 9012',
#     'cvv': '123',
#     'expiry': '12/28',
#     'holder': 'JOHN DOE',
#     'type': 'Visa'
# }
```

#### generate_company(locale: str = 'ru') -> dict

Генерирует данные компании.

```python
from utils.mimesis_gen import generate_company

company = generate_company('ru')
# {
#     'name': 'ООО "Рога и Копыта"',
#     'type': 'LLC',
#     'address': '...',
#     'phone': '...',
#     'email': '...',
#     'website': '...'
# }
```

#### generate_internet() -> dict

Генерирует интернет-данные.

```python
from utils.mimesis_gen import generate_internet

data = generate_internet()
# {
#     'email': 'user@example.com',
#     'ip_v4': '192.168.1.1',
#     'ip_v6': '2001:0db8:...',
#     'mac': '00:1B:44:11:3A:B7',
#     'user_agent': 'Mozilla/5.0...',
#     'password': '...'
# }
```

#### generate_crypto() -> dict

Генерирует криптографические данные.

```python
from utils.mimesis_gen import generate_crypto

crypto = generate_crypto()
# {
#     'uuid': 'a1b2c3d4-...',
#     'token': 'eyJhbGciOiJIUzI1NiIs...',
#     'api_key': 'sk_live_...',
#     'bitcoin': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
#     'ethereum': '0x742d35Cc6634C0532925a3b844Bc9e7595f...',
#     'mnemonic': 'abandon ability able about above absent...'
# }
```

#### generate_full_profile(locale: str = 'ru') -> dict

Генерирует полный профиль (всё вместе).

```python
from utils.mimesis_gen import generate_full_profile

profile = generate_full_profile('ru')
```

### Поддерживаемые локали

| Код | Язык |
|-----|------|
| `ru` | Русский |
| `en` | English |
| `uk` | Українська |

### Поддерживаемые страны (адреса)

`US`, `GB`, `DE`, `FR`, `RU`, `UA`, `PL`, `ES`, `IT`

### Поддерживаемые типы карт

`visa`, `mastercard`, `amex`, `discover`

---

## CryptoPay Webhook

**Файл:** `webhook_cryptopay.py`

Обработка платежей через CryptoPay.

### Класс CryptoPayWebhook

```python
from webhook_cryptopay import CryptoPayWebhook, start_webhook

webhook = CryptoPayWebhook(token=CRYPTO_BOT_TOKEN, sub_manager=sub_manager)
```

### Методы

#### verify_signature(body: bytes, signature: str) -> bool

Проверяет подпись webhook запроса.

```python
is_valid = webhook.verify_signature(body, signature)
```

#### handle_webhook(request) -> web.Response

Обрабатывает входящий webhook.

```python
response = await webhook.handle_webhook(request)
```

### Запуск webhook сервера

```python
await start_webhook(sub_manager)
# Запускает сервер на порту 8443
```

### Настройка в CryptoPay

1. Откройте @CryptoBot
2. Перейдите в настройки приложения
3. Укажите Webhook URL: `https://your-domain.com/webhook/cryptopay`

### Nginx конфигурация

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location /webhook/cryptopay {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Интеграция в bot.py

### Инициализация модулей

```python
from utils.subscription_manager import SubscriptionManager
from utils.rate_limiter import RateLimiter, rate_limit
from utils.error_monitor import ErrorMonitor, handle_errors
from utils.database import Database

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Инициализация
    db = Database(db_path='data/bot.db')
    sub_manager = SubscriptionManager(data_dir='data')
    rate_limiter = RateLimiter()
    error_monitor = ErrorMonitor(
        admin_ids=[ADMIN_ID],
        log_dir='logs'
    )
    
    # Сохранение в bot_data
    app.bot_data['db'] = db
    app.bot_data['sub_manager'] = sub_manager
    app.bot_data['rate_limiter'] = rate_limiter
    app.bot_data['error_monitor'] = error_monitor
```

### Использование декораторов

```python
@handle_errors(error_monitor)
@rate_limit(sub_manager)
async def generate_handler(update, context):
    user_id = update.effective_user.id
    sub_manager = context.bot_data['sub_manager']
    
    # Проверка лимитов
    can_gen, reason = sub_manager.can_generate(user_id)
    if not can_gen:
        await update.message.reply_text(reason)
        return
    
    # Генерация
    result = generate_person('ru')
    
    # Увеличение счётчика
    sub_manager.increment_usage(user_id)
    
    await update.message.reply_text(format_result(result))
```

### Daily cleanup job

```python
from telegram.ext import JobQueue
import datetime

async def daily_cleanup(context):
    sub_manager = context.bot_data['sub_manager']
    sub_manager.cleanup_old_usage()

job_queue = app.job_queue
job_queue.run_daily(daily_cleanup, time=datetime.time(hour=2, minute=0))
```

---

## Примеры использования

### Проверка подписки перед генерацией

```python
async def generate_card_handler(update, context):
    user_id = update.effective_user.id
    sub_manager = context.bot_data['sub_manager']
    
    can, reason = sub_manager.can_generate(user_id)
    if not can:
        await update.callback_query.answer(reason, show_alert=True)
        return
    
    card = generate_card('visa')
    sub_manager.increment_usage(user_id)
    
    text = f"💳 *Карта Visa*\n\n"
    text += f"Номер: `{card['number']}`\n"
    text += f"CVV: `{card['cvv']}`\n"
    text += f"Срок: `{card['expiry']}`\n"
    text += f"Владелец: `{card['holder']}`"
    
    await update.callback_query.message.edit_text(text, parse_mode='Markdown')
```

### Обработка оплаты

```python
async def process_payment(user_id: int, plan: str, invoice_id: str):
    sub_manager = context.bot_data['sub_manager']
    
    sub_manager.upgrade_subscription(user_id, plan, invoice_id)
    
    await bot.send_message(
        user_id,
        f"✅ Подписка {plan.upper()} активирована!\n"
        f"Спасибо за покупку!"
    )
```

### Админ команда статистики ошибок

```python
async def error_stats_cmd(update, context):
    if update.effective_user.id not in [ADMIN_ID]:
        return
    
    error_monitor = context.bot_data['error_monitor']
    stats = error_monitor.get_stats()
    
    await update.message.reply_text(stats, parse_mode='Markdown')
```
