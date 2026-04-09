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

# (Laravel content API)
cd app/clients/ProjeTbtk
composer install
composer require filament/filament:"^3.2" -W
php artisan filament:install --panels --no-interaction
cd ../../..

# 4. .env dosyasını oluştur (aşağıdaki örneğe bak)
cp .env.example .env

# 5. XAMPP'ta MySQL'i başlat, ardından:
mysql -u root -e "CREATE DATABASE IF NOT EXISTS kavramingo CHARACTER SET utf8mb4 COLLATE utf8mb4_turkish_ci;"
mysql -u root -e "CREATE DATABASE IF NOT EXISTS kavramingo_content CHARACTER SET utf8mb4 COLLATE utf8mb4_turkish_ci;"

# Laravel API .env (app/clients/ProjeTbtk/.env)
# DB_CONNECTION=mysql
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_DATABASE=kavramingo_content
# DB_USERNAME=root
# DB_PASSWORD=
# DB_SOCKET=/opt/lampp/var/mysql/mysql.sock

# Not: migrate komutu PHP 8.3 + pdo_mysql ile calismalidir.
# Bu ortamda varsayilan php 8.3 ama pdo_mysql yok; XAMPP php'de pdo_mysql var ama 8.2.
# Yerelde uyumlu PHP ile calistir:
# php artisan migrate --force

# 6. Uygulamayı çalıştır
python app.py
```

### Geliştirme için hızlı başlatma

```bash
# bir kez kurulum / migration
./scripts/bootstrap_dev.sh

# terminal 1: Laravel content API
./scripts/run_api.sh

# terminal 2: Flask uygulama
./scripts/run_flask.sh
```

Servisler:
- Flask app: `http://127.0.0.1:5000`
- Laravel API: `http://127.0.0.1:8000/api/v1`
- Filament panel: `http://127.0.0.1:8000/admin`

### Tamamlandi Durumu

Bu repo icerik yonetimi acisindan API tabanli akisa gecmistir:

- Icerik kaynagi: Laravel API (`app/clients/ProjeTbtk`) + Filament panel
- Flask onboarding/dashboard/quiz: API feed ile calisir
- Toplu icerik yukleme: CSV upsert komutu (`app:import-content-csv`)

Hizli son test:

```bash
./scripts/bootstrap_dev.sh
./scripts/run_api.sh
./scripts/run_flask.sh
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
KAVRAM_API_TOKEN=
KAVRAM_API_MOCK=false

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

- **Yeni içerik API (Laravel / ProjeTbtk)**: `/api/v1/*` endpointleri ve `/admin` paneli eklendi.
- Flask onboarding ve dashboard, API modu aktifken içerik verisini `app/clients/kavram_api.py` üzerinden çeker.
- Flask quiz akisi API feed (`/api/v1/quiz-feed`) uzerinden calisir.
- API hazır değilse `.env` dosyasında `KAVRAM_API_MOCK=true` bırakılarak `mock_data.py` ile geliştirme yapılabilir.
- **ORM kullanılmamıştır.** Tüm sorgular ham SQL + `DictCursor` ile yazılmıştır (`flask-mysqldb`).
- **MySQL bağlantısı** `utf8mb4` charset ile açılır (emoji desteği için `config.py`'de `MYSQL_CHARSET = "utf8mb4"` zorunludur).
- Toplu icerik importu icin Laravel komutu: `app:import-content-csv`

---

## Lisans

Bu proje TÜBİTAK 2204-A öğrenci proje yarışması kapsamında geliştirilmektedir.
