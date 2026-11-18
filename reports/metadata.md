# Metadata seri: nama, satuan, kode SDG

Dihasilkan `python pipeline.py` dari berkas mentah dan `src/konfigurasi.py`. Tabel lengkap ada di `docs/seri.csv`. Bila katalog dan berkas mentah berbeda, berkas mentah yang dipakai dan koreksinya dicatat di `log-keputusan.csv`.

## Nama di berkas mentah dan nama baku

| seri_kode | nama_di_berkas | nama_baku |
|---|---|---|
| var1394 | Proporsi Perempuan Usia Reproduksi (15-49 tahun) atau Pasangannya yang Memiliki Kebutuhan Keluarga Berencana dan Menggunakan Alat Kontrasepsi Metode Modern | Proporsi perempuan usia reproduksi (15–49 tahun) atau pasangannya yang memiliki kebutuhan KB dan menggunakan alat kontrasepsi metode modern |
| var1353 | Angka Kelahiran Pada Perempuan Usia 15-19 Tahun Menurut Provinsi | Angka kelahiran pada perempuan umur 15–19 tahun (per 1.000 perempuan 15–19) |
| SP.ADO.TFRT | Adolescent fertility rate (births per 1,000 women ages 15-19) | Adolescent fertility rate (births per 1,000 women ages 15-19) |
| MDG_0000000003 | Adolescent birth rate | Adolescent birth rate (per 1000 women in the age group) |
| SDGFPALL | Family planning satisfied with modern methods | Family planning satisfied with modern methods (%) |

## Satuan dan kode SDG

| seri_kode | katalog_satuan | satuan | bukti_satuan | katalog_sdg | sdg_kode |
|---|---|---|---|---|---|
| var1394 | persen | persen | var.unit: 'Persen' | 3.7.1 | 3.7.1 |
| var1353 | tidak_ada | per_1000_perempuan_seumur | var.unit dan kolom satuan CSV kosong; judul menyebut perempuan 15–19; definisi baku indikator yang sama di metadata WHO ('per 1,000 females in the respective age group') dan nama WDI ('births per 1,000 women ages 15-19'); besaran angka (puluhan) sesuai per 1.000, bukan persen | 3.7.2 | 3.7.2 |
| SP.ADO.TFRT | — | per_1000_perempuan_seumur | name: '(births per 1,000 women ages 15-19)' | — | 3.7.2 |
| MDG_0000000003 | — | per_1000_perempuan_seumur | kolom RATE_PER_1000_N; UnitOfMeasure: 'Annual number of births per 1000 adolescent women' | 3.7.2 | 3.7.2 |
| SDGFPALL | — | persen | kolom RATE_PER_100_N | 3.7.1 | 3.7.1 |

## Koreksi katalog

| seri_kode | koreksi_katalog |
|---|---|
| var1353 | satuan tidak_ada -> per_1000_perempuan_seumur |
| SP.ADO.TFRT | kode SDG kosong -> 3.7.2 |

## Catatan BPS (var.note)

| var_id | catatan (tanpa tag HTML) |
|---|---|
| 1394 | Sumber : Survei Demografi dan Kesehatan Indonesia |
| 1353 | Sumber: Indonesia Demographic and Health Survey |

## Metadata WDI yang muncul di lebih dari satu berkas

| seri | jumlah_entri | berkas | isi_sama |
|---|---|---|---|
| SP.ADO.TFRT | 2 | sumber2_indikator.json, sumber46_indikator.json | ya |

## Judul dengan spasi di awal/akhir

var1353: teks asli disimpan, versi rapi di kolom nama_di_berkas.
