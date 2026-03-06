# KavramLingo — Proje Planı ve Geliştirme Rehberi

## İçindekiler

1. [Proje Hakkında](#1-proje-hakkında)
2. [Mimari Genel Bakış](#2-mimari-genel-bakış)
3. [Klasör Yapısı ve Açıklamaları](#3-klasör-yapısı-ve-açıklamaları)
4. [Veritabanı Modelleri](#4-veritabanı-modelleri)
5. [PHP Kavram API Sözleşmesi](#5-php-kavram-api-sözleşmesi)
6. [Uygulama Akışı](#6-uygulama-akışı)
7. [Geliştirme Sırası ve Rehber](#7-geliştirme-sırası-ve-rehber)

---

## 1. Proje Hakkında

**KavramLingo**, din kültürü ve ahlak bilgisi dersindeki kavramları öğrencilere oyunlaştırılmış bir yöntemle öğretmeyi amaçlayan bir web uygulamasıdır.

**Hedef kitle:** 5, 6, 7 ve 8. sınıf öğrencileri

**Temel özellikler:**
- Ünite bazlı kavram öğretimi
- 4 farklı oyun/quiz tipi: çoktan seçmeli, eşleştirme, kelime kartı, boşluk doldurma
- Sınıf seviyesine göre ön test ve otomatik seviye belirleme
- Puan, rozet ve sıralama tablosu (gamification)
- Ücretsiz profil oluşturma

**Tech Stack:**
| Katman | Teknoloji |
|---|---|
| Backend (Ana uygulama) | Python, Flask, Flask-SQLAlchemy, Flask-Login |
| Backend (Kavram verisi) | PHP (ayrı servis/repo) |
| Frontend | HTML, CSS, Bootstrap, Vanilla JS (Jinja2 template) |
| Veritabanı | MySQL |
| ORM | Flask-SQLAlchemy + Flask-Migrate |

---

## 2. Mimari Genel Bakış

```
┌──────────────────────────────────────────────────────┐
│                    Tarayıcı (Browser)                │
│              HTML + CSS + Bootstrap + JS             │
└───────────────────────┬──────────────────────────────┘
                        │  HTTP
┌───────────────────────▼──────────────────────────────┐
│              Flask Ana Uygulama                      │
│                                                      │
│  - Kullanıcı kimlik doğrulama (session-based)        │
│  - Quiz motoru (soru üretimi, cevap kontrolü)        │
│  - Gamification (puan, rozet, sıralama)              │
│  - Ön test ve seviye yerleştirme                     │
│  - Jinja2 ile HTML render                            │
└────────────┬─────────────────────────────────────────┘
             │  HTTP (requests)
┌────────────▼─────────────────────────────────────────┐
│              PHP Kavram API (Ayrı Servis)            │
│                                                      │
│  - Kavramlar, üniteler, konular                      │
│  - CRUD işlemleri (ekle, güncelle, sil, listele)     │
│  - Yalnızca veri sağlar, iş mantığı içermez          │
└────────────┬─────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────┐
│                   MySQL Veritabanı                   │
│  (Flask modelleri + PHP tabloları aynı DB'de olabilir│
│   ya da ayrı iki DB kullanılabilir — tercih size)    │
└──────────────────────────────────────────────────────┘
```

> **Not:** PHP API tamamen hazır olmadan önce Flask geliştirmesine devam edebilmek için `app/clients/kavram_api.py` dosyasında geçici sahte (mock) veri döndüren bir mod eklenebilir. Bunun için `KAVRAM_API_MOCK=true` gibi bir `.env` değişkeni kullanılabilir.

---

## 3. Klasör Yapısı ve Açıklamaları

```
kavramingo/
├── plan.md                          ← Bu dosya
└── backend/                         ← Flask ana uygulama kök dizini
    ├── app.py                       ← Uygulamanın başlangıç noktası; create_app() çağrılır ve Flask çalıştırılır
    ├── config.py                    ← Ortama göre konfigürasyon sınıfları (Development, Production)
    ├── requirements.txt             ← Python bağımlılıkları; pip install -r requirements.txt ile kurulur
    ├── .env                         ← Gizli değerler: DB bağlantısı, secret key, PHP API URL
    ├── .gitignore                   ← Git'e dahil edilmeyecek dosyalar (.env, venv, __pycache__ vb.)
    │
    └── app/                         ← Flask uygulama paketi
        ├── __init__.py              ← App factory: Flask nesnesi oluşturulur, extension'lar ve blueprint'ler kayıt edilir
        ├── extensions.py            ← db (SQLAlchemy), login_manager (Flask-Login), migrate (Flask-Migrate) nesneleri burada tanımlanır
        │
        ├── models/                  ← Veritabanı modelleri (SQLAlchemy ORM sınıfları)
        │   ├── __init__.py          ← Tüm modelleri tek noktadan export eder; Flask-Migrate'in modelleri görmesi için gerekli
        │   ├── user.py              ← Kullanıcı modeli: id, ad, email, şifre, sınıf seviyesi, toplam puan
        │   ├── quiz.py              ← QuizSession (bir quiz oturumu) ve QuizAnswer (her bir cevap) modelleri
        │   ├── score.py             ← Puan kayıtları: hangi quiz'den kaç puan kazanıldığı
        │   ├── badge.py             ← Badge (rozet tanımları) ve UserBadge (kullanıcının kazandığı rozetler)
        │   └── progress.py          ← Öğrencinin ünite/konu bazında ilerleme durumu: locked, in_progress, completed, skipped
        │
        ├── modules/                 ← Uygulamanın işlevsel modülleri; her biri bir Flask Blueprint'tir
        │   │
        │   ├── auth/                ← Kimlik doğrulama modülü
        │   │   ├── __init__.py      ← auth_bp Blueprint nesnesi tanımlanır
        │   │   ├── routes.py        ← /auth/login, /auth/register, /auth/logout endpoint'leri
        │   │   └── forms.py         ← Flask-WTF ile giriş ve kayıt formları (validasyon burada yapılır)
        │   │
        │   ├── user/                ← Kullanıcı profili modülü
        │   │   ├── __init__.py      ← user_bp Blueprint nesnesi
        │   │   └── routes.py        ← /user/profile endpoint'i; kullanıcı bilgileri ve rozet görünümü
        │   │
        │   ├── onboarding/          ← Kayıt sonrası ilk kurulum akışı
        │   │   ├── __init__.py      ← onboarding_bp Blueprint nesnesi
        │   │   └── routes.py        ← /onboarding/class-select (sınıf seçimi) ve /onboarding/placement-test (ön test) endpoint'leri
        │   │
        │   ├── quiz/                ← Quiz motoru; tüm oyun tiplerini yönetir
        │   │   ├── __init__.py      ← quiz_bp Blueprint nesnesi
        │   │   ├── routes.py        ← /quiz/multiple-choice, /quiz/matching, /quiz/flashcard, /quiz/fill-blank endpoint'leri
        │   │   └── engine.py        ← Quiz iş mantığı: PHP API'den soru çekme, cevap doğrulama, oturum yönetimi
        │   │
        │   ├── dashboard/           ← Ana sayfa ve ilerleme özeti
        │   │   ├── __init__.py      ← dashboard_bp Blueprint nesnesi
        │   │   └── routes.py        ← / endpoint'i; öğrencinin ünite ilerlemesi, güncel puanı, son rozeti
        │   │
        │   └── leaderboard/         ← Sıralama tablosu modülü
        │       ├── __init__.py      ← leaderboard_bp Blueprint nesnesi
        │       └── routes.py        ← /leaderboard/ endpoint'i; tüm kullanıcılar puan sırasına göre listelenir
        │
        ├── clients/                 ← Dış servis istemcileri
        │   ├── __init__.py
        │   └── kavram_api.py        ← PHP Kavram API'sine HTTP istekleri atan fonksiyonlar; tüm API çağrıları buradan geçer
        │
        ├── services/                ← İş mantığı servisleri; route'lardan bağımsız, test edilebilir saf fonksiyonlar
        │   ├── __init__.py
        │   ├── scoring.py           ← Puan hesaplama: doğru cevap sayısı, süre bonusu vb.
        │   ├── badge_service.py     ← Rozet kazanma koşullarını kontrol eder ve yeni rozetleri veritabanına yazar
        │   └── placement.py         ← Ön test sonuçlarını analiz eder, hangi ünitelerin tamamlandığını/çalışılacağını belirler
        │
        ├── static/                  ← Statik dosyalar (tarayıcıya doğrudan sunulur)
        │   ├── css/                 ← Projeye özgü CSS dosyaları (Bootstrap CDN üzerinden; özel stiller buraya)
        │   ├── js/                  ← Quiz etkileşimleri, animasyonlar için JavaScript dosyaları
        │   └── img/                 ← Rozet görselleri, logo, ikonlar
        │
        └── templates/               ← Jinja2 HTML şablonları
            ├── base.html            ← Ana layout: navbar, Bootstrap CSS/JS, ortak bloklar (title, content, scripts)
            ├── auth/
            │   ├── login.html       ← Giriş formu
            │   └── register.html    ← Kayıt formu (ad, email, şifre, sınıf seçimi)
            ├── onboarding/
            │   ├── class_select.html    ← Sınıf seçimi sayfası (5/6/7/8. sınıf)
            │   └── placement_test.html  ← Ön test arayüzü
            ├── dashboard/
            │   └── index.html       ← Ana sayfa: ünite kartları, puan göstergesi, son kazanılan rozet
            ├── quiz/
            │   ├── multiple_choice.html ← Çoktan seçmeli soru arayüzü
            │   ├── matching.html        ← Eşleştirme oyunu arayüzü (sürükle-bırak veya tıklama)
            │   ├── flashcard.html       ← Kelime kartı arayüzü (kart çevirme animasyonu)
            │   └── fill_blank.html      ← Boşluk doldurma arayüzü
            ├── leaderboard/
            │   └── index.html       ← Sıralama tablosu
            └── user/
                └── profile.html     ← Kullanıcı profili: bilgiler, kazanılan rozetler, istatistikler
```

---

## 4. Veritabanı Modelleri

Flask tarafının yönettiği tablolar:

### users
| Alan | Tür | Açıklama |
|---|---|---|
| id | INT PK | Otomatik artan birincil anahtar |
| name | VARCHAR(100) | Öğrencinin adı |
| email | VARCHAR(150) UNIQUE | Giriş için kullanılan e-posta |
| password_hash | VARCHAR(255) | Hash'lenmiş şifre (werkzeug) |
| grade | INT | Sınıf seviyesi: 5, 6, 7 veya 8 |
| total_score | INT | Toplam birikimli puan |
| created_at | DATETIME | Kayıt tarihi |

### progress
| Alan | Tür | Açıklama |
|---|---|---|
| id | INT PK | |
| user_id | INT FK → users | |
| unite_id | INT | PHP API'den gelen ünite ID'si |
| konu_id | INT | PHP API'den gelen konu ID'si (opsiyonel) |
| status | VARCHAR(20) | `locked`, `in_progress`, `completed`, `skipped` |
| updated_at | DATETIME | Son güncelleme zamanı |

### quiz_sessions
| Alan | Tür | Açıklama |
|---|---|---|
| id | INT PK | |
| user_id | INT FK → users | |
| unite_id | INT | Hangi ünitede quiz yapıldı |
| quiz_type | VARCHAR(50) | `multiple_choice`, `matching`, `flashcard`, `fill_blank` |
| started_at | DATETIME | |
| finished_at | DATETIME | Quiz bitiş zamanı (NULL ise devam ediyor) |

### quiz_answers
| Alan | Tür | Açıklama |
|---|---|---|
| id | INT PK | |
| session_id | INT FK → quiz_sessions | |
| kavram_id | INT | PHP API'den gelen kavram ID'si |
| given_answer | TEXT | Öğrencinin verdiği cevap |
| is_correct | BOOLEAN | Doğru mu? |

### scores
| Alan | Tür | Açıklama |
|---|---|---|
| id | INT PK | |
| user_id | INT FK → users | |
| points | INT | Kazanılan puan miktarı |
| source_quiz_id | INT FK → quiz_sessions | Hangi quiz'den kazanıldı |
| earned_at | DATETIME | |

### badges
| Alan | Tür | Açıklama |
|---|---|---|
| id | INT PK | |
| name | VARCHAR(100) | Rozet adı (örn: "İlk Adım") |
| description | TEXT | Rozet açıklaması |
| condition_type | VARCHAR(50) | `score`, `streak`, `unit_complete`, `quiz_count` |
| condition_value | INT | Koşul eşiği (örn: 100 puan, 7 gün streak) |
| icon | VARCHAR(100) | Rozet görseli dosya adı |

### user_badges
| Alan | Tür | Açıklama |
|---|---|---|
| id | INT PK | |
| user_id | INT FK → users | |
| badge_id | INT FK → badges | |
| earned_at | DATETIME | Kazanılma tarihi |

---

## 5. PHP Kavram API Sözleşmesi

Flask uygulaması, kavram verilerini tamamen PHP API'sinden çeker. PHP yazan kişinin aşağıdaki endpoint'leri sağlaması gerekir:

| Method | Endpoint | Dönüş | Açıklama |
|---|---|---|---|
| GET | `/unites` | `[{id, name, grade}, ...]` | Tüm üniteler |
| GET | `/unites/{id}/konular` | `[{id, name, unite_id}, ...]` | Üniteye ait konular |
| GET | `/konular/{id}/kavramlar` | `[{id, term, definition, konu_id}, ...]` | Konuya ait kavramlar |
| GET | `/kavramlar/{id}` | `{id, term, definition, konu_id, unite_id}` | Tek kavram detayı |
| GET | `/kavramlar/random?unite={id}&limit={n}` | `[{id, term, definition}, ...]` | Rastgele kavramlar (ön test için) |

**Örnek kavram nesnesi:**
```json
{
  "id": 42,
  "term": "Tevhid",
  "definition": "Allah'ın bir ve tek olduğuna inanmak",
  "konu_id": 3,
  "unite_id": 1
}
```

> PHP API hazır olmadan önce `app/clients/kavram_api.py` içine mock veri eklenebilir. `.env` dosyasına `KAVRAM_API_MOCK=true` eklenerek gerçek API olmadan geliştirme yapılabilir.

---

## 6. Uygulama Akışı

### 6.1 Yeni Kullanıcı Akışı

```
[Anasayfa] → [Kayıt ol]
               ↓
         Ad, email, şifre gir
               ↓
         [Sınıf Seç] (5/6/7/8. sınıf)
               ↓
         [Ön Test]
         Sınıfa kadar tüm ünitelerden
         her üniteden 1 soru sorulur
               ↓
         placement.py sonuçları analiz eder
         ┌─────────────────────────────┐
         │ Doğru cevaplanan ünite      │ → status: "completed" / "skipped"
         │ Yanlış cevaplanan ünite     │ → status: "in_progress" (çalışılacak)
         │ Sınıfın üstündeki üniteler  │ → status: "locked"
         └─────────────────────────────┘
               ↓
         [Dashboard] — öğrencinin başlayacağı yer
```

### 6.2 Günlük Kullanım Akışı

```
[Giriş Yap]
     ↓
[Dashboard]
  - Ünite kartları görünür (locked/in_progress/completed)
  - Güncel puan ve rozet gösterilir
     ↓
[Ünite Seç] (in_progress olanlar erişilebilir)
     ↓
[Konu Seç]
     ↓
[Quiz Tipi Seç veya Sırayla İlerle]
  ┌─────────────────────┐
  │ 1. Kelime Kartı     │ ← Kavramı tanı, önce göz at
  │ 2. Çoktan Seçmeli  │ ← Doğru anlamı seç
  │ 3. Eşleştirme      │ ← Kavram-anlam eşleştir
  │ 4. Boşluk Doldurma │ ← Cümleye kavramı yaz
  └─────────────────────┘
     ↓
[Quiz Biter]
  - Cevaplar kontrol edilir
  - scoring.py ile puan hesaplanır
  - Score tabloya yazılır
  - users.total_score güncellenir
  - badge_service.py rozet kontrolü yapar
  - progress.status güncellenir
     ↓
[Sonuç Ekranı]
  - Doğru/yanlış gösterilir
  - Kazanılan puan gösterilir
  - Varsa yeni rozet gösterilir
     ↓
[Dashboard'a Dön]
```

### 6.3 Ön Test Detay Akışı

```
Öğrenci 7. sınıfta → 5, 6, 7. sınıf üniteleri kapsama girer
Her üniteden 1 kavram sorusu çekilir (kavram_api.get_random_kavramlar)
Sorular çoktan seçmeli formatta sorulur

Test biter:
  ├── Ünite X'te doğru cevap → progress: "skipped" (atlayabilir veya tekrar yapabilir)
  └── Ünite Y'de yanlış cevap → progress: "in_progress" (öncelikli çalışılacak)

Öğrenci "Sıfırdan Başla" derse:
  → Tüm progress kayıtları silinir/sıfırlanır
  → 1. üniteden başlar
```

### 6.4 Gamification Akışı

```
Quiz tamamlanır
     ↓
scoring.py → puan hesapla
     ↓
Score tablosuna kayıt ekle
users.total_score += puan
     ↓
badge_service.py → koşulları kontrol et
  - total_score >= 100 mü? → "İlk 100" rozeti
  - İlk quiz tamamlandı mı? → "İlk Adım" rozeti
  - 5 ünite tamamlandı mı? → "Araştırmacı" rozeti
  - vb.
     ↓
Yeni rozet varsa → UserBadge tablosuna ekle
     ↓
Sonuç ekranında göster
```

---

## 7. Geliştirme Sırası ve Rehber

Aşağıdaki sıra önerilir. Her adım bir öncekine bağımlıdır.

---

### Adım 1 — Ortam Kurulumu

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`.env` dosyasını doldur:
```
FLASK_ENV=development
SECRET_KEY=guclu-bir-anahtar-yaz
DB_HOST=localhost
DB_PORT=3306
DB_NAME=kavramingo
DB_USER=root
DB_PASSWORD=sifren
KAVRAM_API_BASE_URL=http://localhost:8000
```

MySQL'de veritabanını oluştur:
```sql
CREATE DATABASE kavramingo CHARACTER SET utf8mb4 COLLATE utf8mb4_turkish_ci;
```

---

### Adım 2 — Veritabanı Migrasyonu

```bash
flask db init        # migrations/ klasörü oluşur (sadece ilk seferde)
flask db migrate -m "initial"
flask db upgrade
```

Uygulamayı test et:
```bash
flask run
# http://localhost:5000 açılmalı (henüz route olmadığı için 404 normal)
```

---

### Adım 3 — Auth Modülü

**Dosyalar:** `app/modules/auth/routes.py`, `app/modules/auth/forms.py`, `app/models/user.py`

Yapılacaklar:
- [ ] `forms.py`: Flask-WTF ile `LoginForm` ve `RegisterForm` yaz
- [ ] `user.py`: `load_user` callback'ini `extensions.py`'deki `login_manager`'a bağla
- [ ] `routes.py`:
  - `GET/POST /auth/register` → formu göster, kaydı yap, `onboarding.class_select`'e yönlendir
  - `GET/POST /auth/login` → giriş yap, `dashboard.index`'e yönlendir
  - `GET /auth/logout` → oturumu kapat, `auth.login`'e yönlendir
- [ ] `templates/auth/login.html` ve `register.html` formlarını Bootstrap ile yaz
- [ ] Şifre hash'leme için `werkzeug.security.generate_password_hash` kullan

---

### Adım 4 — Onboarding Modülü

**Dosyalar:** `app/modules/onboarding/routes.py`, `app/services/placement.py`

Yapılacaklar:
- [ ] `GET /onboarding/class-select` → sınıf seçim sayfasını göster
- [ ] `POST /onboarding/class-select` → sınıfı `users.grade`'e kaydet, ön teste yönlendir
- [ ] `GET /onboarding/placement-test` → PHP API'den o sınıfa kadar tüm ünitelerden 1'er soru çek, sayfayı göster
- [ ] `POST /onboarding/placement-test` → cevapları al, `placement.py` ile analiz et, `progress` tablosunu doldur, dashboard'a yönlendir

> PHP API hazır değilse `kavram_api.py`'ye mock veri ekle.

---

### Adım 5 — Dashboard Modülü

**Dosyalar:** `app/modules/dashboard/routes.py`, `templates/dashboard/index.html`

Yapılacaklar:
- [ ] `GET /` → `@login_required` ile koru
- [ ] Kullanıcının `progress` kayıtlarını çek
- [ ] PHP API'den ünite isimlerini çek
- [ ] Template'e aktar: ünite kartları (locked/in_progress/completed göstergeli), puan, son rozet

---

### Adım 6 — Quiz Motoru

**Dosyalar:** `app/modules/quiz/routes.py`, `app/modules/quiz/engine.py`, `app/services/scoring.py`

Bu adım projenin kalbidir. Sırayla yapılması önerilir:

**6a. Çoktan Seçmeli:**
- [ ] `engine.py`: PHP API'den kavramları çek, 4 seçenekli soru oluştur
- [ ] `GET /quiz/multiple-choice?unite_id=X` → QuizSession oluştur, ilk soruyu göster
- [ ] `POST /quiz/multiple-choice` → cevabı kontrol et, QuizAnswer kaydet, sonraki soruya geç
- [ ] Quiz bitince scoring.py ile puanı hesapla, Score kaydet, sonuç sayfasını göster

**6b. Eşleştirme:**
- [ ] Kavramları ve tanımlarını karışık listele, kullanıcı eşleştirsin
- [ ] Tüm eşleştirmeler bir anda gönderilir (form POST)

**6c. Kelime Kartı:**
- [ ] Kavramı göster, "Biliyor musun?" → çevir → tanımı gör
- [ ] Öğrenci "Bildim / Bilmedim" işaretler, bilmedikleri tekrar gösterilir

**6d. Boşluk Doldurma:**
- [ ] Tanım içinde kavram kelimesi boşluk olarak gösterilir, öğrenci yazar

---

### Adım 7 — Gamification

**Dosyalar:** `app/services/badge_service.py`, `app/services/scoring.py`, `app/models/badge.py`

Yapılacaklar:
- [ ] Rozet tanımlarını `badges` tablosuna seed verisi olarak ekle
- [ ] Her quiz bitişinde `badge_service.check_badges(user)` çağır
- [ ] Yeni kazanılan rozetleri `user_badges`'e kaydet
- [ ] Sonuç ekranında ve profil sayfasında göster

**Örnek rozet koşulları:**
| Rozet | Koşul |
|---|---|
| İlk Adım | İlk quiz tamamlandı |
| Yüzde Geçti | total_score >= 100 |
| Araştırmacı | 5 ünite tamamlandı |
| Hafıza Ustası | 3 gün üst üste quiz çözüldü |
| Sınıf Birincisi | Leaderboard'da 1. olundu |

---

### Adım 8 — Leaderboard

**Dosyalar:** `app/modules/leaderboard/routes.py`, `templates/leaderboard/index.html`

Yapılacaklar:
- [ ] `users` tablosunu `total_score` alanına göre azalan sırada çek
- [ ] İlk 10 veya tüm kullanıcıları listele
- [ ] Giriş yapmış kullanıcının sıralamasını öne çıkar

---

### Adım 9 — Kullanıcı Profili

**Dosyalar:** `app/modules/user/routes.py`, `templates/user/profile.html`

Yapılacaklar:
- [ ] Kullanıcı bilgileri, toplam puan
- [ ] Kazanılan rozetler (ikon + isim + tarih)
- [ ] Ünite bazında ilerleme istatistiği
- [ ] (Opsiyonel) Şifre değiştirme formu

---

### Adım 10 — UI/UX

- [ ] `templates/base.html` ana layout'u tamamla (navbar, footer, Bootstrap 5 CDN)
- [ ] Tüm sayfaları Bootstrap ile düzenle
- [ ] Quiz arayüzlerine JS animasyonları ekle (kart çevirme, doğru/yanlış renk geçişi)
- [ ] Rozet kazanma animasyonu ekle
- [ ] Mobil uyumluluk (Bootstrap responsive zaten sağlar, kontrol et)

---

### Adım 11 — PHP API Entegrasyon Testi

- [ ] PHP API hazır olduğunda `KAVRAM_API_BASE_URL`'i gerçek adresle güncelle
- [ ] Mock modunu kapat
- [ ] Tüm `kavram_api.py` fonksiyonlarını gerçek veriyle test et
- [ ] Hatalı API yanıtı durumunda kullanıcıya anlamlı hata mesajı göster

---

## Geliştirme Notları

**Circular import önleme:**
Flask uygulamalarında en yaygın hata circular import'tur. Blueprint route dosyalarında modelleri `routes.py` içinde import et, `__init__.py` içinde değil.

**Login koruması:**
Giriş gerektiren tüm route'lara `@login_required` dekoratörü ekle. `extensions.py`'de `login_manager.login_view = "auth.login"` ayarı zaten yapıldı.

**PHP API erişilemeyen durumlar:**
`kavram_api.py` fonksiyonlarını `try/except requests.exceptions.RequestException` ile sar. API cevap vermezse sayfayı çökertme, hata mesajı göster.

**Şifre güvenliği:**
`werkzeug.security.generate_password_hash` ve `check_password_hash` kullan. Şifre asla düz metin olarak saklanmamalı.

**Session güvenliği:**
`.env` dosyasındaki `SECRET_KEY` değerini uzun ve tahmin edilemez bir string ile değiştir. Bu değer production'da kesinlikle değiştirilmeli.
