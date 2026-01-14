#!/bin/bash

# ============================================
# DocGen Bot - Запуск в фоне
# ./start.sh
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Убиваем предыдущий процесс
pkill -f "python.*bot.py" 2>/dev/null || true
sleep 1

# Активируем venv если есть
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Проверяем .env
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "   Создай его: cp .env.example .env && nano .env"
    exit 1
fi

# Запускаем в фоне
echo "🚀 Запуск DocGen Bot в фоновом режиме..."
nohup python3 bot.py > logs/bot.log 2>&1 &

sleep 3

# Проверяем запуск
if pgrep -f "python.*bot.py" > /dev/null; then
    PID=$(pgrep -f "python.*bot.py")
    echo "✅ Бот запущен!"
    echo "📋 PID: $PID"
    echo "📄 Логи: tail -f $SCRIPT_DIR/logs/bot.log"
else
    echo "❌ Ошибка запуска!"
    echo "   Проверь логи: cat $SCRIPT_DIR/logs/bot.log"
fi
