# Puan hesaplama mantığı
# Örn: doğru cevap sayısı, süre bonusu vb.


def calculate_score(correct: int, total: int, time_bonus: int = 0) -> int:
    base = correct * 10
    return base + time_bonus
