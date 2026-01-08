# 🚀 Инструкция по деплою DocGen Bot

## Требования
- Ubuntu 20.04+ / Debian 11+
- Python 3.10+
- FFmpeg (для обработки видео)
- 1GB RAM минимум

---

## 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# Создание пользователя (опционально)
sudo useradd -m -s /bin/bash botuser
sudo su - botuser
```

---

## 2. Загрузка бота

### Вариант A: Через GitHub
```bash
cd ~
git clone https://github.com/vaildavis917-cell/docgen-bot.git
cd docgen-bot
```

### Вариант B: Через архив
```bash
cd ~
# Загрузите архив docgen_bot.zip на сервер через SCP/SFTP
unzip docgen_bot.zip
cd docgen_bot
```

---

## 3. Настройка окружения

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

---

## 4. Конфигурация

Создайте файл `.env` с вашими данными:

```bash
nano .env
```

Содержимое `.env`:
```env
BOT_TOKEN=ваш_токен_бота
CRYPTO_BOT_TOKEN=ваш_токен_cryptopay
ADMIN_IDS=8349575599
ADMIN_OPERATOR_ID=7080468696
```

---

## 5. Тестовый запуск

```bash
source venv/bin/activate
python3 bot.py
```

Если бот запустился без ошибок — переходите к настройке systemd.

---

## 6. Настройка автозапуска (systemd)

### Создание сервиса:
```bash
sudo nano /etc/systemd/system/docgen-bot.service
```

Содержимое:
```ini
[Unit]
Description=DocGen Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/docgen_bot
ExecStart=/home/ubuntu/docgen_bot/venv/bin/python3 bot.py
Restart=always
RestartSec=10
StandardOutput=append:/home/ubuntu/docgen_bot/bot.log
StandardError=append:/home/ubuntu/docgen_bot/bot.log

[Install]
WantedBy=multi-user.target
```

> ⚠️ Замените `ubuntu` на имя вашего пользователя и путь к проекту!

### Активация сервиса:
```bash
sudo systemctl daemon-reload
sudo systemctl enable docgen-bot
sudo systemctl start docgen-bot
```

### Проверка статуса:
```bash
sudo systemctl status docgen-bot
```

---

## 7. Полезные команды

```bash
# Просмотр логов
tail -f /home/ubuntu/docgen_bot/bot.log

# Перезапуск бота
sudo systemctl restart docgen-bot

# Остановка бота
sudo systemctl stop docgen-bot

# Просмотр логов systemd
sudo journalctl -u docgen-bot -f
```

---

## 8. Обновление бота

```bash
cd ~/docgen_bot
git pull origin main
sudo systemctl restart docgen-bot
```

---

## Структура файлов

```
docgen_bot/
├── bot.py              # Главный файл бота
├── handlers/           # Обработчики команд
│   ├── admin_handler.py
│   ├── admin_panel.py
│   └── ...
├── utils/              # Утилиты
│   ├── subscription.py
│   └── ...
├── locales/            # Локализация (RU/EN/UA)
├── data/               # Данные (users.json, whitelist.json)
├── .env                # Конфигурация (НЕ ЗАГРУЖАТЬ В GIT!)
├── requirements.txt    # Зависимости Python
└── DEPLOY.md           # Эта инструкция
```

---

## Безопасность

- ⚠️ **Никогда не загружайте `.env` в публичные репозитории!**
- Используйте файрвол: `sudo ufw allow ssh && sudo ufw enable`
- Регулярно обновляйте систему: `sudo apt update && sudo apt upgrade`

---

## Поддержка

Репозиторий: https://github.com/vaildavis917-cell/docgen-bot
