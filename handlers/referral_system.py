from aiogram import F, Router, Bot
from aiogram.types import Message

from aiogram.utils.deep_linking import create_start_link


router = Router(name=__name__)


@router.message(F.text.startswith('Реферальная система'))
async def referral_menu_handler(message: Message, bot: Bot, tg_id: str):
    link = await create_start_link(payload=str(tg_id), encode=True, bot=bot)
    await message.answer_sticker(sticker='CAACAgEAAxkBAAIU6mcIG1GJjS4Dd3MUQAABeYKCalVReQAC-gQAAmvBIEQ5S8LcHjikGTYE')
    await message.answer(text='<b>❗️Реферал - это человек, который впервые заходит в бота по вашей ссылке. Когда человек зайдёт в бота по вашей ссылке, он навсегда становится вашим рефералом.' 
                              '- Когда ваш Реферал получает выплату за задание вы получаете <b>10% от его заработка на ваш баланс</b>.\n\n'
                              '✅ Приглашайте новых пользователей и получайте пассивный доход от их заработка!\n\n'
                              '👁‍🗨 Ссылка для привлечения рефералов: \n</b>'
                              f'<code>{link}</code>'
                         )