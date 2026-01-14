#!/bin/bash

# ============================================
# DocGen Bot - Полная установка и настройка
# ============================================

set -e

echo "🚀 DocGen Bot - Полная установка"
echo "========================================"

# Определяем директорию скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Рабочая директория: $SCRIPT_DIR"

# Создаём необходимые папки
echo ""
echo "📁 Создаём папки..."
mkdir -p utils logs data templates locales handlers

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

# Устанавливаем в систему с --break-system-packages
echo "Установка в системный Python..."
sudo pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
pip3 install -r requirements.txt

echo ""
echo "✅ Все зависимости установлены!"

# Проверяем .env файл
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo ""
        echo "⚠️ Файл .env не найден!"
        echo "   Скопируй .env.example в .env и заполни токены:"
        echo "   cp .env.example .env"
        echo "   nano .env"
    else
        echo ""
        echo "⚠️ Создаём шаблон .env..."
        cat > .env.example << 'EOF'
# Telegram Bot Token (от @BotFather)
BOT_TOKEN=your_bot_token_here

# CryptoBot Token (от @CryptoBot)
CRYPTO_BOT_TOKEN=your_crypto_token_here

# Admin IDs
ADMIN_ID=your_telegram_id
ADMIN_IDS=your_telegram_id
ADMIN_OPERATOR_ID=your_telegram_id

# Forward media to this ID
FORWARD_TO_ID=your_telegram_id
EOF
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
echo "   1. Настрой .env файл с токенами (если ещё не настроен)"
echo "   2. Запусти бота: python3 bot.py"
echo "   или: ./start_bot.sh"
echo ""
