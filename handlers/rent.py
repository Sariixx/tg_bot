import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher import Dispatcher
from keyboards import make_rental_period_reply_kb_dynamic, make_start_date_kb, make_main_kb, make_vehicle_id_kb, BTN_BACK
from utils import get_vehicle_price, is_valid_date, build_vehicle_list, send_menu
from services import RentService
import asyncio

def register_rent_handlers(dp: Dispatcher, bot, last_msg, user_data, user_return_mode, service):
    @dp.message_handler(lambda m: m.text == '🚲 Електровелосипеди')
    async def bikes(m: types.Message):
        user_data[m.from_user.id] = {'selected_type': 'electric_bike', 'state': 'waiting_id'}
        vehicles = await service.get_available_vehicles_by_type('electric_bike')
        text = await build_vehicle_list('electric_bike', service)
        id_kb = make_vehicle_id_kb([v[0] for v in vehicles])
        await send_menu(m.chat.id, text, id_kb, bot, last_msg)

    @dp.message_handler(lambda m: m.text == '🛴 Електросамокати')
    async def scooters(m: types.Message):
        user_data[m.from_user.id] = {'selected_type': 'electric_scooter', 'state': 'waiting_id'}
        vehicles = await service.get_available_vehicles_by_type('electric_scooter')
        text = await build_vehicle_list('electric_scooter', service)
        id_kb = make_vehicle_id_kb([v[0] for v in vehicles])
        await send_menu(m.chat.id, text, id_kb, bot, last_msg)

    @dp.message_handler(lambda m: not user_return_mode.get(m.from_user.id) and m.text.isdigit())
    async def process_rent_request(message: types.Message):
        user_id = message.from_user.id
        if user_id not in user_data or user_data[user_id].get('state') != 'waiting_id':
            await send_menu(message.chat.id, "Оберіть дію:", make_main_kb(), bot, last_msg)
            return
        selected_type = user_data[user_id]['selected_type']
        vehicle_id = int(message.text)
        vehicles = await service.get_available_vehicles_by_type(selected_type)
        vehicle = next((v for v in vehicles if v[0] == vehicle_id), None)
        if not vehicle:
            await message.answer("Неправильний ID або такого транспорту не існує. Спробуйте ще раз.")
            return
        user_data[user_id].update({'vehicle_id': vehicle_id, 'power': vehicle[2], 'range_km': vehicle[3], 'state': 'waiting_period'})
        kb = make_rental_period_reply_kb_dynamic(vehicle[2], vehicle[3])
        await message.answer("Оберіть термін оренди:", reply_markup=kb)

    @dp.message_handler(lambda m: not user_return_mode.get(m.from_user.id) and (m.text.startswith('1 день') or m.text.startswith('1 тиждень')) and user_data.get(m.from_user.id))
    async def process_rental_period_reply(message: types.Message):
        user_id = message.from_user.id
        if user_id not in user_data or user_data[user_id].get('state') != 'waiting_period':
            await send_menu(message.chat.id, "Оберіть дію:", make_main_kb(), bot, last_msg)
            return
        if message.text.startswith('1 день'):
            rental_period = 'day'
        elif message.text.startswith('1 тиждень'):
            rental_period = 'week'
        else:
            rental_period = None
        user_data[user_id]['rental_period'] = rental_period
        user_data[user_id]['state'] = 'waiting_date'
        await message.answer("Оберіть дату початку оренди:", reply_markup=make_start_date_kb())

    @dp.message_handler(lambda m: not user_return_mode.get(m.from_user.id) and m.text not in ['⬅️ Назад', BTN_BACK] and m.text not in ['⬅️ Назад', BTN_BACK] and not m.text.isdigit() and not (m.text.startswith('1 день') or m.text.startswith('1 тиждень')) and user_data.get(m.from_user.id, {}).get('state') == 'waiting_id')
    async def process_wrong_id(message: types.Message):
        user_id = message.from_user.id
        if user_id not in user_data or user_data[user_id].get('state') != 'waiting_id':
            await send_menu(message.chat.id, "Оберіть дію:", make_main_kb(), bot, last_msg)
            return
        await message.answer("Неправильний ID або такого транспорту не існує. Спробуйте ще раз.")

    @dp.message_handler(lambda m: not user_return_mode.get(m.from_user.id) and is_valid_date(m.text) and user_data.get(m.from_user.id) and 'rental_period' in user_data.get(m.from_user.id, {}))
    async def process_start_date(message: types.Message):
        user_id = message.from_user.id
        if user_id not in user_data or user_data[user_id].get('state') != 'waiting_date':
            await send_menu(message.chat.id, "Оберіть дію:", make_main_kb(), bot, last_msg)
            return
        start_date = message.text
        vehicle_id = user_data[user_id]['vehicle_id']
        rental_period = user_data[user_id]['rental_period']
        power = user_data[user_id].get('power', 0)
        range_km = user_data[user_id].get('range_km', 0)
        ok, order_code = await service.create_order(user_id, vehicle_id, message.from_user.username, rental_period, start_date)
        if ok:
            price = get_vehicle_price(power, range_km, rental_period)
            period_ua = '1 день' if rental_period == 'day' else '1 тиждень'
            await message.answer(
                f"Оренду успішно оформлено!\nТермін: {period_ua}\nЦіна: {price} грн\nПочаток: {start_date}\nВаш код оренди: <code>{order_code}</code>",
                parse_mode='HTML',
                reply_markup=make_main_kb()
            )
        else:
            if order_code:
                await message.answer(str(order_code), reply_markup=make_main_kb())
                print(f"[INFO] Відмова в оренді: {order_code}")
            else:
                await message.answer("Помилка при оформленні оренди. Спробуйте пізніше.", reply_markup=make_main_kb())
                print(f"[ERROR] Не вдалося оформити оренду для user_id={user_id}, vehicle_id={vehicle_id}")
        if user_id in user_data:
            del user_data[user_id]

    @dp.message_handler(lambda m: m.from_user.id in user_data)
    async def fallback_handler(message: types.Message):
        await send_menu(message.chat.id, "Оберіть дію:", make_main_kb(), bot, last_msg)
        user_data.pop(message.from_user.id, None)

    @dp.message_handler(lambda m: m.text in ['⬅️ Назад', BTN_BACK])
    async def rent_back(message: types.Message):
        user_data.pop(message.from_user.id, None)
        await send_menu(message.chat.id, "Оберіть дію:", make_main_kb(), bot, last_msg) 