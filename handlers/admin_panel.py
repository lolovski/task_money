import os

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from database.requests.admin_panel import add_balance, delete_balance
from database.requests.category import get_categories, set_category, delete_category
from database.requests.task import set_task
from database.requests.user import add_money, get_user, get_profile_by_id, change_referral_percent
from keyboard.inline.admin_panel import category_selection_keyboard, \
    confirm_add_task_keyboard, delete_category_keyboard, referral_percent_keyboard
from keyboard.reply.admin_panel import admin_start_keyboard
from pyexpat.errors import messages
from utils.mailing import mailing_task

from database.requests.admin_panel import get_admin_stats

load_dotenv()
admin_id = os.getenv('ADMIN_ID')
router = Router(name=__name__)


class TaskForm(StatesGroup):
    title = State()
    text = State()
    description_url = State()
    reward = State()
    limit = State()
    category_id = State()
    final = State()
    message_id = State()


class BalanceForm(StatesGroup):
    user_id = State()
    amount = State()
    action = State()


class UserForm(StatesGroup):
    user_id = State()
    referral_percent = State()


@router.callback_query(F.data.startswith('withdrawal confirm'))
async def withdrawal_confirm_handler(call: CallbackQuery, bot: Bot):
    tg_id = call.data.split()[-1]
    await bot.send_message(chat_id=tg_id, text='<b>Средства успешно выведены!</b>')
    await bot.delete_message(chat_id=admin_id, message_id=call.message.message_id)


@router.callback_query(F.data.startswith('withdrawal cancel'))
async def withdrawal_confirm_handler(call: CallbackQuery, bot: Bot):
    data = call.data.split()
    tg_id = data[-2]
    balance = data[-1]
    await add_money(tg_id, int(balance))
    await bot.send_message(chat_id=tg_id, text='<b>Произошла ошибка при выводе средств!\n'
                                               'Деньги были возвращены на счёт\n'
                                               'Попробуйте еще раз или напишите в поддержку</b>')
    await bot.delete_message(chat_id=admin_id, message_id=call.message.message_id)


@router.message(F.text == 'Добавить задание')
async def start_add_task_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    if is_admin:
        await state.clear()
        await message.delete()
        answer = await message.answer(text='<b>Напишите заголовок задания</b>')
        await state.set_state(TaskForm.text)
        await state.update_data(message_id=answer.message_id)


@router.message(TaskForm.text)
async def add_text_task_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    title = message.text
    context = await state.get_data()
    await state.update_data(title=title)
    await message.delete()
    answer = await bot.edit_message_text(chat_id=message.chat.id, message_id=context['message_id'],
                                text='<b>Напишите текст задания</b>')
    await state.set_state(TaskForm.description_url)
    await state.update_data(message_id=answer.message_id)


@router.message(TaskForm.description_url)
async def add_description_url_task_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    text = message.text
    context = await state.get_data()
    await state.update_data(text=text)
    await message.delete()
    answer = await bot.edit_message_text(chat_id=message.chat.id, message_id=context['message_id'],
                                text='<b>Напишите ссылку на описание задания</b>')
    await state.set_state(TaskForm.reward)
    await state.update_data(message_id=answer.message_id)


@router.message(TaskForm.reward)
async def add_reward_task_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    description_url = message.text
    context = await state.get_data()
    await state.update_data(description_url=description_url)
    await message.delete()
    answer = await bot.edit_message_text(chat_id=message.chat.id, message_id=context['message_id'],
                                text='<b>Напишите награду задания</b>')
    await state.set_state(TaskForm.limit)
    await state.update_data(message_id=answer.message_id)


@router.message(TaskForm.limit)
async def add_limit_task_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    reward = message.text
    context = await state.get_data()
    await state.update_data(reward=reward)
    await message.delete()
    answer = await bot.edit_message_text(chat_id=message.chat.id, message_id=context['message_id'],
                                         text='<b>Напишите лимит на количество выполнений</b>')
    await state.set_state(TaskForm.category_id)
    await state.update_data(message_id=answer.message_id)


@router.message(TaskForm.category_id)
async def add_category_task_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    limit = message.text
    context = await state.get_data()
    await state.update_data(limit=limit)
    await message.delete()
    categories = await get_categories()
    answer = await bot.edit_message_text(chat_id=message.chat.id, message_id=context['message_id'],
                                text='<b>Напишите категорию задания или выберите из списка</b>',
                                         reply_markup=await category_selection_keyboard(categories))
    await state.set_state(TaskForm.final)
    await state.update_data(message_id=answer.message_id)


@router.callback_query(F.data.startswith('add category'))
async def final_call_add_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    category_id = call.data.split()[-1]
    category_name = call.data.split()[-2]
    context = await state.get_data()
    await state.update_data(category_id=category_id)
    answer = await bot.edit_message_text(chat_id=call.message.chat.id, message_id=context['message_id'],
                                         text=f"<b>Заголовок: {context['title']}\n"
                                              f"Текст: {context['text']}\n"
                                              f"Описание: {context['description_url']}\n"
                                              f"Награда: {context['reward']}\n"
                                              f"Категория: {category_name}\n"
                                              f"Лимит: {context['limit']}</b>",
                                         reply_markup=await confirm_add_task_keyboard(),
                                         disable_web_page_preview=True)
    await state.update_data(message_id=answer.message_id)


@router.message(TaskForm.final)
async def final_add_task_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    category = message.text
    category_id = await set_category(category)
    context = await state.get_data()
    await state.update_data(category_id=category_id)
    await message.delete()
    answer = await bot.edit_message_text(chat_id=message.chat.id, message_id=context['message_id'],
                                         text=f"<b>Заголовок: {context['title']}\n"
                                              f"Текст: {context['text']}\n"
                                              f"Описание: {context['description_url']}\n"
                                              f"Награда: {context['reward']}\n"
                                              f"Категория: {category}\n"
                                              f"Лимит: {context['limit']}</b>",
                                         reply_markup=await confirm_add_task_keyboard(),
                                         disable_web_page_preview=True)
    await state.update_data(message_id=answer.message_id)


@router.callback_query(F.data == 'add task confirm')
async def confirm_add_task_handler(call: CallbackQuery, bot: Bot, is_admin: bool, state: FSMContext):
    context = await state.get_data()
    message_id = context.pop('message_id')
    task = await set_task(context)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=message_id,
                                text='<b>Задача успешно добавлена!</b>')

    await state.clear()
    await mailing_task(bot=bot, task=task)


@router.callback_query(F.data == 'add task cancel')
async def cancel_add_task_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    context = await state.get_data()
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=context['message_id'],
                                text='<b>Отмена! Вы в главном меню</b>')
    await state.clear()


@router.message(F.text.startswith('Добавить баланс'))
async def add_balance_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    await state.clear()
    await message.answer('<b>Напишите ID пользователя</b>')
    await state.set_state(BalanceForm.user_id)
    await state.update_data(action='add')


@router.message(F.text.startswith('Удалить баланс'))
async def delete_balance_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    await state.clear()
    await message.answer('<b>Напишите ID пользователя</b>')
    await state.set_state(BalanceForm.user_id)
    await state.update_data(action='delete')


@router.message(BalanceForm.user_id)
async def find_user_balance_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    user = await get_user(user_id=message.text)
    if user is None:
        await message.answer('Пользователь не найден!', reply_markup=admin_start_keyboard)
        await state.clear()
    else:
        await message.answer(text=f'👤 Пользователь: {user.username} \n\n'
                                  f'🏦 Баланс: {user.balance}₽ \n\n'
                                  f'👾 ID: {user.id} \n\n\n'
                                  f'<b>Введите сумму!</b>')
        await state.set_state(BalanceForm.amount)
        await state.update_data(user_id=user.id)


@router.message(BalanceForm.amount)
async def amount_balance_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    amount = message.text
    context = await state.get_data()
    if context['action'] == 'add':
        balance, tg_id = await add_balance(user_id=context['user_id'], amount=amount)
    else:
        balance, tg_id = await delete_balance(user_id=context['user_id'], amount=amount)
    await message.answer('<b>Баланс пользователя изменен!</b>\n'
                         f'Баланс: {balance}₽ ')
    await bot.send_message(chat_id=tg_id, text=f"<b>Ваш баланс изменен!\n"
                                               f"Баланс: {balance}₽</b>")
    await state.clear()



@router.message(F.text == 'Удалить категорию')
async def delete_category_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    if is_admin:
        await state.clear()
        categories = await get_categories()
        await message.delete()
        await message.answer(text='Выберите категорию:',
                             reply_markup=await delete_category_keyboard(categories))


@router.callback_query(F.data.startswith('delete category'))
async def final_delete_category_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    category_id = call.data.split()[-1]
    category = await delete_category(category_id)
    if category is not None:
        await call.message.edit_text(text='Категория успешно удалена!')
    await call.message.answer(text='Вы в главном меню!',
                              reply_markup=admin_start_keyboard)


@router.message(F.text == 'Статистика бота')
async def stats_admin_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    if is_admin:
        await state.clear()
        (count_users, count_tasks,
         count_final_tasks, count_active_tasks,
         count_pending_tasks, total_balance) = await get_admin_stats()
        await message.answer(text=f'Количество юзеров: {count_users}\n'
                                  f'Количество задач: {count_tasks}\n'
                                  f'Из них законченных: {count_final_tasks}\n'
                                  f'Количество активных задач: {count_active_tasks}\n'
                                  f'Количество задач в холде: {count_pending_tasks}\n'
                                  f'Общий баланс юзеров: {total_balance}\n')


@router.message(F.text == 'Найти пользователя')
async def find_user_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    if is_admin:
        await message.answer('Введите ID пользователя')
        await state.set_state(UserForm.user_id)


@router.message(UserForm.user_id)
async def user_data_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    user_id = message.text
    try:
        user_id = int(user_id)
        user, pending_tasks, count_ref = await get_profile_by_id(user_id)
        text_pending_tasks = ' \n'
        for task in pending_tasks:
            text_pending_tasks += f'{task.title} | {task.reward}₽ \n'
        await message.answer(
            text=f'<b>👤 Пользователь: {user.username} \n\n'
                 f'🏦 Баланс: {user.balance}₽ \n\n'
                 f'👾 ID: {user.id} \n\n'
                 f'💰Количество рефералов: {count_ref}\n'
                 f'Процент реферальной программы: {user.referral_percent}%\n'
                 f'📥Задания на проверке: {text_pending_tasks} \n</b>',
            reply_markup=await referral_percent_keyboard(user_id))

    except Exception as e:
        await message.answer('Неверный формат ID')
        print(e)


@router.callback_query(F.data.startswith('change referral percent'))
async def change_ref_handler(callback: CallbackQuery, bot: Bot, is_admin: bool, state: FSMContext):
    user_id = int(callback.data.split()[-1])
    await state.update_data(user_id=user_id)
    await callback.message.edit_text(text='Введите процент реферальной программы')
    await state.set_state(UserForm.referral_percent)


@router.message(UserForm.referral_percent)
async def add_ref_handler(message: Message, bot: Bot, is_admin: bool, state: FSMContext):
    ref_percent = message.text
    try:
        ref_percent = int(ref_percent)

        user_id = (await state.get_data())['user_id']
        await change_referral_percent(ref_percent, user_id)
        user, pending_tasks, count_ref = await get_profile_by_id(user_id)
        text_pending_tasks = ' \n'
        for task in pending_tasks:
            text_pending_tasks += f'{task.title} | {task.reward}₽ \n'
        await message.answer(
            text=f'<b>Процент изменён!\n\n'
                 f'👤 Пользователь: {user.username} \n\n'
                 f'🏦 Баланс: {user.balance}₽ \n\n'
                 f'👾 ID: {user.id} \n\n'
                 f'💰Количество рефералов: {count_ref}\n'
                 f'Процент реферальной программы: {user.referral_percent}%\n'
                 f'📥Задания на проверке: {text_pending_tasks} \n</b>',
            reply_markup=await referral_percent_keyboard(user_id))

    except Exception as e:
        await message.answer('Неверный формат ID')
        print(e)
