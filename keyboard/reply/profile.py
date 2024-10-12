from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
choose_payment_system_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='СБП (номер телефона РФ)')],
    [KeyboardButton(text='Банковская карта (РФ)')],
#   [KeyboardButton(text='Крипта')],
    [KeyboardButton(text='Мобильная связь')],
], resize_keyboard=True)
choose_bank_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='ЮMoney')],
    [KeyboardButton(text='Т-банк')],
    [KeyboardButton(text='Альфа')],
    [KeyboardButton(text='Сбер')],
    [KeyboardButton(text='Райффайзен')],
    [KeyboardButton(text='ВТБ')],
    [KeyboardButton(text='На баланс телефона')]
], resize_keyboard=True)

choose_telecom_operator_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='МТС')],
    [KeyboardButton(text='Мегафон')],
    [KeyboardButton(text='Билайн')],
    [KeyboardButton(text='Теле2')],
    [KeyboardButton(text='СберМобайл')],
    [KeyboardButton(text='Ростелеком')],
    [KeyboardButton(text='Yota')]
])

contact_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить номер', request_contact=True)]
], resize_keyboard=True)