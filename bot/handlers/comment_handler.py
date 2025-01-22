# comment_handler.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from bot.database import Database
from services.bitrix24 import Bitrix24
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommentHandler:
    # Определяем состояния как атрибуты класса
    GET_TASK_ID, GET_COMMENT_TEXT = range(4, 6)

    def __init__(self, db: Database, bitrix: Bitrix24):
        self.db = db
        self.bitrix = bitrix
        self.task_data = {}  # Временное хранилище данных задачи

    async def start_add_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начинает процесс добавления комментария.
        """
        chat_id = update.message.chat_id
        logger.info("Команда /addcomment вызвана")

        # Проверяем, сохранен ли user_id
        user_id = self.db.get_user_id(chat_id)
        if not user_id:
            await update.message.reply_text("Сначала введите ваш user_id через команду /start.")
            return ConversationHandler.END

        await update.message.reply_text("Введите ID задачи, к которой хотите добавить комментарий:")
        logger.info(f"Метод start_add_comment возвращает состояние: {self.GET_TASK_ID}")
        return self.GET_TASK_ID

    async def get_task_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        logger.info("Метод get_task_id вызван")
        """
        Получает ID задачи от пользователя.
        """
        chat_id = update.message.chat_id
        task_id = update.message.text
        logger.info(f"Получен ID задачи: {task_id} от chat_id: {chat_id}")

        # Сохраняем ID задачи во временное хранилище
        self.task_data[chat_id] = {"task_id": task_id}

        # Запрашиваем текст комментария
        await update.message.reply_text(
            "Введите текст комментария.\n"
            "Если хотите указать новый user_id, начните комментарий с !id.\n"
            "Пример: !12345 Это комментарий."
        )

        # Логируем возвращаемое состояние
        logger.info(f"Метод get_task_id возвращает состояние: {self.GET_COMMENT_TEXT}")
        return self.GET_COMMENT_TEXT

    async def get_comment_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Получает текст комментария и отправляет его в Bitrix24.
        """
        chat_id = update.message.chat_id
        comment_text = update.message.text
        logger.info(f"Получен текст комментария: {comment_text} от chat_id: {chat_id}")

        # Получаем ID задачи из временного хранилища
        task_id = int(self.task_data[chat_id]["task_id"])

        # Проверяем, начинается ли комментарий с !
        if comment_text.startswith("!"):
            try:
                # Извлекаем новый user_id из текста комментария
                new_user_id = int(comment_text.split()[0][1:])  # Убираем ! и преобразуем в число
                author_id = new_user_id
                comment_text = " ".join(comment_text.split()[1:])  # Убираем !id из текста комментария
            except (IndexError, ValueError):
                await update.message.reply_text("Неправильный формат. Используйте: !id текст_комментария.")
                return self.GET_COMMENT_TEXT
        else:
            # Используем сохраненный user_id
            user_id = self.db.get_user_id(chat_id)
            author_id = int(user_id)

        # Добавляем комментарий к задаче
        result = self.bitrix.add_comment(task_id, comment_text, author_id)

        if result and result.get("result"):
            await update.message.reply_text("Комментарий успешно добавлен к задаче!")
        else:
            await update.message.reply_text("Ошибка при добавлении комментария. Проверьте данные.")

        # Очищаем временные данные
        del self.task_data[chat_id]
        return ConversationHandler.END

    async def cancel_add_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Отменяет процесс добавления комментария и очищает временные данные.
        """
        chat_id = update.message.chat_id
        logger.info(f"Отмена добавления комментария для chat_id: {chat_id}")

        if chat_id in self.task_data:
            del self.task_data[chat_id]

        await update.message.reply_text("Добавление комментария отменено.")
        return ConversationHandler.END