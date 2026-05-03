# Kavramingo - Kullanim ve Deploy Rehberi

Bu dokuman, projeyi gelistirme ortaminda calistirmak, icerik panelini kullanmak,
CSV ile toplu icerik yuklemek ve production ortamina deploy etmek icin hazirlandi.

## 1) Mimari Ozet

Proje iki ana uygulamadan olusur:

1. Flask uygulamasi (kullanici arayuzu):
   - Port: `5000`
   - Dizin: repo koku
2. Laravel Content API + Filament Panel:
   - Port: `8000`
   - Dizin: `app/clients/ProjeTbtk`

Veritabani:
- Flask uygulama DB: `kavramingo`
- Icerik API DB: `kavramingo_content`
- MySQL: XAMPP

## 2) Gereksinimler

- Linux + XAMPP (`/opt/lampp`)
- Python 3.12+
- Composer
- Node (panel asset gereksinimi icin, zorunlu degil ama onerilir)

## 3) Gelistirme Ortaminda Ilk Kurulum

Repo dizinine gec:

```bash
cd /home/mbkaratas/Desktop/Software/Github/kavramingo-clean
```

XAMPP MySQL baslat:

```bash
xampp startmysql
```

Bootstrap scriptini calistir:

```bash
./scripts/bootstrap_dev.sh
```

Bu script sunlari yapar:
- `kavramingo` ve `kavramingo_content` DB olusturur
- `.env` dosyalarini kontrol eder
- Laravel migration calistirir

## 4) Servisleri Calistirma

Iki terminal kullan:

Terminal A (Laravel API + Panel):

```bash
./scripts/run_api.sh
```

Terminal B (Flask):

```bash
./scripts/run_flask.sh
```

Erisim adresleri:
- Flask: `http://127.0.0.1:5000`
- API: `http://127.0.0.1:8000/api/v1`
- Panel: `http://127.0.0.1:8000/admin`

## 5) Admin Panel Girisi

Ilk admin kullaniciyi olustur:

```bash
cd app/clients/ProjeTbtk
/opt/lampp/bin/php artisan app:create-admin "Kavramingo Admin" "<admin_email>" "<strong_admin_password>"
```

Panel girisi:
- Email: `<admin_email>`
- Sifre: `<strong_admin_password>`

Sonra sifreyi panelden degistirmen onerilir.

## 6) Flask - API Baglantisi

Flask `.env` dosyasinda bu alanlar dolu olmali:

```env
KAVRAM_API_BASE_URL=http://127.0.0.1:8000
KAVRAM_API_TOKEN=<read_token>
KAVRAM_API_MOCK=false
```

Not:
- `KAVRAM_API_MOCK=true` yaparsan mock veriye duser.
- Productionda `KAVRAM_API_MOCK=false` kalmali.

## 7) API Token Uretimi

Tokenleri panelden (`Api Tokens`) ya da DB uzerinden yonetebilirsin.

Gelistirme test token ornegi:

```bash
cd app/clients/ProjeTbtk
/opt/lampp/bin/php artisan tinker --execute="\App\Models\ApiToken::create(['name'=>'flask-read','token_hash'=>hash('sha256','<your_read_token>'),'scopes'=>['content:read'],'is_active'=>true]);"
```

Flask `.env`:

```env
KAVRAM_API_TOKEN=<your_read_token>
```

## 8) Icerik Yonetimi (Panel)

Panelden su kaynaklari yonetilir:
- Units
- Topics
- Concepts
- Questions (MCQ / Flashcard / Matching / Fill Blank)
- Quiz Configs
- Placement Rules
- Api Tokens

Temel is akisi:
1. Unit ekle
2. Unit altina Topic ekle
3. Topic altina Question ekle
4. Flask tarafinda ilgili unitenin quizini baslat

## 9) CSV ile Toplu Icerik Yukleme (Upsert)

Komut:

```bash
cd app/clients/ProjeTbtk
/opt/lampp/bin/php artisan app:import-content-csv {type} {file}
```

`type`:
- `unit`
- `mcq`
- `flashcard`
- `matching`
- `fill_blank`

Repo icindeki ornekler:
- `app/clients/ProjeTbtk/docs/samples/unit-topic.sample.csv`
- `app/clients/ProjeTbtk/docs/samples/mcq.sample.csv`
- `app/clients/ProjeTbtk/docs/samples/flashcard.sample.csv`
- `app/clients/ProjeTbtk/docs/samples/matching.sample.csv`
- `app/clients/ProjeTbtk/docs/samples/fill-blank.sample.csv`

Ornek import:

```bash
cd app/clients/ProjeTbtk
/opt/lampp/bin/php artisan app:import-content-csv unit docs/samples/unit-topic.sample.csv
/opt/lampp/bin/php artisan app:import-content-csv mcq docs/samples/mcq.sample.csv
```

Upsert kurali:
- Unit: `(grade, unit_no)`
- Topic: `(unit_id, topic_no)`
- Question: `question_code`

## 10) Test Senaryosu (Onerilen)

1. Panelde 1 unit + 1 topic + her quiz tipinden soru ekle
2. Flask'ta kayit/giris yap
3. Onboarding adimlarini gec
4. Dashboard'dan quiz baslat
5. Sorularin panelden girdigin icerikten geldigini dogrula
6. Sonuc ve skor kaydini kontrol et

## 11) Production Deploy (Onerilen)

Bu repo su an gelistirme odakli. Production icin onerilen yol:

### A) Servis Modeli

- Flask: `gunicorn` + `systemd`
- Laravel: Apache/Nginx + PHP-FPM
- MySQL: ayri servis (XAMPP yerine native MySQL/MariaDB onerilir)

### B) Reverse Proxy

Tek domain altinda:
- `https://app.domain.com/` -> Flask
- `https://app.domain.com/api/` ve `/admin` -> Laravel

### C) Guvenlik

- `APP_DEBUG=false`
- guclu `SECRET_KEY`
- HTTPS zorunlu
- tokenlari panelden yonet, gereksiz tokenlari revoke et
- DB yedeklerini otomatik al

### D) Deploy Akisi

1. `git pull`
2. Flask dependency kontrolu (`pip install -r requirements.txt`)
3. Laravel dependency kontrolu (`composer install --no-dev`)
4. Migration (`php artisan migrate --force`)
5. Servis restart (Flask + web server)

## 12) Sik Hatalar ve Cozumler

### `ImportError: libmariadb.so.3`

Flask calistirmadan once:

```bash
export LD_LIBRARY_PATH=/opt/lampp/lib:${LD_LIBRARY_PATH:-}
```

`./scripts/run_flask.sh` bunu otomatik yapar.

### `SQLSTATE ... could not find driver`

Laravel komutlarini XAMPP php ile calistir:

```bash
/opt/lampp/bin/php artisan migrate --force
```

### API 401 hatasi

- `KAVRAM_API_TOKEN` dogru mu?
- token aktif mi?
- token scope: `content:read` var mi?

## 13) Operasyon Checklist

- [ ] XAMPP MySQL acik
- [ ] Flask `.env` dogru
- [ ] Laravel `.env` dogru
- [ ] Migrationlar guncel
- [ ] Admin panel girisi calisiyor
- [ ] `quiz-feed` endpoint token ile 200 donuyor
- [ ] Flask quiz sorulari panel iceriginden geliyor

---

Hata bildirirken asagidakileri birlikte paylasirsan cozum hizlanir:
- Hata mesaji (tam)
- Hangi URL/komut
- Son yaptigin adim
- Gerekirse ekran goruntusu
