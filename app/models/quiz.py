"""
QuizSession ve QuizAnswer modelleri — flask_mysqldb ile çalışır.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class QuizSession:
    id: Optional[int] = None
    user_id: Optional[int] = None
    unite_id: Optional[int] = None      # PHP API ünite ID
    quiz_type: str = ""                 # multiple_choice | matching | flashcard | fill_blank
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    @staticmethod
    def from_row(row: dict) -> "QuizSession":
        return QuizSession(
            id=row.get("id"),
            user_id=row.get("user_id"),
            unite_id=row.get("unite_id"),
            quiz_type=row.get("quiz_type", ""),
            started_at=row.get("started_at"),
            finished_at=row.get("finished_at"),
        )


@dataclass
class QuizAnswer:
    id: Optional[int] = None
    session_id: Optional[int] = None
    kavram_id: Optional[int] = None    # PHP API kavram ID
    given_answer: Optional[str] = None
    is_correct: bool = False

    @staticmethod
    def from_row(row: dict) -> "QuizAnswer":
        return QuizAnswer(
            id=row.get("id"),
            session_id=row.get("session_id"),
            kavram_id=row.get("kavram_id"),
            given_answer=row.get("given_answer"),
            is_correct=bool(row.get("is_correct", 0)),
        )
