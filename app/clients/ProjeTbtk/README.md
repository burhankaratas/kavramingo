# ProjeTbtk Content API

Bu klasor, Kavramingo icerik yonetimi icin Laravel API + Filament panelidir.

## Hizli Baslangic

```bash
cd app/clients/ProjeTbtk
composer install
/opt/lampp/bin/php artisan migrate --force
/opt/lampp/bin/php artisan serve --host=127.0.0.1 --port=8000
```

Panel:
- `http://127.0.0.1:8000/admin`

API:
- `http://127.0.0.1:8000/api/v1/*`

## Admin Kullanici

```bash
/opt/lampp/bin/php artisan app:create-admin "Kavramingo Admin" "<admin_email>" "<strong_admin_password>"
```

## CSV Import (Upsert)

Komut:

```bash
/opt/lampp/bin/php artisan app:import-content-csv {type} {file}
```

Type:
- `unit`
- `mcq`
- `flashcard`
- `matching`
- `fill_blank`

Ornek dosyalar:
- `docs/samples/unit-topic.sample.csv` (unit importta kullanilir)
- `docs/samples/mcq.sample.csv`
- `docs/samples/flashcard.sample.csv`
- `docs/samples/matching.sample.csv`
- `docs/samples/fill-blank.sample.csv`

Detaylar:
- `docs/content-import.md`

## Kavramlardan Otomatik MCQ Uretimi

Her unite icin kavram ve tanimlardan 5 sikli (A-B-C-D-E) MCQ uretmek icin:

```bash
/opt/lampp/bin/php artisan app:generate-mcq-from-concepts --per-unit=50 --difficulty=easy
```

Secenekler:
- `--grade=9|10|11|12` -> sadece secili sinif
- `--per-unit=50` -> unite basi soru sayisi
- `--difficulty=easy|medium|hard` -> soru zorluk etiketi
