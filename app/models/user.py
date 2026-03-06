"""
User modeli — flask_mysqldb ile çalışır.
SQLAlchemy ORM'den bağımsız saf Python sınıfı.
Flask-Login için UserMixin miras alınır.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from flask_login import UserMixin


@dataclass
class User(UserMixin):
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    password_hash: str = ""
    grade: Optional[int] = None        # 5, 6, 7 veya 8
    total_score: int = 0
    created_at: Optional[datetime] = None

    # Flask-Login get_id() — UserMixin bunu id üzerinden döndürür
    def get_id(self):
        return str(self.id)

    @staticmethod
    def from_row(row: dict) -> "User":
        """DictCursor satırından User nesnesi oluşturur."""
        return User(
            id=row.get("id"),
            name=row.get("name", ""),
            email=row.get("email", ""),
            password_hash=row.get("password_hash", ""),
            grade=row.get("grade"),
            total_score=row.get("total_score", 0),
            created_at=row.get("created_at"),
        )
