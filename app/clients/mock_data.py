"""
PHP API hazır olana kadar kullanılacak sahte (mock) veri.
Gerçek MEB din kültürü ve ahlak bilgisi müfredatına uygundur.
KAVRAM_API_MOCK=true olduğunda kavram_api.py bu veriyi kullanır.
"""

import random

# ── Üniteler ────────────────────────────────────────────────────────────────
# Her ünite: {id, name, grade}
UNITES = [
    # 9. Sınıf
    {"id": 1,  "name": "Kur'an-ı Kerim",              "grade": 9},
    {"id": 2,  "name": "Hz. Muhammed",                 "grade": 9},
    {"id": 3,  "name": "İman",                         "grade": 9},
    {"id": 4,  "name": "İbadet",                       "grade": 9},
    {"id": 5,  "name": "Hz. Muhammed'in Hayatı",       "grade": 9},
    # 10. Sınıf
    {"id": 6,  "name": "Kur'an ve Yorumu",             "grade": 10},
    {"id": 7,  "name": "Allah'a İman",                 "grade": 10},
    {"id": 8,  "name": "İbadetler ve Anlam",           "grade": 10},
    {"id": 9,  "name": "Ahlak ve Değerler",            "grade": 10},
    {"id": 10, "name": "Din ve Kültür",                "grade": 10},
    # 11. Sınıf
    {"id": 11, "name": "Kur'an'ın Temel Kavramları",  "grade": 11},
    {"id": 12, "name": "Peygamberlere İman",           "grade": 11},
    {"id": 13, "name": "İslam'ın Şartları",            "grade": 11},
    {"id": 14, "name": "İslam Ahlakı",                 "grade": 11},
    {"id": 15, "name": "İslam Medeniyeti",             "grade": 11},
    # 12. Sınıf
    {"id": 16, "name": "Kur'an'ın Anlaşılması",       "grade": 12},
    {"id": 17, "name": "Hz. Muhammed ve Sünnet",       "grade": 12},
    {"id": 18, "name": "Kader İnancı",                 "grade": 12},
    {"id": 19, "name": "İslam ve Yorum",               "grade": 12},
    {"id": 20, "name": "Yaşayan Dinler",               "grade": 12},
]

# ── Konular ──────────────────────────────────────────────────────────────────
# Her konu: {id, name, unite_id}
KONULAR = [
    # Ünite 1
    {"id": 1,  "name": "Kur'an'ın Özellikleri",      "unite_id": 1},
    {"id": 2,  "name": "Kur'an'ı Okumak",            "unite_id": 1},
    # Ünite 2
    {"id": 3,  "name": "Hz. Muhammed'in Özellikleri","unite_id": 2},
    {"id": 4,  "name": "Peygamberlik Görevi",        "unite_id": 2},
    # Ünite 3
    {"id": 5,  "name": "İmanın Temelleri",           "unite_id": 3},
    {"id": 6,  "name": "Allah'ın Sıfatları",         "unite_id": 3},
    # Ünite 4
    {"id": 7,  "name": "Namaz",                      "unite_id": 4},
    {"id": 8,  "name": "Oruç",                       "unite_id": 4},
    # Ünite 5
    {"id": 9,  "name": "Mekke Dönemi",               "unite_id": 5},
    {"id": 10, "name": "Medine Dönemi",              "unite_id": 5},
    # Ünite 6
    {"id": 11, "name": "Tefsir",                     "unite_id": 6},
    {"id": 12, "name": "Meal",                       "unite_id": 6},
    # Ünite 7
    {"id": 13, "name": "Tevhid",                     "unite_id": 7},
    {"id": 14, "name": "Esmâ-ül Hüsnâ",             "unite_id": 7},
    # Ünite 8
    {"id": 15, "name": "Zekat",                      "unite_id": 8},
    {"id": 16, "name": "Hac",                        "unite_id": 8},
    # Ünite 9
    {"id": 17, "name": "Ahlaki Değerler",            "unite_id": 9},
    {"id": 18, "name": "Dürüstlük",                  "unite_id": 9},
    # Ünite 10
    {"id": 19, "name": "İslam Sanatı",               "unite_id": 10},
    {"id": 20, "name": "Cami Mimarisi",              "unite_id": 10},
    # Ünite 11
    {"id": 21, "name": "Sure ve Ayet",               "unite_id": 11},
    {"id": 22, "name": "Kur'an Kavramları",          "unite_id": 11},
    # Ünite 12
    {"id": 23, "name": "Peygamberlerin Özellikleri", "unite_id": 12},
    {"id": 24, "name": "Ulül Azm Peygamberler",     "unite_id": 12},
    # Ünite 13
    {"id": 25, "name": "Kelime-i Şehadet",           "unite_id": 13},
    {"id": 26, "name": "Namaz ve Oruç",              "unite_id": 13},
    # Ünite 14
    {"id": 27, "name": "Güzel Ahlak",                "unite_id": 14},
    {"id": 28, "name": "Kötü Huylardan Kaçınmak",   "unite_id": 14},
    # Ünite 15
    {"id": 29, "name": "Bilim ve Medeniyet",         "unite_id": 15},
    {"id": 30, "name": "İslam Alimleri",             "unite_id": 15},
    # Ünite 16
    {"id": 31, "name": "Kur'an'ı Anlamak",          "unite_id": 16},
    {"id": 32, "name": "Kur'an ve Bilim",           "unite_id": 16},
    # Ünite 17
    {"id": 33, "name": "Sünnet ve Hadis",            "unite_id": 17},
    {"id": 34, "name": "Hadis Çeşitleri",            "unite_id": 17},
    # Ünite 18
    {"id": 35, "name": "Kader ve Kaza",              "unite_id": 18},
    {"id": 36, "name": "Tevekkül",                   "unite_id": 18},
    # Ünite 19
    {"id": 37, "name": "Mezhepler",                  "unite_id": 19},
    {"id": 38, "name": "İçtihat",                    "unite_id": 19},
    # Ünite 20
    {"id": 39, "name": "Hristiyanlık",               "unite_id": 20},
    {"id": 40, "name": "Yahudilik",                  "unite_id": 20},
]

# ── Kavramlar ────────────────────────────────────────────────────────────────
# Her kavram: {id, term, definition, konu_id, unite_id}
KAVRAMLAR = [
    # Konu 1 — Kur'an'ın Özellikleri
    {"id": 1,  "term": "Mushaf",       "definition": "Kur'an-ı Kerim'in yazılı olduğu kitap.", "konu_id": 1, "unite_id": 1},
    {"id": 2,  "term": "Sure",         "definition": "Kur'an'ın bölümlerinden her biri; 114 sure vardır.", "konu_id": 1, "unite_id": 1},
    {"id": 3,  "term": "Ayet",         "definition": "Kur'an'daki her bir cümle veya cümle grubuna verilen ad.", "konu_id": 1, "unite_id": 1},
    {"id": 4,  "term": "Cüz",          "definition": "Kur'an'ın 30 eşit parçasından her biri.", "konu_id": 1, "unite_id": 1},
    # Konu 2 — Kur'an'ı Okumak
    {"id": 5,  "term": "Tecvid",       "definition": "Kur'an'ı doğru ve güzel okuma kurallarını öğreten ilim.", "konu_id": 2, "unite_id": 1},
    {"id": 6,  "term": "Hafız",        "definition": "Kur'an-ı Kerim'i ezbere bilen kişi.", "konu_id": 2, "unite_id": 1},
    # Konu 3 — Hz. Muhammed'in Özellikleri
    {"id": 7,  "term": "Sıdk",         "definition": "Doğruluk; Hz. Muhammed'in temel özelliklerinden biri.", "konu_id": 3, "unite_id": 2},
    {"id": 8,  "term": "Emanet",       "definition": "Güvenilirlik; peygamberlerin sahip olduğu temel özellik.", "konu_id": 3, "unite_id": 2},
    {"id": 9,  "term": "Fetanet",      "definition": "Zeka ve anlayış keskinliği; peygamberlerin özelliği.", "konu_id": 3, "unite_id": 2},
    {"id": 10, "term": "İsmet",        "definition": "Günah işlemekten korunmuş olma; peygamberlerin özelliği.", "konu_id": 3, "unite_id": 2},
    # Konu 4 — Peygamberlik Görevi
    {"id": 11, "term": "Vahiy",        "definition": "Allah'ın peygamberlere bildirdiği ilahi mesaj.", "konu_id": 4, "unite_id": 2},
    {"id": 12, "term": "Nübüvvet",     "definition": "Peygamberlik makamı ve görevi.", "konu_id": 4, "unite_id": 2},
    {"id": 13, "term": "Risalet",      "definition": "Allah'ın emirlerini insanlara iletme görevi.", "konu_id": 4, "unite_id": 2},
    # Konu 5 — İmanın Temelleri
    {"id": 14, "term": "İman",         "definition": "Allah'a ve İslam'ın temel esaslarına içtenlikle inanmak.", "konu_id": 5, "unite_id": 3},
    {"id": 15, "term": "Tevhid",       "definition": "Allah'ın bir ve tek olduğuna inanmak.", "konu_id": 5, "unite_id": 3},
    {"id": 16, "term": "Ahiret",       "definition": "Ölümden sonraki sonsuz hayat.", "konu_id": 5, "unite_id": 3},
    {"id": 17, "term": "Melek",        "definition": "Allah'ın nurdan yarattığı, emirlerine itaat eden varlıklar.", "konu_id": 5, "unite_id": 3},
    # Konu 6 — Allah'ın Sıfatları
    {"id": 18, "term": "Vücud",        "definition": "Allah'ın var olması; O'nun zorunlu sıfatı.", "konu_id": 6, "unite_id": 3},
    {"id": 19, "term": "Kıdem",        "definition": "Allah'ın başlangıcının olmaması.", "konu_id": 6, "unite_id": 3},
    {"id": 20, "term": "Beka",         "definition": "Allah'ın sonunun olmaması, ebedi olması.", "konu_id": 6, "unite_id": 3},
    {"id": 21, "term": "Vahdaniyet",   "definition": "Allah'ın bir ve tek olması.", "konu_id": 6, "unite_id": 3},
    {"id": 22, "term": "Kudret",       "definition": "Allah'ın her şeye gücünün yetmesi.", "konu_id": 6, "unite_id": 3},
    # Konu 7 — Namaz
    {"id": 23, "term": "Farz",         "definition": "Yapılması zorunlu olan dini görev.", "konu_id": 7, "unite_id": 4},
    {"id": 24, "term": "Abdest",       "definition": "Namaz öncesi belirli uzuvları yıkama ve mesh etme.", "konu_id": 7, "unite_id": 4},
    {"id": 25, "term": "Kıble",        "definition": "Namaz kılarken yönelinen Kabe'nin bulunduğu yön.", "konu_id": 7, "unite_id": 4},
    {"id": 26, "term": "Rekat",        "definition": "Namazda belirli hareketlerin bir bütün olarak yapılması.", "konu_id": 7, "unite_id": 4},
    # Konu 8 — Oruç
    {"id": 27, "term": "Ramazan",      "definition": "İslam takviminin oruç tutulan dokuzuncu ayı.", "konu_id": 8, "unite_id": 4},
    {"id": 28, "term": "İftar",        "definition": "Oruçlunun akşam ezanıyla orucunu açması.", "konu_id": 8, "unite_id": 4},
    {"id": 29, "term": "Sahur",        "definition": "Oruç öncesi sabah vakti yapılan yemek.", "konu_id": 8, "unite_id": 4},
    # Konu 9 — Mekke Dönemi
    {"id": 30, "term": "Hira",         "definition": "Hz. Muhammed'e ilk vahyin geldiği Mekke'deki dağ ve mağara.", "konu_id": 9, "unite_id": 5},
    {"id": 31, "term": "Kabe",         "definition": "Mekke'de bulunan ve Müslümanların kıblesi olan kutsal yapı.", "konu_id": 9, "unite_id": 5},
    {"id": 32, "term": "Kureyş",       "definition": "Hz. Muhammed'in mensup olduğu Mekke'nin önde gelen kabilesi.", "konu_id": 9, "unite_id": 5},
    # Konu 10 — Medine Dönemi
    {"id": 33, "term": "Hicret",       "definition": "Hz. Muhammed ve sahabelerin Mekke'den Medine'ye göç etmesi.", "konu_id": 10, "unite_id": 5},
    {"id": 34, "term": "Ensar",        "definition": "Medine'de Müslümanlara yardım eden yerli Müslümanlar.", "konu_id": 10, "unite_id": 5},
    {"id": 35, "term": "Muhacir",      "definition": "Mekke'den Medine'ye hicret eden Müslümanlar.", "konu_id": 10, "unite_id": 5},
    # Konu 11 — Tefsir
    {"id": 36, "term": "Tefsir",       "definition": "Kur'an ayetlerini açıklayan ve yorumlayan ilim dalı.", "konu_id": 11, "unite_id": 6},
    {"id": 37, "term": "Müfessir",     "definition": "Kur'an'ı tefsir eden alim.", "konu_id": 11, "unite_id": 6},
    # Konu 12 — Meal
    {"id": 38, "term": "Meal",         "definition": "Kur'an'ın başka bir dile anlamına yakın çevirisi.", "konu_id": 12, "unite_id": 6},
    {"id": 39, "term": "Tercüme",      "definition": "Bir metni başka bir dile kelimesi kelimesine çevirme.", "konu_id": 12, "unite_id": 6},
    # Konu 13 — Tevhid
    {"id": 40, "term": "Şirk",         "definition": "Allah'a ortak koşmak; en büyük günah.", "konu_id": 13, "unite_id": 7},
    {"id": 41, "term": "Muvahhid",     "definition": "Allah'ın birliğine inanan, tevhid inancını benimseyen kişi.", "konu_id": 13, "unite_id": 7},
    # Konu 14 — Esmâ-ül Hüsnâ
    {"id": 42, "term": "Esmâ-ül Hüsnâ", "definition": "Allah'ın 99 güzel ismi.", "konu_id": 14, "unite_id": 7},
    {"id": 43, "term": "Rahman",       "definition": "Dünyada bütün varlıklara merhamet eden Allah'ın ismi.", "konu_id": 14, "unite_id": 7},
    {"id": 44, "term": "Rahim",        "definition": "Ahirette müminlere sonsuz merhamet eden Allah'ın ismi.", "konu_id": 14, "unite_id": 7},
    # Konu 15 — Zekat
    {"id": 45, "term": "Zekat",        "definition": "Belirli bir servete sahip Müslümanların yılda bir kez vermesi gereken mali ibadet.", "konu_id": 15, "unite_id": 8},
    {"id": 46, "term": "Nisap",        "definition": "Zekat yükümlülüğü için gereken asgari servet miktarı.", "konu_id": 15, "unite_id": 8},
    {"id": 47, "term": "Fitre",        "definition": "Ramazan ayı sonunda verilen sadaka.", "konu_id": 15, "unite_id": 8},
    # Konu 16 — Hac
    {"id": 48, "term": "Hac",          "definition": "Gücü yeten Müslümanların ömründe bir kez Mekke'ye yapması gereken ibadet.", "konu_id": 16, "unite_id": 8},
    {"id": 49, "term": "Tavaf",        "definition": "Kabe'nin etrafında yedi kez dönme ibadeti.", "konu_id": 16, "unite_id": 8},
    {"id": 50, "term": "Arafat",       "definition": "Hacda vakfe yapılan Mekke yakınındaki yer.", "konu_id": 16, "unite_id": 8},
    # Konu 17 — Ahlaki Değerler
    {"id": 51, "term": "Adalet",       "definition": "Hak ve hukuka uygun davranma, herkese hakkını verme.", "konu_id": 17, "unite_id": 9},
    {"id": 52, "term": "Merhamet",     "definition": "Acıma ve şefkat duygusu, canlılara iyi davranmak.", "konu_id": 17, "unite_id": 9},
    {"id": 53, "term": "Sabır",        "definition": "Güçlüklere katlanma, acelecilikten uzak durma erdemi.", "konu_id": 17, "unite_id": 9},
    # Konu 18 — Dürüstlük
    {"id": 54, "term": "Doğruluk",     "definition": "Söz ve davranışlarda gerçeğe uygun hareket etme.", "konu_id": 18, "unite_id": 9},
    {"id": 55, "term": "Yalan",        "definition": "Gerçeğe aykırı söz söyleme; İslam'da yasaklanan davranış.", "konu_id": 18, "unite_id": 9},
    # Konu 19 — İslam Sanatı
    {"id": 56, "term": "Hat",          "definition": "İslam yazı sanatı; Arap harflerini estetik biçimde yazma.", "konu_id": 19, "unite_id": 10},
    {"id": 57, "term": "Tezhip",       "definition": "El yazması kitapları altın ve renkli boyalarla süsleme sanatı.", "konu_id": 19, "unite_id": 10},
    {"id": 58, "term": "Ebru",         "definition": "Su yüzeyine yağlı boyalarla desen oluşturma sanatı.", "konu_id": 19, "unite_id": 10},
    # Konu 20 — Cami Mimarisi
    {"id": 59, "term": "Minare",       "definition": "Caminin ezan okunmak için yapılan uzun ince kulesi.", "konu_id": 20, "unite_id": 10},
    {"id": 60, "term": "Mihrap",       "definition": "Camide imamın namaz kıldırırken durduğu girintili yer.", "konu_id": 20, "unite_id": 10},
    {"id": 61, "term": "Minber",       "definition": "Camide imamın Cuma hutbesi okuduğu yüksekçe yer.", "konu_id": 20, "unite_id": 10},
    # Konu 21 — Sure ve Ayet
    {"id": 62, "term": "Besmele",      "definition": "'Bismillahirrahmanirrahim' ifadesi; her işe Allah'ın adıyla başlamak.", "konu_id": 21, "unite_id": 11},
    {"id": 63, "term": "Fatiha",       "definition": "Kur'an'ın ilk suresi; namazda okunan temel sure.", "konu_id": 21, "unite_id": 11},
    {"id": 64, "term": "Bakara",       "definition": "Kur'an'ın en uzun suresi; 286 ayetten oluşur.", "konu_id": 21, "unite_id": 11},
    # Konu 22 — Kur'an Kavramları
    {"id": 65, "term": "Nüzul",        "definition": "Kur'an'ın Allah tarafından indirilmesi.", "konu_id": 22, "unite_id": 11},
    {"id": 66, "term": "Esbab-ı Nüzul","definition": "Kur'an ayetlerinin iniş sebepleri.", "konu_id": 22, "unite_id": 11},
    # Konu 23 — Peygamberlerin Özellikleri
    {"id": 67, "term": "Tebliğ",       "definition": "Peygamberlerin Allah'ın mesajını insanlara ulaştırması.", "konu_id": 23, "unite_id": 12},
    {"id": 68, "term": "Mucize",       "definition": "Peygamberlerin Allah'ın izniyle gösterdiği olağanüstü olaylar.", "konu_id": 23, "unite_id": 12},
    # Konu 24 — Ulül Azm Peygamberler
    {"id": 69, "term": "Ulül Azm",     "definition": "En büyük sınavlara sabırla katlanan beş peygamber: Nuh, İbrahim, Musa, İsa, Muhammed.", "konu_id": 24, "unite_id": 12},
    # Konu 25 — Kelime-i Şehadet
    {"id": 70, "term": "Kelime-i Şehadet", "definition": "Allah'tan başka ilah olmadığına ve Hz. Muhammed'in O'nun elçisi olduğuna şahitlik etmek.", "konu_id": 25, "unite_id": 13},
    {"id": 71, "term": "Kelime-i Tevhid",  "definition": "'Lâ ilâhe illallah' — Allah'tan başka ilah yoktur.", "konu_id": 25, "unite_id": 13},
    # Konu 26 — Namaz ve Oruç (7. sınıf)
    {"id": 72, "term": "Sünnet Namaz", "definition": "Farz namazların öncesinde veya sonrasında kılınan nafile namaz.", "konu_id": 26, "unite_id": 13},
    {"id": 73, "term": "Teravih",      "definition": "Ramazan ayında yatsı namazından sonra kılınan sünnet namaz.", "konu_id": 26, "unite_id": 13},
    # Konu 27 — Güzel Ahlak
    {"id": 74, "term": "Cömertlik",    "definition": "Malını ve imkânını ihtiyaç sahipleriyle paylaşma erdemi.", "konu_id": 27, "unite_id": 14},
    {"id": 75, "term": "Tevazu",       "definition": "Alçakgönüllülük; kibir ve gururdan uzak olma.", "konu_id": 27, "unite_id": 14},
    {"id": 76, "term": "Vefa",         "definition": "Verilen sözü tutma ve iyiliği unutmama erdemi.", "konu_id": 27, "unite_id": 14},
    # Konu 28 — Kötü Huylardan Kaçınmak
    {"id": 77, "term": "Kibir",        "definition": "Kendini üstün görme, büyüklenme; İslam'da yasaklanan huy.", "konu_id": 28, "unite_id": 14},
    {"id": 78, "term": "Haset",        "definition": "Kıskançlık; başkasındaki nimeti çekememe.", "konu_id": 28, "unite_id": 14},
    {"id": 79, "term": "Gıybet",       "definition": "Birini arkasından çekiştirmek; İslam'da yasaklanan davranış.", "konu_id": 28, "unite_id": 14},
    # Konu 29 — Bilim ve Medeniyet
    {"id": 80, "term": "İlim",         "definition": "Bilgi; İslam'da ilim öğrenmek farzdır.", "konu_id": 29, "unite_id": 15},
    {"id": 81, "term": "Medrese",      "definition": "Orta Çağ İslam dünyasında yüksek öğretim kurumu.", "konu_id": 29, "unite_id": 15},
    # Konu 30 — İslam Alimleri
    {"id": 82, "term": "İbn-i Sina",   "definition": "Ortaçağ'ın en büyük İslam hekimi ve filozofu.", "konu_id": 30, "unite_id": 15},
    {"id": 83, "term": "El-Biruni",    "definition": "Matematik, astronomi ve coğrafya alanında çalışmalar yapan İslam alimi.", "konu_id": 30, "unite_id": 15},
    {"id": 84, "term": "Farabi",       "definition": "Mantık ve felsefe alanında çalışmalar yapan İslam filozofu.", "konu_id": 30, "unite_id": 15},
    # Konu 31 — Kur'an'ı Anlamak
    {"id": 85, "term": "Muhkem",       "definition": "Anlamı açık ve kesin olan Kur'an ayetleri.", "konu_id": 31, "unite_id": 16},
    {"id": 86, "term": "Müteşabih",    "definition": "Anlamı kapalı veya yoruma açık olan Kur'an ayetleri.", "konu_id": 31, "unite_id": 16},
    # Konu 32 — Kur'an ve Bilim
    {"id": 87, "term": "İ'caz",        "definition": "Kur'an'ın benzerinin yapılamaması; Kur'an'ın mucizevi özelliği.", "konu_id": 32, "unite_id": 16},
    # Konu 33 — Sünnet ve Hadis
    {"id": 88, "term": "Sünnet",       "definition": "Hz. Muhammed'in söz, fiil ve onaylarının tümü.", "konu_id": 33, "unite_id": 17},
    {"id": 89, "term": "Hadis",        "definition": "Hz. Muhammed'in sözlerini, davranışlarını aktaran rivayetler.", "konu_id": 33, "unite_id": 17},
    {"id": 90, "term": "Sahih Hadis",  "definition": "Güvenilir raviler zinciriyle aktarılan doğruluğu kesin hadis.", "konu_id": 33, "unite_id": 17},
    # Konu 34 — Hadis Çeşitleri
    {"id": 91, "term": "Mütevâtir",    "definition": "Yalan üzere birleşmeleri mümkün olmayan çok sayıda ravi tarafından aktarılan hadis.", "konu_id": 34, "unite_id": 17},
    {"id": 92, "term": "Ahad Hadis",   "definition": "Az sayıda ravi tarafından nakledilen hadis.", "konu_id": 34, "unite_id": 17},
    # Konu 35 — Kader ve Kaza
    {"id": 93, "term": "Kader",        "definition": "Allah'ın her şeyi önceden bilmesi ve takdir etmesi.", "konu_id": 35, "unite_id": 18},
    {"id": 94, "term": "Kaza",         "definition": "Takdir edilen şeyin zamanı gelince gerçekleşmesi.", "konu_id": 35, "unite_id": 18},
    # Konu 36 — Tevekkül
    {"id": 95, "term": "Tevekkül",     "definition": "Gerekli çabayı gösterdikten sonra sonucu Allah'a bırakmak.", "konu_id": 36, "unite_id": 18},
    {"id": 96, "term": "Dua",          "definition": "Kulun Allah'a yalvarması, istemesi.", "konu_id": 36, "unite_id": 18},
    # Konu 37 — Mezhepler
    {"id": 97, "term": "Mezhep",       "definition": "İslam hukukunda belirli bir alimin yöntemini izleyen ilmi gelenek.", "konu_id": 37, "unite_id": 19},
    {"id": 98, "term": "Hanefi",       "definition": "İmam Ebu Hanife'nin kurduğu, Türkiye'de yaygın mezhep.", "konu_id": 37, "unite_id": 19},
    # Konu 38 — İçtihat
    {"id": 99, "term": "İçtihat",      "definition": "Dini bir konuda Kur'an ve Sünnet'ten hüküm çıkarma çabası.", "konu_id": 38, "unite_id": 19},
    {"id": 100,"term": "Fıkıh",        "definition": "İslam hukuku; ibadet ve günlük hayata dair dini hükümleri inceleyen ilim.", "konu_id": 38, "unite_id": 19},
    # Konu 39 — Hristiyanlık
    {"id": 101,"term": "İncil",        "definition": "Hz. İsa'ya indirilen ve Hristiyanların kutsal kitabı.", "konu_id": 39, "unite_id": 20},
    {"id": 102,"term": "Kilise",       "definition": "Hristiyanların ibadet ettiği dini mekan.", "konu_id": 39, "unite_id": 20},
    # Konu 40 — Yahudilik
    {"id": 103,"term": "Tevrat",       "definition": "Hz. Musa'ya indirilen ve Yahudilerin kutsal kitabı.", "konu_id": 40, "unite_id": 20},
    {"id": 104,"term": "Sinagog",      "definition": "Yahudilerin ibadet ettiği dini mekan.", "konu_id": 40, "unite_id": 20},
]


# ── Yardımcı index'ler (hız için) ────────────────────────────────────────────
_KAVRAM_BY_ID    = {k["id"]: k for k in KAVRAMLAR}
_KAVRAM_BY_KONU  = {}
_KAVRAM_BY_UNITE = {}
_KONULAR_BY_UNITE = {}

for k in KAVRAMLAR:
    _KAVRAM_BY_KONU.setdefault(k["konu_id"], []).append(k)
    _KAVRAM_BY_UNITE.setdefault(k["unite_id"], []).append(k)

for kn in KONULAR:
    _KONULAR_BY_UNITE.setdefault(kn["unite_id"], []).append(kn)


# ── Erişim fonksiyonları ─────────────────────────────────────────────────────

def mock_get_unites():
    return list(UNITES)

def mock_get_konular(unite_id):
    return list(_KONULAR_BY_UNITE.get(unite_id, []))

def mock_get_kavramlar(konu_id):
    return list(_KAVRAM_BY_KONU.get(konu_id, []))

def mock_get_kavram(kavram_id):
    return _KAVRAM_BY_ID.get(kavram_id)

def mock_get_random_kavramlar(unite_id, limit=10):
    havuz = _KAVRAM_BY_UNITE.get(unite_id, [])
    return random.sample(havuz, min(limit, len(havuz)))
