# Ekstraksi: jumlah baris per berkas

Dihasilkan `python pipeline.py`. Peran *data* berisi angka; *meta* berisi judul, definisi, atau catatan unduhan. Semua baris `data/raw/MANIFEST.csv` tertangani.

| berkas | pembaca | peran | baris | catatan |
|---|---|---|---|---|
| bps/2026-10-20/json/sdg3_3_7_1_v1394.json | bps_json | data | 69 | 1 halaman |
| bps/2026-10-20/json/sdg3_3_7_2_v1353.json | bps_json | data | 69 | 1 halaman |
| bps/2026-10-20/manifest_asal.json | bps_manifest_asal | meta | 36 | semua tabel unduhan BPS, bukan hanya kasus ini |
| bps/2026-10-20/sdg3_3_7_1_v1394.csv | bps_csv | data | 69 |  |
| bps/2026-10-20/sdg3_3_7_2_v1353.csv | bps_csv | data | 69 |  |
| wdi/2026-10-20/data/kelompok-03-hal-01.json | wdi_data | data | 66 | 2,112 baris di berkas, 1 seri kasus disaring |
| wdi/2026-10-20/metadata/sumber.json | wdi_sumber | meta | 71 |  |
| wdi/2026-10-20/metadata/sumber2_indikator.json | wdi_meta | meta | 1 | metadata seri kasus saja |
| wdi/2026-10-20/metadata/sumber46_indikator.json | wdi_meta | meta | 1 | metadata seri kasus saja |
| who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv | who_csv | data | 26 |  |
| who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv | who_csv | data | 6 |  |
| who_gho/2026-10-20/datadot/ddiindicators_skip0000.json | who_ddi | meta | 2 | definisi lengkap seri kasus |
| who_gho/2026-10-20/odata/Indicator.json | who_odata | meta | 2 |  |

Jumlah: 13 berkas dari 13 di MANIFEST, 374 baris mentah di berkas data.


# TUGAS 1 - Pembaca BPS (2 CSV, 2 JSON) di src/ekstraksi/ dengan _berkas_raw dan _sha256_raw

### Hasil Pembacaan Dataset BPS dan Bukti Lineage

### 1. Hasil Pemeriksaan Berkas BPS


Hasil pembacaan setiap berkas menggunakan fungsi pembaca yang tersedia pada `src/ekstraksi/bps.py` adalah sebagai berikut.

| No. | Nama Berkas             | Format | Jumlah Baris |
| --- | ----------------------- | ------ | -----------: |
| 1   | `sdg3_3_7_1_v1394.csv`  | CSV    |           69 |
| 2   | `sdg3_3_7_1_v1394.json` | JSON   |           69 |
| 3   | `sdg3_3_7_2_v1353.csv`  | CSV    |           69 |
| 4   | `sdg3_3_7_2_v1353.json` | JSON   |           69 |
|     | **Total**               |        |      **276** |



### 2. Contoh Hasil Pembacaan CSV dan JSON

Hasil ekstraksi dari berkas CSV dan JSON disusun dalam bentuk tabel data dengan informasi indikator, wilayah, tahun, dan nilai. Berikut contoh keluaran yang memperlihatkan hasil pembacaan kedua format.

**a. Contoh hasil pembacaan CSV**

Berkas: `sdg3_3_7_1_v1394.csv`

Contoh baris di dalam csv :&#x20;

```text
var_id,wilayah_id,wilayah,turvar_id,turvar,tahun_id,tahun,periode_id,periode,nilai,satuan
1394,1100,ACEH,0,Tidak ada,112,2012,0,Tahun,44.4,Persen
```

Berkas: `sdg3_3_7_2_v1353.csv`

Contoh baris di dalam csv :&#x20;

```text
var_id,wilayah_id,wilayah,turvar_id,turvar,tahun_id,tahun,periode_id,periode,nilai,satuan
1353,1100,ACEH,0,Tidak ada,112,2012,0,Tahun,25,
```

**b. Contoh hasil pembacaan JSON**

Contoh keluaran dari `sdg3_3_7_1_v1394.json`:

| Kolom         | Contoh Nilai        |
| ------------- | ------------------- |
| `var_id`      | 1394                |
| `wilayah_id`  | 5200                |
| `wilayah`     | NUSA TENGGARA BARAT |
| `turvar_id`   | 0                   |
| `turvar`      | Tidak ada           |
| `tahun_id`    | 112                 |
| `tahun`       | 2012                |
| `turtahun_id` | 0                   |
| `turtahun`    | Tahun               |
| `nilai`       | 55.1                |
| `_halaman`    | 1                   |

Contoh keluaran dari `sdg3_3_7_2_v1353.json`:

| Kolom         | Contoh Nilai      |
| ------------- | ----------------- |
| `var_id`      | 1353              |
| `wilayah_id`  | 7400              |
| `wilayah`     | SULAWESI TENGGARA |
| `turvar_id`   | 0                 |
| `turvar`      | Tidak ada         |
| `tahun_id`    | 112               |
| `tahun`       | 2012              |
| `turtahun_id` | 0                 |
| `turtahun`    | Tahun             |
| `nilai`       | 57                |
| `_halaman`    | 1                 |

### 3. Bukti Data Lineage

Untuk menjaga keterlacakan data, hasil ekstraksi dilengkapi dengan dua kolom lineage, yaitu `_berkas_raw` dan `_sha256_raw`.

- `_berkas_raw` menunjukkan lokasi berkas mentah yang menjadi sumber data.
- `_sha256_raw` merupakan nilai hash SHA-256 yang digunakan sebagai identitas digital berkas sumber.

Berikut contoh lineage dari hasil pembacaan JSON.

**a. Lineage `var1394`**

| Kolom         | Nilai                                                              |
| ------------- | ------------------------------------------------------------------ |
| `_berkas_raw` | `bps/2026-10-20/json/sdg3_3_7_1_v1394.json`                        |
| `_sha256_raw` | `6ae359c6df0dfd6ce210233dc28ada9060be0996f855288d6c4fbfee88b55c74` |

**b. Lineage `var1353`**

| Kolom         | Nilai                                                              |
| ------------- | ------------------------------------------------------------------ |
| `_berkas_raw` | `bps/2026-10-20/json/sdg3_3_7_2_v1353.json`                        |
| `_sha256_raw` | `230ce163135e9ea9e078649b2812136780e9e2db9d4c110dc3e21f2fe50faf5a` |

Dengan adanya kedua kolom tersebut, asal setiap baris hasil ekstraksi dapat ditelusuri kembali ke berkas mentah yang digunakan. Nilai hash juga dapat digunakan untuk memeriksa identitas berkas sumber.

**c. Lineage dalam satu baris** 


Berikut merupakan contoh hasil pembacaan data BPS yang telah dilengkapi dengan informasi lineage. Informasi lineage digunakan untuk mengetahui asal berkas data dan memastikan data dapat ditelusuri kembali ke sumber aslinya.

| var_id | wilayah | tahun | nilai | _berkas_raw | _sha256_raw |
|---|---|---|---|---|---|
| 1394 | NUSA TENGGARA BARAT | 2012 | 55.1 | `bps/2026-10-20/json/sdg3_3_7_1_v1394.json` | `6ae359c6df0dfd6ce210233dc28ada9060be0996f855288d6c4fbfee88b55c74` |

Dari hasil tersebut, kolom `_berkas_raw` menunjukkan lokasi berkas sumber yang digunakan, sedangkan `_sha256_raw` merupakan nilai hash untuk mengidentifikasi berkas sumber. Dengan demikian, setiap data hasil ekstraksi memiliki informasi asal-usul yang dapat ditelusuri kembali.

### 4. Pemeriksaan Judul Tabel Indikator `var1353`

Pemeriksaan khusus dilakukan terhadap judul tabel pada berkas JSON indikator `var1353` untuk memastikan kelompok umur yang dicakup oleh indikator.

Berdasarkan informasi pada `var[0].label`, judul tabel aslinya adalah:

> Angka Kelahiran Pada Perempuan Usia 15-19 Tahun Menurut Provinsi

Berdasarkan judul tersebut, indikator `var1353` mencakup perempuan pada kelompok usia **15–19 tahun**.

Sumber pemeriksaan:

- `data/raw/bps/2026-10-20/json/sdg3_3_7_2_v1353.json`
- Bagian `var[0].label`

Informasi kelompok umur ini perlu dipertahankan karena menjadi acuan ketika indikator BPS dibandingkan atau diintegrasikan dengan indikator dari sumber lain pada tahap berikutnya.

### 5. Hasil Pemeriksaan Pembacaan JSON dan Rekapitulasi

Pemeriksaan pembacaan JSON dilakukan untuk memastikan seluruh kunci pada data dapat dikenali oleh fungsi pembaca. Hasil pemeriksaan menunjukkan bahwa tidak terdapat kunci JSON yang gagal dibaca.

| Pemeriksaan                             |   Hasil |
| --------------------------------------- | ------: |
| Jumlah berkas data BPS                  |       4 |
| Jumlah baris CSV `var1394`              |      69 |
| Jumlah baris JSON `var1394`             |      69 |
| Jumlah baris CSV `var1353`              |      69 |
| Jumlah baris JSON `var1353`             |      69 |
| Total baris data hasil ekstraksi        | **276** |
| Kunci JSON gagal dibaca (`tak_terbaca`) |   **0** |

Jumlah baris pada tabel rekapitulasi dicocokkan dengan hasil pembacaan masing-masing berkas. Dengan demikian, total 276 baris merupakan akumulasi dari empat berkas data, bukan termasuk 36 baris metadata pada `manifest_asal.json`.

### 6. Bukti Hasil Eksekusi Ekstraksi BPS

Hasil berikut diperoleh dari eksekusi kode pemeriksaan pada `src/ekstraksi/cek_ekstraksi_bps.py`, tepatnya pada bagian **hasil ekstraksi BPS**.

| Berkas | Jumlah Baris | Jumlah Lineage | Status |
|---|---:|---:|---|
| `sdg3_3_7_1_v1394.csv` | 69 | 1 | BERHASIL |
| `sdg3_3_7_1_v1394.json` | 69 | 1 | BERHASIL |
| `sdg3_3_7_2_v1353.csv` | 69 | 1 | BERHASIL |
| `sdg3_3_7_2_v1353.json` | 69 | 1 | BERHASIL |
| **Total** | **276** | | **BERHASIL** |

# TUGAS 2 - Pembaca WDI (4 JSON) di src/ekstraksi/ dengan _berkas_raw dan _sha256_raw

## 1. Laporan Hitungan Per Berkas WDI

Pembacaan data WDI dilakukan terhadap empat berkas hasil pengunduhan `python unduh_data.py --kasus 3`. Data observasi dan metadata indikator disaring berdasarkan `indicator.id == SP.ADO.TFRT`, sedangkan metadata sumber dibaca tanpa penyaringan indikator karena berisi daftar sumber data.

| Berkas WDI | Baris mentah | Baris keluaran |
|---|---:|---:|
| `data/kelompok-03-hal-01.json` | 2.112 | 66 |
| `metadata/sumber.json` | 71 | 71 |
| `metadata/sumber2_indikator.json` | 1.498 | 1 |
| `metadata/sumber46_indikator.json` | 408 | 1 |
| **Total** | **4.089** | **139** |
s.

## 2. Contoh Keluaran Data Setelah Penyaringan

Berikut contoh lima baris hasil pembacaan dari berkas `kelompok-03-hal-01.json` setelah disaring menggunakan indikator `SP.ADO.TFRT`.

| indicator_id | indicator_nama | country_id | date | value |
|---|---|---|---:|---:|
| SP.ADO.TFRT | Adolescent fertility rate (births per 1,000 women ages 15-19) | ID | 2025 | null |
| SP.ADO.TFRT | Adolescent fertility rate (births per 1,000 women ages 15-19) | ID | 2024 | 25.646 |
| SP.ADO.TFRT | Adolescent fertility rate (births per 1,000 women ages 15-19) | ID | 2023 | 26.419 |
| SP.ADO.TFRT | Adolescent fertility rate (births per 1,000 women ages 15-19) | ID | 2022 | 26.581 |
| SP.ADO.TFRT | Adolescent fertility rate (births per 1,000 women ages 15-19) | ID | 2021 | 26.824 |

Nilai `null` pada tahun 2025 tetap dipertahankan karena pembaca hanya bertugas melakukan ekstraksi dan penyaringan, bukan pembersihan data.

## 3. Bukti Lineage

Setiap baris hasil pembacaan dilengkapi dengan dua kolom lineage untuk memastikan data dapat ditelusuri kembali ke berkas sumbernya.

Contoh lineage dari berkas `kelompok-03-hal-01.json`:

| Kolom | Contoh Nilai |
|---|---|
| `_berkas_raw` | `wdi/2026-10-20/data/kelompok-03-hal-01.json` |
| `_sha256_raw` | `9a8729675761d697bd5556d66fd903ed841ee454e7324d41084dc09b9905f912` |

Nilai SHA256 diperoleh melalui fungsi `sha256_raw()` dari `src.common.manifest`, sehingga hash tidak ditulis secara manual.

Contoh implementasi pada pembaca:

```python
df["_berkas_raw"] = jalur
df["_sha256_raw"] = sha256_raw(jalur)
```

Kedua kolom tersebut juga perlu tersedia pada hasil pembacaan metadata agar setiap baris keluaran, baik data observasi maupun metadata, dapat ditelusuri ke berkas mentahnya.

## 4. Hasil Eksekusi Pipeline

Pengujian dilakukan dengan menjalankan perintah `python pipeline.py` dari direktori utama proyek. Hasil eksekusi yang diperoleh adalah:

```text
data/raw: 13 berkas cocok dengan MANIFEST.csv
ekstraksi  selesai dalam 0.1 s
           Silver: 235 baris -> data\silver\silver.parquet
silver     selesai dalam 1.3 s
gold       selesai dalam 0.2 s
validasi   selesai dalam 0.1 s
```

Pemeriksaan skema keluaran Silver juga dilakukan menggunakan perintah:

```bash
python -m src.common.skema data/silver/silver.parquet
```

Hasil pemeriksaan:

```text
LOLOS 235 baris, 5 seri, 35 wilayah, 5 berkas sumber
```

Hasil tersebut menunjukkan bahwa 13 berkas mentah cocok dengan `MANIFEST.csv`, proses ekstraksi dan tahapan pipeline berhasil dijalankan, serta keluaran Silver lolos pemeriksaan skema.


# Tugas 3 - Pembaca WHO GHO (2 CSV, 2 JSON) di src/ekstraksi/ dengan _berkas_raw dan _sha256_raw
 

### 1. Contoh keluaran WHO an dengan rincian umur terpisah

Pada indikator `MDG_0000000003`, terdapat dua kelompok umur, yaitu `Y10T14` (perempuan usia 10–14 tahun) dan `Y15T19` (perempuan usia 15–19 tahun). Kedua kelompok umur tersebut tetap dipertahankan sebagai baris yang berbeda.

Contoh keluaran dari berkas `27D371A_MDG_0000000003.csv`:

| IND_CODE | DIM_TIME | DIM_AGE | RATE_PER_1000_N |
|---|---:|---|---:|
| MDG_0000000003 | 2003 | Y10T14 | 1.404004693 |
| MDG_0000000003 | 2008 | Y10T14 | 0.811197817 |
| MDG_0000000003 | 2001 | Y15T19 | 50.93315506 |
| MDG_0000000003 | 2008 | Y15T19 | 46.88329315 |

Berdasarkan seluruh isi berkas CSV, jumlah data untuk setiap kelompok umur adalah:

| DIM_AGE | Keterangan | Jumlah baris |
|---|---|---:|
| Y10T14 | Perempuan usia 10–14 tahun | 12 |
| Y15T19 | Perempuan usia 15–19 tahun | 14 |
| **Total** | | **26** |

Hasil tersebut menunjukkan bahwa rincian umur tetap terpisah dan dapat dibedakan melalui kolom `DIM_AGE`.

### 2. Contoh keluaran dengan lineage per baris

Setiap baris hasil pembacaan CSV WHO dilengkapi informasi lineage melalui kolom `_berkas_raw` dan `_sha256_raw`. Kolom `_berkas_raw` menunjukkan lokasi berkas sumber, sedangkan `_sha256_raw` menunjukkan nilai hash SHA-256 berkas tersebut berdasarkan `MANIFEST.csv`.

Contoh keluaran dari berkas `MDG_0000000003.csv`:

| IND_CODE | DIM_TIME | DIM_AGE | RATE_PER_1000_N | _berkas_raw | _sha256_raw |
|---|---:|---|---:|---|---|
| MDG_0000000003 | 2003 | Y10T14 | 1.404004693 | `who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv` | `efd85410d3d2939a3fabcb1a17489a3860985eec2685d49787919c3657a7e702` |
| MDG_0000000003 | 2008 | Y10T14 | 0.811197817 | `who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv` | `efd85410d3d2939a3fabcb1a17489a3860985eec2685d49787919c3657a7e702` |
| MDG_0000000003 | 2001 | Y15T19 | 50.93315506 | `who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv` | `efd85410d3d2939a3fabcb1a17489a3860985eec2685d49787919c3657a7e702` |
| MDG_0000000003 | 2008 | Y15T19 | 46.88329315 | `who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv` | `efd85410d3d2939a3fabcb1a17489a3860985eec2685d49787919c3657a7e702` |

Nilai `_berkas_raw` dan `_sha256_raw` tetap sama pada setiap baris yang berasal dari berkas CSV yang sama. Hal ini memungkinkan setiap observasi ditelusuri kembali ke sumber data mentahnya.

Untuk berkas metadata JSON, pembacaan mencantumkan kolom `_berkas_raw` sebagai penanda asal data. Pada implementasi pembaca metadata yang terdapat dalam `src/ekstraksi/who_gho.py`, kolom `_sha256_raw` belum ditambahkan pada hasil metadata JSON.

### 3. Contoh keluaran indikator SDGFPALLta.

Contoh keluaran dari berkas `8074BD9_SDGFPALL.csv`:

| IND_CODE | DIM_TIME | DIM_AGE | RATE_PER_100_N |
|---|---:|---|---:|
| SDGFPALL | 2016 | Y15T49 | 77.6 |
| SDGFPALL | 2017 | Y15T49 | 77.0 |
| SDGFPALL | 2002 | Y15T49 | 77.1 |
| SDGFPALL | 2015 | Y15T49 | 78.2 |
| SDGFPALL | 2012 | Y15T49 | 79.0 |
| SDGFPALL | 2007 | Y15T49 | 77.0 |

Jumlah data pada berkas tersebut adalah 6 baris.

### 4. Pencocokan jumlah keluaran dengan laporan per berkas

Jumlah baris hasil pembacaan WHO GHO dicocokkan dengan jumlah yang tercantum dalam `reports/ekstraksi.md`. Hasil pencocokannya adalah sebagai berikut.

| Berkas | Pembaca | Peran | Jumlah baris |
|---|---|---|---:|
| `who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv` | `who_csv` | Data | 26 |
| `who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv` | `who_csv` | Data | 6 |
| `who_gho/2026-10-20/datadot/ddiindicators_skip0000.json` | `who_ddi` | Meta | 2 |
| `who_gho/2026-10-20/odata/Indicator.json` | `who_odata` | Meta | 2 |
| **Total** | | | **36** |

Berdasarkan tabel tersebut, jumlah keluaran WHO GHO adalah 36 baris, yang terdiri dari 32 baris data dan 4 baris metadata. Jumlah ini sesuai dengan laporan ekstraksi pada `reports/ekstraksi.md`.

