from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from task_money.database.models import Task


async def task_acceptance(task_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Приступить✅', callback_data=f'task acceptance confirm {task_id}'))
    keyboard.add(InlineKeyboardButton(text='Не принимать❌', callback_data='task acceptance cancel'))
    return keyboard.adjust(2).as_markup()


async def task_panel(tasks: List[Task], current_page, count_page):
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text=f'{task.title} | {task.reward}₽', callback_data=f'task {task.id}'))
    if (current_page == 0) and (count_page > 1):
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Вперед', callback_data=f'next page task {current_page}'))

    elif (current_page + 1 == count_page) and (count_page > 1):
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'last page task {current_page}'))

    elif count_page < 2:
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel page task {current_page}'))
    else:
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'last page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Вперед', callback_data=f'next page task {current_page}'))
    return keyboard.adjust(1,1,1,1,2,3).as_markup()


async def task_keyboard(task_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Начать задание', callback_data=f'start task {task_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'return task panel {task_id}'))
    return keyboard.as_markup()


async def task_execution_keyboard(task_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Я выполнил', callback_data=f'executed task {task_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад в меню', callback_data='return main menu'))
    return keyboard.adjust(1).as_markup()


async def task_execution_menu_keyboard(task_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add()
    keyboard.add(InlineKeyboardButton(text='Я выполнил', callback_data=f'executed task {task_id}'))
    keyboard.add(InlineKeyboardButton(text='Отменить задание', callback_data=f'cancel executed task {task_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад в меню', callback_data='return main menu'))
    return keyboard.adjust(1).as_markup()


async def category_keyboard(categories):
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category {category.name}'))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data='return main menu'))
    return keyboard.adjust(1).as_markup()


photo_video_confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Всё', callback_data='final task completion')],
    [InlineKeyboardButton(text='Ещё', callback_data='add more')]
])