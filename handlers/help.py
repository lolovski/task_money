import os

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dotenv import load_dotenv

from keyboard.reply.start import start_keyboard

load_dotenv()
admin_id = os.getenv('ADMIN_ID')
router = Router(name=__name__)

class HelpForm(StatesGroup):
    text = State()


@router.message(F.text.startswith('Помощь'))
async def help_handler(message: Message, bot: Bot, tg_id: str, state: FSMContext):
    await state.clear()
    await message.answer_sticker('CAACAgEAAxkBAAIU82cJOaO2Eoa35Ye3LsQDOmYEZrQOAAIFAwACsDEZRD6QIu2pBJeJNgQ')
    await message.answer("<b>Подробно опишите свою проблему\n"
                         "Укажите свой ID (см. Профиль)\n"
                         "При необходимости укажите название задания\n\n"
                         "Укажите свой профиль телеграм, и мы вам ответим</b>")
    await state.set_state(HelpForm.text)

@router.message(HelpForm.text)
async def help_text_handler(message: Message, bot: Bot, tg_id: str, state: FSMContext):
    await message.answer('<b>Проблема отправлена админу и уже решается</b>', reply_markup=start_keyboard)
    await bot.send_message(chat_id=str(admin_id), text=f'<b>Новое обращение в поддержку!</b>\n\n'
                                                       f'{message.text}\n\n'
                                                       f'telegram_id: {tg_id}')

    await state.clear()