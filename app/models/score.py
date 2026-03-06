"""
Score modeli — flask_mysqldb ile çalışır.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Score:
    id: Optional[int] = None
    user_id: Optional[int] = None
    points: int = 0
    source_quiz_id: Optional[int] = None
    earned_at: Optional[datetime] = None

    @staticmethod
    def from_row(row: dict) -> "Score":
        return Score(
            id=row.get("id"),
            user_id=row.get("user_id"),
            points=row.get("points", 0),
            source_quiz_id=row.get("source_quiz_id"),
            earned_at=row.get("earned_at"),
        )
