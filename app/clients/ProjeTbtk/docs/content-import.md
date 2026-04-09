# Content CSV Import

Bu dokuman, panel disindan toplu icerik yukleme (upsert) icindir.

## Komut

```bash
/opt/lampp/bin/php artisan app:import-content-csv {type} {file}
```

`type` degerleri:
- `unit-topic`
- `mcq`
- `flashcard`
- `matching`
- `fill_blank`

## Upsert Kurali

- `unit-topic`: Unit icin unique anahtar `(grade, unit_no)`, Topic icin `(unit_id, topic_no)`
- Soru tipleri: unique anahtar `question_code`
- `question_code` varsa guncellenir, yoksa olusturulur

## CSV Ornekleri

Ornek dosyalar:
- `storage/app/content-csv/unit-topic.sample.csv`
- `storage/app/content-csv/mcq.sample.csv`
- `storage/app/content-csv/flashcard.sample.csv`
- `storage/app/content-csv/matching.sample.csv`
- `storage/app/content-csv/fill-blank.sample.csv`

## Import Sirasi

1. `unit-topic`
2. `mcq`
3. `flashcard`
4. `matching`
5. `fill_blank`

## Notlar

- Matching importunda ayni `question_code` birden fazla satirda olmali (pair bazli).
- Matching soru basina 3-6 cift disinda satirlar skip edilir.
- Import transaction icinde calisir; hata olursa ilgili batch geri alinir.
