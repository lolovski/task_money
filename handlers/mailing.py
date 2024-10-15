import os

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from database.requests.admin_panel import add_balance, delete_balance
from database.requests.category import get_categories, set_category, delete_category
from database.requests.task import set_task
from database.requests.user import add_money, get_user, get_users
from keyboard.inline.admin_panel import category_selection_keyboard, \
    confirm_add_task_keyboard, delete_category_keyboard
from keyboard.reply.admin_panel import admin_start_keyboard
from utils.mailing import mailing_task
from keyboard.inline.mailing import get_final_post_keyboard, get_check_post_keyboard
from database.requests.admin_panel import get_admin_stats

load_dotenv()
admin_id = os.getenv('ADMIN_ID')
router = Router(name=__name__)


class MailingForm(StatesGroup):
    text = State()
    photo = State()
    button_name = State()
    button_url = State()

    message_id = State()



@router.message(F.text == "Рассылка")
async def mailing_handler(message: Message, bot: Bot, state: FSMContext, is_admin: bool):
    if is_admin:
        await state.clear()
        await message.delete()
        answer = await message.answer('Отправьте <b>текст</b> поста')
        await state.set_state(MailingForm.text)
        await state.update_data(message_id=answer.message_id)

@router.message(MailingForm.text)
async def mailing_text_handler(message: Message, bot: Bot, state: FSMContext, is_admin: bool):
    text = message.text
    context = await state.get_data()
    await message.delete()
    answer = await bot.edit_message_text(text='Напишите <b>текст</b> кнопки',
                                         chat_id=message.chat.id, message_id=context['message_id'])
    await state.set_state(MailingForm.button_name)
    await state.update_data(message_id=answer.message_id)
    await state.update_data(text=text)


@router.message(MailingForm.button_name)
async def mailing_button_name_handler(message: Message, bot: Bot, state: FSMContext, is_admin: bool):
    button_name = message.text
    context = await state.get_data()
    await message.delete()
    answer = await bot.edit_message_text(text='Отправьте <b>Ссылку</b> кнопки',
                                         chat_id=message.chat.id, message_id=context['message_id'])
    await state.set_state(MailingForm.button_url)
    await state.update_data(button_name=button_name)
    await state.update_data(message_id=answer.message_id)


@router.message(MailingForm.button_url)
async def mailing_button_url_handler(message: Message, bot: Bot, state: FSMContext, is_admin: bool):
    button_url = message.text
    context = await state.get_data()
    await message.delete()
    answer = await bot.edit_message_text(text='Отправьте <b>фото</b> поста',
                                         chat_id=message.chat.id, message_id=context['message_id'])
    await state.set_state(MailingForm.photo)
    await state.update_data(button_url=button_url)
    await state.update_data(message_id=answer.message_id)


@router.message(MailingForm.photo)
async def mailing_photo_handler(message: Message, bot: Bot, state: FSMContext, is_admin: bool):
    if message.photo is not None:
        context = await state.get_data()
        photo = message.photo[-1]
        context = await state.get_data()
        await message.delete()
        await bot.delete_message(chat_id=message.chat.id, message_id=context['message_id'])
        try:
            answer = await message.answer_photo(
                photo=photo.file_id,
                caption=context['text'],
                reply_markup=await get_check_post_keyboard(context['button_name'], context['button_url'])
            )

            await state.update_data(photo=photo.file_id)
            await state.update_data(message_id=answer.message_id)
            await message.answer(
                text='Рассылать?',
                reply_markup=await get_final_post_keyboard()
            )
        except:
            await state.clear()

            await message.answer('Некорректные данные!\n'
                                 'Вы в главном меню',
                                 reply_markup=admin_start_keyboard)


@router.callback_query(F.data == 'mailing post cancel')
async def mailing_cancel_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    context = await state.get_data()
    await state.clear()
    await call.message.delete()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=context['message_id'])

    await call.message.answer(text='Вы в главном меню', reply_markup=admin_start_keyboard)


@router.callback_query(F.data == 'mailing post final')
async def mailing_final_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    context = await state.get_data()
    await state.clear()
    await call.message.delete()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=context['message_id'])
    await call.message.answer(text='Рассылка началась', reply_markup=admin_start_keyboard)
    await mailing(bot, context)


async def mailing(bot: Bot, context):
    users = await get_users()
    for user in users:

        await bot.send_photo(chat_id=user.tg_id, photo=context['photo'],
                             caption=context['text'], reply_markup=await get_check_post_keyboard(context['button_name'], context['button_url']))
