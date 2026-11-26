# Tabel nasional Gold (tahap 6)

Dihasilkan `python pipeline.py` (`src/gold/nasional.py`) dari Silver. Berkas utama: `data/gold/tabel-nasional.csv` dan `data/gold/tabel-nasional.parquet`.

- Butir: satu baris per **periode x seri**; 89 baris, 5 seri, 65 periode.

- Seri utama: `var1394`, `var1353`. Pembanding: `MDG_0000000003`, `SDGFPALL`, `SP.ADO.TFRT`.

- BPS menerbitkan baris Indonesia (kode 9999) untuk kedua seri utama pada 2012 dan 2017, sehingga **tidak ada agregasi provinsi**. Bila baris Indonesia tidak tersedia, tabel tidak mengarang agregat: baris seri/periode itu tidak dibuat dan keputusannya dinyatakan sebagai tidak punya padanan nasional, karena bobot populasi perempuan 15-19 tidak tersedia di paket.

- `MDG_0000000003` memakai rincian `umur=15-19`; rincian `10-14` tidak dipakai karena penyebutnya berbeda.

- Kolom `asal_angka` menyatakan asal setiap angka: `baris Indonesia (BPS)` atau `pembanding nasional (WHO GHO/WDI)`.

## Rekap

| kelompok | seri_kode | baris |
|---|---|---|
| pembanding | SP.ADO.TFRT | 65 |
| pembanding | MDG_0000000003 | 14 |
| pembanding | SDGFPALL | 6 |
| utama | var1353 | 2 |
| utama | var1394 | 2 |

## Cuplikan

| periode | seri_kode | kelompok | rincian | nilai | satuan | asal_angka |
|---|---|---|---|---|---|---|
| 1960 | SP.ADO.TFRT | pembanding | total | 145.32 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1961 | SP.ADO.TFRT | pembanding | total | 146.86 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1962 | SP.ADO.TFRT | pembanding | total | 148.43 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1963 | SP.ADO.TFRT | pembanding | total | 149.22 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1964 | SP.ADO.TFRT | pembanding | total | 150.50 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1965 | SP.ADO.TFRT | pembanding | total | 151.70 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1966 | SP.ADO.TFRT | pembanding | total | 146.17 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1967 | SP.ADO.TFRT | pembanding | total | 141.68 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1968 | SP.ADO.TFRT | pembanding | total | 137.00 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1969 | SP.ADO.TFRT | pembanding | total | 133.37 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1970 | SP.ADO.TFRT | pembanding | total | 130.61 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
| 1971 | SP.ADO.TFRT | pembanding | total | 130.34 | per_1000_perempuan_seumur | pembanding nasional (WDI) |
