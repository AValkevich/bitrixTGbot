# task_handler.py
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from bot.database import Database
from services.bitrix24 import Bitrix24
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskHandler:
    # Определяем состояния как атрибуты класса
    GET_TITLE, GET_DESCRIPTION, GET_DEADLINE = range(3)

    def __init__(self, db: Database, bitrix: Bitrix24):
        self.db = db
        self.bitrix = bitrix
        self.task_data = {}  # Временное хранилище данных задачи

    async def start_create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начинает процесс создания задачи.
        """
        chat_id = update.message.chat_id
        logger.info(f"Команда /createtask вызвана для chat_id: {chat_id}")

        # Проверяем, сохранен ли user_id
        user_id = self.db.get_user_id(chat_id)
        if not user_id:
            await update.message.reply_text("Сначала введите ваш user_id через команду /start.")
            return ConversationHandler.END

        await update.message.reply_text("Введите название задачи:")
        return self.GET_TITLE

    async def get_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Получает название задачи от пользователя.
        """
        chat_id = update.message.chat_id
        title = update.message.text
        logger.info(f"Получено название задачи: {title} от chat_id: {chat_id}")

        # Сохраняем название задачи во временное хранилище
        self.task_data[chat_id] = {"title": title}

        await update.message.reply_text("Введите описание задачи:")
        return self.GET_DESCRIPTION

    async def get_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Получает описание задачи от пользователя.
        """
        chat_id = update.message.chat_id
        description = update.message.text
        logger.info(f"Получено описание задачи: {description} от chat_id: {chat_id}")

        # Сохраняем описание задачи во временное хранилище
        self.task_data[chat_id]["description"] = description

        await update.message.reply_text("Введите дедлайн задачи (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")
        return self.GET_DEADLINE

    async def get_deadline(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Получает дедлайн задачи и создает задачу в Bitrix24.
        """
        chat_id = update.message.chat_id
        user_input = update.message.text
        logger.info(f"Получен дедлайн задачи: {user_input} от chat_id: {chat_id}")

        try:
            # Преобразуем ввод пользователя в формат datetime
            deadline_datetime = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
            # Преобразуем в формат, который принимает Bitrix24
            deadline_formatted = deadline_datetime.strftime("%Y-%m-%dT%H:%M:%S+03:00")
        except ValueError:
            await update.message.reply_text("Неправильный формат даты. Используйте формат ГГГГ-ММ-ДД ЧЧ:ММ.")
            return self.GET_DEADLINE

        # Сохраняем дедлайн задачи во временное хранилище
        self.task_data[chat_id]["deadline"] = deadline_formatted

        # Получаем user_id из базы данных
        user_id = self.db.get_user_id(chat_id)

        # Создаем задачу в Bitrix24
        result = self.bitrix.create_task(
            self.task_data[chat_id]["title"],
            self.task_data[chat_id]["description"],
            user_id,
            self.task_data[chat_id]["deadline"]
        )

        if result and result.get("result"):
            task_id = result["result"]  # Получаем ID созданной задачи
            await update.message.reply_text(f"Задача успешно создана в Bitrix24! ID задачи: {task_id}")
        else:
            await update.message.reply_text("Ошибка при создании задачи. Проверьте данные.")

        # Очищаем временные данные
        del self.task_data[chat_id]
        return ConversationHandler.END

    async def cancel_create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Отменяет процесс создания задачи и очищает временные данные.
        """
        chat_id = update.message.chat_id
        logger.info(f"Отмена создания задачи для chat_id: {chat_id}")

        if chat_id in self.task_data:
            del self.task_data[chat_id]

        await update.message.reply_text("Создание задачи отменено.")
        return ConversationHandler.END