from aiogram import Bot, Dispatcher, executor
from config import TOKEN
from services import RentService
from db import get_db
import asyncio
from handlers.menu import register_menu_handlers
from handlers.rent import register_rent_handlers
from handlers.cancel import register_cancel_handlers
from handlers.orders import register_orders_handlers
from utils import send_menu, get_vehicle_price
from keyboards import make_main_kb

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
service = RentService()

async def on_startup(dp):
    await get_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(1)
    print('База даних готова')

user_return_mode = {}
user_data = {}
last_msg = {}

if __name__ == "__main__":
    register_menu_handlers(dp, send_menu, bot, last_msg)
    register_rent_handlers(dp, bot, last_msg, user_data, user_return_mode, service)
    register_cancel_handlers(dp, send_menu, bot, last_msg, user_return_mode, service, make_main_kb)
    register_orders_handlers(dp, service, get_vehicle_price)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)