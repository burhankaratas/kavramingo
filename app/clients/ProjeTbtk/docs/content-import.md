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

## Kavramlardan Otomatik Eslestirme Uretimi

Kavram bankasindaki kayitlardan otomatik matching sorulari uretmek icin:

```bash
/opt/lampp/bin/php artisan app:generate-matching-from-concepts --pair-count=4 --max-per-unit=200
```

Secenekler:
- `--grade=9|10|11|12` -> sadece secili sinif
- `--pair-count=3..6` -> bir sorudaki cift sayisi
- `--max-per-unit=0|N` -> unite basi maksimum soru (0 = limitsiz)

Komut upsert mantiginda calisir; ayni kombinasyon kodu varsa gunceller.

## Kavramlardan Otomatik Bosluk Doldurma Uretimi

Kavram tanimlarindan otomatik bosluk doldurma sorulari uretmek icin:

```bash
/opt/lampp/bin/php artisan app:generate-fillblank-from-concepts --variants=2 --max-per-unit=300
```

Secenekler:
- `--grade=9|10|11|12` -> sadece secili sinif
- `--variants=1|2` -> kavram basi soru varyanti (2 onerilir)
- `--max-per-unit=0|N` -> unite basi maksimum soru (0 = limitsiz)

Soru kalibi ornegi:
- `<kavram tanimi> Bu kavrama ___ denir.`
- `Tanim: <kavram tanimi> Yukaridaki tanimin kavrami: ___`
