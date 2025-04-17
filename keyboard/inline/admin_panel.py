from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def withdrawal_admin_keyboard(balance, tg_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Вывел✅', callback_data=f'withdrawal confirm {tg_id}'))
    keyboard.add(InlineKeyboardButton(text='Отмена❌', callback_data=f'withdrawal cancel {tg_id} {balance}'))
    return keyboard.adjust(2).as_markup()


async def confirm_add_task_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Подтвердить✅', callback_data='add task confirm'))
    keyboard.add(InlineKeyboardButton(text='Отмена❌', callback_data='add task cancel'))
    return keyboard.adjust(2).as_markup()


async def category_selection_keyboard(categories):
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'add category {category.name} {category.id}'))

    return keyboard.adjust(1).as_markup()


async def delete_category_keyboard(categories):
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'delete category {category.id}'))
    return keyboard.adjust(2).as_markup()


async def referral_percent_keyboard(user_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Изменить процент', callback_data=f'change referral percent {user_id}'))
    return keyboard.as_markup()