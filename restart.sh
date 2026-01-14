#!/bin/bash

# ============================================
# DocGen Bot - Перезапуск
# ./restart.sh
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Перезапуск DocGen Bot..."

# Останавливаем
$SCRIPT_DIR/stop.sh

# Запускаем
$SCRIPT_DIR/start.sh
