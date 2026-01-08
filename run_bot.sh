#!/bin/bash
# Скрипт автоматического перезапуска бота

cd /home/ubuntu/docgen_bot

while true; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Запуск бота..."
    python3 bot.py
    
    EXIT_CODE=$?
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Бот остановлен с кодом: $EXIT_CODE"
    
    # Пауза перед перезапуском
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Перезапуск через 10 секунд..."
    sleep 10
done
