#!/bin/bash

# ============================================
# DocGen Bot - Статус
# ./status.sh
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📊 DocGen Bot Status"
echo "===================="

if pgrep -f "python.*bot.py" > /dev/null; then
    PID=$(pgrep -f "python.*bot.py")
    echo "✅ Статус: ЗАПУЩЕН"
    echo "📋 PID: $PID"
    echo ""
    echo "📈 Использование ресурсов:"
    ps -p $PID -o pid,ppid,%cpu,%mem,etime,cmd --no-headers 2>/dev/null || echo "   Не удалось получить"
    echo ""
    echo "📄 Последние логи:"
    tail -5 $SCRIPT_DIR/logs/bot.log 2>/dev/null || echo "   Логи не найдены"
else
    echo "❌ Статус: ОСТАНОВЛЕН"
fi

echo ""
echo "📁 Размер данных:"
du -sh $SCRIPT_DIR/data 2>/dev/null || echo "   Папка data не найдена"
du -sh $SCRIPT_DIR/logs 2>/dev/null || echo "   Папка logs не найдена"
