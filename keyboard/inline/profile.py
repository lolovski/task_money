from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


money_withdrawal_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вывести средства', callback_data='money withdrawal')],
])

confirm_delete_partner_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить🙊', callback_data='confirm delete_partner'), InlineKeyboardButton(text='Назад◀️', callback_data='main_profile cancel delete_partner')],
])

choice_add_partner_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ссылка-приглашение (база)', callback_data='add_partner link')],
    [InlineKeyboardButton(text='Назад◀️', callback_data='main_profile cancel add_partner')],
])

returning_main_profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад◀️', callback_data='main_profile returning')],
])
