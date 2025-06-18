import datetime
from aiogram.types import ReplyKeyboardMarkup

def is_valid_date(text):
    try:
        datetime.datetime.strptime(text, '%d.%m.%Y')
        return True
    except Exception:
        return False

def get_vehicle_price(power, range_km, rental_period):
    if power >= 500 or range_km >= 80:
        return 450 if rental_period == 'day' else 2000
    else:
        return 300 if rental_period == 'day' else 1500

async def build_vehicle_list(v_type: str, service) -> str:
    vehicles = await service.get_available_vehicles_by_type(v_type)
    if not vehicles:
        return "Немає доступних моделей."
    name = "електровелосипеди" if v_type == 'electric_bike' else 'електросамокати'
    text = f"Доступні {name}:\n\n"
    for v in vehicles:
        day_price = get_vehicle_price(v[2], v[3], 'day')
        week_price = get_vehicle_price(v[2], v[3], 'week')
        text += (f"ID: {v[0]}\nМодель: {v[1]}\nПотужність: {v[2]} Вт\n"
                 f"Запас ходу: {v[3]} км\nЦіна: {day_price} грн/день, {week_price} грн/тиждень\n"
                 f"Залишилось: {v[5]} шт.\n\n")
    text += "\nДля оренди введіть ID бажаної моделі"
    return text

async def send_menu(chat_id: int, text: str, kb: ReplyKeyboardMarkup, bot, last_msg):
    if chat_id in last_msg:
        try:
            await bot.edit_message_text(text, chat_id, last_msg[chat_id], reply_markup=kb)
            return
        except Exception as e:
            if "message is not modified" in str(e).lower():
                try:
                    await bot.edit_message_reply_markup(chat_id, last_msg[chat_id], reply_markup=kb)
                except Exception:
                    pass
                return
    msg = await bot.send_message(chat_id, text, reply_markup=kb)
    last_msg[chat_id] = msg.message_id 