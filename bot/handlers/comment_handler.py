from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from bot.database import Database
from services.bitrix24 import Bitrix24
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommentHandler:
    GET_TASK_ID, GET_COMMENT_TEXT = range(4, 6)

    def __init__(self, db: Database, bitrix: Bitrix24):
        self.db = db
        self.bitrix = bitrix
        self.task_data = {}

    async def start_add_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id

        bitrix_id = self.db.get_bitrix_id(chat_id)
        if not bitrix_id:
            await update.message.reply_text("Сначала введите ваш Bitrix24 ID через команду /start.")
            return ConversationHandler.END

        await update.message.reply_text("Введите ID задачи, к которой хотите добавить комментарий:")
        return self.GET_TASK_ID

    async def get_task_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        task_id = update.message.text
        self.task_data[chat_id] = {"task_id": task_id}
        await update.message.reply_text(
            "Введите текст комментария."
        )
        return self.GET_COMMENT_TEXT

    async def get_comment_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        comment_text = update.message.text
        task_id = int(self.task_data[chat_id]["task_id"])

        # Используем текущий Bitrix24 ID из базы данных
        bitrix_id = self.db.get_bitrix_id(chat_id)
        author_id = int(bitrix_id)

        result = self.bitrix.add_comment(task_id, comment_text, author_id)

        if result and result.get("result"):
            await update.message.reply_text("Комментарий успешно добавлен к задаче!")
        else:
            await update.message.reply_text("Ошибка при добавлении комментария. Проверьте данные.")

        del self.task_data[chat_id]
        return ConversationHandler.END

    async def cancel_add_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        if chat_id in self.task_data:
            del self.task_data[chat_id]
        await update.message.reply_text("Добавление комментария отменено.")
        return ConversationHandler.END