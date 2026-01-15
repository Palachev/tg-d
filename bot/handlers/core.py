from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from bot.analysis import analyze_answers
from bot.session import SessionManager

router = Router()

INTRO_TEXT = (
    "Этот бот не даёт советов. Он задаёт вопросы. "
    "Отвечай честно — только для себя."
)

WARNING_TEXT = "Никто не увидит твои ответы. Они используются только для анализа."


@router.message(Command("start"))
async def start_handler(message: Message, session_manager: SessionManager) -> None:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Начать")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(INTRO_TEXT)
    await message.answer(WARNING_TEXT, reply_markup=keyboard)


@router.message(Command("reset"))
async def reset_handler(message: Message, session_manager: SessionManager) -> None:
    session_manager.reset_session(message.from_user.id)
    await message.answer(
        "Сессия сброшена. Если готов, нажми «Начать».",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Начать")]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


@router.message()
async def message_handler(message: Message, session_manager: SessionManager) -> None:
    text = (message.text or "").strip()
    if not text:
        return

    if text.lower() == "начать":
        if not session_manager.can_start(message.from_user.id):
            await message.answer(
                "Прошлая сессия была недавно. Вернись через 7 дней для нового анализа.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return
        session_manager.start_session(message.from_user.id, locale="ru")
        first_question = session_manager.current_question(message.from_user.id)
        await message.answer(first_question, reply_markup=ReplyKeyboardRemove())
        return

    session = session_manager.get_session(message.from_user.id)
    if not session:
        await message.answer("Нажми «Начать», чтобы запустить сессию самоанализа.")
        return

    session_manager.record_answer(message.from_user.id, text)
    if session_manager.is_complete(message.from_user.id):
        answers = session_manager.finalize(message.from_user.id)
        result = analyze_answers(answers)
        await message.answer(_format_report(result))
        return

    next_question = session_manager.current_question(message.from_user.id)
    if next_question:
        await message.answer(next_question)


def _format_report(result: dict) -> str:
    summary = result["summary"]
    strengths = "\n".join(f"• {item}" for item in result["strengths"])
    growth = "\n".join(f"• {item}" for item in result["growth"])
    conclusion = result["conclusion"]
    return (
        "Твой отчёт:\n\n"
        f"Резюме: {summary}\n\n"
        f"Сильные стороны:\n{strengths}\n\n"
        f"Зоны роста:\n{growth}\n\n"
        f"Честный вывод: {conclusion}"
    )
