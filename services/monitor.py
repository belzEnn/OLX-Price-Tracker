import asyncio
import logging
from os import getenv

from aiogram import Bot

from parsers.olx import fetch_listings
from services.subscription import get_all_subscriptions
from services.redis import is_seen, mark_seen
from bot.services.formatter import format_listing

logger = logging.getLogger(__name__)

POLL_INTERVAL = int(getenv("POLL_INTERVAL", "300"))


async def run_monitor(bot: Bot) -> None:
    logger.info(f"Monitor started, interval={POLL_INTERVAL}s")

    while True:
        subscriptions = await get_all_subscriptions()

        if not subscriptions:
            logger.debug("No active subscriptions")
        else:
            for chat_id, query in subscriptions:
                await _check(bot, chat_id, query)

        await asyncio.sleep(POLL_INTERVAL)


async def _check(bot: Bot, chat_id: int, query: str) -> None:
    try:
        listings = await fetch_listings(query, limit=40)
    except Exception as e:
        logger.error(f"Monitor fetch error [chat={chat_id}, query={query}]: {e}")
        return

    for listing in listings:
        if await is_seen(chat_id, query, listing.id):
            continue

        await mark_seen(chat_id, query, listing.id)

        try:
            text = f"🔔 <b>Нове оголошення по запиту «{query}»</b>\n\n" + format_listing(listing)
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"Monitor send error [chat={chat_id}, listing={listing.id}]: {e}")