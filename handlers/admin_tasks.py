import os
from typing import List

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from task_money.database.models import Task
from task_money.database.requests.admin_tasks import get_pending_tasks, get_active_tasks, get_actuality_tasks, \
    get_this_active_tasks, get_this_pending_tasks
from task_money.database.requests.task import get_task, delete_task, get_active_task, cancel_executed_task, \
    cancel_pending_task, complete_pending_task, get_active_task_by_id, get_pending_task_by_id
from task_money.keyboard.inline.admin_tasks import actuality_admin_tasks_keyboard, active_admin_tasks_keyboard, \
    pending_admin_tasks_keyboard, actuality_task_keyboard, active_task_keyboard, pending_task_keyboard, \
    active_tasks_keyboard, pending_tasks_keyboard
from task_money.keyboard.reply.admin_panel import admin_start_keyboard

load_dotenv()
admin_id = os.getenv('ADMIN_ID')
router = Router(name=__name__)


class AdminTasks(StatesGroup):
    current_page = State()
    tasks = State()
    message_id = State()


@router.message(F.text.startswith('Актуальные задания'))
async def actuality_tasks_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    if is_admin is True:
        await state.clear()
        await state.set_state(AdminTasks.current_page)
        await state.update_data(current_page=0)
        actuality_tasks = await get_actuality_tasks()
        await state.update_data(tasks=actuality_tasks)
        text, keyboard = await admin_task_paginator(tasks=actuality_tasks, current_page=0,
                                                    keyboard_func=actuality_admin_tasks_keyboard)
        await message.delete()
        answer = await message.answer(text=text, reply_markup=keyboard)
        await state.update_data(message_id=answer.message_id)


@router.callback_query(F.data.startswith('actuality admin task'))
async def actuality_admin_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    task_id = call.data.split()[-1]
    task = await get_task(task_id)
    await call.message.edit_text(text=f"<b>{task.id} {task.title}\n"
                                      f"Описание: {task.text}\n"
                                      f"Награда: {task.reward}\n</b>",
                                 reply_markup=await actuality_task_keyboard(task)
                                 )


@router.callback_query(F.data.startswith('actuality admin delete task'))
async def actuality_admin_delete_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    task_id = call.data.split()[-1]

    active_users, pending_users, task = await delete_task(task_id)

    if active_users is not None:
        for user in active_users:
            await bot.send_message(chat_id=user.tg_id, text='<b>Вы слишком долго выполняли задание!\n'
                                                            'Выполнение было отменено /start</b>')
    if pending_users is not None:
        for user in pending_users:
            await bot.send_message(chat_id=user.tg_id, text=f'<b>Задание {task.title} не прошло модерацию\n'
                                                            'Выполняйте все условия! /start</b>')
    await call.message.edit_text(text=f"<b>Задание было удалено!</b>")
    await state.clear()
    await call.message.answer(text='<b>Вы в главном меню</b>', reply_markup=admin_start_keyboard)


@router.callback_query(F.data.startswith('return actuality admin task'))
async def return_task_panel_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    actuality_tasks = context['tasks']
    text, keyboard = await admin_task_paginator(actuality_tasks, current_page=context['current_page'],
                                                keyboard_func=actuality_admin_tasks_keyboard)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('actuality admin next page task'))
async def next_page_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    current_page = int(call.data.split()[-1]) + 1
    await state.update_data(current_page=current_page)
    text, keyboard = await admin_task_paginator(tasks, current_page, actuality_admin_tasks_keyboard)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('actuality admin last page task'))
async def next_page_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    current_page = int(call.data.split()[-1]) - 1
    await state.update_data(current_page=current_page)
    text, keyboard = await admin_task_paginator(tasks, current_page, actuality_admin_tasks_keyboard)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.message(F.text.startswith('Задания на выполнении'))
async def active_tasks_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    if is_admin is True:
        await state.clear()
        await state.set_state(AdminTasks.current_page)
        await state.update_data(current_page=0)
        active_tasks = await get_active_tasks()
        await state.update_data(tasks=active_tasks)
        text, keyboard = await admin_task_paginator(tasks=active_tasks, current_page=0,
                                                    keyboard_func=active_admin_tasks_keyboard)
        await message.delete()
        answer = await message.answer(text=text, reply_markup=keyboard)
        await state.update_data(message_id=answer.message_id)


@router.callback_query(F.data.startswith('active admin task'))
async def active_admin_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    task_id = call.data.split()[-1]
    active_tasks = await get_this_active_tasks(task_id)
    if active_tasks is not None:
        await call.message.edit_text(text=f"<b>Выберите ID исполнителя из списка</b>",
                                     reply_markup=await active_tasks_keyboard(active_tasks, task_id)
                                     )
    else:
        await call.message.edit_text(text='Заданий нет',
                                     reply_markup=await active_tasks_keyboard(active_tasks, task_id))
        await call.answer()


@router.callback_query(F.data.startswith('this active task'))
async def this_active_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    active_task_id = call.data.split()[-1]
    active_task = await get_active_task_by_id(active_task_id)
    task = await get_task(active_task.task_id)
    await call.message.edit_text(text=f"<b>{task.id} {task.title}\n"
                                      f"Описание: {task.text}\n"
                                      f"Награда: {task.reward}\n"
                                      f'ID юзера: {active_task.user_id}\n'
                                      f"Начало работы: {active_task.start_date.strftime("%Y-%m-%d %H:%M")}</b>",
                                 reply_markup=await active_task_keyboard(task)
                                 )


@router.callback_query(F.data.startswith('active admin delete task'))
async def active_admin_delete_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    task_id = call.data.split()[-1]

    active_users, pending_users, task = await delete_task(task_id)

    if active_users is not None:
        for user in active_users:
            await bot.send_message(chat_id=user.tg_id, text='<b>Вы слишком долго выполняли задание!\n'
                                                            'Выполнение было отменено /start</b>')
    if pending_users is not None:
        for user in pending_users:
            await bot.send_message(chat_id=user.tg_id, text=f'<b>Задание {task.title} не прошло модерацию\n'
                                                            'Выполняйте все условия! /start</b>')
    await call.message.edit_text(text=f"<b>Задание было удалено!</b>")
    await state.clear()
    await call.message.answer(text='<b>Вы в главном меню</b>', reply_markup=admin_start_keyboard)


@router.callback_query(F.data.startswith('active admin cancel task'))
async def active_admin_cancel_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    task_id = call.data.split()[-1]
    user = await cancel_executed_task(task_id)
    if user is not None:
        await bot.send_message(chat_id=user.tg_id, text='<b>Вы слишком долго выполняли задание!\n'
                                                        'Выполнение было отменено /start</b>')
    await call.message.edit_text(text="<b>Выполнение было отменено!</b>")
    await state.clear()
    await call.message.answer(text='<b>Вы в главном меню</b>', reply_markup=admin_start_keyboard)


@router.callback_query(F.data.startswith('return active admin task'))
async def return_task_panel_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    text, keyboard = await admin_task_paginator(tasks, current_page=context['current_page'],
                                                keyboard_func=active_admin_tasks_keyboard)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('active admin next page task'))
async def next_page_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    current_page = int(call.data.split()[-1]) + 1
    await state.update_data(current_page=current_page)
    text, keyboard = await admin_task_paginator(tasks, current_page, active_admin_tasks_keyboard)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('active admin last page task'))
async def next_page_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    current_page = int(call.data.split()[-1]) - 1
    await state.update_data(current_page=current_page)
    text, keyboard = await admin_task_paginator(tasks, current_page, active_admin_tasks_keyboard)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.message(F.text.startswith('Задания на проверке'))
async def pending_tasks_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    if is_admin is True:
        await state.clear()
        await state.set_state(AdminTasks.current_page)
        await state.update_data(current_page=0)
        pending_tasks = await get_pending_tasks()
        await state.update_data(tasks=pending_tasks)
        text, keyboard = await admin_task_paginator(tasks=pending_tasks, current_page=0,
                                                    keyboard_func=pending_admin_tasks_keyboard)
        await message.delete()
        answer = await message.answer(text=text, reply_markup=keyboard)
        await state.update_data(message_id=answer.message_id)


@router.callback_query(F.data.startswith('pending admin task'))
async def active_admin_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    task_id = call.data.split()[-1]
    pending_tasks = await get_this_pending_tasks(task_id)
    if pending_tasks is not None:
        await call.message.edit_text(text=f"<b>Выберите ID исполнителя из списка</b>",
                                     reply_markup=await pending_tasks_keyboard(pending_tasks, task_id)
                                     )
    else:
        await call.message.edit_text(text='Заданий нет',
                                     reply_markup=await pending_tasks_keyboard(pending_tasks, task_id))
        await call.answer()


@router.callback_query(F.data.startswith('this pending task'))
async def pending_admin_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    pending_task_id = call.data.split()[-1]
    pending_task = await get_pending_task_by_id(pending_task_id)
    task = await get_task(pending_task.task_id)
    await call.message.edit_text(text=f"<b>{task.id} {task.title}\n"
                                      f"Описание: {task.text}\n"
                                      f"Награда: {task.reward}\n"
                                      f'ID юзера: {pending_task.user_id}</b>\n',

                                 reply_markup=await pending_task_keyboard(task)
                                 )


@router.callback_query(F.data.startswith('pending admin delete task'))
async def pending_admin_delete_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    task_id = call.data.split()[-1]

    active_users, pending_users, task = await delete_task(task_id)

    if active_users is not None:
        for user in active_users:
            await bot.send_message(chat_id=user.tg_id, text='<b>Вы слишком долго выполняли задание!\n'
                                                            'Выполнение было отменено /start</b>')
    if pending_users is not None:
        for user in pending_users:
            await bot.send_message(chat_id=user.tg_id, text=f'<b>Задание {task.title} не прошло модерацию\n'
                                                            'Выполняйте все условия! /start</b>')
    await call.message.edit_text(text=f"<b>Задание было удалено!</b>")
    await state.clear()
    await call.message.answer(text='<b>Вы в главном меню</b>', reply_markup=admin_start_keyboard)


@router.callback_query(F.data.startswith('pending admin cancel task'))
async def pending_admin_cancel_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    task_id = call.data.split()[-1]
    user = await cancel_pending_task(task_id)

    if user is not None:
        await bot.send_message(chat_id=user.tg_id, text='<b>Задание не прошло проверку модератора!\n'
                                                        'В следующий раз выполняйте все условия!</b>')
    await call.message.edit_text(text=f"<b>Выполнение было отменено!</b>")
    await state.clear()
    await call.message.answer(text='Вы в главном меню', reply_markup=admin_start_keyboard)


@router.callback_query(F.data.startswith('pending admin complete task'))
async def active_admin_cancel_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    task_id = call.data.split()[-1]
    user, referral = await complete_pending_task(task_id)
    if user is not None:
        await bot.send_message(chat_id=user.tg_id, text='<b>Задание успешно прошло проверку!\n'
                                                        f'Ваш текущий баланс: {user.balance}</b>')
        if referral is not None:
            await bot.send_message(chat_id=referral.tg_id, text='<b>Ваш реферал выполнил задание!\n'
                                                            'Текущий баланс: {referral.balance}</b>')
    await call.message.edit_text(text="<b>Задание завершено!</b>")
    await state.clear()
    await call.message.answer(text='<b>Вы в главном меню</b>', reply_markup=admin_start_keyboard)


@router.callback_query(F.data.startswith('return pending admin task'))
async def return_task_panel_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    text, keyboard = await admin_task_paginator(tasks, current_page=context['current_page'],
                                                keyboard_func=pending_admin_tasks_keyboard)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('pending admin next page task'))
async def next_page_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    current_page = int(call.data.split()[-1]) + 1
    await state.update_data(current_page=current_page)
    text, keyboard = await admin_task_paginator(tasks, current_page, pending_admin_tasks_keyboard)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('pending admin last page task'))
async def next_page_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    current_page = int(call.data.split()[-1]) - 1
    await state.update_data(current_page=current_page)
    text, keyboard = await admin_task_paginator(tasks, current_page, pending_admin_tasks_keyboard)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('admin cancel page task'))
async def admin_cancel_page_task_handler(call: CallbackQuery, bot: Bot, is_admin: bool, state: FSMContext):
    await call.message.delete()
    await state.clear()
    await call.message.answer(text='<b>Вы в главном меню</b>', reply_markup=admin_start_keyboard)


async def admin_task_paginator(tasks: List[Task], current_page, keyboard_func):
    number_tasks = len(tasks)
    text = '---------' * 4 + '\n\n'
    if number_tasks % 4 == 0:
        count_page = number_tasks / 4
    else:
        count_page = number_tasks // 4 + 1
    if (count_page >= 1) and (current_page != 0) and (current_page != count_page):
        current_tasks = tasks[current_page * 4:current_page * 4 + 4]
    elif (current_page == 0) and (count_page >= 1) and (current_page != count_page):
        current_tasks = tasks[0:4]
    elif (current_page == count_page) and (count_page >= 1):
        current_tasks = tasks[-4:]
    else:
        current_tasks = tasks
    keyboard = await keyboard_func(current_tasks, current_page, count_page)
    if count_page > 0:
        for current_task in current_tasks:
            text += (f"<b>{current_task.id} {current_task.title}\n"
                     f"Описание: {current_task.text}\n"
                     f"Награда: {current_task.reward}\n"
                     f"\n{'---------' * 7}\n\n</b>")
        return text, keyboard
    return 'Тут пусто', keyboard
