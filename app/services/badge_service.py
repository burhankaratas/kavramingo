"""
Rozet kazanma koşullarını kontrol eder ve yeni rozetleri veritabanına yazar.
mysql: flask_mysqldb.MySQL nesnesi (current_app dışından inject edilir)
"""
from datetime import datetime


def check_badges(user_id: int, mysql) -> list:
    """
    Kullanıcının mevcut durumuna göre henüz kazanılmamış rozetleri kontrol eder.
    Yeni kazanılan rozetleri user_badges tablosuna ekler.
    Döndürür: kazanılan Badge satırlarının listesi (dict)
    """
    cur = mysql.connection.cursor()
    newly_earned = []

    # Kullanıcı verisini çek
    cur.execute("SELECT total_score FROM users WHERE id = %s", (user_id,))
    user_row = cur.fetchone()
    if not user_row:
        cur.close()
        return []

    total_score = user_row["total_score"]

    # Tamamlanan ünite sayısı
    cur.execute(
        "SELECT COUNT(*) AS cnt FROM progress WHERE user_id = %s AND status = 'completed'",
        (user_id,)
    )
    unit_row = cur.fetchone()
    completed_units = unit_row["cnt"] if unit_row else 0

    # Toplam quiz sayısı
    cur.execute(
        "SELECT COUNT(*) AS cnt FROM quiz_sessions WHERE user_id = %s AND finished_at IS NOT NULL",
        (user_id,)
    )
    quiz_row = cur.fetchone()
    quiz_count = quiz_row["cnt"] if quiz_row else 0

    # Kullanıcının zaten sahip olduğu rozet ID'leri
    cur.execute("SELECT badge_id FROM user_badges WHERE user_id = %s", (user_id,))
    owned_ids = {r["badge_id"] for r in cur.fetchall()}

    # Tüm rozetleri çek ve koşulları kontrol et
    cur.execute("SELECT * FROM badges")
    all_badges = cur.fetchall()

    for badge in all_badges:
        if badge["id"] in owned_ids:
            continue  # Zaten kazanılmış

        earned = False
        ct = badge["condition_type"]
        cv = badge["condition_value"]

        if ct == "score" and total_score >= cv:
            earned = True
        elif ct == "unit_complete" and completed_units >= cv:
            earned = True
        elif ct == "quiz_count" and quiz_count >= cv:
            earned = True
        # streak koşulu için ek sorgu gerekir — şimdilik atlanıyor

        if earned:
            cur.execute(
                "INSERT INTO user_badges (user_id, badge_id, earned_at) VALUES (%s, %s, %s)",
                (user_id, badge["id"], datetime.utcnow())
            )
            newly_earned.append(badge)

    mysql.connection.commit()
    cur.close()
    return newly_earned
