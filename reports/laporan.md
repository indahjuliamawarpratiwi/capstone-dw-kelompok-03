# Laporan Sprint 1 — Profil dan Anomali Seri Kesehatan Reproduksi Remaja

**NIM:** 124450127  
**Kasus:** 03 — Kesehatan reproduksi remaja  
**Seri utama:** BPS `var1394` (SDG 3.7.1) dan `var1353` (SDG 3.7.2)  
**Seri pembanding:** WHO GHO `MDG_0000000003`, `SDGFPALL`; WDI `SP.ADO.TFRT`  
**Prinsip kerja:** tahap ini **menemukan dan menandai**, bukan memperbaiki. Tidak ada nilai yang diubah atau diimputasi.

## 1. Ringkasan

- Seri utama hanya memiliki dua gelombang observasi, yaitu **2012 dan 2017**, bukan panel tahunan 2012–2017. Jumlah provinsi yang teramati adalah 33 pada 2012 dan 34 pada 2017; baris Indonesia (9999) dipisahkan dari grid provinsi.
- `var1394` (persen) relatif stabil: rata-rata provinsi 54,32 (2012) dan 53,96 (2017). `var1353` (per 1.000 perempuan 15–19) turun cukup tajam: rata-rata 56,06 (2012) menjadi 41,71 (2017).
- Tujuh calon anomali ditandai: **3 pada `var1394`** dan **4 pada `var1353`**. Tiga di antaranya dikategorikan **patahan/revisi seri**, empat **outlier asli**, dan **nol galat input**. Tidak ada perbaikan nilai.
- Grid 38 provinsi × 2012–2017 × 2 seri berisi 456 sel. Sebanyak **134 sel terisi (29,39%)** dan **322 sel kosong**. Seluruh 322 sel kosong bersifat struktural: 304 karena tahun 2013–2016 tidak diterbitkan, 16 karena empat provinsi Papua baru belum ada, dan 2 karena Kalimantan Utara belum tercakup pada 2012. **Sel kosong sejati = 0.**

## 2. Data, lineage, dan artefak

Data mentah yang dipakai berasal dari snapshot `data/raw/` tanggal 2026-10-20 dan sudah cocok dengan `MANIFEST.csv`.

| Sumber | Berkas | Seri | Baris Silver |
|---|---|---|---:|
| BPS | `bps/2026-10-20/sdg3_3_7_1_v1394.csv` | `var1394` | 69 |
| BPS | `bps/2026-10-20/sdg3_3_7_2_v1353.csv` | `var1353` | 69 |
| WHO GHO | `who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv` | `MDG_0000000003` | 26 |
| WHO GHO | `who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv` | `SDGFPALL` | 6 |
| WDI | `wdi/2026-10-20/data/kelompok-07-hal-01.json` | `SP.ADO.TFRT` | 65 |

Total Silver sementara: **235 baris, 5 seri, 35 wilayah** (34 provinsi + Indonesia), dan 5 berkas sumber. Setiap baris memuat `_berkas_raw` dan `_sha256_raw` dari `src.common.manifest.sha256_raw`. Pemeriksaan skema:

```bash
python -m src.common.skema data/silver/silver.parquet
# LOLOS 235 baris, 5 seri, 35 wilayah, 5 berkas sumber
```

Artefak utama:

- Tabel: [`tabel/`](tabel/)
- Grafik: [`gambar/`](gambar/)
- Log keputusan: `log-keputusan.csv` (K-032–K-028)
- Metrik: `results/124450127/metrics.json`

## 3. Metode

1. **Statistik deskriptif** dihitung per seri dan per tahun untuk baris provinsi saja; baris 9999 Indonesia dilaporkan terpisah.
2. **Calon anomali level** ditandai bila nilai berada di luar pagar IQR 1,5 atau memiliki `|z| ≥ 2` di dalam tahun yang sama.
3. **Calon anomali perubahan** ditandai bila `delta 2017 − 2012` memiliki `|z_delta| ≥ 2` atau berada di luar pagar IQR perubahan.
4. **Patahan seri** diindikasikan bila arah perubahan didominasi satu arah pada ≥70% provinsi; keputusan akhir tetap kualitatif dan tidak mengubah nilai.
5. **Deduplikasi** memakai kunci `sumber + seri + wilayah + periode + rincian + berkas`. CSV dan JSON dari snapshot yang sama diperlakukan sebagai dua representasi, bukan dua observasi.

## 4. Jawaban #5 — Statistik deskriptif dan anomali `var1394`, `var1353`

### 4.1 Statistik per seri

| Seri | Tahun | n | Mean | Median | IQR | Min | Maks |
|---|---|---:|---:|---:|---:|---:|---:|
| `var1394` (persen) | 2012 | 33 | 54,32 | 55,10 | 14,00 | 19,10 (Papua) | 66,40 (Kalimantan Selatan) |
| `var1394` (persen) | 2017 | 34 | 53,96 | 56,05 | 13,68 | 35,90 (Papua, Papua Barat) | 69,40 (Kalimantan Tengah) |
| `var1394` (persen) | Semua | 67 | 54,14 | 55,10 | 13,50 | 19,10 | 69,40 |
| `var1353` (per 1.000) | 2012 | 33 | 56,06 | 53,00 | 29,00 | 20,00 (DKI Jakarta) | 104,00 (Kalimantan Barat) |
| `var1353` (per 1.000) | 2017 | 34 | 41,71 | 44,50 | 21,00 | 15,00 (DI Yogyakarta) | 83,00 (Kalimantan Tengah) |
| `var1353` (per 1.000) | Semua | 67 | 48,78 | 49,00 | 26,50 | 15,00 | 104,00 |

Tabel lengkap: [`tabel/statistik_seri.csv`](tabel/statistik_seri.csv). Statistik per provinsi, termasuk nilai 2012/2017, delta, dan z-score: [`tabel/statistik_provinsi.csv`](tabel/statistik_provinsi.csv). Nilai nasional: [`tabel/statistik_nasional.csv`](tabel/statistik_nasional.csv).

Nilai nasional:

| Seri | 2012 | 2017 |
|---|---:|---:|
| `var1394` | 57,9% | 57,2% |
| `var1353` | 48 per 1.000 | 36 per 1.000 |

Grafik:

- Boxplot per tahun: [`gambar/boxplot_var1394_var1353.png`](gambar/boxplot_var1394_var1353.png)
- Deret waktu provinsi `var1394`: [`gambar/deret_waktu_var1394.png`](gambar/deret_waktu_var1394.png)
- Deret waktu provinsi `var1353`: [`gambar/deret_waktu_var1353.png`](gambar/deret_waktu_var1353.png)
- z-score per tahun: [`gambar/zscore_anomali.png`](gambar/zscore_anomali.png)
- Perubahan 2012→2017 per provinsi: [`gambar/perubahan_2012_2017.png`](gambar/perubahan_2012_2017.png)

### 4.2 Daftar calon anomali

Tabel lengkap: [`tabel/anomali.csv`](tabel/anomali.csv). Ringkasnya:

| Seri | Provinsi | Periode | Nilai | Metode | Alasan ditandai | Kategori |
|---|---|---|---:|---|---|---|
| `var1353` | Kalimantan Barat (6100) | 2012 | 104 | z = 2,23 | Di atas ambang z; bagian dari level 2012 yang tinggi | patahan |
| `var1353` | Sulawesi Barat (7600) | 2012 | 101 | z = 2,09 | Di atas ambang z; level 2012 tinggi | patahan |
| `var1353` | Sulawesi Barat (7600) | 2012→2017 | −55 | z_delta = −2,54 | Penurunan terbesar; bagian dari penurunan serentak | patahan |
| `var1353` | Kalimantan Tengah (6200) | 2017 | 83 | IQR+z = 2,69 | Di luar pagar IQR 2017 [−1,75; 82,25]; tetap tinggi saat provinsi lain turun | outlier asli |
| `var1394` | Papua (9400) | 2012 | 19,1 | IQR+z = −3,42 | Di luar pagar IQR 2012 [27,00; 83,00] | outlier asli |
| `var1394` | Papua Barat (9100) | 2017 | 35,9 | z = −2,05 | Di bawah ambang z 2017 | outlier asli |
| `var1394` | Papua (9400) | 2017 | 35,9 | z = −2,05; z_delta = 4,08 | Rendah pada 2017, tetapi naik 16,8 poin dari 2012 | outlier asli |

Catatan: `var1353` 2012 tidak memiliki nilai yang melewati pagar IQR karena IQR-nya lebar (−4,5 sampai 111,5); dua nilai tinggi terdeteksi lewat z-score. Sebaliknya, Kalimantan Tengah 2017 terdeteksi oleh IQR dan z-score.

## 5. Jawaban #6 — Profil seri pembanding

Tabel panjang seri × periode × rincian: [`tabel/ketersediaan_pembanding_panjang.csv`](tabel/ketersediaan_pembanding_panjang.csv). Ringkasan: [`tabel/ketersediaan_pembanding_ringkas.csv`](tabel/ketersediaan_pembanding_ringkas.csv).

| Seri | Sumber | Rincian | Satuan | Periode tersedia | Irisan katalog 2012–2017 | Irisan observasi utama (2012, 2017) | Sebanding? |
|---|---|---|---|---|---|---|---|
| `MDG_0000000003` | WHO GHO | Perempuan, umur 15–19; Indonesia | per 1.000 perempuan 15–19 | 2001–2016; 14 tahun (2001–2011, 2013, 2015, 2016) | 3 tahun terisi: 2013, 2015, 2016 | 0 | Ya (kandidat) untuk `var1353` |
| `MDG_0000000003` | WHO GHO | Perempuan, umur 10–14; Indonesia | per 1.000 perempuan 10–14 | 2002–2016; 12 tahun | 3 tahun terisi: 2013, 2015, 2016 | 0 | Tidak; umur berbeda |
| `SDGFPALL` | WHO GHO | Perempuan, umur 15–49; Indonesia | persen | 2002, 2007, 2012, 2015, 2016, 2017 | 4 tahun: 2012, 2015, 2016, 2017 | 2 tahun: 2012, 2017 | Ya untuk `var1394` |
| `SP.ADO.TFRT` | WDI | Total, umur 15–19; Indonesia | per 1.000 perempuan 15–19 | 1960–2024; 65 tahun (2025 kosong) | 6 tahun: 2012–2017 | 2 tahun: 2012, 2017 | Ya, definisi sama; metode berbeda |

Rincian yang kandidat sebanding:

- **`SDGFPALL` ↔ `var1394`**: sama-sama perempuan usia 15–49, kebutuhan KB terpenuhi dengan metode modern, satuan persen. Perbedaan utama adalah metode survei dan denominator; selisih nasional 2012 sebesar **−21,1 poin persentase** (57,9 vs 79,0) dan 2017 sebesar **−19,8 pp** (57,2 vs 77,0). Selisih dijelaskan, tidak dihapus.
- **`SP.ADO.TFRT` ↔ `var1353`**: sama-sama laju kelahiran perempuan 15–19 per 1.000. Selisih nasional 2012 sebesar **+3,38 per 1.000** (48,0 vs 44,616) dan 2017 sebesar **+3,21 per 1.000** (36,0 vs 32,792). WDI memakai estimasi UN WPP, BPS memakai survei DHS.
- **`MDG_0000000003` (Y15T19) ↔ `var1353`**: umur dan satuan sama, tetapi **tidak ada tahun observasi yang benar-benar beririsan**. Nilai 2012 tidak tersedia di WHO, dan 2017 berada di luar cakupan WHO (berhenti 2016). Nilai terdekat adalah 2016 sebesar 36,11 per 1.000, berdekatan dengan BPS 2017 sebesar 36.
- **`MDG_0000000003` (Y10T14)** ditolak sebagai pembanding `var1353` karena kelompok umurnya berbeda.

Grafik pembanding: [`gambar/pembanding_nasional.png`](gambar/pembanding_nasional.png). Angka selisih yang dipakai di narasi di atas adalah besaran turunan; operan dan rumusnya dirinci di bagian 11.

## 6. Jawaban #7 — Grid provinsi × periode, kelengkapan, dan satuan

### 6.1 Aturan grid

- Grid memakai **38 provinsi susunan 2025** dari `vervar` BPS, dengan 9999 Indonesia dikeluarkan dari grid provinsi.
- Rentang periode katalog adalah 2012–2017, sehingga grid tahunan berisi 6 tahun.
- Tahun **2013–2016** diberi status `tidak_terbit` karena BPS hanya menerbitkan gelombang survei 2012 dan 2017. Ini bukan missing dan tidak diinterpolasi.
- Provinsi **9200 Papua Barat Daya, 9500 Papua Selatan, 9600 Papua Tengah, dan 9700 Papua Pegunungan** diberi status `belum_ada` karena baru dibentuk tahun 2022.
- **6500 Kalimantan Utara** pada 2012 diberi status `belum_tercakup`; provinsi ini baru muncul pada gelombang 2017.

Tabel grid per sel: [`tabel/grid_panel.csv`](tabel/grid_panel.csv). Ringkasan: [`tabel/kelengkapan_grid.csv`](tabel/kelengkapan_grid.csv). Baris Indonesia: [`tabel/grid_nasional.csv`](tabel/grid_nasional.csv).

### 6.2 Kelengkapan panel per seri

Setiap seri memiliki 38 provinsi × 6 tahun = 228 sel.

| Seri | Tahun | Sel terisi | Persen terisi | Tidak terbit | Belum ada | Belum tercakup | Missing sejati |
|---|---|---:|---:|---:|---:|---:|---:|
| `var1394` | 2012 | 33 | 86,84% | 0 | 4 | 1 | 0 |
| `var1394` | 2013–2016 | 0 | 0,00% | 38/tahun | 0 | 0 | 0 |
| `var1394` | 2017 | 34 | 89,47% | 0 | 4 | 0 | 0 |
| `var1394` | Semua | 67 | 29,39% | 152 | 8 | 1 | 0 |
| `var1353` | 2012 | 33 | 86,84% | 0 | 4 | 1 | 0 |
| `var1353` | 2013–2016 | 0 | 0,00% | 38/tahun | 0 | 0 | 0 |
| `var1353` | 2017 | 34 | 89,47% | 0 | 4 | 0 | 0 |
| `var1353` | Semua | 67 | 29,39% | 152 | 8 | 1 | 0 |

Jika hanya tahun survei yang dihitung, kelengkapan adalah **67/76 = 88,16%** per seri. Sel kosong pada tahun survei hanya berasal dari provinsi yang belum ada/tercakup, bukan dari nilai yang hilang.

Grafik grid: [`gambar/kelengkapan_panel.png`](gambar/kelengkapan_panel.png).

### 6.3 Satuan angka kelahiran remaja

`var1353` ditetapkan bersatuan **per 1.000 perempuan usia 15–19 tahun**, bukan persen. Dasar keputusan:

- Metadata WHO `MDG_0000000003` memakai kolom `RATE_PER_1000_N` untuk `DIM_AGE = Y15T19`.
- Metadata WDI `SP.ADO.TFRT` menyebut *births per 1,000 women ages 15-19*.
- Kolom `satuan` pada CSV BPS kosong; nilai BPS 15–104 konsisten dengan laju per 1.000, bukan persentase 0–100.

Keputusan dicatat sebagai **K-018** di `log-keputusan.csv`.

### 6.4 Batas pemakaian panel provinsi

- Tahun terakhir seri utama adalah **2017**. Panel provinsi tidak dapat dipakai untuk analisis setelah 2017.
- Tahun 2012 hanya mencakup **33 provinsi**; tahun 2017 mencakup **34 provinsi**. Empat provinsi Papua baru (9200/9500/9600/9700) tidak ada pada kedua tahun, dan Kalimantan Utara (6500) tidak ada pada 2012.
- Karena itu, perbandingan 38 provinsi secara lengkap untuk 2012–2017 **tidak didukung** oleh data mentah. Analisis lintas waktu harus dibatasi pada 33 provinsi yang berpasangan, atau menyatakan ketidakseimbangan panel secara eksplisit.

## 7. Jawaban #8 — Outlier asli, patahan seri, galat input, dan deduplikasi

### 7.1 Kategori anomali

Ringkasan: [`tabel/ringkasan_kategori_anomali.csv`](tabel/ringkasan_kategori_anomali.csv). Bukti patahan: [`tabel/ringkasan_patahan.csv`](tabel/ringkasan_patahan.csv).

| Kategori | `var1394` | `var1353` | Total | Perlakuan |
|---|---:|---:|---:|---|
| Outlier asli | 3 | 1 | 4 | Ditandai, nilai dipertahankan |
| Patahan/revisi seri | 0 | 3 | 3 | Ditandai, nilai dipertahankan |
| Galat input | 0 | 0 | 0 | Tidak ada yang diperbaiki |

**Patahan `var1353`.** Dari 33 provinsi yang berpasangan, **26 provinsi turun (78,8%)**, 5 naik, dan 2 tetap; median perubahan **−11 per 1.000**, rata-rata **−14,09**. Pola searah hampir serentak ini adalah kandidat patahan/revisi seri atau perubahan metode/definisi. WDI juga turun dari 44,62 (2012) menjadi 32,79 (2017), sehingga tren nyata belum dapat dikesampingkan. Nilai tidak diubah; keputusan dicatat sebagai **K-023**.

**Batas dua titik dan patahan wilayah.** Seri utama hanya memiliki dua periode observasi (2012 dan 2017), sehingga uji patahan seri tidak dapat memisahkan secara tegas perubahan metode dari tren nyata. Klasifikasi `var1353` di atas tetap **kandidat** (K-023, ditegaskan K-027). Kaltara (6500) tidak memiliki baris observasi pada 2012 dan baru tercatat pada 2017, sedangkan Kaltim (6400) tercatat pada kedua periode. Berdasarkan acuan resmi README kasus 03 dan keputusan K-013, nilai Kaltim tahun 2012 masih mencakup wilayah Kaltara. Namun, cakupan tersebut belum dapat diverifikasi ulang dari data mentah karena berkas sumber BPS tidak tersedia secara lokal. Oleh karena itu, kondisi ini dicatat sebagai potensi patahan wilayah (K-027), bukan sebagai koreksi nilai.

**Bukan patahan `var1394`.** Arah perubahan campuran: 21 provinsi turun (63,6%), 12 naik, median hanya **−1,2**. Tidak ada indikasi lonjakan serentak. Anomali Papua dan Papua Barat dikategorikan outlier asli karena nilai ekstremnya konsisten dengan posisi kedua provinsi yang memang rendah, bukan kesalahan input.

**Galat input.** Tidak ditemukan nilai negatif, nilai di luar domain satuan, kode wilayah ganda, atau nilai yang melanggar metadata. `var1353` maksimum 104 per 1.000 masih mungkin secara substantif. Karena tidak ada bukti galat input, **tidak ada nilai yang dikoreksi**. Keputusan dicatat sebagai **K-022**.

### 7.2 Aturan deduplikasi

- Kunci unik: `sumber + seri_kode + wilayah_kode + periode + rincian + _berkas_raw`.
- Angka sama dari dua snapshot/representasi **bukan duplikat yang salah**; angka berbeda adalah **revisi**, bukan dirata-rata.
- CSV dan JSON BPS dari snapshot 2026-10-20 dibandingkan per `(wilayah, tahun)`: **69 nilai per seri, 69 sama, 0 berbeda, 0 hanya di satu sisi**. Keduanya identik, sehingga CSV dipakai sebagai kanonik dan JSON sebagai pemeriksa. Bukti: [`tabel/deduplikasi_csv_json.csv`](tabel/deduplikasi_csv_json.csv).
- Tidak ada snapshot kedua untuk seri yang sama pada paket ini, sehingga belum ada revisi yang dapat diamati. Snapshot BPS 2026-10-17 berisi seri SDG 4 (pendidikan) dan tidak dipakai untuk kasus ini.

**Contoh dampak aturan deduplikasi (K-028).** Untuk `var1353`, Kalimantan Barat (6100) tahun 2012, CSV memuat **104** dan JSON juga memuat **104** — satu observasi yang sama. Jika JSON ikut dimuat sebagai observasi kedua, baris seri utama naik dari **138 menjadi 276**, total Silver dari **235 menjadi 373**, dan setiap pasangan wilayah–tahun memiliki dua baris Silver kandidat. Karena kunci Silver memuat `_berkas_raw`, kedua baris tidak melanggar kunci primer: duplikasinya bersifat **analitik**, bukan pelanggaran skema. Karena itu CSV dipertahankan sebagai kanonik dan JSON sebagai pemeriksa; dampak baris sesuai K-021/K-028 adalah **0**.

## 8. Keputusan yang tercatat

| ID | Keputusan | Dampak baris/sel |
|---|---|---:|
| K-018 | Satuan `var1353` = per 1.000 perempuan 15–19, bukan persen | 69 |
| K-019 | 2013–2016 = `tidak_terbit`, tidak diinterpolasi | 304 |
| K-020 | Empat provinsi Papua baru = `belum_ada`; Kalimantan Utara 2012 = `belum_tercakup` | 18 |
| K-021 | CSV dan JSON snapshot sama = representasi, bukan duplikat | 0 |
| K-022 | IQR/z-score untuk anomali; hanya galat input yang boleh diperbaiki | 7 |
| K-023 | Penurunan serentak `var1353` = kandidat patahan, bukan galat input | 3 |
| K-024 | Pembanding: MDG Y15T19 dan WDI untuk `var1353`; SDGFPALL untuk `var1394` | 0 |
| K-025 | Indonesia (9999) dipisahkan dari grid provinsi | 0 |
| K-026 | Selisih pembanding nasional sebagai besaran turunan | 0 |
| K-027 | Potensi patahan wilayah Kaltim–Kaltara, bukan koreksi nilai | 0 |
| K-028 | Contoh dampak dedup Kalbar 2012 = 104 di CSV dan JSON | 0 |

## 9. Reproduksi dan metrik

```bash
# dari akar repositori, dengan venv yang sudah berisi requirements.txt
python -m src.silver.profil
python -m src.common.skema data/silver/silver.parquet
python -m src.common.hasil 124450127 baris_silver=235 sel_kosong_grid=322 outlier_ditandai=7
```

Metrik yang tersimpan di `results/124450127/metrics.json`:

| Metrik | Nilai |
|---|---:|
| `baris_silver` | 235 |
| `baris_seri_utama` | 138 |
| `sel_kosong_grid` | 322 |
| `sel_kosong_struktural` | 322 |
| `sel_kosong_sejati` | 0 |
| `outlier_ditandai` | 7 |
| `patahan_seri` | 1 |

## 10. Keterbatasan dan langkah berikutnya

- Hanya ada dua gelombang survei, sehingga uji tren, autokorelasi, dan pemisahan tegas antara tren nyata dan patahan belum dapat dilakukan. Klasifikasi patahan `var1353` masih kandidat dan perlu diverifikasi ke metadata/rilis BPS.
- Pembanding WHO/WDI hanya tersedia pada tingkat nasional, sehingga tidak dapat dipakai untuk mengisi atau memvalidasi nilai provinsi.
- `MDG_0000000003` tidak memiliki nilai 2012 dan berhenti pada 2016; pembanding ini tidak dapat dipasangkan langsung pada tahun observasi utama.
- Nilai 2025 WDI kosong dan tidak diisi.
- Grid 38 provinsi tidak sepenuhnya didukung data 2012/2017; analisis panel harus membatasi diri pada provinsi yang benar-benar ada pada kedua tahun atau melaporkan ketidakseimbangan secara eksplisit.
- Langkah berikutnya: verifikasi patahan `var1353` ke rilis/metadata BPS, lengkapi pembanding nasional pada Gold, dan dokumentasikan aturan missing/patahan di data dictionary serta skema validasi.

## 11. Rujukan angka

Setiap angka di laporan ini ditautkan ke tabel hasil yang sudah di-commit atau ke keputusan di `log-keputusan.csv`. Angka turunan disertai operan dan rumusnya. Semua tabel berikut berada di `reports/tabel/`, kecuali dinyatakan lain.

| Angka di laporan | Nilai | Sumber tabel / hasil | Log |
|---|---|---|---|
| Baris Silver | 235 | `results/124450127/metrics.json`; `reports/validasi.md`; `data/silver/silver.parquet` | — |
| Baris seri utama | 138 | `statistik_seri.csv` (67+67 provinsi) + 4 baris nasional; `silver.parquet` | — |
| Seri / wilayah / berkas sumber | 5 / 35 / 5 | `reports/validasi.md`; `silver.parquet` | — |
| Baris per sumber (BPS 2 berkas, WHO MDG, WHO SDGFPALL, WDI) | 69 / 69 / 26 / 6 / 65 | `silver.parquet` dikelompokkan per `_berkas_raw` | K-029, K-030, K-034 |
| Tahun observasi utama | 2012, 2017 | `statistik_seri.csv`; `grid_panel.csv`; `data/raw/bps/2026-10-20/` | K-019 |
| Provinsi teramati 2012 / 2017 | 33 / 34 | `statistik_seri.csv` kolom `n`; `kelengkapan_grid.csv` | K-020, K-025 |
| Mean `var1394` 2012 / 2017 | 54,32 / 53,96 | `statistik_seri.csv`, baris `var1394` | — |
| Median / IQR `var1394` 2012 / 2017 | 55,10 / 14,00; 56,05 / 13,68 | `statistik_seri.csv`, baris `var1394` | — |
| Min–maks `var1394` 2012 / 2017 | 19,10–66,40; 35,90–69,40 | `statistik_seri.csv`, kolom `min`/`max` | — |
| Mean `var1353` 2012 / 2017 | 56,06 / 41,71 | `statistik_seri.csv`, baris `var1353` | K-018 |
| Median / IQR `var1353` 2012 / 2017 | 53,00 / 29,00; 44,50 / 21,00 | `statistik_seri.csv`, baris `var1353` | — |
| Min–maks `var1353` 2012 / 2017 | 20,00–104,00; 15,00–83,00 | `statistik_seri.csv`, kolom `min`/`max` | — |
| Nilai nasional `var1394` 2012 / 2017 | 57,9 / 57,2 | `statistik_nasional.csv`; `grid_nasional.csv` | — |
| Nilai nasional `var1353` 2012 / 2017 | 48 / 36 | `statistik_nasional.csv`; `grid_nasional.csv` | K-018 |
| Satuan `var1353` | per 1.000 perempuan 15–19 | `log-keputusan.csv` K-018; `silver.parquet` kolom `satuan` | K-018 |
| Jumlah calon anomali | 7 (3 `var1394`, 4 `var1353`) | `anomali.csv`; `ringkasan_kategori_anomali.csv`; `results/124450127/metrics.json` | K-022 |
| Kategori anomali | 4 outlier asli, 3 patahan, 0 galat input | `ringkasan_kategori_anomali.csv` | K-022, K-023, K-027 |
| z-score anomali | 2,23; 2,09; −2,54; 2,69; −3,42; −2,05; 4,08 | `anomali.csv` kolom `z_skor` / `z_delta` | — |
| Pagar IQR 2012 `var1394` / 2017 `var1353` | [27,00; 83,00] / [−1,75; 82,25] | `anomali.csv` kolom `batas_bawah` / `batas_atas` | — |
| Penurunan serentak `var1353` | 26/33 (78,8%), median −11, mean −14,09 | `ringkasan_patahan.csv`, baris `var1353` | K-023 |
| Arah perubahan `var1394` | 21 turun, 12 naik, median −1,2 | `ringkasan_patahan.csv`, baris `var1394` | — |
| Catatan cakupan wilayah Kaltim dan Kaltara | Kaltim (6400): 54,1/59,3 dan 50/53; Kaltara (6500): belum tercatat pada 2012, 46,9 dan 33 pada 2017 | `statistik_provinsi.csv`; `silver.parquet` | K-027 |
| Total sel grid | 456 = 38 × 6 × 2 | `grid_panel.csv` (456 baris); `kelengkapan_grid.csv` | K-019 |
| Sel terisi | 134 (29,39%) | `kelengkapan_grid.csv` kolom `n_terisi`; `results/124450127/metrics.json` | — |
| Sel kosong | 322 | `grid_panel.csv`; `results/124450127/metrics.json` | K-019, K-020 |
| `tidak_terbit` | 304 = 38 × 4 tahun × 2 seri | `kelengkapan_grid.csv` kolom `n_tidak_terbit` | K-019 |
| `belum_ada` + `belum_tercakup` | 16 + 2 = 18 | `kelengkapan_grid.csv` kolom `n_belum_ada` / `n_belum_tercakup` | K-020 |
| Missing sejati | 0 | `kelengkapan_grid.csv` kolom `n_missing`; `results/124450127/metrics.json` | K-019, K-020 |
| Persen terisi per seri | 2012: 33/38 = 86,84%; 2017: 34/38 = 89,47% | `kelengkapan_grid.csv` | — |
| Kelengkapan tahun survei | 67/76 = 88,16% per seri | `kelengkapan_grid.csv` (33+34 terisi dari 2×38) | — |
| Perbandingan CSV vs JSON | 69/69 sama, 0 beda, 0 hanya satu sisi | `deduplikasi_csv_json.csv` | K-021, K-028 |
| Contoh dedup Kalbar 2012 `var1353` | 104 (CSV) = 104 (JSON) | `data/raw/bps/2026-10-20/sdg3_3_7_2_v1353.csv` dan `json/sdg3_3_7_2_v1353.json` | K-028 |
| Dampak bila JSON ikut dimuat | seri utama 138→276; Silver 235→373 | jumlah baris `baca_bps()` + `baca_bps_json()` di `src/silver/profil.py` | K-028 |
| WDI `SP.ADO.TFRT` 2012 / 2017 | 44,616 / 32,792 | `ketersediaan_pembanding_panjang.csv`; `silver.parquet` | K-024 |
| WHO `SDGFPALL` 2012 / 2017 | 79,0 / 77,0 | `ketersediaan_pembanding_panjang.csv`; `silver.parquet` | K-024 |
| WHO `MDG_0000000003` Y15T19 2016 | 36,109833 | `ketersediaan_pembanding_panjang.csv`; `silver.parquet` | K-024 |
| Selisih `var1394` − `SDGFPALL` | −21,1 pp = 57,9 − 79,0; −19,8 pp = 57,2 − 77,0 | `statistik_nasional.csv` + `ketersediaan_pembanding_panjang.csv` | K-026 |
| Selisih `var1353` − `SP.ADO.TFRT` | +3,38 = 48,0 − 44,616; +3,21 = 36,0 − 32,792 | `statistik_nasional.csv` + `ketersediaan_pembanding_panjang.csv` | K-026 |
| Berkas manifest / cocok SHA256 / `data_hash` | 13 / 13 / `5b38cf44…` | `data/raw/MANIFEST.csv`; `python -c "from src.common.hasil import data_hash; print(data_hash())"` | — |

Bukti metrics anggota lain dan status sinkronisasi `data_hash` tercantum di `reports/individu/124450127.md` bagian 4.1; saya tidak mengubah berkas `results/<nim>/` milik anggota lain.
