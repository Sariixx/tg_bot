import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher import Dispatcher
from keyboards import BTN_CANCEL, make_main_kb, BTN_BACK
from utils import get_vehicle_price

def register_cancel_handlers(dp: Dispatcher, send_menu, bot, last_msg, user_return_mode, service, make_main_kb):
    @dp.message_handler(lambda m: m.text == BTN_CANCEL)
    async def want_cancel(m: types.Message):
        orders = await service.get_user_orders(m.from_user.id)
        if not orders:
            await m.answer("У вас немає активних оренд.")
            return
        text = "Введіть ID транспорту для скасування оренди:\n"
        for o in orders:
            price = get_vehicle_price(o[3], 0, o[4])
            period = '1 день' if o[4] == 'day' else '1 тиждень'
            start = o[5] if o[5] else "-"
            code = o[6] if len(o) > 6 else "-"
            text += f"{o[1]}. {o[2]} — {period}, {price} грн, початок: {start}, код: {code}\n"
        await m.answer(text)
        user_return_mode[m.from_user.id] = True

    @dp.message_handler(lambda message: message.text.isdigit() and user_return_mode.get(message.from_user.id))
    async def process_return_request(message: types.Message):
        vehicle_id = int(message.text)
        orders = await service.get_user_orders(message.from_user.id)
        if not any(str(o[1]) == str(vehicle_id) for o in orders):
            await message.answer("Неправильний ID або такого транспорту не існує у ваших орендах. Спробуйте ще раз.")
            return
        ok, resp = await service.return_vehicle(message.from_user.id, vehicle_id)
        await send_menu(message.chat.id, resp, make_main_kb(), bot, last_msg)
        user_return_mode.pop(message.from_user.id, None)

    @dp.message_handler(lambda message: not message.text.isdigit() and user_return_mode.get(message.from_user.id))
    async def process_return_wrong_id(message: types.Message):
        await message.answer("Неправильний ID або такого транспорту не існує у ваших орендах. Спробуйте ще раз.") 