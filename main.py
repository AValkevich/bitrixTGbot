from bot.bot import MyBot
from config.config import TOKEN

if __name__ == "__main__":
    bot = MyBot(TOKEN)
    bot.run()