"""
Uygulama başlangıcında veritabanı tablolarını oluşturur.
Her tablo CREATE TABLE IF NOT EXISTS ile yazılmıştır — mevcut veriye dokunmaz.
badges tablosuna category/emoji/color kolonları eklenir ve 18 rozet seed edilir.
"""
from app.extensions import mysql

# ── 18 Rozet Kataloğu ─────────────────────────────────────────────────────────
# (name, description, condition_type, condition_value, emoji, category, color)
BADGES_CATALOG = [
    # Başlangıç — #4361EE
    ("İlk Adım",       "İlk quizini tamamladın!",       "quiz_count",    1,  "🌱", "baslangic",   "#4361EE"),
    ("Azimli",         "5 quiz tamamladın.",             "quiz_count",    5,  "💪", "baslangic",   "#4361EE"),
    ("Kararlı",        "10 quiz tamamladın.",            "quiz_count",    10, "🎯", "baslangic",   "#4361EE"),
    # Seri — #D9730D
    ("3 Gün Serisi",   "3 gün üst üste çalıştın.",      "streak",        3,  "🔥", "seri",        "#D9730D"),
    ("7 Gün Serisi",   "7 gün üst üste çalıştın.",      "streak",        7,  "⚡", "seri",        "#D9730D"),
    ("14 Gün Serisi",  "14 gün üst üste çalıştın.",     "streak",        14, "🌟", "seri",        "#D9730D"),
    ("30 Gün Serisi",  "30 gün üst üste çalıştın.",     "streak",        30, "🏅", "seri",        "#D9730D"),
    # Quiz Ustası — #7209B7
    ("Meraklı",        "25 quiz tamamladın.",            "quiz_count",    25, "🤓", "quiz",        "#7209B7"),
    ("Azimkar",        "50 quiz tamamladın.",            "quiz_count",    50, "📚", "quiz",        "#7209B7"),
    ("Quiz Ustası",    "100 quiz tamamladın.",           "quiz_count",    100,"🧠", "quiz",        "#7209B7"),
    ("Efsane",         "200 quiz tamamladın.",           "quiz_count",    200,"👑", "quiz",        "#7209B7"),
    # Mükemmellik — #059669
    ("Gümüş",          "500 puan kazandın.",             "score",         500,"🥈", "mukemmellik", "#059669"),
    ("Altın",          "1000 puan kazandın.",            "score",        1000,"🥇", "mukemmellik", "#059669"),
    ("Platin",         "5000 puan kazandın.",            "score",        5000,"💎", "mukemmellik", "#059669"),
    ("Elmas",          "10000 puan kazandın.",           "score",       10000,"💠", "mukemmellik", "#059669"),
    # Ünite — #0099B8
    ("İlk Ünite",      "İlk üniteni tamamladın.",        "unit_complete", 1,  "📖", "unite",       "#0099B8"),
    ("Gezgin",         "8 ünite tamamladın.",            "unit_complete", 8,  "🧭", "unite",       "#0099B8"),
    ("Mezun",          "16 ünite tamamladın.",           "unit_complete", 16, "🎓", "unite",       "#0099B8"),
]


def _column_exists(cur, table: str, column: str) -> bool:
    """INFORMATION_SCHEMA üzerinden kolon varlığını kontrol eder."""
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME   = %s
          AND COLUMN_NAME  = %s
    """, (table, column))
    return cur.fetchone()["cnt"] > 0


def _seed_badges(cur):
    """18 rozeti DB'ye yazar. Varsa category/emoji/color günceller, yoksa ekler."""
    for (name, desc, ctype, cval, emoji, category, color) in BADGES_CATALOG:
        cur.execute("SELECT id FROM badges WHERE name = %s", (name,))
        row = cur.fetchone()
        if row:
            cur.execute("""
                UPDATE badges
                SET description=%s, condition_type=%s, condition_value=%s,
                    emoji=%s, category=%s, color=%s
                WHERE id=%s
            """, (desc, ctype, cval, emoji, category, color, row["id"]))
        else:
            cur.execute("""
                INSERT INTO badges
                    (name, description, condition_type, condition_value, emoji, category, color)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, desc, ctype, cval, emoji, category, color))


def init_db(app):
    """Tüm tabloları oluşturur."""
    with app.app_context():
        cur = mysql.connection.cursor()

        # ── users ──────────────────────────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                name          VARCHAR(100)  NOT NULL,
                email         VARCHAR(150)  NOT NULL UNIQUE,
                password_hash VARCHAR(255)  NOT NULL,
                grade         INT           DEFAULT NULL COMMENT '9,10,11 veya 12',
                total_score   INT           NOT NULL DEFAULT 0,
                streak        INT           NOT NULL DEFAULT 0 COMMENT 'Güncel günlük seri (her quiz sonunda güncellenir)',
                created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
        """)

        # Mevcut users tablosuna streak kolonu güvenle ekle (migration)
        if not _column_exists(cur, "users", "streak"):
            cur.execute(
                "ALTER TABLE users ADD COLUMN streak INT NOT NULL DEFAULT 0 "
                "COMMENT 'Güncel günlük seri (her quiz sonunda güncellenir)'"
            )

        # ── progress ───────────────────────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id         INT AUTO_INCREMENT PRIMARY KEY,
                user_id    INT         NOT NULL,
                unite_id   INT         NOT NULL COMMENT 'PHP API ünite ID',
                konu_id    INT         DEFAULT NULL COMMENT 'PHP API konu ID (opsiyonel)',
                status     VARCHAR(20) NOT NULL DEFAULT 'locked'
                               COMMENT 'locked | in_progress | completed | skipped',
                updated_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_progress_user FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
        """)

        # ── quiz_sessions ──────────────────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                user_id     INT         NOT NULL,
                unite_id    INT         DEFAULT NULL COMMENT 'PHP API ünite ID',
                quiz_type   VARCHAR(50) NOT NULL
                                COMMENT 'multiple_choice | matching | flashcard | fill_blank',
                started_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
                finished_at DATETIME    DEFAULT NULL COMMENT 'NULL ise quiz devam ediyor',
                CONSTRAINT fk_qs_user FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
        """)

        # ── quiz_answers ───────────────────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quiz_answers (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                session_id   INT      NOT NULL,
                kavram_id    INT      NOT NULL COMMENT 'PHP API kavram ID',
                given_answer TEXT     DEFAULT NULL,
                is_correct   TINYINT(1) NOT NULL DEFAULT 0,
                CONSTRAINT fk_qa_session FOREIGN KEY (session_id)
                    REFERENCES quiz_sessions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
        """)

        # ── scores ─────────────────────────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id             INT AUTO_INCREMENT PRIMARY KEY,
                user_id        INT      NOT NULL,
                points         INT      NOT NULL DEFAULT 0,
                source_quiz_id INT      DEFAULT NULL,
                earned_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_score_user FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_score_quiz FOREIGN KEY (source_quiz_id)
                    REFERENCES quiz_sessions(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
        """)

        # ── badges ─────────────────────────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS badges (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                name            VARCHAR(100) NOT NULL,
                description     TEXT         DEFAULT NULL,
                condition_type  VARCHAR(50)  NOT NULL
                                    COMMENT 'score | streak | unit_complete | quiz_count',
                condition_value INT          NOT NULL,
                icon            VARCHAR(100) DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
        """)

        # Yeni kolonları güvenle ekle / charset'i güncelle
        # emoji 4-byte karakter içerdiğinden CHARACTER SET utf8mb4 zorunlu
        _BADGE_COLS = [
            ("category", "VARCHAR(50)  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL"),
            ("emoji",    "VARCHAR(20)  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL"),
            ("color",    "VARCHAR(20)  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL"),
        ]
        for col, defn in _BADGE_COLS:
            if _column_exists(cur, "badges", col):
                # Mevcut kolonu utf8mb4'e zorla (önceki yanlış charset olabilir)
                cur.execute(f"ALTER TABLE badges MODIFY COLUMN `{col}` {defn}")
            else:
                cur.execute(f"ALTER TABLE badges ADD COLUMN `{col}` {defn}")

        # 18 rozet kataloğunu seed et / güncelle
        _seed_badges(cur)

        # ── user_badges ────────────────────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_badges (
                id        INT AUTO_INCREMENT PRIMARY KEY,
                user_id   INT      NOT NULL,
                badge_id  INT      NOT NULL,
                earned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_ub_user  FOREIGN KEY (user_id)
                    REFERENCES users(id)  ON DELETE CASCADE,
                CONSTRAINT fk_ub_badge FOREIGN KEY (badge_id)
                    REFERENCES badges(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
        """)

        mysql.connection.commit()
        cur.close()
