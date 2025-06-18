from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BTN_CANCEL = '↩️ Скасувати оренду'
BTN_BACK = '🔙 Назад'
BTN_AVAILABLE = '🚲 Доступний транспорт'
BTN_MY_RENTALS = '📋 Мої оренди'
BTN_BIKES = '🚲 Електровелосипеди'
BTN_SCOOTERS = '🛴 Електросамокати'
BTN_DAY = "1 день - 300 грн"
BTN_WEEK = "1 тиждень - 1500 грн"

def make_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(BTN_AVAILABLE), KeyboardButton(BTN_MY_RENTALS))
    kb.add(KeyboardButton(BTN_CANCEL))
    return kb

def make_transport_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(BTN_BIKES), KeyboardButton(BTN_SCOOTERS))
    kb.add(KeyboardButton(BTN_BACK))
    return kb

def make_rental_period_reply_kb_dynamic(power, range_km):
    from utils import get_vehicle_price  # уникнути циклічного імпорту
    day_price = get_vehicle_price(power, range_km, 'day')
    week_price = get_vehicle_price(power, range_km, 'week')
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(KeyboardButton(f"1 день - {day_price} грн"), KeyboardButton(f"1 тиждень - {week_price} грн"))
    kb.add(KeyboardButton(BTN_BACK))
    return kb

def make_start_date_kb() -> ReplyKeyboardMarkup:
    import datetime
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    today = datetime.date.today()
    kb.add(*[KeyboardButton((today + datetime.timedelta(days=i)).strftime('%d.%m.%Y')) for i in range(7)])
    kb.add(KeyboardButton(BTN_BACK))
    return kb

# Динамічна клавіатура з ID доступних транспортних засобів
def make_vehicle_id_kb(ids, include_back: bool = True) -> ReplyKeyboardMarkup:
    """Створює клавіатуру з кнопками-ID доступних моделей.

    ids: список числових ID.
    include_back: чи додавати кнопку «Назад» внизу.
    """
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for vid in ids:
        kb.insert(KeyboardButton(str(vid)))
    if include_back:
        kb.add(KeyboardButton('⬅️ Назад'))
    return kb 