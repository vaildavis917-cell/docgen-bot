#!/bin/bash
# Установка автоперезапуска бота в 2:00 по Киеву
# Запустите: chmod +x setup_cron.sh && ./setup_cron.sh

BOT_DIR="$HOME/docgen-bot"

# Делаем скрипт исполняемым
chmod +x "$BOT_DIR/restart_bot.sh"

# Устанавливаем таймзону Киева
export TZ='Europe/Kyiv'

# Добавляем задачу в cron (2:00 по Киеву)
# Cron использует серверное время, поэтому конвертируем
# Киев = UTC+2 (зимой) или UTC+3 (летом)
# 2:00 Киев = 0:00 UTC (зимой) или 23:00 UTC-1 (летом)

# Универсальный способ - используем TZ в cron
CRON_JOB="0 2 * * * TZ='Europe/Kyiv' $BOT_DIR/restart_bot.sh"

# Проверяем, есть ли уже такая задача
(crontab -l 2>/dev/null | grep -v "restart_bot.sh"; echo "$CRON_JOB") | crontab -

echo "✅ Cron задача установлена!"
echo "Бот будет перезапускаться каждый день в 2:00 по Киеву"
echo ""
echo "Проверить: crontab -l"
echo "Удалить: crontab -e (и удалить строку с restart_bot.sh)"
