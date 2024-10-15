from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_check_post_keyboard(text, url):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=text, url=url))
    return keyboard.as_markup()


async def get_final_post_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Да✅', callback_data='mailing post final'))
    keyboard.add(InlineKeyboardButton(text='Отмена❌', callback_data='mailing post cancel'))
    return keyboard.adjust(2).as_markup()

