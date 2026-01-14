#!/bin/bash

# ============================================
# DocGen Bot - Скрипт установки зависимостей
# ============================================

set -e

echo "🚀 DocGen Bot - Установка зависимостей"
echo "========================================"

# Определяем директорию скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Рабочая директория: $SCRIPT_DIR"

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Устанавливаем..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

echo "✅ Python: $(python3 --version)"

# Проверяем pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip не найден. Устанавливаем..."
    sudo apt install -y python3-pip
fi

# Проверяем ffmpeg (для видео)
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Устанавливаем ffmpeg..."
    sudo apt update
    sudo apt install -y ffmpeg
fi

echo "✅ FFmpeg: $(ffmpeg -version 2>&1 | head -n1)"

# Устанавливаем зависимости Python
echo ""
echo "📦 Устанавливаем Python зависимости..."
echo "--------------------------------------"

# Пробуем разные способы установки
if sudo pip3 install -r requirements.txt --break-system-packages 2>/dev/null; then
    echo "✅ Зависимости установлены (pip3 + break-system-packages)"
elif sudo pip install -r requirements.txt --break-system-packages 2>/dev/null; then
    echo "✅ Зависимости установлены (pip + break-system-packages)"
elif pip3 install -r requirements.txt --user 2>/dev/null; then
    echo "✅ Зависимости установлены (pip3 --user)"
elif pip install -r requirements.txt --user 2>/dev/null; then
    echo "✅ Зависимости установлены (pip --user)"
else
    echo "⚠️ Пробуем через venv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Зависимости установлены (venv)"
    echo "⚠️ Не забудь активировать venv перед запуском: source venv/bin/activate"
fi

# Проверяем .env файл
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo ""
        echo "⚠️ Файл .env не найден!"
        echo "   Скопируй .env.example в .env и заполни токены:"
        echo "   cp .env.example .env"
        echo "   nano .env"
    fi
fi

# Делаем скрипты исполняемыми
chmod +x start_bot.sh 2>/dev/null || true
chmod +x restart_bot.sh 2>/dev/null || true
chmod +x setup_cron.sh 2>/dev/null || true
chmod +x run_bot.sh 2>/dev/null || true

echo ""
echo "========================================"
echo "✅ Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Настрой .env файл с токенами"
echo "   2. Запусти бота: python3 bot.py"
echo "   или: ./start_bot.sh"
echo ""
