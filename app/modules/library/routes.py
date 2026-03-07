"""
app/modules/library/routes.py
─────────────────────────────
Ünite Kütüphanesi — tüm sınıfların tüm ünitelerine erişim.

GET /library/            → tüm üniteler
GET /library/?grade=9    → sadece 9. sınıf üniteleri
"""

from flask import render_template, request
from flask_login import login_required

from app.modules.library import library_bp


# ── Ünite kataloğu (JSON'daki unit_id'lerle eşleşiyor) ───────────────────────
UNITS = [
    # 9. Sınıf
    {
        "unit_id": 1,
        "grade": 9,
        "number": 1,
        "name": "Bilgi ve İnanç",
        "description": "İslam inancının temelleri, iman esasları ve tevhid kavramı üzerine sorular.",
        "question_count": 20,
    },
    {
        "unit_id": 2,
        "grade": 9,
        "number": 2,
        "name": "Kur'an-ı Kerim",
        "description": "Kur'an'ın inişi, özellikleri, mucizeleri ve hayatımızdaki yeri.",
        "question_count": 18,
    },
    {
        "unit_id": 3,
        "grade": 9,
        "number": 3,
        "name": "Hz. Muhammed'i Tanıyalım",
        "description": "Peygamberimizin hayatı, kişiliği, görevleri ve sünnetinin önemi.",
        "question_count": 22,
    },
    {
        "unit_id": 4,
        "grade": 9,
        "number": 4,
        "name": "İbadet",
        "description": "İslam'ın beş şartı, ibadetlerin hikmetleri ve günlük hayata yansımaları.",
        "question_count": 20,
    },
    # 10. Sınıf
    {
        "unit_id": 5,
        "grade": 10,
        "number": 1,
        "name": "Kaza, Kader ve İnsan Özgürlüğü",
        "description": "Kader inancı, özgür irade ve insan sorumluluğu arasındaki denge.",
        "question_count": 18,
    },
    {
        "unit_id": 6,
        "grade": 10,
        "number": 2,
        "name": "Hz. Muhammed ve Aile Hayatı",
        "description": "Peygamberimizin aile hayatı, evlilik anlayışı ve aile kurumuna katkıları.",
        "question_count": 16,
    },
    {
        "unit_id": 7,
        "grade": 10,
        "number": 3,
        "name": "İslam'da Ahlak Anlayışı",
        "description": "İslami ahlakın kaynakları, temel erdemler ve güzel ahlakın önemi.",
        "question_count": 20,
    },
    {
        "unit_id": 8,
        "grade": 10,
        "number": 4,
        "name": "Din ve Laiklik",
        "description": "Din-devlet ilişkisi, laiklik ilkesi ve Türkiye'deki uygulamaları.",
        "question_count": 18,
    },
    # 11. Sınıf
    {
        "unit_id": 9,
        "grade": 11,
        "number": 1,
        "name": "Din, Kültür ve Medeniyet",
        "description": "İslam medeniyetinin kültüre katkıları, sanat, mimari ve bilime etkileri.",
        "question_count": 20,
    },
    {
        "unit_id": 10,
        "grade": 11,
        "number": 2,
        "name": "İslam ve Bilim",
        "description": "İslam'ın bilime bakışı, Müslüman bilim insanları ve bilimsel miras.",
        "question_count": 18,
    },
    {
        "unit_id": 11,
        "grade": 11,
        "number": 3,
        "name": "Asr-ı Saadetten Örnek Şahsiyetler",
        "description": "Hz. Peygamber döneminde yetişen sahabe ve onların İslam'a katkıları.",
        "question_count": 22,
    },
    {
        "unit_id": 12,
        "grade": 11,
        "number": 4,
        "name": "İslam Tasavvufu",
        "description": "Tasavvufun tanımı, temel kavramları, önemli tarikatlar ve temsilcileri.",
        "question_count": 18,
    },
    # 12. Sınıf
    {
        "unit_id": 13,
        "grade": 12,
        "number": 1,
        "name": "Bir Mesaj Olarak Din",
        "description": "Dinin insan hayatındaki işlevi, evrensel mesajı ve insanlığa katkısı.",
        "question_count": 16,
    },
    {
        "unit_id": 14,
        "grade": 12,
        "number": 2,
        "name": "Güncel Dini Meseleler",
        "description": "Çağımızda din-bilim ilişkisi, din istismarı ve din özgürlüğü gibi konular.",
        "question_count": 20,
    },
    {
        "unit_id": 15,
        "grade": 12,
        "number": 3,
        "name": "Diyanet İşleri Başkanlığı",
        "description": "Diyanet'in kuruluşu, görevleri, yapısı ve toplumsal işlevleri.",
        "question_count": 16,
    },
    {
        "unit_id": 16,
        "grade": 12,
        "number": 4,
        "name": "Din Görevlisinin Önemi",
        "description": "Din görevlilerinin toplumsal rolü, nitelikleri ve mesleki sorumlulukları.",
        "question_count": 14,
    },
]

QUIZ_TYPES = [
    {"key": "multiple_choice", "label": "Çoktan Seçmeli", "icon": "bi-check2-circle",     "color": "#4361EE"},
    {"key": "flashcard",       "label": "Flashcard",       "icon": "bi-card-text",          "color": "#D9730D"},
    {"key": "matching",        "label": "Eşleştirme",      "icon": "bi-shuffle",            "color": "#06D6A0"},
    {"key": "fill_blank",      "label": "Boşluk Doldurma", "icon": "bi-pencil-fill",        "color": "#7209B7"},
]

GRADE_META = {
    9:  {"color": "#4361EE", "bg": "#EEF1FD", "label": "9. Sınıf"},
    10: {"color": "#7209B7", "bg": "#F5F3FF", "label": "10. Sınıf"},
    11: {"color": "#D9730D", "bg": "#FFF4E0", "label": "11. Sınıf"},
    12: {"color": "#059669", "bg": "#ECFDF5", "label": "12. Sınıf"},
}


@library_bp.route("/")
@login_required
def index():
    grade_filter = request.args.get("grade", "all")

    if grade_filter in ("9", "10", "11", "12"):
        filtered = [u for u in UNITS if u["grade"] == int(grade_filter)]
    else:
        grade_filter = "all"
        filtered = UNITS

    # Filtrelenmiş üniteleri sınıfa göre grupla (template'de kolay kullanım için)
    grouped = {}
    for u in filtered:
        grouped.setdefault(u["grade"], []).append(u)

    return render_template(
        "library/index.html",
        units=filtered,
        grouped=grouped,
        grade_filter=grade_filter,
        quiz_types=QUIZ_TYPES,
        grade_meta=GRADE_META,
        total_units=len(UNITS),
    )
