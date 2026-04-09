# Content CSV Import

Bu dokuman, panel disindan toplu icerik yukleme (upsert) icindir.

## Komut

```bash
/opt/lampp/bin/php artisan app:import-content-csv {type} {file}
```

`type` degerleri:
- `unit`
- `mcq`
- `flashcard`
- `matching`
- `fill_blank`

## Upsert Kurali

- `unit`: Unit icin unique anahtar `(grade, unit_no)`
- Soru tipleri: unique anahtar `question_code`
- `question_code` varsa guncellenir, yoksa olusturulur

## CSV Ornekleri

Ornek dosyalar:
- `docs/samples/unit-topic.sample.csv`
- `docs/samples/mcq.sample.csv`
- `docs/samples/flashcard.sample.csv`
- `docs/samples/matching.sample.csv`
- `docs/samples/fill-blank.sample.csv`

Istersen bu dosyalari `storage/app/content-csv/` klasorune kopyalayip ordan da import edebilirsin.

## Import Sirasi

1. `unit`
2. `mcq`
3. `flashcard`
4. `matching`
5. `fill_blank`

## Notlar

- Unit importu her unite icin otomatik bir "Genel" topic olusturur.
- Panelde soru eklerken konu secimi yerine unite secersin; teknik olarak default topic kullanilir.
- Matching importunda ayni `question_code` birden fazla satirda olmali (pair bazli).
- Matching soru basina 3-6 cift disinda satirlar skip edilir.
- Import transaction icinde calisir; hata olursa ilgili batch geri alinir.
