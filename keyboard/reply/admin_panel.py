from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

admin_start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить задание'),
     KeyboardButton(text='Актуальные задания')],
    [KeyboardButton(text='Задания на выполнении'),
     KeyboardButton(text='Задания на проверке')],
    [KeyboardButton(text='Добавить баланс'),
     KeyboardButton(text='Удалить баланс')],
    [KeyboardButton(text='Удалить категорию'),
     KeyboardButton(text='Статистика бота')],
    [KeyboardButton(text='Рассылка'),
     KeyboardButton(text='Найти пользователя')]
    ], resize_keyboard=True)
