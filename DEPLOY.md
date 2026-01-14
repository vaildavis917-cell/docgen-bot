# 🚀 Deployment Guide v2.2.0

Руководство по развёртыванию DocGen Bot.

## Требования

- Ubuntu 20.04+ / Debian 11+
- Python 3.10+
- FFmpeg (для обработки видео)
- 1GB RAM минимум

## Архитектура

```
docgen-bot/
├── bot.py                      # Main bot
├── webhook_cryptopay.py        # Webhook server
├── utils/
│   ├── database.py             # SQLite
│   ├── subscription_manager.py # Подписки
│   ├── rate_limiter.py         # Rate limiting
│   └── error_monitor.py        # Мониторинг ошибок
├── data/
│   └── bot.db                  # SQLite database
└── logs/
    └── bot_YYYYMMDD.log        # Daily logs
```

---

## Быстрый деплой

```bash
# 1. Клонирование
git clone https://github.com/vaildavis917-cell/docgen-bot.git
cd docgen-bot

# 2. Полная установка одной командой
chmod +x setup.sh
./setup.sh
```

Скрипт `setup.sh` автоматически:
- Создаст все папки
- Проверит Python, pip, ffmpeg
- Установит зависимости
- Создаст `.env.example`
- Запустит бота (если `.env` настроен)

---

## Ручная установка

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3 python3-pip ffmpeg git
```

### 2. Загрузка бота

```bash
cd ~
git clone https://github.com/vaildavis917-cell/docgen-bot.git
cd docgen-bot
```

### 3. Установка Python зависимостей

```bash
# Для Python 3.12+
sudo pip install -r requirements.txt --break-system-packages

# Или через venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Конфигурация

```bash
cp .env.example .env
nano .env
```

Содержимое `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
CRYPTO_BOT_TOKEN=your_cryptobot_token
ADMIN_ID=your_telegram_id
ADMIN_IDS=your_telegram_id
ADMIN_OPERATOR_ID=your_telegram_id
FORWARD_TO_ID=id_for_media_forwarding
WEBHOOK_PORT=8443
```

### 5. Запуск

```bash
./start.sh
```

---

## Управление ботом

| Команда | Описание |
|---------|----------|
| `./setup.sh` | Полная установка + запуск |
| `./run.sh` | Запуск в консоли |
| `./start.sh` | Запуск в фоне |
| `./stop.sh` | Остановка |
| `./restart.sh` | Перезапуск |
| `./status.sh` | Статус и логи |
| `./update.sh` | Обновление (git pull + restart) |

---

## Production Checklist

| Задача | Статус |
|--------|--------|
| Database backup настроен | ☐ |
| Nginx reverse proxy для webhook | ☐ |
| SSL сертификат установлен | ☐ |
| Systemd service настроен | ☐ |
| Health check endpoint работает | ☐ |
| Error alerts в Telegram настроены | ☐ |
| Rate limiting протестирован | ☐ |
| CryptoPay webhook зарегистрирован | ☐ |

---

## Systemd Service

Создайте файл `/etc/systemd/system/docgen-bot.service`:

```ini
[Unit]
Description=DocGen Telegram Bot v2.2
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/docgen-bot
ExecStart=/usr/bin/python3 /root/docgen-bot/bot.py
Restart=always
RestartSec=10

# Graceful shutdown timeout
TimeoutStopSec=30
KillMode=mixed

# Logs
StandardOutput=append:/var/log/docgen-bot/stdout.log
StandardError=append:/var/log/docgen-bot/stderr.log

[Install]
WantedBy=multi-user.target
```

Активация:

```bash
sudo mkdir -p /var/log/docgen-bot
sudo systemctl daemon-reload
sudo systemctl enable docgen-bot
sudo systemctl start docgen-bot
sudo systemctl status docgen-bot
```

---

## Nginx + SSL (для Webhook)

### Установка Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Конфигурация Nginx

Файл `/etc/nginx/sites-available/docgen-bot`:

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
    
    location /health {
        proxy_pass http://127.0.0.1:8443;
    }
}
```

Активация:

```bash
sudo ln -s /etc/nginx/sites-available/docgen-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Database Backup

### Автоматический бэкап (cron)

```bash
crontab -e

# Добавить строку (бэкап каждые 6 часов)
0 */6 * * * cp /root/docgen-bot/data/bot.db /root/docgen-bot/backups/bot_$(date +\%Y\%m\%d_\%H\%M).db
```

### Ручной бэкап

```bash
cp data/bot.db backups/bot_$(date +%Y%m%d_%H%M%S).db
```

---

## Мониторинг

### Health Check

```bash
curl http://your-server:8443/health
```

### Логи

```bash
# Real-time логи systemd
journalctl -u docgen-bot -f

# Логи бота
tail -f logs/bot_$(date +%Y%m%d).log

# Только ошибки
grep ERROR logs/bot_*.log
```

### UptimeRobot

Настройте мониторинг на https://uptimerobot.com:
- URL: `https://your-domain.com/health`
- Interval: 5 минут

---

## Log Rotation

Файл `/etc/logrotate.d/docgen-bot`:

```
/root/docgen-bot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
}
```

---

## Обновление

```bash
cd /root/docgen-bot
./update.sh
```

Скрипт автоматически:
- Создаст бэкап данных
- Остановит бота
- Загрузит обновления (git pull)
- Обновит зависимости
- Запустит бота

---

## Rollback

```bash
# 1. Остановка
systemctl stop docgen-bot

# 2. Откат кода
git checkout v2.1.0

# 3. Восстановление данных
rm -rf data/
cp -r backups/data_YYYYMMDD data/

# 4. Запуск
systemctl start docgen-bot
```

---

## Troubleshooting

### Бот не запускается

```bash
cat logs/bot.log          # Проверить логи
cat .env                   # Проверить конфигурацию
pip list | grep telegram   # Проверить зависимости
```

### Database locked

Перезапустите бота: `./restart.sh`

### Webhook не работает

```bash
sudo nginx -t                    # Проверить nginx
netstat -tlnp | grep 8443        # Проверить порт
curl -v https://your-domain.com/health  # Проверить SSL
```

### Высокое потребление памяти

```bash
ps aux | grep bot.py    # Проверить память
./restart.sh            # Перезапустить если > 500MB
```

---

## Безопасность

- ⚠️ **Никогда не загружайте `.env` в публичные репозитории!**
- Используйте файрвол: `sudo ufw allow ssh && sudo ufw enable`
- Регулярно обновляйте систему: `sudo apt update && sudo apt upgrade`

---

## Поддержка

Репозиторий: https://github.com/vaildavis917-cell/docgen-bot
