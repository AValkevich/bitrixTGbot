# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from bot.handlers.start_handler import StartHandler
from bot.handlers.task_handler import TaskHandler
from bot.handlers.comment_handler import CommentHandler
from bot.database import Database
from services.bitrix24 import Bitrix24
from config.config import TOKEN, BITRIX_WEBHOOK_CREATE_TASK, BITRIX_WEBHOOK_ADD_COMMENT

class MyBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(self.token).build()
        self.db = Database()
        self.bitrix = Bitrix24(BITRIX_WEBHOOK_CREATE_TASK, BITRIX_WEBHOOK_ADD_COMMENT)

        # Инициализация обработчиков
        start_handler = StartHandler(self.db)
        task_handler = TaskHandler(self.db, self.bitrix)
        comment_handler = CommentHandler(self.db, self.bitrix)

        # Регистрация ConversationHandler для ввода user_id
        conv_handler_start = ConversationHandler(
            entry_points=[CommandHandler("start", start_handler.handle_start)],
            states={
                start_handler.GET_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_handler.handle_message)],
            },
            fallbacks=[CommandHandler("cancel", start_handler.cancel)],
        )
        self.application.add_handler(conv_handler_start)

        # Регистрация ConversationHandler для создания задачи
        conv_handler_task = ConversationHandler(
            entry_points=[CommandHandler("createtask", task_handler.start_create_task)],
            states={
                task_handler.GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_handler.get_title)],
                task_handler.GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_handler.get_description)],
                task_handler.GET_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_handler.get_deadline)],
            },
            fallbacks=[CommandHandler("cancel", task_handler.cancel_create_task)],
        )
        self.application.add_handler(conv_handler_task)

        # Регистрация ConversationHandler для добавления комментария
        conv_handler_comment = ConversationHandler(
            entry_points=[CommandHandler("addcomment", comment_handler.start_add_comment)],
            states={
                comment_handler.GET_TASK_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment_handler.get_task_id)],
                comment_handler.GET_COMMENT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment_handler.get_comment_text)],
            },
            fallbacks=[CommandHandler("cancel", comment_handler.cancel_add_comment)],
        )
        self.application.add_handler(conv_handler_comment)

    def run(self):
        """
        Запускает бота.
        """
        try:
            self.application.run_polling()
        finally:
            self.db.close()