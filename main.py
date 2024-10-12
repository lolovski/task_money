import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from task_money.middleware.admin_panel import AdminMiddleware
from task_money.middleware.user import UserChannelMiddleware


dp = Dispatcher()


dot = load_dotenv('.env')

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp.update.middleware.register(UserChannelMiddleware(bot=bot))
dp.update.middleware.register(AdminMiddleware())


async def main() -> None:
    # wait async_main()
    # await add_visits()
    from task_money.handlers.basic import router as basic_router
    dp.include_router(basic_router)
    from task_money.handlers.start import router as start_router
    dp.include_router(start_router)
    from task_money.handlers.profile import router as profile_router
    dp.include_router(profile_router)
    from task_money.handlers.admin_panel import router as admin_panel_router
    dp.include_router(admin_panel_router)
    from task_money.handlers.task import router as task_router
    dp.include_router(task_router)
    from task_money.handlers.admin_tasks import router as admin_task_router
    dp.include_router(admin_task_router)
    from task_money.handlers.referral_system import router as referral_system_router
    dp.include_router(referral_system_router)
    from task_money.handlers.help import router as help_router
    dp.include_router(help_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
