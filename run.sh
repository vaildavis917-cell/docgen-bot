#!/bin/bash

# ============================================
# DocGen Bot - Быстрый запуск
# ./run.sh
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

echo "🚀 Запуск DocGen Bot..."
python3 bot.py
