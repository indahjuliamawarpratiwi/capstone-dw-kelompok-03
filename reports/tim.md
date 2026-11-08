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

# 3. Permasalahan Data dan Penanganannya

## 3.1 Profiling Data

Profiling dilakukan untuk memperoleh gambaran awal mengenai karakteristik dataset sebelum dilakukan pembersihan.

Beberapa aspek yang perlu diperiksa meliputi:

1. Jumlah baris dan kolom.
2. Tipe data setiap variabel.
3. Jumlah missing value.
4. Jumlah data duplikat.
5. Distribusi nilai indikator.
6. Konsistensi kode wilayah dan periode.
7. Keberadaan nilai ekstrem atau perubahan nilai yang tidak wajar.

Berdasarkan pemeriksaan awal, ditemukan perbedaan struktur antara data BPS dan WHO. Data BPS menggunakan kode wilayah dan tahun, sedangkan WHO menggunakan kode wilayah M49, dimensi waktu, jenis waktu, jenis kelamin, dan kelompok umur.

Perbedaan struktur tersebut menjadi perhatian utama dalam proses standardisasi.

## 3.2 Identifikasi Potensi Permasalahan

Beberapa potensi permasalahan yang perlu diperiksa adalah sebagai berikut:

| Permasalahan | Indikasi | Penanganan yang Direncanakan |
|---|---|---|
| Perbedaan nama kolom | BPS dan WHO memiliki nama kolom berbeda | Standardisasi nama kolom |
| Perbedaan kode wilayah | BPS menggunakan kode wilayah sendiri, WHO menggunakan M49 | Pemetaan kode wilayah |
| Perbedaan periode | Format periode dan jenis waktu berbeda | Standardisasi periode |
| Missing value | Nilai indikator dapat tidak tersedia | Identifikasi dan dokumentasi |
| Duplikasi | Kemungkinan observasi berulang | Pemeriksaan berdasarkan kunci observasi |
| Perbedaan satuan | Indikator dapat menggunakan satuan berbeda | Pemeriksaan metadata indikator |
| Nilai ekstrem | Nilai dapat berbeda jauh dari distribusi umum | Pemeriksaan statistik dan konteks sumber |

Permasalahan di atas merupakan aspek yang perlu diuji. Belum seluruhnya dapat dinyatakan ditemukan karena proses profiling lengkap belum dilakukan.

## 3.3 Penanganan Data

Proses pembersihan direncanakan mencakup:

1. Pemeriksaan missing value pada setiap variabel.
2. Pemeriksaan data duplikat berdasarkan kombinasi sumber, seri, wilayah, periode, dan rincian.
3. Penyeragaman tipe data numerik pada kolom nilai.
4. Penyeragaman format periode.
5. Pemeriksaan konsistensi nama dan kode wilayah.
6. Pemeriksaan satuan berdasarkan metadata.
7. Dokumentasi setiap perubahan dalam `log-keputusan.csv`.

Setiap perubahan data harus memiliki alasan yang jelas dan tidak menghilangkan informasi penting dari sumber aslinya.

---

# 4. Integrasi dan Rekonsiliasi Data

## 4.1 Standardisasi Struktur Data

Integrasi dilakukan dengan menyusun data dari berbagai sumber ke dalam struktur yang seragam.

Struktur tabel Silver yang digunakan mengacu pada ketentuan kasus, yaitu:

| Kolom | Keterangan |
|---|---|
| sumber | Nama sumber data |
| seri_kode | Kode indikator |
| wilayah_kode | Kode wilayah |
| nama_wilayah | Nama wilayah |
| periode | Periode pengamatan |
| jenis_periode | Jenis periode |
| rincian | Dimensi atau kategori tambahan |
| nilai | Nilai indikator |
| satuan | Satuan indikator |
| _berkas_raw | Lokasi berkas mentah |
| _sha256_raw | Hash berkas mentah |

Satu baris merepresentasikan satu kombinasi indikator, wilayah, periode, rincian, dan sumber data.

## 4.2 Integrasi Sumber Data

Integrasi dilakukan dengan mempertahankan identitas setiap sumber data. Data BPS, WHO, dan WDI tidak langsung digabungkan menjadi satu nilai karena masing-masing dapat memiliki definisi, cakupan, dan metode pengukuran yang berbeda.

Data dari setiap sumber tetap disimpan sebagai observasi tersendiri pada lapisan Silver.

Selanjutnya, proses rekonsiliasi dilakukan pada lapisan Gold dengan membandingkan indikator yang memiliki kesesuaian definisi, satuan, periode, dan cakupan wilayah.

## 4.3 Rekonsiliasi

Rekonsiliasi bertujuan untuk mengetahui kesesuaian nilai indikator antar-sumber.

Aspek yang perlu diperhatikan meliputi:

- Kesamaan definisi indikator.
- Kesamaan satuan pengukuran.
- Kesamaan periode pengamatan.
- Kesamaan cakupan wilayah.
- Perbedaan metode pengumpulan data.

Perbedaan nilai antar-sumber tidak secara otomatis menunjukkan kesalahan. Perbedaan tersebut dapat disebabkan oleh metodologi, cakupan populasi, maupun periode pengukuran yang berbeda.

Hasil rekonsiliasi belum dapat disimpulkan sebelum data Silver dan Gold selesai dibentuk dan dibandingkan.

---

# 5. Validasi dan Reproduksibilitas

## 5.1 Validasi Data

Validasi bertujuan untuk memastikan data hasil pengolahan sesuai dengan struktur dan aturan yang telah ditentukan.

Validasi yang direncanakan meliputi:

1. Pemeriksaan kelengkapan kolom wajib.
2. Pemeriksaan tipe data.
3. Pemeriksaan nilai numerik.
4. Pemeriksaan kombinasi kunci observasi.
5. Pemeriksaan konsistensi periode dan wilayah.
6. Pemeriksaan kesesuaian hash dengan manifest.
7. Pemeriksaan kesesuaian data hasil pengolahan dengan sumber mentah.

Validasi dapat diimplementasikan menggunakan Pandera atau Great Expectations.

## 5.2 Reproduksibilitas

Reproduksibilitas merupakan kemampuan untuk menjalankan kembali proses pengolahan data dan memperoleh hasil yang konsisten.

Untuk mendukung reproduksibilitas, proyek menggunakan:

- Penyimpanan data mentah tanpa mengubah berkas sumber.
- Pencatatan sumber dan hash berkas.
- Dokumentasi keputusan pengolahan.
- Penyimpanan kode program dalam repositori GitHub.
- Pencatatan perubahan melalui commit.
- Pemisahan data raw, Silver, dan Gold.

Dengan pendekatan tersebut, proses pengolahan dapat ditelusuri dan diperiksa kembali oleh