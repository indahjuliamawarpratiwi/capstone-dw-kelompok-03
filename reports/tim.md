# LAPORAN CAPSTONE DATA WRANGLING
## INDIKATOR SDG INDONESIA DARI BANYAK SUMBER
### KASUS 03 — KESEHATAN REPRODUKSI REMAJA

---

# 1. Ringkasan Eksekutif

## 1.1 Latar Belakang

Data merupakan salah satu komponen penting dalam proses pengambilan keputusan, khususnya dalam mengevaluasi pencapaian Tujuan Pembangunan Berkelanjutan atau Sustainable Development Goals (SDGs). Salah satu aspek yang menjadi perhatian adalah kesehatan reproduksi remaja, yang berkaitan dengan akses terhadap informasi, pelayanan kesehatan reproduksi, serta pemenuhan kebutuhan keluarga berencana.

Informasi mengenai indikator kesehatan reproduksi dapat diperoleh dari berbagai lembaga, seperti Badan Pusat Statistik (BPS), World Health Organization (WHO), dan World Development Indicators (WDI). Masing-masing sumber memiliki struktur, format, definisi, cakupan wilayah, serta periode pengamatan yang berbeda. Oleh karena itu, diperlukan proses data wrangling untuk mengumpulkan, memeriksa, membersihkan, mentransformasikan, dan mengintegrasikan data agar dapat digunakan untuk analisis lebih lanjut.

## 1.2 Tujuan

Kegiatan Capstone Data Wrangling ini bertujuan untuk:

1. Mengumpulkan data indikator kesehatan reproduksi remaja dari berbagai sumber resmi.
2. Mengidentifikasi format, struktur, dan karakteristik masing-masing dataset.
3. Melakukan profiling untuk mengetahui kondisi awal data.
4. Mengidentifikasi permasalahan kualitas data, seperti missing value, duplikasi, dan ketidakkonsistenan format.
5. Menyusun data dalam struktur yang terstandarisasi.
6. Mempertahankan informasi lineage agar setiap nilai dapat ditelusuri ke sumber aslinya.
7. Menyiapkan data terintegrasi yang dapat digunakan untuk analisis lebih lanjut.

## 1.3 Ruang Lingkup

Pengerjaan difokuskan pada Kasus 03, yaitu Kesehatan Reproduksi Remaja. Sumber data yang digunakan meliputi:

- Badan Pusat Statistik (BPS).
- World Health Organization (WHO).
- World Development Indicators (WDI).

Data dikumpulkan dalam paket data yang terdiri atas 13 berkas mentah sesuai dengan manifest yang disediakan.

## 1.4 Hasil Sementara

Berdasarkan proses pengunduhan dan pemeriksaan awal, diperoleh 13 berkas yang sesuai dengan MANIFEST.csv. Data terdiri atas berkas CSV dan JSON dari sumber BPS, WHO, dan WDI.

Pemeriksaan awal menunjukkan bahwa data BPS memiliki dua dataset CSV dengan masing-masing 69 baris dan 11 kolom. Sementara itu, data WHO memiliki dua dataset CSV, masing-masing sebanyak 26 baris dan 6 baris dengan 14 kolom. Data WDI tersedia dalam bentuk JSON beserta beberapa berkas metadata.

Hasil tersebut menjadi dasar untuk melanjutkan proses profiling, pembersihan, transformasi, dan integrasi data.

---

# 2. Data dan Lineage

## 2.1 Sumber Data

Data yang digunakan dalam proyek ini berasal dari tiga sumber utama, yaitu BPS, WHO, dan WDI.

| Sumber | Format | Jumlah Berkas | Keterangan |
|---|---|---:|---|
| BPS | CSV | 2 | Data indikator |
| BPS | JSON | 2 | Struktur dan metadata indikator |
| BPS | JSON | 1 | Manifest asal |
| WDI | JSON | 1 | Data indikator |
| WDI | JSON | 3 | Metadata |
| WHO | CSV | 2 | Data indikator |
| WHO | JSON | 2 | Metadata indikator |
| **Total** | | **13** | |

Seluruh berkas disimpan dalam direktori `data/raw/` dengan mempertahankan struktur folder berdasarkan sumber dan tanggal snapshot.

## 2.2 Struktur Penyimpanan Data Mentah

Struktur penyimpanan data mentah yang digunakan adalah sebagai berikut:

```text
data/
├── raw/
│   ├── MANIFEST.csv
│   ├── bps/
│   │   └── 2026-10-20/
│   │       ├── sdg3_3_7_1_v1394.csv
│   │       ├── sdg3_3_7_2_v1353.csv
│   │       ├── manifest_asal.json
│   │       └── json/
│   ├── wdi/
│   │   └── 2026-10-20/
│   │       ├── data/
│   │       └── metadata/
│   └── who_gho/
│       └── 2026-10-20/
│           ├── datadot/
│           └── odata/
├── silver/
└── gold/
```

Pemisahan direktori dilakukan untuk menjaga keaslian data mentah dan memudahkan proses penelusuran sumber data.

## 2.3 Pemeriksaan Manifest dan Hash

Pemeriksaan manifest dilakukan menggunakan file `MANIFEST.csv` yang berisi informasi nama berkas, ukuran berkas, dan nilai SHA-256.

Setiap berkas memiliki nilai hash yang berfungsi sebagai identitas digital untuk memeriksa integritas berkas. Dengan demikian, perubahan pada berkas mentah dapat diketahui melalui perbedaan nilai hash.

Hasil pengunduhan menunjukkan bahwa sebanyak 13 berkas telah sesuai dengan manifest yang disediakan.

## 2.4 Struktur Dataset

Berdasarkan pemeriksaan awal, struktur dataset CSV yang diperoleh adalah:

**A. Dataset BPS**

| Nama Dataset | Jumlah Baris | Jumlah Kolom |
|---|---:|---:|
| sdg3_3_7_1_v1394.csv | 69 | 11 |
| sdg3_3_7_2_v1353.csv | 69 | 11 |

Kolom yang tersedia meliputi:

`var_id`, `wilayah_id`, `wilayah`, `turvar_id`, `turvar`, `tahun_id`, `tahun`, `periode_id`, `periode`, `nilai`, dan `satuan`.

**B. Dataset WHO**

| Nama Dataset | Jumlah Baris | Jumlah Kolom |
|---|---:|---:|
| 27D371A_MDG_0000000003.csv | 26 | 14 |
| 8074BD9_SDGFPALL.csv | 6 | 14 |

Kolom yang tersedia antara lain:

`IND_ID`, `IND_CODE`, `IND_UUID`, `IND_PER_CODE`, `DIM_TIME`, `DIM_TIME_TYPE`, `DIM_GEO_CODE_M49`, `DIM_GEO_CODE_TYPE`, `DIM_PUBLISH_STATE_CODE`, `IND_NAME`, `GEO_NAME_SHORT`, `DIM_SEX`, `DIM_AGE`, dan kolom nilai indikator.

**C. Dataset WDI**

Data WDI tersedia dalam format JSON, disertai tiga berkas metadata. Pemeriksaan struktur dan pemetaan variabel secara menyeluruh masih diperlukan sebelum data dapat dimasukkan ke dalam tabel terstandarisasi.

## 2.5 Lineage Data

Lineage merupakan informasi yang menjelaskan asal-usul data, mulai dari sumber awal hingga data hasil pengolahan.

Dalam proyek ini, informasi lineage direncanakan disimpan melalui kolom:

- `_berkas_raw`: lokasi relatif berkas mentah.
- `_sha256_raw`: nilai hash SHA-256 dari berkas mentah.

Kedua kolom tersebut diperlukan agar setiap observasi dapat ditelusuri kembali ke berkas sumbernya.

---

# 3. Masalah data dan penanganannya

Bagian ini merangkum temuan Sprint 1 (profil seri, panel provinsi×periode, anomali, deduplikasi, dan keputusan katalog) yang dapat ditarik ulang dari Silver, tabel/grafik profil, log, dan metrik. Artefak: `reports/laporan.md`, `reports/tabel/*`, `reports/gambar/*`, `log-keputusan.csv` (K-003–K-010), `data/silver/silver.parquet`, dan `results/124450127/metrics.json`.

## 3.1 Profil seri utama dan pembanding

Silver sementara berisi **235 baris, 5 seri, 35 wilayah, 5 berkas sumber** (`python -m src.common.skema data/silver/silver.parquet`; `results/124450127/metrics.json`: `baris_silver=235`, `baris_seri_utama=138`). Seri utama BPS hanya teramati pada **2012 dan 2017** (bukan panel tahunan 2012–2017): 33 provinsi pada 2012 dan 34 pada 2017, dengan baris Indonesia (9999) dipisah dari grid provinsi (K-010; `reports/tabel/statistik_seri.csv`, `reports/tabel/grid_nasional.csv`).

| Seri | Satuan | 2012 (n, mean, median, IQR, min–maks) | 2017 (n, mean, median, IQR, min–maks) | Nasional 2012/2017 |
|---|---|---|---|---|
| `var1394` | persen | 33; 54,32; 55,10; 14,00; 19,10 (Papua)–66,40 (Kalsel) | 34; 53,96; 56,05; 13,68; 35,90 (Papua, Pabar)–69,40 (Kalteng) | 57,9%; 57,2% |
| `var1353` | per 1.000 perempuan 15–19 | 33; 56,06; 53,00; 29,00; 20,00 (DKI)–104,00 (Kalbar) | 34; 41,71; 44,50; 21,00; 15,00 (DIY)–83,00 (Kalteng) | 48; 36 |

Statistik per provinsi (termasuk delta dan z-score): `reports/tabel/statistik_provinsi.csv`, `reports/tabel/statistik_nasional.csv`. Grafik: `reports/gambar/boxplot_var1394_var1353.png`, `deret_waktu_var1394.png`, `deret_waktu_var1353.png`, `zscore_anomali.png`, `perubahan_2012_2017.png`, `pembanding_nasional.png`.

Profil seri pembanding nasional (`reports/tabel/ketersediaan_pembanding_panjang.csv`, `ketersediaan_pembanding_ringkas.csv`; K-009): `SDGFPALL` (WHO, perempuan 15–49, %) beririsan 2012/2015/2016/2017 dan observasi utama 2012,2017 — kandidat sebanding untuk `var1394`; `SP.ADO.TFRT` (WDI, 15–19, per 1.000, 1960–2024) beririsan observasi utama 2012,2017 — sebanding definisi untuk `var1353`; `MDG_0000000003` umur 15–19 (WHO, per 1.000) beririsan katalog 2013/2015/2016 tetapi **tidak beririsan** pada observasi utama (2012,2017) — kandidat kontekstual; `MDG_0000000003` umur 10–14 ditolak karena kelompok umur berbeda.

## 3.2 Celah panel provinsi × periode

Grid dibentuk sebelum membahas missing: **38 provinsi × 6 tahun (2012–2017) × 2 seri = 456 sel**. Hasil: **134 terisi (29,39%)**, **322 kosong**, dan **0 missing sejati** (`reports/tabel/grid_panel.csv`, `kelengkapan_grid.csv`, `gambar/kelengkapan_panel.png`; `results/124450127/metrics.json`: `sel_kosong_grid=322`, `sel_kosong_struktural=322`, `sel_kosong_sejati=0`).

| Sebab sel kosong | Bukti | Dampak | Log |
|---|---|---:|---|
| Tahun 2013–2016 tidak diterbitkan (gelombang survei hanya 2012, 2017) — **bukan missing** | Silver/data mentah hanya memuat 2012,2017; 38 prov × 4 tahun × 2 seri | 304 sel `tidak_terbit` | K-004 |
| Provinsi baru belum ada: 9200 Papua Barat Daya, 9500 Papua Selatan, 9600 Papua Tengah, 9700 Papua Pegunungan (dibentuk 2022) pada 2012 & 2017 | Referensi 38 provinsi 2025 | 16 sel `belum_ada` | K-005 |
| 6500 Kalimantan Utara belum tercakup pada gelombang 2012 | Muncul di 2017 | 2 sel `belum_tercakup` | K-005 |
| Indonesia (9999) dipisah dari grid provinsi | Agregat nasional bukan unit panel | 0 sel grid (dilaporkan terpisah) | K-010 |

Batas pemakaian panel: tahun terakhir tersedia **2017**; kelengkapan tahun survei **67/76 = 88,16%** per seri (2012: 33/38, 2017: 34/38). Perbandingan penuh 38 provinsi 2012–2017 tidak didukung data mentah; analisis lintas waktu harus membatasi pada provinsi berpasangan atau menyatakan ketidakseimbangan (laporan §6.4).

## 3.3 Koreksi katalog dan deduplikasi/revisi

- **Satuan `var1353` (koreksi katalog):** ditetapkan **per 1.000 perempuan usia 15–19 tahun** (bukan persen), karena kolom satuan BPS kosong sementara metadata WHO `MDG_0000000003` (RATE_PER_1000_N, Y15T19) dan WDI `SP.ADO.TFRT` konsisten dan nilai 15–104 sesuai laju per 1.000 (K-003, 69 baris terdampak).
- **Deduplikasi:** kunci `sumber+seri_kode+wilayah_kode+periode+rincian+_berkas_raw`. CSV dan JSON BPS snapshot 2026-10-20 adalah dua representasi, bukan dua observasi; perbandingan `(wilayah,tahun)` menunjukkan **69 nilai per seri identik, 0 berbeda, 0 hanya satu sisi** sehingga CSV kanonik dan JSON pemeriksa (K-006, `reports/tabel/deduplikasi_csv_json.csv`). Tidak ada snapshot kedua untuk seri ini, sehingga **tidak ada revisi teramati**.

## 3.4 Calon anomali, patahan seri, dan galat input

Anomali level ditandai bila di luar pagar IQR 1,5 atau `|z| ≥ 2` per tahun; perubahan 2012–2017 ditandai bila `|z_delta| ≥ 2` atau di luar pagar IQR delta. Tujuannya menemukan, bukan memperbaiki; **hanya galat input yang boleh diperbaiki** (K-007).

Terdeteksi **7 calon anomali** (3 `var1394`, 4 `var1353`; `reports/tabel/anomali.csv`, `ringkasan_kategori_anomali.csv`, `ringkasan_patahan.csv`; `results/124450127/metrics.json`: `outlier_ditandai=7`, `patahan_seri=1`):

| Seri | Provinsi | Periode | Nilai | Metode | Kategori | Alasan |
|---|---|---|---:|---|---|---|
| `var1353` | Kalimantan Barat (6100) | 2012 | 104 | z=2,23 | patahan | Level 2012 tinggi, bagian pola perubahan serentak |
| `var1353` | Sulawesi Barat (7600) | 2012 | 101 | z=2,09 | patahan | Level 2012 tinggi |
| `var1353` | Sulawesi Barat (7600) | 2012→2017 | −55 | z_delta=−2,54 | patahan | Penurunan terbesar, bagian penurunan serentak |
| `var1353` | Kalimantan Tengah (6200) | 2017 | 83 | IQR+z=2,69 | outlier asli | Di luar pagar 2017 [−1,75; 82,25], tetap tinggi |
| `var1394` | Papua (9400) | 2012 | 19,1 | IQR+z=−3,42 | outlier asli | Di luar pagar 2012 [27,00; 83,00] |
| `var1394` | Papua Barat (9100) | 2017 | 35,9 | z=−2,05 | outlier asli | Rendah pada 2017 |
| `var1394` | Papua (9400) | 2017 | 35,9 | z=−2,05; z_delta=4,08 | outlier asli | Rendah tetapi naik 16,8 poin dari 2012 |

- **Patahan/revisi seri (kandidat):** `var1353` turun pada **26 dari 33 provinsi berpasangan (78,8%)**, naik 5, tetap 2; median −11, rata-rata −14,09 per 1.000. Pola searah hampir serentak khas perubahan definisi/metode/revisi; WDI juga turun (44,62→32,79) sehingga tren nyata belum dikesampingkan. Nilai tidak diubah (K-008).
- **Outlier asli:** 4 temuan (3 `var1394`, 1 `var1353`) dipertahankan; `var1394` tidak menunjukkan patahan serentak (21 turun, 12 naik, median −1,2).
- **Galat input:** **0** temuan (tidak ada nilai negatif, di luar domain, kode ganda, atau pelanggaran metadata) sehingga **tidak ada perbaikan nilai** (K-007).

---

# 4. Integrasi dan rekonsiliasi data (status)

Struktur Silver mengikuti skema `src/common/skema.py` (`sumber, seri_kode, wilayah_kode, nama_wilayah, periode, jenis_periode, rincian, nilai, satuan, _berkas_raw, _sha256_raw`) dengan lineage dari manifest/hash. Integrasi mempertahankan identitas sumber: BPS, WHO, dan WDI disimpan sebagai observasi terpisah.

Rincian kandidat sebanding untuk tahap 6 (K-009; `reports/tabel/ketersediaan_pembanding_ringkas.csv`): `var1394` ↔ `SDGFPALL` (perempuan 15–49, %, irisan observasi 2012,2017; selisih nasional 57,9 vs 79,0 dan 57,2 vs 77,0 dijelaskan, bukan dihapus); `var1353` ↔ `SP.ADO.TFRT` (15–19, per 1.000, irisan 2012,2017; selisih +3,38 dan +3,21 per 1.000); `var1353` ↔ `MDG_0000000003` Y15T19 tanpa irisan tahun observasi langsung (WHO terdekat 2016 = 36,11). Rekonsiliasi/selisih final dan Gold merupakan kelanjutan sprint berikutnya.

---

# 5. Validasi dan reproduksibilitas

Validasi Silver tersedia melalui `python -m src.common.skema data/silver/silver.parquet` (lolos 235 baris). Keputusan wrangling dan dampak baris/sel terdokumentasi di `log-keputusan.csv`; metrik artefak Sprint 1 disimpan di `results/124450127/metrics.json` (dapat dibangkitkan ulang dengan `python -m src.common.hasil 124450127 ...`). Data mentah tidak diubah, lineage (`_berkas_raw`, `_sha256_raw`) dipertahankan, dan artefak profil/gambar/tabel dapat ditarik ulang dari Silver/log/kode (`src/silver/profil.py`, laporan, tabel). Reproduksi penuh pipeline dari `data/raw/` mengikuti `pipeline.py` sesuai tahap yang tersedia di repositori.
