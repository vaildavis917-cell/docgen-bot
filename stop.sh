#!/bin/bash

# ============================================
# DocGen Bot - Остановка
# ./stop.sh
# ============================================

echo "🛑 Остановка DocGen Bot..."

if pgrep -f "python.*bot.py" > /dev/null; then
    pkill -f "python.*bot.py"
    sleep 2
    echo "✅ Бот остановлен"
else
    echo "⚠️ Бот не запущен"
fi
