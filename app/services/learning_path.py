from __future__ import annotations

from typing import Any

from app.clients.kavram_api import get_unites


STEP_TYPES = {
    1: "multiple_choice",
    2: "flashcard",
    3: "matching",
    4: "fill_blank",
}

STEP_META = {
    1: {"title": "Kavrami Tani", "quiz_type": "multiple_choice"},
    2: {"title": "Flash Tekrar", "quiz_type": "flashcard"},
    3: {"title": "Eslestir", "quiz_type": "matching"},
    4: {"title": "Uygula", "quiz_type": "fill_blank"},
}


def _units_for_grade(grade: int) -> list[dict[str, Any]]:
    units = []
    for u in get_unites(grade=grade, per_page=300):
        try:
            units.append(
                {
                    "id": int(u.get("id", 0)),
                    "grade": int(u.get("grade", grade)),
                    "unit_no": int(u.get("unit_no", 1)),
                    "name": u.get("name", "Unite"),
                }
            )
        except (TypeError, ValueError):
            continue

    units = [x for x in units if x["id"] > 0]
    units.sort(key=lambda x: x["unit_no"])
    return units


def ensure_steps_for_user(user_id: int, grade: int, mysql) -> None:
    units = _units_for_grade(grade)
    if not units:
        return

    cur = mysql.connection.cursor()
    try:
        for idx, u in enumerate(units):
            default_status = "in_progress" if idx == 0 else "locked"
            for step_no in [1, 2, 3, 4]:
                cur.execute(
                    """
                    INSERT INTO progress_steps (user_id, unite_id, step_no, status)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = status
                    """,
                    (user_id, u["id"], step_no, default_status),
                )
        mysql.connection.commit()
    finally:
        cur.close()


def get_path_for_user(user_id: int, grade: int, mysql) -> list[dict[str, Any]]:
    ensure_steps_for_user(user_id, grade, mysql)

    units = _units_for_grade(grade)
    if not units:
        return []

    cur = mysql.connection.cursor()
    try:
        unit_ids = [u["id"] for u in units]
        fmt = ",".join(["%s"] * len(unit_ids))
        cur.execute(
            f"""
            SELECT unite_id, step_no, status
            FROM progress_steps
            WHERE user_id=%s AND unite_id IN ({fmt})
            ORDER BY unite_id, step_no
            """,
            [user_id] + unit_ids,
        )
        rows = cur.fetchall()
    finally:
        cur.close()

    by_unit: dict[int, dict[int, str]] = {}
    for r in rows:
        by_unit.setdefault(r["unite_id"], {})[r["step_no"]] = r["status"]

    path = []
    for u in units:
        steps = []
        unit_steps = by_unit.get(u["id"], {})
        completed_count = 0
        for step_no in [1, 2, 3, 4]:
            status = unit_steps.get(step_no, "locked")
            if status == "completed":
                completed_count += 1
            meta = STEP_META[step_no]
            steps.append(
                {
                    "step_no": step_no,
                    "status": status,
                    "title": meta["title"],
                    "quiz_type": meta["quiz_type"],
                }
            )

        path.append(
            {
                "unit_id": u["id"],
                "unit_no": u["unit_no"],
                "name": u["name"],
                "steps": steps,
                "progress_pct": int(completed_count / 4 * 100),
                "completed": completed_count == 4,
            }
        )

    return path


def unlock_next_step(user_id: int, unit_id: int, completed_step: int, grade: int, mysql) -> None:
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            """
            UPDATE progress_steps
            SET status='completed', completed_at=UTC_TIMESTAMP()
            WHERE user_id=%s AND unite_id=%s AND step_no=%s
            """,
            (user_id, unit_id, completed_step),
        )

        next_step = completed_step + 1
        if next_step <= 4:
            cur.execute(
                """
                UPDATE progress_steps
                SET status='in_progress'
                WHERE user_id=%s AND unite_id=%s AND step_no=%s AND status='locked'
                """,
                (user_id, unit_id, next_step),
            )
        else:
            # unite bitti -> sonraki unite step1 ac
            units = _units_for_grade(grade)
            ids = [u["id"] for u in units]
            if unit_id in ids:
                idx = ids.index(unit_id)
                if idx + 1 < len(ids):
                    next_unit = ids[idx + 1]
                    cur.execute(
                        """
                        UPDATE progress_steps
                        SET status='in_progress'
                        WHERE user_id=%s AND unite_id=%s AND step_no=1 AND status='locked'
                        """,
                        (user_id, next_unit),
                    )

        mysql.connection.commit()
    finally:
        cur.close()


def can_start_quiz(user_id: int, unit_id: int, quiz_type: str, mysql) -> bool:
    expected_step = None
    for step_no, qtype in STEP_TYPES.items():
        if qtype == quiz_type:
            expected_step = step_no
            break
    if expected_step is None:
        return False

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            """
            SELECT status FROM progress_steps
            WHERE user_id=%s AND unite_id=%s AND step_no=%s
            """,
            (user_id, unit_id, expected_step),
        )
        row = cur.fetchone()
    finally:
        cur.close()

    if not row:
        return False
    return row["status"] in ("in_progress", "completed")
