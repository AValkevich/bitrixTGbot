# config.py
import os

# Получаем данные из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BITRIX_WEBHOOK_CREATE_TASK = os.getenv('BITRIX_WEBHOOK_CREATE_TASK')
BITRIX_WEBHOOK_ADD_COMMENT = os.getenv('BITRIX_WEBHOOK_ADD_COMMENT')