import asyncio
import logging

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI

from bot.handlers import search as search_handler
from routers import search

load_dotenv()

logger = logging.getLogger(__name__)

BOT_TOKEN = getenv("BOT_TOKEN")

async def start_bot():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(search_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Telegram bot started")
    await dp.start_polling(bot)


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot_task = asyncio.create_task(start_bot())
    yield
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        logger.info("Telegram bot stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(search.router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Go to 127.0.0.1/docs"}