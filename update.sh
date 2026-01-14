#!/bin/bash

# ============================================
# DocGen Bot - Обновление
# ./update.sh
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Обновление DocGen Bot..."
echo ""

# 1. Бэкап данных
echo "📦 Создание бэкапа..."
BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp -r data $BACKUP_DIR/ 2>/dev/null || true
cp .env $BACKUP_DIR/ 2>/dev/null || true
echo "✅ Бэкап создан: $BACKUP_DIR"

# 2. Остановка бота
echo ""
echo "🛑 Остановка бота..."
$SCRIPT_DIR/stop.sh

# 3. Обновление кода
echo ""
echo "📥 Загрузка обновлений..."
git pull

# 4. Обновление зависимостей
echo ""
echo "📦 Обновление зависимостей..."
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt --upgrade
else
    sudo pip3 install -r requirements.txt --break-system-packages --upgrade 2>/dev/null || \
    pip3 install -r requirements.txt --upgrade
fi

# 5. Запуск
echo ""
echo "🚀 Запуск бота..."
$SCRIPT_DIR/start.sh

echo ""
echo "✅ Обновление завершено!"
