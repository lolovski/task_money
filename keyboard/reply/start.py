from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

start_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Приступить к заданию')],
                                               [KeyboardButton(text='Реферальная система📣'),
                                                KeyboardButton(text='Профиль🎩')],
                                               [KeyboardButton(text='Помощь🛡')],
                                               ], resize_keyboard=True)

start_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Задания')],
    [KeyboardButton(text='Реклама')],

], resize_keyboard=True)