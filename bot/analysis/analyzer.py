from __future__ import annotations

from collections import Counter
from typing import Dict, List, Tuple


KEYWORDS = {
    "fear": ["страх", "бою", "боишь", "опас", "тревог"],
    "avoidance": ["избега", "убега", "пряч", "не хочу", "отклады"],
    "procrastination": ["отклады", "потом", "завтра", "не сейчас"],
    "motivation": ["важно", "цель", "хочу", "мечта", "смысл"],
    "responsibility": ["ответствен", "должен", "обязан", "вина"],
}

PATTERN_LABELS = {
    "fear": "страх",
    "avoidance": "избегание",
    "procrastination": "прокрастинация",
    "motivation": "внутренняя мотивация",
    "responsibility": "уровень ответственности",
}


def _count_patterns(answers: List[str]) -> Counter:
    counter: Counter = Counter()
    for answer in answers:
        lower = answer.lower()
        for key, tokens in KEYWORDS.items():
            if any(token in lower for token in tokens):
                counter[key] += 1
    return counter


def _top_patterns(counter: Counter, limit: int = 5) -> List[Tuple[str, int]]:
    if not counter:
        return []
    return counter.most_common(limit)


def analyze_answers(answers: List[str]) -> Dict[str, List[str] | str]:
    counter = _count_patterns(answers)
    patterns = [PATTERN_LABELS[key] for key, _ in _top_patterns(counter, 5)]

    summary_parts = [
        "Ты отвечал последовательно и без возможности вернуться к прошлым вопросам.",
        "В ответах заметны повторяющиеся темы, которые формируют твой фон самоощущения.",
    ]
    if patterns:
        summary_parts.append(
            "Наиболее явно проявились: " + ", ".join(patterns[:3]) + "."
        )
    else:
        summary_parts.append("Повторяющиеся темы выражены слабо, картина скорее разрозненная.")
    summary_parts.extend(
        [
            "Это не диагноз, а отражение того, что ты сам описал своими словами.",
            "Отчёт фиксирует именно твоё восприятие, без интерпретаций и советов.",
        ]
    )

    strengths = _derive_strengths(answers, counter)
    growth = _derive_growth_zones(answers, counter)
    honest_conclusion = _honest_conclusion(counter)

    return {
        "summary": " ".join(summary_parts),
        "strengths": strengths,
        "growth": growth,
        "conclusion": honest_conclusion,
    }


def _derive_strengths(answers: List[str], counter: Counter) -> List[str]:
    strengths: List[str] = []
    if any("чест" in answer.lower() for answer in answers):
        strengths.append("Готовность замечать и признавать внутренние противоречия.")
    if counter.get("responsibility", 0) > 0:
        strengths.append("Осознание ответственности даже там, где она даётся тяжело.")
    if counter.get("motivation", 0) > 0:
        strengths.append("Наличие личных ориентиров и целей, которые ты всё ещё держишь в фокусе.")
    if not strengths:
        strengths = [
            "Способность фиксировать свои состояния без оправданий.",
            "Готовность смотреть на себя без внешней оценки.",
            "Внимательность к внутренним реакциям.",
        ]
    return strengths[:3]


def _derive_growth_zones(answers: List[str], counter: Counter) -> List[str]:
    growth: List[str] = []
    if counter.get("fear", 0) > 0:
        growth.append("Страх часто задаёт тон решениям и сужает выбор.")
    if counter.get("avoidance", 0) > 0:
        growth.append("Избегание вытесняет важные темы и откладывает изменения.")
    if counter.get("procrastination", 0) > 0:
        growth.append("Промедление становится привычной формой защиты.")
    if counter.get("motivation", 0) == 0:
        growth.append("Личные цели не звучат явно, из-за этого теряется внутренний фокус.")
    if counter.get("responsibility", 0) == 0:
        growth.append("Ответственность описывается размыто, из-за чего решения распадаются.")
    return growth[:3]


def _honest_conclusion(counter: Counter) -> str:
    if counter.get("avoidance", 0) or counter.get("procrastination", 0):
        return "Если ничего не менять, через год будет больше незавершённых историй и меньше ясности о себе."
    if counter.get("fear", 0):
        return "Если ничего не менять, через год страх будет по-прежнему диктовать границы твоей жизни."
    if counter.get("motivation", 0):
        return "Если ничего не менять, через год цели останутся прежними, а расстояние до них — тем же."
    return "Если ничего не менять, через год ты всё так же будешь искать честные ответы на себя без внешних опор."
