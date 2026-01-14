#!/bin/bash

# ============================================
# DocGen Bot v2.2.0 - Полная установка и запуск
# Одна команда для всего: ./setup.sh
# ============================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║     DocGen Bot v2.2.0 Setup            ║"
echo "║     Полная установка и запуск          ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Определяем директорию скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}📁 Рабочая директория: $SCRIPT_DIR${NC}"

# === 1. Создание папок ===
echo ""
echo -e "${BLUE}[1/7] Создание папок...${NC}"
mkdir -p utils logs data templates locales handlers
echo -e "${GREEN}✅ Папки созданы${NC}"

# === 2. Проверка Python ===
echo ""
echo -e "${BLUE}[2/7] Проверка Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️ Python3 не найден. Устанавливаем...${NC}"
    sudo apt update
    sudo apt install -y python3 python3-pip
fi
echo -e "${GREEN}✅ Python: $(python3 --version)${NC}"

# === 3. Проверка pip ===
echo ""
echo -e "${BLUE}[3/7] Проверка pip...${NC}"
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo -e "${YELLOW}⚠️ pip не найден. Устанавливаем...${NC}"
    sudo apt install -y python3-pip
fi
echo -e "${GREEN}✅ pip установлен${NC}"

# === 4. Установка ffmpeg ===
echo ""
echo -e "${BLUE}[4/7] Проверка ffmpeg...${NC}"
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️ ffmpeg не найден. Устанавливаем...${NC}"
    sudo apt update
    sudo apt install -y ffmpeg
fi
echo -e "${GREEN}✅ FFmpeg: $(ffmpeg -version 2>&1 | head -n1 | cut -d' ' -f1-3)${NC}"

# === 5. Установка зависимостей Python ===
echo ""
echo -e "${BLUE}[5/7] Установка Python зависимостей...${NC}"

# Пробуем разные способы установки
if sudo pip3 install -r requirements.txt --break-system-packages 2>/dev/null; then
    echo -e "${GREEN}✅ Зависимости установлены (system-wide)${NC}"
elif pip3 install -r requirements.txt --break-system-packages 2>/dev/null; then
    echo -e "${GREEN}✅ Зависимости установлены (user)${NC}"
elif pip3 install -r requirements.txt 2>/dev/null; then
    echo -e "${GREEN}✅ Зависимости установлены${NC}"
else
    echo -e "${YELLOW}⚠️ Создаём venv...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Зависимости установлены (venv)${NC}"
    echo -e "${YELLOW}⚠️ Не забудь активировать venv: source venv/bin/activate${NC}"
fi

# === 6. Проверка .env ===
echo ""
echo -e "${BLUE}[6/7] Проверка конфигурации...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠️ Файл .env не найден!${NC}"
        echo -e "${YELLOW}   Скопируй .env.example в .env и заполни токены:${NC}"
        echo -e "${YELLOW}   cp .env.example .env && nano .env${NC}"
    else
        echo -e "${YELLOW}⚠️ Создаём .env.example...${NC}"
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

# Webhook (опционально)
WEBHOOK_PORT=8443
EOF
        echo -e "${YELLOW}   Создай .env файл: cp .env.example .env && nano .env${NC}"
    fi
else
    echo -e "${GREEN}✅ .env файл найден${NC}"
fi

# === 7. Делаем скрипты исполняемыми ===
echo ""
echo -e "${BLUE}[7/7] Настройка скриптов...${NC}"
chmod +x *.sh 2>/dev/null || true
echo -e "${GREEN}✅ Скрипты настроены${NC}"

# === Итог ===
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════╗"
echo "║     ✅ Установка завершена!            ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Проверяем .env перед запуском
if [ -f ".env" ]; then
    echo -e "${BLUE}🚀 Запускаем бота...${NC}"
    echo ""
    
    # Убиваем предыдущий процесс если есть
    pkill -f "python.*bot.py" 2>/dev/null || true
    sleep 1
    
    # Запускаем
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python3 bot.py
else
    echo -e "${YELLOW}📋 Следующие шаги:${NC}"
    echo -e "   1. Создай .env файл: ${BLUE}cp .env.example .env${NC}"
    echo -e "   2. Заполни токены: ${BLUE}nano .env${NC}"
    echo -e "   3. Запусти бота: ${BLUE}python3 bot.py${NC}"
    echo ""
fi
