# Tabel nasional Gold (tahap 6)

Dihasilkan `python pipeline.py` (`src/gold/nasional_gold.py`) dari Silver. Berkas utama: `data/gold/nasional.parquet`; alias kompatibilitas: `data/gold/tabel-nasional.csv` dan `data/gold/tabel-nasional.parquet`.

- Butir: satu baris per **periode x seri**; **89 baris**, 5 seri, 65 periode.

- Parquet `data/gold/nasional.parquet`: **89 baris**.

- SQL `gold_nasional`: **89 baris** (status: **sama**).

- Laporan ini: **89 baris** pada tabel bagian 3.

- Seri utama: `var1394`, `var1353`. Pembanding: `MDG_0000000003`, `SDGFPALL`, `SP.ADO.TFRT`.

- `asal` menyatakan asal setiap angka: `baris_indonesia`, `pembanding`, atau `agregat`.

- BPS menerbitkan baris Indonesia (kode 9999) untuk kedua seri utama pada 2012 dan 2017, sehingga tidak ada agregasi provinsi. Bila baris Indonesia tidak tersedia, seri tidak diagregasi dan dinyatakan tidak punya padanan nasional karena bobot populasi perempuan 15-19 tidak tersedia di paket.

- `MDG_0000000003` memakai rincian `umur=15-19`; rincian `10-14` tidak dipakai karena penyebutnya berbeda.

## 1. Rekap per seri dan asal

| seri_kode | asal | baris | periode_awal | periode_akhir | rincian | sumber |
|---|---|---|---|---|---|---|
| MDG_0000000003 | pembanding | 14 | 2001 | 2016 | umur=15-19 | who_gho |
| SDGFPALL | pembanding | 6 | 2002 | 2017 | total | who_gho |
| SP.ADO.TFRT | pembanding | 65 | 1960 | 2024 | total | wdi |
| var1353 | baris_indonesia | 2 | 2012 | 2017 | total | bps |
| var1394 | baris_indonesia | 2 | 2012 | 2017 | total | bps |

## 2. Asal per seri

| seri_kode | asal_seri |
|---|---|
| MDG_0000000003 | pembanding |
| SDGFPALL | pembanding |
| SP.ADO.TFRT | pembanding |
| var1353 | baris_indonesia |
| var1394 | baris_indonesia |

## 3. Semua baris

| periode | seri_kode | rincian | nilai | satuan | asal | _berkas_raw |
|---|---|---|---|---|---|---|
| 2001 | MDG_0000000003 | umur=15-19 | 50.93 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2002 | MDG_0000000003 | umur=15-19 | 53.12 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2003 | MDG_0000000003 | umur=15-19 | 55.92 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2004 | MDG_0000000003 | umur=15-19 | 51.00 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2005 | MDG_0000000003 | umur=15-19 | 52.28 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2006 | MDG_0000000003 | umur=15-19 | 50.95 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2007 | MDG_0000000003 | umur=15-19 | 49.48 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2008 | MDG_0000000003 | umur=15-19 | 46.88 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2009 | MDG_0000000003 | umur=15-19 | 47.00 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2010 | MDG_0000000003 | umur=15-19 | 46.86 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2011 | MDG_0000000003 | umur=15-19 | 48.49 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2013 | MDG_0000000003 | umur=15-19 | 47.37 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2015 | MDG_0000000003 | umur=15-19 | 39.92 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2016 | MDG_0000000003 | umur=15-19 | 36.11 | per_1000_perempuan_seumur | pembanding | who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv |
| 2002 | SDGFPALL | total | 77.10 | persen | pembanding | who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv |
| 2007 | SDGFPALL | total | 77.00 | persen | pembanding | who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv |
| 2012 | SDGFPALL | total | 79.00 | persen | pembanding | who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv |
| 2015 | SDGFPALL | total | 78.20 | persen | pembanding | who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv |
| 2016 | SDGFPALL | total | 77.60 | persen | pembanding | who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv |
| 2017 | SDGFPALL | total | 77.00 | persen | pembanding | who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv |
| 1960 | SP.ADO.TFRT | total | 145.32 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1961 | SP.ADO.TFRT | total | 146.86 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1962 | SP.ADO.TFRT | total | 148.43 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1963 | SP.ADO.TFRT | total | 149.22 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1964 | SP.ADO.TFRT | total | 150.50 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1965 | SP.ADO.TFRT | total | 151.70 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1966 | SP.ADO.TFRT | total | 146.17 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1967 | SP.ADO.TFRT | total | 141.68 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1968 | SP.ADO.TFRT | total | 137.00 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1969 | SP.ADO.TFRT | total | 133.37 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1970 | SP.ADO.TFRT | total | 130.61 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1971 | SP.ADO.TFRT | total | 130.34 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1972 | SP.ADO.TFRT | total | 128.41 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1973 | SP.ADO.TFRT | total | 129.78 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1974 | SP.ADO.TFRT | total | 127.19 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1975 | SP.ADO.TFRT | total | 122.33 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1976 | SP.ADO.TFRT | total | 120.75 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1977 | SP.ADO.TFRT | total | 119.24 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1978 | SP.ADO.TFRT | total | 119.36 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1979 | SP.ADO.TFRT | total | 116.81 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1980 | SP.ADO.TFRT | total | 114.38 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1981 | SP.ADO.TFRT | total | 112.03 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1982 | SP.ADO.TFRT | total | 109.14 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1983 | SP.ADO.TFRT | total | 103.68 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1984 | SP.ADO.TFRT | total | 100.63 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1985 | SP.ADO.TFRT | total | 91.20 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1986 | SP.ADO.TFRT | total | 83.35 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1987 | SP.ADO.TFRT | total | 83.04 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1988 | SP.ADO.TFRT | total | 78.71 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1989 | SP.ADO.TFRT | total | 76.18 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1990 | SP.ADO.TFRT | total | 74.85 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1991 | SP.ADO.TFRT | total | 72.29 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1992 | SP.ADO.TFRT | total | 68.46 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1993 | SP.ADO.TFRT | total | 65.43 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1994 | SP.ADO.TFRT | total | 64.40 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1995 | SP.ADO.TFRT | total | 63.92 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1996 | SP.ADO.TFRT | total | 61.50 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1997 | SP.ADO.TFRT | total | 59.25 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1998 | SP.ADO.TFRT | total | 56.66 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 1999 | SP.ADO.TFRT | total | 54.83 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2000 | SP.ADO.TFRT | total | 53.85 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2001 | SP.ADO.TFRT | total | 53.02 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2002 | SP.ADO.TFRT | total | 51.76 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2003 | SP.ADO.TFRT | total | 50.41 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2004 | SP.ADO.TFRT | total | 48.21 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2005 | SP.ADO.TFRT | total | 48.10 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2006 | SP.ADO.TFRT | total | 47.77 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2007 | SP.ADO.TFRT | total | 47.67 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2008 | SP.ADO.TFRT | total | 46.29 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2009 | SP.ADO.TFRT | total | 45.59 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2010 | SP.ADO.TFRT | total | 45.68 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2011 | SP.ADO.TFRT | total | 45.59 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2012 | SP.ADO.TFRT | total | 44.62 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2013 | SP.ADO.TFRT | total | 42.67 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2014 | SP.ADO.TFRT | total | 40.13 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2015 | SP.ADO.TFRT | total | 37.86 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2016 | SP.ADO.TFRT | total | 35.36 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2017 | SP.ADO.TFRT | total | 32.79 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2018 | SP.ADO.TFRT | total | 30.65 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2019 | SP.ADO.TFRT | total | 28.88 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2020 | SP.ADO.TFRT | total | 27.18 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2021 | SP.ADO.TFRT | total | 26.82 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2022 | SP.ADO.TFRT | total | 26.58 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2023 | SP.ADO.TFRT | total | 26.42 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2024 | SP.ADO.TFRT | total | 25.65 | per_1000_perempuan_seumur | pembanding | wdi/2026-10-20/data/kelompok-03-hal-01.json |
| 2012 | var1353 | total | 48.00 | per_1000_perempuan_seumur | baris_indonesia | bps/2026-10-20/json/sdg3_3_7_2_v1353.json |
| 2017 | var1353 | total | 36.00 | per_1000_perempuan_seumur | baris_indonesia | bps/2026-10-20/json/sdg3_3_7_2_v1353.json |
| 2012 | var1394 | total | 57.90 | persen | baris_indonesia | bps/2026-10-20/json/sdg3_3_7_1_v1394.json |
| 2017 | var1394 | total | 57.20 | persen | baris_indonesia | bps/2026-10-20/json/sdg3_3_7_1_v1394.json |
