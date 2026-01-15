from bot.questions.questions_ru import QUESTIONS_RU


def get_questions(locale: str = "ru") -> list[str]:
    if locale == "ru":
        return QUESTIONS_RU
    raise ValueError(f"Unsupported locale: {locale}")
