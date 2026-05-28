import asyncio
import logging

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI

from db.database import init_db
from bot.handlers import search as search_handler
from routers import search
from services.monitor import run_monitor

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = getenv("BOT_TOKEN")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialized")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(search_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)

    bot_task = asyncio.create_task(dp.start_polling(bot))
    monitor_task = asyncio.create_task(run_monitor(bot))

    yield

    monitor_task.cancel()
    bot_task.cancel()
    try:
        await asyncio.gather(monitor_task, bot_task)
    except asyncio.CancelledError:
        logger.info("Bot and monitor stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(search.router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Go to 127.0.0.1/docs"}
