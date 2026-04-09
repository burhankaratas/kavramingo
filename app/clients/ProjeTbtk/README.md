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
/opt/lampp/bin/php artisan app:create-admin "Kavramingo Admin" "admin@kavramingo.local" "Admin123!"
```

## CSV Import (Upsert)

Komut:

```bash
/opt/lampp/bin/php artisan app:import-content-csv {type} {file}
```

Type:
- `unit-topic`
- `mcq`
- `flashcard`
- `matching`
- `fill_blank`

Ornek dosyalar:
- `docs/samples/unit-topic.sample.csv`
- `docs/samples/mcq.sample.csv`
- `docs/samples/flashcard.sample.csv`
- `docs/samples/matching.sample.csv`
- `docs/samples/fill-blank.sample.csv`

Detaylar:
- `docs/content-import.md`
