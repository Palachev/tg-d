import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from bot.handlers.core import router
from bot.session import SessionManager


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is required")

    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    dispatcher["session_manager"] = SessionManager()

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
