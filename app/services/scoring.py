"""
app/services/scoring.py
───────────────────────
Quiz puan hesaplama servisi.

Kurallar (kullanıcı tarafından belirlendi):
  - Temel puan      : 10 / doğru cevap
  - Tip çarpanı     : flashcard ×0.5 | multiple_choice ×1.0
                      matching ×1.2  | fill_blank ×1.5
  - Süre bonusu     : Soru başına max 30 sn → kalan süre oranında bonus (max +5 puan)
  - Combo bonusu    : 3 üst üste doğru → ×1.2  |  5 üst üste → ×1.5
  - Yanlış ceza     : −5 puan (toplam 0'ın altına düşmez)
  - Mükemmel bonus  : tüm cevaplar doğruysa +50 XP

─────────────────────────────────────────────
KENDI SORULARINI EKLEMEK / DEĞİŞTİRMEK İÇİN:
  Bu dosyayı değiştirmene gerek yok.
  Soruları app/data/quiz/grade_X.json dosyalarında düzenle.

  JSON yapısı:
    "id"            → benzersiz kimlik, değiştirme (9_1_mc_1 gibi)
    "type"          → multiple_choice | flashcard | matching | fill_blank
    "question"      → soru metni (multiple_choice / fill_blank için)
    "options"       → seçenekler listesi (sadece multiple_choice)
    "correct_index" → doğru seçeneğin indeksi 0'dan başlar (sadece multiple_choice)
    "answer"        → doğru cevap metni (fill_blank için)
    "pairs"         → eşleşme çiftleri listesi (matching için)
    "term/definition"→ kavram ve tanımı (flashcard için)
    "explanation"   → cevap sonrası gösterilecek açıklama
    "hint"          → ipucu metni

  Yeni soru eklemek:
    İlgili grade_X.json dosyasını aç, ilgili ünitenin "questions" listesine
    aynı yapıda yeni bir nesne ekle. id'yi sıradaki numarayla ver.
    Örnek: "9_1_mc_6" (9. sınıf, ünite 1, multiple_choice, 6. soru)

  Mevcut soruyu değiştirmek:
    Sadece "question", "options", "correct_index" veya "answer" alanını güncelle.
    "id" alanını ASLA değiştirme; bu alan quiz_answers tablosunda referans olarak kullanılır.
─────────────────────────────────────────────
"""

from __future__ import annotations

# ── Sabitler ──────────────────────────────────────────────────────────────────

BASE_SCORE: int = 10
"""Her doğru cevap için temel puan."""

WRONG_PENALTY: int = 5
"""Yanlış cevap cezası (puandan düşülür)."""

PERFECT_BONUS: int = 50
"""Tüm soruları doğru bitirince eklenen bonus XP."""

MAX_TIME_PER_QUESTION: int = 30
"""Soru başına maksimum süre (saniye). Süre bonusu buna göre hesaplanır."""

MAX_TIME_BONUS: float = 5.0
"""Bir soru için alınabilecek maksimum süre bonusu (puan)."""

# Quiz tipine göre çarpanlar
TYPE_MULTIPLIERS: dict[str, float] = {
    "flashcard":       0.5,   # en kolay → en az puan
    "multiple_choice": 1.0,
    "matching":        1.2,
    "fill_blank":      1.5,   # en zor  → en çok puan
}

# Bu tiplerde XP kazanılmaz (kullanıcı "bildim/bilmedim" seçimine göre puan kasmasın)
ZERO_SCORE_TYPES: set[str] = {"flashcard"}

# Combo eşikleri: {üst_üste_doğru_sayısı: çarpan}
# Örn: 3 üst üste doğru cevap → tüm çarpanlar ×1.2 olur
COMBO_THRESHOLDS: dict[int, float] = {
    3: 1.2,
    5: 1.5,
}


# ── Yardımcı ──────────────────────────────────────────────────────────────────

def _combo_multiplier(combo_count: int) -> float:
    """Mevcut combo sayısına göre çarpanı döndür."""
    result = 1.0
    for threshold, mult in sorted(COMBO_THRESHOLDS.items(), reverse=True):
        if combo_count >= threshold:
            result = mult
            break
    return result


def _time_bonus(time_taken: float | None) -> float:
    """
    Kalan süreye göre bonus puan hesapla.
    time_taken: soruya harcanan süre (saniye). None ise bonus eklenmez.
    """
    if time_taken is None or time_taken < 0:
        return 0.0
    remaining = max(0.0, MAX_TIME_PER_QUESTION - time_taken)
    ratio = remaining / MAX_TIME_PER_QUESTION          # 0.0 – 1.0
    return round(ratio * MAX_TIME_BONUS, 2)


# ── Ana fonksiyonlar ──────────────────────────────────────────────────────────

def calculate_answer_score(
    is_correct: bool,
    quiz_type: str,
    time_taken: float | None = None,
    combo_count: int = 0,
) -> int:
    """
    Tek bir cevap için puan hesapla.

    Parametreler
    ------------
    is_correct  : Cevap doğru mu?
    quiz_type   : 'multiple_choice' | 'flashcard' | 'matching' | 'fill_blank'
    time_taken  : Soruya harcanan süre (saniye). None → süre bonusu uygulanmaz.
    combo_count : Bu cevaptan ÖNCE kaç üst üste doğru yapıldı.

    Dönüş
    -----
    int: Puan (minimum 0, negatife düşmez).
         Yanlış cevap −WRONG_PENALTY döndürebilir; toplam hesabında 0'a çekilir.
    """
    if not is_correct:
        # Yanlış cevap cezası; negatif değer döner, toplam 0'a çekilir
        return -WRONG_PENALTY

    multiplier  = TYPE_MULTIPLIERS.get(quiz_type, 1.0)
    base        = BASE_SCORE * multiplier
    t_bonus     = _time_bonus(time_taken)
    c_mult      = _combo_multiplier(combo_count)

    raw = (base + t_bonus) * c_mult
    return max(0, round(raw))


def calculate_quiz_score(
    answers: list[bool],
    quiz_type: str,
    times: list[float] | None = None,
) -> dict:
    """
    Bir quiz oturumunun tamamı için puan hesapla.

    Parametreler
    ------------
    answers   : Her sorunun doğru/yanlış sonucu [True, False, True, ...]
    quiz_type : Quiz tipi (tüm sorular aynı tipe ait sayılır)
    times     : Her soruya harcanan süre listesi (saniye). None → süre bonusu yok.
                Verilirse len(times) == len(answers) olmalı.

    Dönüş
    -----
    dict:
        total_score    (int)  : Nihai toplam puan (0'ın altına düşmez)
        perfect_bonus  (int)  : Mükemmel quiz ise PERFECT_BONUS, değilse 0
        is_perfect     (bool) : Tüm cevaplar doğru mu?
        correct_count  (int)  : Doğru cevap sayısı
        wrong_count    (int)  : Yanlış cevap sayısı
        breakdown      (list) : Her soru için ayrıntılı bilgi

    Örnek kullanım
    --------------
    >>> result = calculate_quiz_score(
    ...     answers=[True, True, False, True],
    ...     quiz_type='multiple_choice',
    ...     times=[8.5, 12.0, 25.0, 5.2],
    ... )
    >>> result['total_score']
    35
    """
    if times is not None and len(times) != len(answers):
        raise ValueError("times ve answers listeleri aynı uzunlukta olmalı.")

    # Flashcard gibi "zero-score" tiplerde XP verilmez ama doğru/yanlış sayısı tutulur
    if quiz_type in ZERO_SCORE_TYPES:
        return {
            "total_score":   0,
            "perfect_bonus": 0,
            "is_perfect":    all(answers),
            "correct_count": sum(1 for a in answers if a),
            "wrong_count":   sum(1 for a in answers if not a),
            "breakdown":     [
                {"question_index": i, "is_correct": a, "score": 0, "combo_at_end": 0, "time_taken": None}
                for i, a in enumerate(answers)
            ],
        }

    running_total: int = 0
    combo: int = 0
    breakdown: list[dict] = []

    for i, is_correct in enumerate(answers):
        t = times[i] if times is not None else None
        score = calculate_answer_score(is_correct, quiz_type, t, combo)

        if is_correct:
            combo += 1
        else:
            combo = 0

        running_total += score
        breakdown.append(
            {
                "question_index": i,
                "is_correct":     is_correct,
                "score":          score,
                "combo_at_end":   combo,
                "time_taken":     t,
            }
        )

    # Toplam 0'ın altına düşmesin
    running_total = max(0, running_total)

    is_perfect = all(answers)
    perfect_bonus = PERFECT_BONUS if is_perfect else 0
    total_score = running_total + perfect_bonus

    return {
        "total_score":   total_score,
        "perfect_bonus": perfect_bonus,
        "is_perfect":    is_perfect,
        "correct_count": sum(1 for a in answers if a),
        "wrong_count":   sum(1 for a in answers if not a),
        "breakdown":     breakdown,
    }


def format_score_summary(result: dict) -> str:
    """
    calculate_quiz_score çıktısını okunabilir bir özet metne dönüştür.
    Template'lerde ya da flash mesajlarda kullanılabilir.

    Örnek çıktı:
        "12/15 doğru · 95 XP kazandın 🎉"
    """
    correct = result["correct_count"]
    total   = correct + result["wrong_count"]
    score   = result["total_score"]
    suffix  = " 🎉 Mükemmel!" if result["is_perfect"] else ""
    return f"{correct}/{total} doğru · {score} XP kazandın{suffix}"
