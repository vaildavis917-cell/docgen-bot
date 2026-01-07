#!/bin/bash

# Скрипт запуска DocGen Bot

cd /home/ubuntu/docgen_bot

# Убиваем предыдущий процесс если есть
pkill -f "python.*bot.py" 2>/dev/null

# Ждем завершения
sleep 1

# Запускаем бота
echo "🚀 Запуск DocGen Bot..."
nohup python3 bot.py > bot.log 2>&1 &

# Ждем запуска
sleep 3

# Проверяем
if pgrep -f "python.*bot.py" > /dev/null; then
    echo "✅ Бот успешно запущен!"
    echo "📋 PID: $(pgrep -f 'python.*bot.py')"
    echo "📄 Логи: /home/ubuntu/docgen_bot/bot.log"
else
    echo "❌ Ошибка запуска бота!"
    echo "Проверьте логи: cat /home/ubuntu/docgen_bot/bot.log"
fi
