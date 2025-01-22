from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from bot.handlers.start_handler import StartHandler
from bot.handlers.task_handler import TaskHandler
from bot.handlers.comment_handler import CommentHandler
from bot.database import Database
from services.bitrix24 import Bitrix24
from config.config import TOKEN, BITRIX_WEBHOOK_CREATE_TASK, BITRIX_WEBHOOK_ADD_COMMENT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(self.token).build()
        self.db = Database()
        self.bitrix = Bitrix24(BITRIX_WEBHOOK_CREATE_TASK, BITRIX_WEBHOOK_ADD_COMMENT)

        start_handler = StartHandler(self.db)
        task_handler = TaskHandler(self.db, self.bitrix)
        comment_handler = CommentHandler(self.db, self.bitrix)

        # ConversationHandler для создания задачи
        conv_handler_task = ConversationHandler(
            entry_points=[
                CommandHandler("createtask", task_handler.start_create_task),
                MessageHandler(filters.Text("Создать задачу"), task_handler.start_create_task)
            ],
            states={
                task_handler.GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_handler.get_title)],
                task_handler.GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_handler.get_description)],
                task_handler.GET_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_handler.get_deadline)],
            },
            fallbacks=[CommandHandler("cancel", task_handler.cancel_create_task)],
        )
        self.application.add_handler(conv_handler_task)

        # ConversationHandler для добавления комментария
        conv_handler_comment = ConversationHandler(
            entry_points=[
                CommandHandler("addcomment", comment_handler.start_add_comment),
                MessageHandler(filters.Text("Добавить комментарий"), comment_handler.start_add_comment)
            ],
            states={
                comment_handler.GET_TASK_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment_handler.get_task_id)],
                comment_handler.GET_COMMENT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment_handler.get_comment_text)],
            },
            fallbacks=[CommandHandler("cancel", comment_handler.cancel_add_comment)],
        )
        self.application.add_handler(conv_handler_comment)

        # ConversationHandler для изменения Bitrix24 ID
        conv_handler_change_bitrix_id = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Text("Изменить Bitrix24 ID"), start_handler.handle_change_bitrix_id)
            ],
            states={
                start_handler.CHANGE_BITRIX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_handler.handle_new_bitrix_id)],
            },
            fallbacks=[CommandHandler("cancel", start_handler.cancel)],
        )
        self.application.add_handler(conv_handler_change_bitrix_id)

        # Обработчик для команды /start
        self.application.add_handler(CommandHandler("start", start_handler.handle_start))

    def run(self):
        try:
            logger.info("Бот запущен.")
            self.application.run_polling()
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
        finally:
            self.db.close()