import os
import re

from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.payload import decode_payload
from dotenv import load_dotenv

from database.requests.user import get_user_by_tg_id, set_user
from keyboard.inline.start import channel_url_keyboard, adopt_rules
from keyboard.reply.admin_panel import admin_start_keyboard
from keyboard.reply.start import start_keyboard

load_dotenv()
router = Router(name=__name__)

channels = [['-1001992734440', 'https://t.me/+sYXDBJmF7jo2ZGIy'], ['-1002081507096', 'https://t.me/+UlaqmVGZgCJlM2Ri']]
admin_id = os.getenv("ADMIN_ID")

class UserForm(StatesGroup):
    referral_id = State()


@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot, command: CommandObject, tg_id: str, is_admin: bool, state: FSMContext) -> None:
    await state.set_state(UserForm.referral_id)
    if is_admin:
        await state.clear()
        return await message.answer("<b>Добро пожаловать, хозяин!</b>", reply_markup=admin_start_keyboard)
    args = command.args
    if args is not None:
        referral_id = decode_payload(args)
    else:
        referral_id = None
    await state.update_data(referral_id=referral_id)
    user = await get_user_by_tg_id(tg_id)
    username = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ\s]', '', message.from_user.full_name)
    user_chanel_status1 = await bot.get_chat_member(chat_id=channels[0][0], user_id=tg_id)
    user_chanel_status2 = await bot.get_chat_member(chat_id=channels[1][0], user_id=tg_id)
    if user_chanel_status1.status == 'left' or user_chanel_status2.status == 'left':
        await message.answer(f"<b>Добро пожаловать!\n"
                             f"Подпишитесь на наши каналы!</b>", reply_markup=channel_url_keyboard)
    else:
        if user is None:
            await set_user(tg_id, username, referral_id=referral_id)
            await message.answer("<b>Добро пожаловать!\n"
                                 "Чтобы начать задание нажмите кнопку Приступить к заданию</b>",
                                 reply_markup=adopt_rules)
        else:
            await message.answer(f"<b>С возвращением!\n</b>",
                                 reply_markup=start_keyboard)
        await state.clear()


@router.callback_query(F.data == 'check_subscription')
async def check_subscription_handler(call: CallbackQuery, bot: Bot, state: FSMContext, tg_id: str) -> None:
    username = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ\s]', '', call.from_user.full_name)
    user_chanel_status1 = await bot.get_chat_member(chat_id=channels[0][0], user_id=tg_id)
    user_chanel_status2 = await bot.get_chat_member(chat_id=channels[1][0], user_id=tg_id)
    if user_chanel_status1.status == 'left' or user_chanel_status2.status == 'left':
        await bot.answer_callback_query(callback_query_id=call.id,
            text='Вы не подписаны!', show_alert=True,)
        await call.answer()
    else:
        user = await get_user_by_tg_id(tg_id)
        if user is None:
            context = await state.get_data()
            await set_user(tg_id, username, referral_id=context['referral_id'])
            await state.clear()
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await call.message.answer(text="<b>Вы успешно вошли!\n\n"
                                       "Чтобы начать задание нажмите кнопку <b>Приступить к заданию</b></b>",
                                  reply_markup=adopt_rules)
        await call.answer()


@router.callback_query(F.data == 'adopt rules')
async def adopt_rules_handler(call: CallbackQuery, bot: Bot) -> None:
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(text='<b>Чтобы начать задание нажмите кнопку <b>Задания</b></b>', reply_markup=start_keyboard)

    await call.answer()


@router.message(F.text == 'Задания')
async def start_task_handler(message: Message) -> None:
    await message.answer(text='Чтобы начать задание нажмите кнопку <b>Задания</b>',
                              reply_markup=start_keyboard)


