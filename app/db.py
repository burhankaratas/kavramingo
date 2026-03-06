"""
Uygulama başlangıcında veritabanı tablolarını oluşturur.
Her tablo CREATE TABLE IF NOT EXISTS ile yazılmıştır — mevcut veriye dokunmaz.
"""
from app.extensions import mysql


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
                grade         INT           DEFAULT NULL COMMENT '5,6,7 veya 8',
                total_score   INT           NOT NULL DEFAULT 0,
                created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
        """)

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
