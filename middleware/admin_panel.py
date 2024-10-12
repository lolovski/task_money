import os
from typing import Callable, Awaitable, Any, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from dotenv import load_dotenv

load_dotenv()

admin_id = os.getenv('ADMIN_ID')
channel_id = os.getenv("CHANNEL_ID")


class AdminMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        ...

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ):
        current_event = event.message or event.callback_query
        tg_id = current_event.from_user.id
        data['is_admin'] = (str(tg_id) == str(admin_id))
        return await handler(event, data)
