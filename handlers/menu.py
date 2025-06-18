from aiogram import types
from aiogram.dispatcher import Dispatcher
from keyboards import make_main_kb, make_transport_kb, BTN_AVAILABLE, BTN_MY_RENTALS, BTN_CANCEL, BTN_BIKES, BTN_SCOOTERS, BTN_BACK

def register_menu_handlers(dp: Dispatcher, send_menu, bot, last_msg):
    @dp.message_handler(commands='start')
    async def cmd_start(m: types.Message):
        await send_menu(m.chat.id, 'Вітаємо! Оберіть дію:', make_main_kb(), bot, last_msg)

    @dp.message_handler(lambda m: m.text == BTN_AVAILABLE)
    async def show_types(m: types.Message):
        await send_menu(m.chat.id, 'Оберіть тип транспорту:', make_transport_kb(), bot, last_msg)

    @dp.message_handler(lambda m: m.text == BTN_BACK)
    async def back(m: types.Message):
        await send_menu(m.chat.id, 'Оберіть дію:', make_main_kb(), bot, last_msg) 