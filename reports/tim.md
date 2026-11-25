# Laporan tim — Kelompok 3, Kasus 03 Kesehatan reproduksi remaja

Status: **Sprint 2 selesai**. Seluruh angka di bawah dapat ditelusuri ke `data/silver/silver.parquet`, `data/gold/*.parquet`, `data/gold/gudang.duckdb`, `reports/`, `results/kelompok-03/metrics.json`, dan `log-keputusan.csv` (K-001–K-044).

## 1. Ringkasan

Sprint 2 mengubah Silver yang sudah lolos Sprint 1 menjadi tiga lapis Gold: panel provinsi, tabel nasional, dan tabel rekonsiliasi, lalu memuatnya ke DuckDB dan memvalidasi seluruh lapis. Silver tetap **235 baris, 5 seri, 35 wilayah, 5 berkas sumber**. Gold menghasilkan **152 sel panel**, **89 baris nasional**, **28 baris rekonsiliasi**, dan **6 tabel DuckDB**. Validasi berjalan dengan **22 aturan** (12 Sprint 1 + 10 Gold), semuanya lolos.

Fokus kasus tetap pada pembedaan hal yang tampak “sama”: `var1353` hanya umur 15–19, satuan angka kelahiran remaja tidak ditulis BPS, kelompok umur WHO 10–14 tidak sepadan, penyebut `var1394` dan `SDGFPALL` berbeda, WHO tidak memiliki 2012/2017, dan Kaltim 2012 masih mencakup Kaltara.

## 2. Data dan lineage

Respons JSON mentah tetap disimpan apa adanya di `data/raw/` sebagai lapis Bronze/arsip lineage, bukan
dimuat sebagai dokumen ke dalam basis data. Untuk Silver dan Gold dipakai **DuckDB** (`data/gold/gudang.duckdb`,
dibuat ulang oleh `python pipeline.py`, tidak di-commit): DDL ada di `src/gold/silver.sql` dengan empat tabel
ber-kunci primer jelas — `silver` (235 baris), `panel_gold` (134), `nasional` (101), dan `rekonsiliasi` (2).
DuckDB dipilih karena skema lapis ini stabil, kunci komposit serta CHECK dapat dipaksakan, dan tabel dapat
di-query/join/agregasi langsung dari Parquet tanpa server; JSON dokumen lebih fleksibel untuk variasi field
sumber tetapi nested/heterogen, sulit divalidasi dan lambat untuk query analitik. Dengan demikian JSON cocok
pada Bronze untuk keterlacakan, sedangkan tabel SQL cocok pada Silver (konsistensi) dan Gold (panel,
agregasi nasional, serta pasangan rekonsiliasi).

## Masalah data dan penanganannya
Paket mentah terdiri dari **13 berkas** snapshot 17–20 Oktober 2026 (BPS 2 CSV + 2 JSON + 1 manifest asal; WDI 1 data + 3 metadata; WHO GHO 2 CSV + 2 metadata). `ekstraksi.jalankan()` membaca seluruh berkas manifest dengan `_berkas_raw` dan `_sha256_raw` dari `src.common.manifest.sha256_raw`;lympi **0 berkas terlewat** dan **0 SHA256 tidak cocok**. Silver memuat 374 baris data observasi terpilih dari 5 seri.

Bukti: `reports/ekstraksi.md`, `src/ekstraksi/`, `src/common/manifest.py`, `log-keputusan.csv` K-002, K-013, K-018.

## 3. Masalah data dan penanganannya

| Masalah | Bukti | Keputusan | Baris terdampak | Log |
|---|---|---|---|---|
| Kelompok umur `var1353` | `var.label`: perempuan 15–19 | cakupan seri; pembanding WHO `umur=15-19` | 0 | K-003 |
| Satuan `var1353` kosong | definisi WHO, nama WDI, besaran angka | `per_1000_perempuan_seumur` | 69 | K-007 |
| Dua kelompok umur WHO dalam satu berkas | `DIM_AGE` Y10T14/Y15T19 | rincian `umur=10-14`, `umur=15-19`; 10-14 tidak masuk Gold | 3 nilai rincian | K-006, K-041 |
| Penyebut KB berbeda | BPS jauh di bawah WHO pada tahun sama | P3 kategori definisi berbeda | 2 tahun | K-009, K-042 |
| Panel dua titik survei | hanya 2012 dan 2017 | tidak diinterpolasi | 0 | K-005, K-039 |
| Provinsi belum dibentuk | Kaltara 2012, empat provinsi Papua baru | `belum_ada`, tetap tampil di grid | 18 sel | K-001, K-020 |
| Wilayah induk mengecil | Kaltim 2012→2017 mencakup Kaltara | `patahan_wilayah`, bukan koreksi nilai | 2 | K-013, K-027 |
| Calon anomali | IQR antarprovinsi dan perubahan | 3 outlier + 2 patahan wilayah ditandai, nilai tidak diubah | 5 sel | K-004, K-038 |
| BPS dua format | 69/69 nilai identik per seri | JSON kanonik, CSV pemeriksa | 138 | K-002, K-028 |
| Tabel nasional terlalu luas | 101 baris memuat 12 baris umur 10-14 | Gold nasional memuat hanya rincian yang dipakai pasangan | 12 | K-041 |

Tidak ada sel benar-benar missing dan tidak ada galat input. Panel provinsi hanya berlaku untuk 2012 dan 2017.

## 4. Panel Gold

`data/gold/panel.parquet` berisi **152 sel** = 38 provinsi × 2 tahun × 2 indikator (`var1394`, `var1353`). Rincian panel hanya `total`; Indonesia (9999) tidak masuk panel. **134 sel terisi (29,39%)**, **18 sel `belum_ada`**, dan **0 missing sejati**. Penanda terbawa: **3 `outlier`** (Papua 2012, Papua Barat 2017, Kalimantan Tengah 2017 untuk `var1353`) dan **2 `patahan_wilayah`** (Kaltim 2017 pada kedua indikator). Nilai tidak diubah.

Aturan: satu nilai per `(seri_kode, wilayah_kode, periode)` dengan duplikat ditolak, snapshot/berkas kanonik mengikuti K-002, sel kosong tidak diisi, penanda Sprint 1 dibawa apa adanya (K-035, K-038, K-041). Bukti: `reports/panel-gold.md`, `data/gold/panel.parquet`, `data/gold/panel_lebar.parquet`.

Panel lebar lokal berupa **34 baris × 6 kolom** (kode+provinsi, empat kolom `var1394_2012`, `var1353_2012`, `var1394_2017`, `var1353_2017`), berbeda dari kunci yang memakai periode sebagai baris. Keduanya menyimpan nilai yang sama; format lokal dipertahankan karena sudah lolos validasi.

## 5. Tabel nasional Gold

`data/gold/nasional.parquet` berisi **89 baris** dan 13 kolom: `seri_kode`, `rincian`, `sumber`, `periode`, `jenis_periode`, `nilai`, `satuan`, `batas_bawah`, `batas_atas`, `rujukan_tahun`, `asal`, `_berkas_raw`, `_sha256_raw`. Satu baris = seri × rincian × periode tingkat Indonesia. Rincian yang masuk: `total` untuk BPS/WDI/SDGFPALL dan `umur=15-19` untuk MDG. `asal` = `baris_indonesia` untuk 4 baris BPS dan `pembanding` untuk 85 baris WHO/WDI. Kunci unik `(seri_kode, rincian, periode)`. Bukti: `src/gold/nasional_gold.py`, K-036, K-041.

## 6. Integrasi dan rekonsiliasi

`data/gold/rekonsiliasi.parquet` berisi **28 baris**: P1 6, P2 2, P3 4, P4 16. **20 baris memiliki selisih**, **8 baris tanpa pasangan** (P1 4, P3 2, P4 2). Selisih = `nilai_utama − nilai_pembanding`; selisih relatif = `100 × selisih / nilai_pembanding` (bertanda). Median selisih relatif mutlak: **8,68%** untuk 6 baris berseri utama provinsi dan **5,61%** untuk 20 baris semua pasangan.

| Pasangan | Yang dibandingkan | Median relatif | Kategori | Alasan |
|---|---|---:|---|---|
| P1 | `var1353` vs `SP.ADO.TFRT` | 8,68% | metode berbeda | SDKI vs model WPP |
| P2 | `var1353` vs MDG `umur=15-19` | 0,66% | metode berbeda | WHO tanpa 2012/2017; tahun terdekat ≤1 tahun |
| P3 | `var1394` vs `SDGFPALL` | 26,21% | definisi berbeda | penyebut KB berbeda |
| P4 | MDG `umur=15-19` vs WDI | 4,68% | metode berbeda | survei/registrasi vs model WPP |

P2 memasangkan **2012↔2011** (48,0 vs 48,489563) dan **2017↔2016** (36,0 vs 36,109833), keduanya selisih satu tahun, tercatat per baris. Baris tanpa pasangan menyimpan nilai pembanding sumber, tetapi `nilai_utama`, `selisih`, dan `selisih_relatif` kosong. Tidak ada selisih yang dihapus atau disamakan paksa. Bukti: `reports/rekonsiliasi.md`, K-042.

## 7. Basis data SQL

`data/gold/gudang.duckdb` dibuat ulang setiap pemuatan dan tidak di-commit. Tabel sebenarnya ada **6**:

| Tabel | Baris | Kunci primer |
|---|---:|---|
| `seri` | 5 | `seri_kode` |
| `silver` | 235 | `sumber + seri_kode + wilayah_kode + periode + rincian + _berkas_raw` |
| `gold_panel` | 152 | `indikator + wilayah_kode + periode` |
| `gold_nasional` | 89 | `seri_kode + rincian + periode` |
| `rekonsiliasi` | 28 | `pasangan_id + seri_pembanding + rincian_pembanding + periode` |
| `dokumen_mentah` | 9 | `_berkas_raw` |

Total baris Gold relasional = **269**. Constraint: foreign key ke `seri`, CHECK untuk wilayah, jenis periode, status sel, kategori baku, dan `selisih = utama − pembanding`; uji duplikasi kunci ditolak. Tabel `dokumen_mentah` menyimpan teks JSON mentah apa adanya. Metrik `tabel_sql=5` mengikuti kunci (tabel relasional, tidak termasuk dokumen). Bukti: `src/gold/gold.sql`, `src/gold/muat_sql.py`, `reports/basis-data.md`, K-043.

## 8. Validasi dan reproduksibilitas

`src/validasi/__init__.py` menjalankan **22 aturan**: 7 umum, 3 keras kasus, 2 peringatan kasus, dan 10 Gold. Semua **LOLOS**, tanpa peringatan. Aturan Gold mencakup kunci panel unik, satu satuan per indikator, status/nilai, keterlacakan ke Silver, nilai Gold = Silver, nasional unik, kategori baku, selisih konsisten, baris berpasangan dihitung, dan periode utama tidak dibuang. Konsistensi DuckDB terhadap parquet juga diperiksa (0 selisih). Artefak tidak diubah oleh validasi. Bukti: `reports/validasi.md`, `src/validasi/gold.py`, `tests/test_validasi_gold.py`, K-044.

Pengujian memakai `pytest` dengan cache dinonaktifkan. Tes yang menulis ulang artefak tidak dijalankan pada audit akhir; tes pembacaan dan aturan dijalankan terpisah.

## 9. Keterbatasan dan penyesuaian terhadap kunci

- Panel lokal memakai kolom `seri_kode`; kunci memakai `indikator`. Pemuatan SQL memetakan `seri_kode` ke `indikator`, sehingga skema DuckDB sesuai kunci.
- `panel_lebar` lokal 34×6 (indikator per kolom), kunci 67×6 (periode per baris). Nilai panel sama; format lokal dipertahankan.
- `data/gold/nasional.parquet` lokal 13 kolom mengikuti struktur kunci, tetapi kunci menuliskan `asal` dan rincian yang dipakai; lokal mengikuti aturan K-041.
- `rekonsiliasi.parquet` lokal memiliki 28 kolom (tambahan tahun pasangan, sumber, lineage); tabel SQL memuat hanya 16 kolom sesuai DDL kunci.
- Penanda Gold lokal 5 sel (3 outlier + 2 `patahan_wilayah`), kunci menyebut 3 sel outlier. Perbedaan ini sudah dinyatakan pada K-038 dan laporan audit sebelumnya.
- Waktu eksekusi pipeline tidak diukur pada sesi ini, sehingga tidak diklaim sama dengan ±2,8 detik pada kunci.
- Sprint 3 (arsip WDI 142 rilis, pandas vs DuckDB/Dask, validasi akhir, laporan akhir) belum dikerjakan.

## 10. Pembagian kerja

| Anggota | NIM | Komponen | Bagian laporan |
|---|---|---|---|
| Anash Tasya Ausyaqila | 124450050 | Reproduksi dan Demo — Validasi dan Dokumentasi | Validasi dan Reproduksibilitas |
| Indah Julia Mawar Pratiwi | 124450055 | Koordinator — Integrasi, Penyimpanan, dan Skala | Integrasi dan Rekonsiliasi |
| Queenta Thifaal Nabila | 124450059 | Integrator — Ekstraksi dan Lineage | Data dan Lineage |
| Hazel Mahesa Handhaka | 124450114 | Anggota — pendukung pipeline | Sesuai kesepakatan tim |
| Risa Romadona | 124450127 | Analis Utama — Profil, Pembersihan, Gold, dan Analisis | Masalah Data dan Penanganannya; Integrasi dan Rekonsiliasi |

## 11. Rujukan artefak

- Silver: `data/silver/silver.parquet`, `src/silver/`, `log-keputusan.csv` K-001–K-034.
- Gold: `data/gold/panel.parquet`, `panel_lebar.parquet`, `nasional.parquet`, `rekonsiliasi.parquet`, `src/gold/`, `log-keputusan.csv` K-035–K-043.
- SQL: `data/gold/gudang.duckdb`, `src/gold/gold.sql`, `src/gold/muat_sql.py`, `reports/basis-data.md`, K-043.
- Validasi: `src/validasi/`, `reports/validasi.md`, `results/kelompok-03/metrics.json`, K-044.
- Angka dan grafik: `reports/angka.json`, `reports/tabel/`, `reports/gambar/`.
