# KavramLingo

> Lise öğrencilerine (9–12. sınıf) Din Kültürü ve Ahlak Bilgisi dersindeki kavramları oyunlaştırılmış yöntemle öğreten web uygulaması.

TÜBİTAK 2204-A kapsamında geliştirilmektedir.

---

## Özellikler

- **4 farklı quiz modu** — Çoktan seçmeli, eşleştirme, flashcard, boşluk doldurma
- **Rozet sistemi** — 18 rozet, 5 kategori (Başlangıç / Seri / Quiz Ustası / Mükemmellik / Ünite), streak takibi ile
- **Liderboard** — Sınıfa göre filtrelenebilir sıralama tablosu
- **Ünite kütüphanesi** — 4 sınıf × 16 ünite kataloğu
- **Günlük seri & XP** — Streak korunumu, her quiz sonrası puan kazanımı
- **Onboarding akışı** — Seviye testi ile sınıf belirleme
- **Profil & Ayarlar** — İstatistikler, şifre değiştirme, hesap yönetimi

---

## Teknoloji Yığını

| Katman | Kullanılan |
|---|---|
| Backend | Python 3.12, Flask 3.0 |
| Veritabanı | MySQL (XAMPP), flask-mysqldb (ham SQL + DictCursor) |
| Kimlik doğrulama | Flask-Login, Flask-WTF |
| Arayüz | Bootstrap 5.3, Bootstrap Icons, Nunito (Google Fonts) |
| E-posta | Flask-Mail (Gmail SMTP) |
| Ortam yönetimi | python-dotenv |

---

## Kurulum

### Gereksinimler

- Python 3.10+
- XAMPP (MySQL)
- `kavramingo` adında bir MySQL veritabanı

### Adımlar

```bash
# 1. Repoyu klonla
git clone https://github.com/kullanici-adi/kavramingo.git
cd kavramingo

# 2. Sanal ortam oluştur ve aktifleştir
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. .env dosyasını oluştur (aşağıdaki örneğe bak)
cp .env.example .env

# 5. XAMPP'ta MySQL'i başlat, ardından:
mysql -u root -e "CREATE DATABASE IF NOT EXISTS kavramingo CHARACTER SET utf8mb4 COLLATE utf8mb4_turkish_ci;"

# 6. Uygulamayı çalıştır
python app.py
```

Tablolar uygulama ilk çalıştığında `init_db()` tarafından **otomatik oluşturulur**. Elle SQL çalıştırmaya gerek yoktur.

---

## Ortam Değişkenleri

`.env` dosyasını proje kök dizinine oluştur:

```env
# Uygulama
SECRET_KEY=gizli-bir-anahtar

# Veritabanı
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=kavramingo
DB_SOCKET=/opt/lampp/var/mysql/mysql.sock   # Linux/macOS XAMPP yolu

# PHP Kavram API (hazır değilse mock mod aktif)
KAVRAM_API_BASE_URL=http://localhost:8000
KAVRAM_API_MOCK=true

# Google reCAPTCHA v2 (boş bırakılırsa geliştirme modunda atlanır)
RECAPTCHA_SITE_KEY=
RECAPTCHA_SECRET_KEY=

# Gmail SMTP (şifre sıfırlama için)
MAIL_USERNAME=
MAIL_PASSWORD=
```

> **Not:** `DB_SOCKET` yalnızca Linux/macOS XAMPP kurulumlarında gereklidir. Windows'ta bu satırı kaldır.

---

## Proje Yapısı

```
kavramingo/
├── app.py                        # Uygulama giriş noktası
├── config.py                     # Ortama göre yapılandırma (Dev/Prod)
├── requirements.txt
│
└── app/
    ├── __init__.py               # create_app() factory, blueprint kayıtları
    ├── db.py                     # init_db() — tablo oluşturma + rozet seed
    ├── extensions.py             # mysql, login_manager nesneleri
    │
    ├── data/quiz/                # Soru bankaları (JSON, sınıfa göre)
    │   ├── grade_9.json
    │   ├── grade_10.json
    │   ├── grade_11.json
    │   └── grade_12.json
    │
    ├── models/                   # Dataclass modelleri (ORM yok)
    │   └── badge.py
    │
    ├── services/
    │   ├── badge_service.py      # Rozet kontrolü, streak hesaplama
    │   ├── quiz_engine.py        # Soru karıştırma, oturum yönetimi
    │   └── scoring.py            # XP hesaplama
    │
    ├── clients/
    │   ├── kavram_api.py         # PHP API istemcisi
    │   └── mock_data.py          # KAVRAM_API_MOCK=true için sahte veri
    │
    ├── modules/                  # Blueprint'ler
    │   ├── auth/                 # Giriş, kayıt, şifre sıfırlama
    │   ├── dashboard/            # Ana sayfa
    │   ├── library/              # Ünite kütüphanesi
    │   ├── leaderboard/          # Sıralama tablosu
    │   ├── onboarding/           # Seviye testi akışı
    │   ├── quiz/                 # Quiz motorları (4 mod)
    │   └── user/                 # Profil, ayarlar, rozetler
    │
    └── templates/
        ├── app_base.html         # Oturum açık sayfalar için navbar + layout
        ├── onboarding_base.html  # Onboarding akışı için minimal layout
        └── ...                   # Modül başına klasörler
```

---

## Veritabanı Şeması

Tablolar `app/db.py` içinde `CREATE TABLE IF NOT EXISTS` ile tanımlanmıştır.

| Tablo | Açıklama |
|---|---|
| `users` | Kullanıcı bilgileri, sınıf, toplam XP |
| `progress` | Kullanıcı × ünite ilerleme durumu |
| `quiz_sessions` | Başlatılan/tamamlanan quiz oturumları |
| `quiz_answers` | Oturum başına verilen cevaplar |
| `scores` | XP kayıt geçmişi |
| `badges` | 18 rozet kataloğu (seed ile doldurulur) |
| `user_badges` | Kullanıcı × rozet kazanım kaydı |

---

## Geliştirme Notları

- **PHP API** henüz entegre edilmedi. `.env` dosyasında `KAVRAM_API_MOCK=true` bırakıldığında uygulama `mock_data.py` üzerinden çalışır.
- **ORM kullanılmamıştır.** Tüm sorgular ham SQL + `DictCursor` ile yazılmıştır (`flask-mysqldb`).
- **MySQL bağlantısı** `utf8mb4` charset ile açılır (emoji desteği için `config.py`'de `MYSQL_CHARSET = "utf8mb4"` zorunludur).
- Backend bağlantısı (dashboard, quiz geçmişi) henüz tamamlanmamış olup arayüz mock veriyle çalışmaktadır.

---

## Lisans

Bu proje TÜBİTAK 2204-A öğrenci proje yarışması kapsamında geliştirilmektedir.
