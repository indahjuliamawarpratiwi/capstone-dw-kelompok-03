# Panel Gold provinsi dan tabel nasional

Dihasilkan `python pipeline.py` (`src/gold/panel.py`). Satu sel = satu seri x provinsi x periode.

## Aturan pemilihan

- Sumber kanonik BPS: JSON sesuai K-002; CSV tetap pembanding.

- Panel hanya `var1394` dan `var1353`, rincian `total`; `9999` tidak masuk panel (K-025).

- Satu nilai per sel; duplikat kunci tidak diizinkan.

- Tabel nasional memuat rincian yang dipakai `PASANGAN` dari BPS, WHO, dan WDI dengan kolom `asal`; rincian umur `10-14` tetap hanya di Silver.

- Penanda Sprint 1 dibawa apa adanya; nilai anomali tidak diubah.

- Hanya periode tahunan; tidak ada agregasi semesteran atau bulanan.

## Ringkasan

| ukuran | nilai |
|---|---|
| baris panel | 152 |
| sel terisi | 134 |
| sel kosong berkategori | 18 |
| sel bertanda | 5 |
| baris tabel nasional | 89 |

Rincian sel kosong: `reports/grid-sel-kosong.csv`. Penanda: `reports/anomali.csv`.
