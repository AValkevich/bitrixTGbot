from bot.bot import MyBot
from config.config import TOKEN
import logging

# Отключаем логирование httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

if __name__ == "__main__":
    bot = MyBot(TOKEN)
    bot.run()