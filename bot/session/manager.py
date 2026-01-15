from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import os
from typing import Dict, List, Optional

from bot.questions import get_questions


@dataclass
class SessionState:
    locale: str
    started_at: datetime
    answers: List[str] = field(default_factory=list)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: Dict[str, SessionState] = {}
        self._last_completed: Dict[str, datetime] = {}
        self._salt = os.getenv("BOT_SALT", "honestly-about-yourself")
        self._cooldown = timedelta(days=7)

    def _hash_user(self, user_id: int) -> str:
        digest = hashlib.sha256(f"{self._salt}:{user_id}".encode("utf-8")).hexdigest()
        return digest

    def can_start(self, user_id: int) -> bool:
        key = self._hash_user(user_id)
        last_done = self._last_completed.get(key)
        if not last_done:
            return True
        return datetime.now(timezone.utc) - last_done >= self._cooldown

    def start_session(self, user_id: int, locale: str = "ru") -> SessionState:
        key = self._hash_user(user_id)
        state = SessionState(locale=locale, started_at=datetime.now(timezone.utc))
        self._sessions[key] = state
        return state

    def reset_session(self, user_id: int) -> None:
        key = self._hash_user(user_id)
        self._sessions.pop(key, None)

    def get_session(self, user_id: int) -> Optional[SessionState]:
        return self._sessions.get(self._hash_user(user_id))

    def record_answer(self, user_id: int, answer: str) -> None:
        session = self.get_session(user_id)
        if not session:
            raise ValueError("Session not found")
        session.answers.append(answer.strip())

    def current_question(self, user_id: int) -> Optional[str]:
        session = self.get_session(user_id)
        if not session:
            return None
        questions = get_questions(session.locale)
        if len(session.answers) >= len(questions):
            return None
        return questions[len(session.answers)]

    def is_complete(self, user_id: int) -> bool:
        session = self.get_session(user_id)
        if not session:
            return False
        return len(session.answers) >= len(get_questions(session.locale))

    def finalize(self, user_id: int) -> List[str]:
        session = self.get_session(user_id)
        if not session:
            raise ValueError("Session not found")
        key = self._hash_user(user_id)
        self._last_completed[key] = datetime.now(timezone.utc)
        self._sessions.pop(key, None)
        return session.answers
