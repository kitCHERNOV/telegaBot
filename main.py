from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message


from app.handlers import router

import asyncio
import logging
import requests




TOKEN = '5447372857:AAH3FmgX0hvrSV7Wfms9-RwrCOyTDHOr8Lc'
IMAGE_API_URL = ''

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()



async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except:
        print("exit")