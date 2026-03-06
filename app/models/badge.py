"""
Badge ve UserBadge modelleri — flask_mysqldb ile çalışır.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Badge:
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    condition_type: str = ""           # score | streak | unit_complete | quiz_count
    condition_value: int = 0
    icon: Optional[str] = None

    @staticmethod
    def from_row(row: dict) -> "Badge":
        return Badge(
            id=row.get("id"),
            name=row.get("name", ""),
            description=row.get("description"),
            condition_type=row.get("condition_type", ""),
            condition_value=row.get("condition_value", 0),
            icon=row.get("icon"),
        )


@dataclass
class UserBadge:
    id: Optional[int] = None
    user_id: Optional[int] = None
    badge_id: Optional[int] = None
    earned_at: Optional[datetime] = None

    @staticmethod
    def from_row(row: dict) -> "UserBadge":
        return UserBadge(
            id=row.get("id"),
            user_id=row.get("user_id"),
            badge_id=row.get("badge_id"),
            earned_at=row.get("earned_at"),
        )
