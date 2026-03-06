"""
Progress modeli — flask_mysqldb ile çalışır.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Progress:
    id: Optional[int] = None
    user_id: Optional[int] = None
    unite_id: Optional[int] = None     # PHP API ünite ID
    konu_id: Optional[int] = None      # PHP API konu ID (opsiyonel)
    status: str = "locked"             # locked | in_progress | completed | skipped
    updated_at: Optional[datetime] = None

    @staticmethod
    def from_row(row: dict) -> "Progress":
        return Progress(
            id=row.get("id"),
            user_id=row.get("user_id"),
            unite_id=row.get("unite_id"),
            konu_id=row.get("konu_id"),
            status=row.get("status", "locked"),
            updated_at=row.get("updated_at"),
        )
