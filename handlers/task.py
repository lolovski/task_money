import os
from typing import List

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
from dotenv import load_dotenv

from task_money.database.models import Task
from task_money.database.requests.category import get_categories, get_category_tasks
from task_money.database.requests.task import get_task
from task_money.database.requests.task import set_active_task, set_pending_task, get_active_task, get_user_active_task, \
    cancel_executed_task
from task_money.keyboard.inline.task import category_keyboard
from task_money.keyboard.inline.task import task_panel, task_keyboard, task_execution_keyboard, \
    task_execution_menu_keyboard, photo_video_confirm_keyboard
from task_money.keyboard.reply.start import start_keyboard

load_dotenv()
admin_id = os.getenv('ADMIN_ID')
router = Router(name=__name__)


class TaskState(StatesGroup):
    category = State()
    category_tasks = State()
    current_page = State()
    message_id = State()
    task = State()
    active_task_id = State()
    photo_album = State()
    video_album = State()


@router.callback_query(F.data.startswith('task acceptance confirm'))
async def task_acceptance_confirm_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):

    task_id = call.data.split()[-1]
    task = await get_task(task_id)
    if task is not None:
        active_task = await set_active_task(task_id, tg_id)
        if active_task is not None:
            await call.message.edit_text(
                text=f'👾<b><a href="{task.description_url}">ИНСТРУКЦИЯ К ВЫПОЛНЕНИЮ</a></b>\n',
                reply_markup=await task_execution_keyboard(task_id),
                disable_web_page_preview=True
            )

        else:
            await bot.answer_callback_query(callback_query_id=call.id, text='Задание уже начал другой человек',
                                            show_alert=True)
            await call.message.delete()
    else:
        await bot.answer_callback_query(callback_query_id=call.id, text='Задание неактуально',
                                        show_alert=True)
        await call.message.delete()


@router.message(F.text == 'Приступить к заданию')
async def task_acceptance_confirm_handler(message: Message, bot: Bot, tg_id: str, state: FSMContext):
    await state.clear()
    active_task: Task = await get_user_active_task(tg_id)
    if active_task is not None:
        return await message.answer(text=f'📝<b>У вас есть незаконченное задание:\n'
                                         f"{active_task.title}\n"
                                         f'👾<a href="{active_task.description_url}">ИНСТРУКЦИЯ К ВЫПОЛНЕНИЮ</a></b>\n',
                                    reply_markup=await task_execution_menu_keyboard(active_task.id),
                                    disable_web_page_preview=True)

    categories = await get_categories()
    await message.delete()
    await message.answer(
        text='<b>Выбери категорию из списка:</b>',
        reply_markup=await category_keyboard(categories=categories)
    )
    await state.set_state(TaskState.category_tasks)



@router.callback_query(F.data.startswith('category'))
async def task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    category_name = call.data.split()[-1]
    tasks, category = await get_category_tasks(tg_id=tg_id, category_name=category_name)
    await state.set_state(TaskState.category_tasks)
    await state.update_data(current_page=0)
    await state.update_data(tasks=tasks, category=category)
    text, keyboard = await task_paginator(tasks, current_page=0)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('next page task'))
async def next_page_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    current_page = int(call.data.split()[-1]) + 1
    await state.update_data(current_page=current_page)
    text, keyboard = await task_paginator(tasks, current_page)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('last page task'))
async def next_page_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    tasks = context['tasks']
    current_page = int(call.data.split()[-1]) - 1
    await state.update_data(current_page=current_page)
    text, keyboard = await task_paginator(tasks, current_page)
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('task acceptance cancel'))
async def task_acceptance_cancel_handler(call: CallbackQuery, bot: Bot, tg_id: str):
    await call.message.delete()


@router.callback_query(F.data.startswith('cancel page task'))
async def task_cancel_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    await state.clear()
    categories = await get_categories()
    await call.message.edit_text(
        text='<b>Выбери категорию из списка:</b>',
        reply_markup=await category_keyboard(categories=categories)
    )
    await state.set_state(TaskState.category_tasks)


@router.callback_query(F.data.startswith('task'))
async def task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    task_id = call.data.split()[-1]
    task = await get_task(task_id=task_id)
    await state.update_data(task=task)
    await call.message.edit_text(text=f"<b>{task.title} | {task.reward}₽\n\n"
                                      f"📋{task.text}\n\n"
                                      f"⚒️{task.category.name}</b>",
                                 reply_markup=await task_keyboard(task_id))


@router.callback_query(F.data.startswith('return task panel'))
async def return_task_panel_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    await state.set_state(TaskState.category_tasks)
    text, keyboard = await task_paginator(context['tasks'], current_page=context['current_page'])
    await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('start task'))
async def run_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    task = context['task']

    active_task = await set_active_task(task.id, tg_id)
    if active_task is not None:
        await call.message.edit_text(
            text=f'👾<b><a href="{task.description_url}">ИНСТРУКЦИЯ К ВЫПОЛНЕНИЮ</a></b>\n',
            reply_markup=await task_execution_keyboard(task.id),
            disable_web_page_preview=True
        )

    else:
        context = await state.get_data()
        await state.set_state(TaskState.category_tasks)
        text, keyboard = await task_paginator(context['tasks'], current_page=context['current_page'])
        await bot.answer_callback_query(callback_query_id=call.id, text='Задание уже начал другой человек', show_alert=True)
        await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data.startswith('return main menu'))
async def return_main_menu_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer('<b>Вы вернулись в главое меню!</b>',
                              reply_markup=start_keyboard)


@router.callback_query(F.data.startswith('executed task'))
async def photo_execute_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    active_task_id = call.data.split()[-1]
    answer = await call.message.edit_text(text='<b>Отправьте фото или видео с доказательствами!\n'
                                               '(Строго по одному)</b>')
    await state.set_state(TaskState.active_task_id)
    await state.update_data(active_task_id=active_task_id, message_id=answer.message_id)


@router.message(TaskState.active_task_id, F.photo)
async def execute_photo_task_handler(message: Message, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    photo_album = context.get('photo_album', [])
    photo = message.photo[-1]
    photo_album.append(photo.file_id)
    await state.update_data(photo_album=photo_album)
    await message.delete()
    await message.answer('<b>Фото добавлено\n'
                         'Добавить ещё?</b>',
                         reply_markup=photo_video_confirm_keyboard)

@router.callback_query(F.data == 'add more')
async def add_more_photo_video_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('<b>Отправьте новое фото/видео</b>')


@router.message(TaskState.active_task_id, F.video)
async def execute_video_task_handler(message: Message, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()
    video_album = context.get('video_album', [])
    video = message.video
    video_album.append(video.file_id)
    await state.update_data(video_album=video_album)
    await message.delete()
    await message.answer('<b>Видео добавлено\n'
                         'Добавить ещё?</b>',
                         reply_markup=photo_video_confirm_keyboard)


@router.callback_query(F.data.startswith('final task completion'))
async def final_task_completion_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    context = await state.get_data()

    task_id = context['active_task_id']
    active_task = await get_active_task(task_id)
    if active_task is None:
        return await call.message.answer(text='q')
    task, pending_task = await set_pending_task(task_id=task_id)

    photo_album = context.get('photo_album')
    video_album = context.get('video_album')
    media = []
    if video_album is not None:
        for video in video_album:
            media.append(InputMediaVideo(media=video))
    if photo_album is not None:
        for photo in photo_album:
            media.append(InputMediaPhoto(media=photo))

    await state.clear()
    await call.message.answer(text='<b>Задание было отправлено на модерацию!\n'
                              'Админ скоро примет выполненное задание, и деньги появятся у вас на счету\n'
                              'Вы можете приступить к новому заданию!</b>',
                         reply_markup=start_keyboard)
    await bot.send_media_group(chat_id=str(admin_id),
                               media=media)
    await bot.send_message(chat_id=str(admin_id),
                           text='<b>Новое задание на проверке!\n'
                                f'ID Задания: {task.id}\n'
                                f'ID юзера: {pending_task.user_id}\n'
                                f'Заголовок задания: {task.title}\n</b>')


@router.callback_query(F.data.startswith('go executed task'))
async def go_executed_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    task_id = call.data.split()[-1]
    task = await get_task(task_id=task_id)
    await call.message.edit_text(text=f"<b>{task.title} | {task.reward}₽\n\n"
                                      f"📋{task.text}\n\n"
                                      f"⚒️{task.category.name}</b>",
                                 reply_markup=await task_execution_keyboard(task_id))


@router.callback_query(F.data.startswith('cancel executed task'))
async def cancel_executed_task_handler(call: CallbackQuery, bot: Bot, tg_id: str, state: FSMContext):
    task_id = call.data.split()[-1]
    await cancel_executed_task(task_id=task_id)
    await call.message.edit_text(text='<b>Задание было отменено!</b>')
    await call.message.answer('<b>Вы можете приступить к новому заданию!</b>',
                              reply_markup=start_keyboard)


async def task_paginator(tasks: List[Task], current_page):
    number_tasks = len(tasks)
    text = '<b>Выберите задание из списка:</b>\n'
    if number_tasks % 4 == 0:
        count_page = number_tasks / 4
    else:
        count_page = number_tasks // 4 + 1
    if (count_page >= 1) and (current_page != 0) and (current_page != count_page):
        current_tasks = tasks[current_page*4:current_page*4+4]
    elif (current_page == 0) and (count_page >= 1) and (current_page != count_page):
        current_tasks = tasks[0:4]
    elif (current_page == count_page) and (count_page >= 1):
        current_tasks = tasks[-4:]
    else:
        current_tasks = tasks
    keyboard = await task_panel(current_tasks, current_page, count_page)
    if count_page > 0:

        return text, keyboard
    return '<b>Заданий пока нет</b>', keyboard

