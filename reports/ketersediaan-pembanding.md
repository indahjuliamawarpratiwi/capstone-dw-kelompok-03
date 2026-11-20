# Ketersediaan seri pembanding nasional

Dihasilkan `python pipeline.py` (`src/silver/pembanding.py`). Tahun survei seri utama: 2012, 2017.

## Ringkasan per seri dan rincian

| seri_kode | sumber | rincian | satuan | jumlah_tahun | awal | akhir | tahun_survei_utama_tersedia | batas_bawah_atas |
|---|---|---|---|---|---|---|---|---|
| MDG_0000000003 | who_gho | umur=10-14 | per_1000_perempuan_seumur | 12 | 2002 | 2016 | (tidak ada) | tidak |
| MDG_0000000003 | who_gho | umur=15-19 | per_1000_perempuan_seumur | 14 | 2001 | 2016 | (tidak ada) | tidak |
| SDGFPALL | who_gho | total | persen | 6 | 2002 | 2017 | 2012, 2017 | tidak |
| SP.ADO.TFRT | wdi | total | per_1000_perempuan_seumur | 65 | 1960 | 2024 | 2012, 2017 | tidak |

## WDI: baris ada vs nilai ada

| indicator_id | baris_ada | nilai_ada |
|---|---|---|
| SP.ADO.TFRT | 66 | 65 |

## Ketersediaan pada tahun survei seri utama (1 = ada)

| seri_kode | rincian | 2012 | 2017 |
|---|---|---|---|
| MDG_0000000003 | umur=10-14 | 0 | 0 |
| MDG_0000000003 | umur=15-19 | 0 | 0 |
| SDGFPALL | total | 1 | 1 |
| SP.ADO.TFRT | total | 1 | 1 |

## Rincian yang kandidat sebanding

| pasangan | seri_utama | pembanding | alasan |
|---|---|---|---|
| P1 | var1353 | SP.ADO.TFRT (total) | BPS total = umur 15–19 (judul); WDI hanya 15–19 |
| P2 | var1353 | MDG_0000000003 (umur=15-19) | WHO rincian umur=15-19; baris 10-14 tidak sebanding |
| P3 | var1394 | SDGFPALL (total) | keduanya perempuan 15–49 tanpa rincian |
| P4 | MDG_0000000003 | SP.ADO.TFRT (total) | WHO umur=15-19 |

Matriks lengkap seri x rincian x tahun: `reports/ketersediaan-pembanding.csv`.
