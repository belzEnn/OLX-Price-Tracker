from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.search import search_listings
from services.subscription import subscribe, unsubscribe, get_subscriptions, is_subscribed
from bot.services.formatter import format_listings_message
from bot.keyboards.search import main_keyboard, results_keyboard

router = Router()

RESULTS_PER_PAGE = 5


class SearchState(StatesGroup):
    waiting_for_query = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 <b>Привіт!</b>\n\n"
        "Натисни кнопку щоб шукати оголошення",
        reply_markup=main_keyboard(),
    )


@router.message(F.text == "Пошук")
async def btn_search(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_for_query)
    await message.answer(
        "Що шукаємо? (наприклад: <code>iPhone 14</code>):",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text == "Мої підписки")
async def btn_subscriptions(message: Message):
    subs = await get_subscriptions(message.from_user.id)

    if not subs:
        await message.answer("У тебе поки немає підписок 🤷", reply_markup=main_keyboard())
        return

    text = "🔔 <b>Твої підписки:</b>\n\n" + "\n".join(f"• {q}" for q in subs)
    await message.answer(text, reply_markup=main_keyboard())


@router.message(SearchState.waiting_for_query)
async def handle_query(message: Message, state: FSMContext):
    query = message.text.strip()
    await state.clear()
    await message.answer("Шукаю…", reply_markup=main_keyboard())
    await _send_results(message, query, offset=0, user_id=message.from_user.id)


@router.callback_query(F.data.startswith("next:"))
async def callback_next_page(call: CallbackQuery):
    _, query, offset_str = call.data.split(":", 2)
    await call.answer()
    await _send_results(call.message, query, offset=int(offset_str), user_id=call.from_user.id)


@router.callback_query(F.data.startswith("sub:"))
async def callback_subscribe(call: CallbackQuery):
    query = call.data[4:]
    await subscribe(call.from_user.id, query)
    await call.answer(f"🔔 Підписка на «{query}» активована!", show_alert=False)
    kb = results_keyboard(query, next_offset=0, has_more=False, subscribed=True)
    await call.message.edit_reply_markup(reply_markup=kb)


@router.callback_query(F.data.startswith("unsub:"))
async def callback_unsubscribe(call: CallbackQuery):
    query = call.data[6:]
    await unsubscribe(call.from_user.id, query)
    await call.answer(f"🔕 Підписку скасовано", show_alert=False)
    kb = results_keyboard(query, next_offset=0, has_more=False, subscribed=False)
    await call.message.edit_reply_markup(reply_markup=kb)


async def _send_results(message: Message, query: str, offset: int, user_id: int):
    try:
        listings = await search_listings(query, limit=RESULTS_PER_PAGE, offset=offset)
    except Exception as e:
        await message.answer(f"❌ Помилка при пошуку:\n<code>{e}</code>")
        return

    if not listings:
        await message.answer("😕 Нічого не знайдено." if offset == 0 else "Більше результатів немає.")
        return

    header = f"<b>{query}:</b>\n\n"
    body = format_listings_message(listings)

    has_more = len(listings) >= RESULTS_PER_PAGE
    next_offset = offset + RESULTS_PER_PAGE
    subscribed = await is_subscribed(user_id, query)

    kb = results_keyboard(query, next_offset, has_more, subscribed)
    await message.answer(header + body, disable_web_page_preview=True, reply_markup=kb)
