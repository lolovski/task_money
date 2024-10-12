import os
from typing import Callable, Awaitable, Any, Dict

from aiogram import BaseMiddleware
from aiogram import Bot
from aiogram.types import Message
from aiogram.types import Update
from dotenv import load_dotenv

load_dotenv()

admin_id = os.getenv('ADMIN_ID')
channels = [['-1001992734440', 'https://t.me/+sYXDBJmF7jo2ZGIy'], ['-1002081507096', 'https://t.me/+UlaqmVGZgCJlM2Ri']]


class UserChannelMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        text = ('Вы не подписаны на канал!\n'
                'Нажмите /start, чтобы продолжить')
        current_event = event.message or event.callback_query
        if not current_event:
            return await handler(event, data)
        tg_id = current_event.from_user.id
        data['tg_id'] = tg_id
        user_chanel_status1 = await self.bot.get_chat_member(chat_id=channels[0][0], user_id=current_event.from_user.id)
        user_chanel_status2 = await self.bot.get_chat_member(chat_id=channels[1][0], user_id=current_event.from_user.id)
        if isinstance(current_event, Message):
            if current_event.text is None:
                return await handler(event, data)
            if current_event.text.startswith('/start'):
                return await handler(event, data)
            if user_chanel_status1.status == 'left' or user_chanel_status2.status == "left":
                return await current_event.answer(text)
            return await handler(event, data)

        else:
            if current_event.data == 'check_subscription':
                return await handler(event, data)
            if user_chanel_status1.status == 'left' or user_chanel_status2.status == 'left':
                await current_event.message.edit_reply_markup()
                return await current_event.messag.answer(text)
            return await handler(event, data)








