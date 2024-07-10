from dependencies import Bot, Dispatcher
from api import API_TOKEN

# База данных
DB_NAME = 'quiz_bot.db'

bot = Bot(token=API_TOKEN)

dp = Dispatcher()