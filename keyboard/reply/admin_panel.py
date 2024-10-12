from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

admin_start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить задание'),
     KeyboardButton(text='Актуальные задания')],
    [KeyboardButton(text='Задания на выполнении'),
     KeyboardButton(text='Задания на проверке')],
    [KeyboardButton(text='Добавить баланс'),
     KeyboardButton(text='Удалить баланс')],
    [KeyboardButton(text='Удалить категорию')]
    ], resize_keyboard=True)
