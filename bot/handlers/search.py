from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.search import search_listings
from bot.services.formatter import format_listings_message
from bot.keyboards.search import main_keyboard, next_keyboard

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
        "Що шукаємо? (наприклад: <code>Iphone 17</code>):",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(SearchState.waiting_for_query)
async def handle_query(message: Message, state: FSMContext):
    query = message.text.strip()
    await state.clear()
    await message.answer("Шукаю…", reply_markup=main_keyboard())
    await _send_results(message, query, offset=0)


@router.callback_query(F.data.startswith("next:"))
async def callback_next_page(call: CallbackQuery):
    _, query, offset_str = call.data.split(":", 2)
    await call.answer()
    await _send_results(call.message, query, offset=int(offset_str))


async def _send_results(message: Message, query: str, offset: int = 0):
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
    kb = next_keyboard(query, offset + RESULTS_PER_PAGE) if has_more else None

    await message.answer(header + body, disable_web_page_preview=True, reply_markup=kb)