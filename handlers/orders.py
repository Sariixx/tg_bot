from aiogram import types
from aiogram.dispatcher import Dispatcher

def register_orders_handlers(dp: Dispatcher, service, get_vehicle_price):
    @dp.message_handler(lambda message: message.text == '📋 Мої оренди')
    async def myorders(message: types.Message):
        orders = await service.get_user_orders(message.from_user.id)
        if not orders:
            await message.answer("У вас немає активних оренд.")
            return
        text = "Ваші активні оренди:\n\n"
        for o in orders:
            day_price = get_vehicle_price(o[3], 0, 'day')
            week_price = get_vehicle_price(o[3], 0, 'week')
            period = '1 день' if o[4] == 'day' else '1 тиждень'
            price = get_vehicle_price(o[3], 0, o[4])
            start = o[5] if o[5] else "-"
            code = o[6] if len(o) > 6 else "-"
            text += f"ID: {o[1]}\nМодель: {o[2]}\nТермін: {period}\nЦіна: {price} грн\nПочаток: {start}\nКод оренди: {code}\n\n"
        await message.answer(text) 