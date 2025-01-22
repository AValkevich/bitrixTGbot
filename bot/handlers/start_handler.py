# start_handler.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.database import Database
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StartHandler:
    # Состояние для ожидания ввода user_id
    GET_USER_ID = 1

    def __init__(self, db: Database):
        self.db = db

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает команду /start.
        """
        chat_id = update.message.chat_id
        logger.info(f"Команда /start вызвана для chat_id: {chat_id}")

        # Проверяем, сохранен ли user_id
        user_id = self.db.get_user_id(chat_id)
        if user_id:
            await update.message.reply_text(
                f"Ваш сохраненный user_id: {user_id}. Используйте следующие команды:\n"
                "/createtask - Создать новую задачу\n"
                "/addcomment - Добавить комментарий к задаче"
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text("Привет! Пожалуйста, введите ваш user_id:")
            return self.GET_USER_ID

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает ввод user_id после команды /start.
        """
        chat_id = update.message.chat_id
        text = update.message.text
        logger.info(f"Получено сообщение: {text} от chat_id: {chat_id}")

        # Сохраняем user_id в базу данных
        self.db.save_user_id(chat_id, text)
        await update.message.reply_text(
            f"Ваш user_id {text} сохранен. Теперь вы можете использовать следующие команды:\n"
            "/createtask - Создать новую задачу\n"
            "/addcomment - Добавить комментарий к задаче"
        )
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Отменяет процесс ввода user_id.
        """
        await update.message.reply_text("Ввод user_id отменен.")
        return ConversationHandler.END