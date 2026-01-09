#!/bin/bash
# Скрипт автоперезапуска бота
# Запускается cron в 2:00 по Киеву (Europe/Kyiv)

BOT_DIR="$HOME/docgen-bot"
LOG_FILE="$BOT_DIR/restart.log"

echo "[$(date)] Автоперезапуск бота..." >> "$LOG_FILE"

# Останавливаем бота
pkill -f "python3 bot.py" 2>/dev/null
sleep 2

# Переходим в директорию бота
cd "$BOT_DIR"

# Обновляем из git (опционально)
# git pull >> "$LOG_FILE" 2>&1

# Запускаем бота в фоне
source venv/bin/activate 2>/dev/null || true
nohup python3 bot.py >> "$BOT_DIR/bot.log" 2>&1 &

echo "[$(date)] Бот перезапущен. PID: $!" >> "$LOG_FILE"
