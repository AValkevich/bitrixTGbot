from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from bot.database import Database
from services.bitrix24 import Bitrix24
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskHandler:
    GET_TITLE, GET_DESCRIPTION, GET_DEADLINE = range(3)

    def __init__(self, db: Database, bitrix: Bitrix24):
        self.db = db
        self.bitrix = bitrix
        self.task_data = {}

    async def start_create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id

        bitrix_id = self.db.get_bitrix_id(chat_id)
        if not bitrix_id:
            await update.message.reply_text("Сначала введите ваш Bitrix24 ID через команду /start.")
            return ConversationHandler.END

        await update.message.reply_text("Введите название задачи:")
        return self.GET_TITLE

    async def get_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        title = update.message.text
        self.task_data[chat_id] = {"title": title}
        await update.message.reply_text("Введите описание задачи:")
        return self.GET_DESCRIPTION

    async def get_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        description = update.message.text
        self.task_data[chat_id]["description"] = description
        await update.message.reply_text("Введите дедлайн задачи (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")
        return self.GET_DEADLINE

    async def get_deadline(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        user_input = update.message.text

        try:
            deadline_datetime = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
            deadline_formatted = deadline_datetime.strftime("%Y-%m-%dT%H:%M:%S+03:00")
        except ValueError:
            await update.message.reply_text("Неправильный формат даты. Используйте формат ГГГГ-ММ-ДД ЧЧ:ММ.")
            return self.GET_DEADLINE

        self.task_data[chat_id]["deadline"] = deadline_formatted
        bitrix_id = self.db.get_bitrix_id(chat_id)

        result = self.bitrix.create_task(
            self.task_data[chat_id]["title"],
            self.task_data[chat_id]["description"],
            bitrix_id,
            self.task_data[chat_id]["deadline"]
        )

        if result and result.get("result"):
            task_id = result["result"]
            await update.message.reply_text(f"Задача успешно создана в Bitrix24! ID задачи: {task_id}")
        else:
            await update.message.reply_text("Ошибка при создании задачи. Проверьте данные.")

        del self.task_data[chat_id]
        return ConversationHandler.END

    async def cancel_create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        if chat_id in self.task_data:
            del self.task_data[chat_id]
        await update.message.reply_text("Создание задачи отменено.")
        return ConversationHandler.END