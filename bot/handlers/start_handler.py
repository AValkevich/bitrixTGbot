from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from bot.database import Database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StartHandler:
    GET_BITRIX_ID, CHANGE_BITRIX_ID = range(2)

    def __init__(self, db: Database):
        self.db = db

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id

        bitrix_id = self.db.get_bitrix_id(chat_id)
        if bitrix_id:
            await update.message.reply_text(
                f"Ваш текущий Bitrix24 ID: {bitrix_id}. Используйте меню ниже для выбора действия:",
                reply_markup=self.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text("Привет! Пожалуйста, введите ваш Bitrix24 ID:")
            return self.GET_BITRIX_ID

    def get_main_menu_keyboard(self):
        keyboard = [
            [KeyboardButton("Создать задачу")],
            [KeyboardButton("Добавить комментарий")],
            [KeyboardButton("Изменить Bitrix24 ID")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    async def handle_bitrix_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        bitrix_id = update.message.text
        self.db.save_bitrix_id(chat_id, bitrix_id)
        await update.message.reply_text(
            f"Ваш Bitrix24 ID {bitrix_id} сохранен. Используйте меню ниже для выбора действия:",
            reply_markup=self.get_main_menu_keyboard()
        )
        return ConversationHandler.END

    async def handle_change_bitrix_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        await update.message.reply_text("Введите новый Bitrix24 ID:")
        return self.CHANGE_BITRIX_ID

    async def handle_new_bitrix_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.message.chat_id
        new_bitrix_id = update.message.text
        self.db.save_bitrix_id(chat_id, new_bitrix_id)
        await update.message.reply_text(
            f"Ваш Bitrix24 ID изменен на {new_bitrix_id}. Используйте меню ниже для выбора действия:",
            reply_markup=self.get_main_menu_keyboard()
        )
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Ввод данных отменен.")
        return ConversationHandler.END