# Capstone Data Wrangling — Kelompok 03, Kasus 03 Kesehatan reproduksi remaja

Repositori tim untuk **Capstone Data Wrangling: Indikator SDG Indonesia dari Banyak Sumber**
(Program Studi Sains Data ITERA, Data Science Workbench). Kasus yang dikerjakan adalah **Kasus 03 —
Kesehatan Reproduksi Remaja**.

Data berasal dari BPS, World Bank (WDI), dan WHO GHO, persis seperti diunduh dari sumbernya pada
17–20 Oktober 2026 (lapis Bronze). Pipeline mengubah data mentah menjadi Silver (rapi, ber-provenans)
dan Gold (panel siap analisis), lalu memvalidasi serta mendokumentasikannya.

## Menjalankan

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python unduh_data.py --kasus 3
python pipeline.py
python -m src.common.skema data/silver/silver.parquet
python -m pytest -q
```

Hasil yang diharapkan:

| Ukuran | Nilai |
|---|---|
| Berkas di MANIFEST / dibaca | 13 / 13 |
| Baris mentah di berkas data | 374 |
| Baris Silver | 235 (5 seri, 3 nilai rincian) |
| Pemeriksa skema | LOLOS |
| Aturan validasi | 12 aturan: 12 lolos, 0 peringatan |
| Tes | 15 lolos, 1 dilewati (berkas BNPB tidak dipakai kasus ini) |
| Waktu `python pipeline.py` | ±1 detik |

Semua laporan di `reports/` dan `docs/data-dictionary.md` ditulis ulang oleh `python pipeline.py`,
jadi angkanya selalu sesuai dengan data. `data/gold/gudang.duckdb` dibuat ulang oleh pipeline dan
tidak di-commit.

## Struktur

```text
unduh_data.py          unduh paket kasus dari Release dan periksa sha256
pipeline.py            satu perintah reproduksi: ekstraksi -> silver -> gold -> validasi
src/common/            manifest (lineage sha256), skema (pemeriksa Silver), hasil (metrics.json)
src/ekstraksi/         tahap 1: pembaca BPS, WDI, WHO GHO (dan BNPB/ILOSTAT untuk kasus lain)
src/silver/            tahap 2–4: profil, pembersihan, metadata, grid, anomali, Silver
src/gold/              tahap 4–6: tabel nasional, pasangan rekonsiliasi, skema dan pemuat DuckDB
src/validasi/          tahap 8: aturan umum dan aturan khas kasus
src/dokumen.py         penulis data dictionary dan laporan otomatis
data/silver/, data/gold/   keluaran (basis data tidak di-commit)
log-keputusan.csv      setiap keputusan wrangling: apa, alternatif yang ditolak, alasan, dampak baris
docs/data-dictionary.md    kamus data Silver dan Gold
results/<nim>/metrics.json angka hasil komponen
reports/tim.md, reports/individu/<nim>.md, AI_LOG.md
```

## Peta backlog Sprint 1 → bukti

| Backlog | Di mana | Yang ditunjukkan |
|---|---|---|
| Penjaga data: `data/raw` cocok MANIFEST | `unduh_data.py`, `results/124450055/metrics.json` (`data_hash`) | sha256 13 berkas lolos; semua anggota harus punya `data_hash` yang sama |
| Pembaca BPS (2 JSON, 1 catatan unduhan, 2 CSV) | `src/ekstraksi/bps.py` | kunci `datacontent` dipotong menurut panjang kode di daftar label; metadata `var` ikut dibaca |
| Pembaca WDI (4 JSON) | `src/ekstraksi/wdi.py` | penyaringan kode persis (bukan awalan); `value: null` dibawa apa adanya |
| Pembaca WHO GHO (2 CSV, 2 JSON) | `src/ekstraksi/who_gho.py` | kolom nilai dikenali dari akhiran `_N/_NL/_NU`; kolom `DIM_*` utuh |
| `ekstraksi.jalankan()` | `src/ekstraksi/__init__.py`, `reports/ekstraksi.md` | tidak ada berkas MANIFEST yang terlewat; jumlah baris per berkas |
| Profil dan calon anomali seri utama | `src/silver/profil.py`, `reports/profil-seri-utama.md`, `reports/gambar/` | 3 calon anomali dengan alasan |
| Profil seri pembanding (3 seri) | `src/silver/pembanding.py`, `reports/ketersediaan-pembanding.md` | periode, rincian, irisan dengan seri utama |
| Grid 38 provinsi × periode | `src/silver/grid.py`, `reports/kelengkapan-panel.md` | 18 sel kosong: 18 belum_ada, 0 batas_lama, 0 tidak_diterbitkan, 0 missing |
| Outlier, patahan, galat, duplikat | `src/silver/anomali.py`, `reports/anomali.md`, `reports/anomali.csv` | 3 outlier, 0 patahan seri, 2 patahan wilayah, 0 galat input |
| Satuan, periode, kode SDG dari metadata | `src/silver/metadata.py`, `docs/seri.csv`, `reports/metadata.md` | 2 koreksi katalog dengan bukti dari berkas mentah |
| Silver pertama | `src/silver/bangun.py`, `data/silver/silver.parquet` | lolos `python -m src.common.skema` |
| Tabel nasional + pasangan rekonsiliasi | `src/gold/nasional.py`, `reports/tabel-nasional.csv`, `reports/pasangan-rekonsiliasi.md` | 4 pasangan selisih, 0 konteks |
| Rancangan skema SQL | `src/gold/silver.sql`, `src/gold/muat_sql.py`, `reports/basis-data.md` | Silver dimuat ke DuckDB dengan kunci primer dan CHECK |
| Aturan validasi dasar | `src/validasi/aturan.py`, `src/validasi/khusus.py`, `reports/validasi.md` | 7 aturan umum, 3 aturan khas kasus, 2 peringatan |
| Data dictionary | `docs/data-dictionary.md` | semua kolom, kamus rincian, contoh penelusuran satu baris |
| Laporan tim dan perorangan | `reports/tim.md`, `reports/individu/`, `sprint/sprint-1/` | ringkasan temuan, pembagian kerja, bukti angka |
| Reproduksi | `DEMO.md` | perintah dan waktu jalan |

## Keputusan yang paling menentukan

1. **Kelompok umur `var1353` (K-003).** Judul JSON: "Angka Kelahiran Pada Perempuan Usia 15-19 Tahun".
   Seri BPS hanya 15–19 (umur dicatat sebagai cakupan seri, rincian `total`); pembanding WHO yang
   sebanding adalah rincian `umur=15-19`, bukan baris 10–14 atau gabungan.
2. **Satuan ketika metadata BPS diam (K-007).** `var.unit` dan kolom satuan CSV kosong. Satuan
   ditetapkan `per_1000_perempuan_seumur` dari tiga bukti: definisi baku indikator yang sama di
   metadata WHO, nama WDI, dan besaran angkanya (puluhan). Satu satuan dipakai untuk BPS, WDI, dan
   kedua kelompok umur WHO, karena penyebutnya selalu perempuan pada kelompok umur yang sama.
3. **KB BPS bukan ukuran yang sama dengan WHO (K-009).** Penyebut `SDGFPALL` adalah permintaan KB
   total; judul `var1394` tidak menyebut penyebutnya, dan angka BPS Indonesia jauh di bawah WHO pada
   tahun yang sama. Pasangan P3 tetap dihitung selisihnya di Sprint 2 dengan kategori *definisi*.
4. **Panel dua titik survei (K-005, K-013).** Hanya 2012 dan 2017; Kalimantan Utara 2012 `belum_ada`,
   Kalimantan Timur 2012→2017 ditandai `patahan_wilayah`. Tahun antarsurvei tidak diisi.
5. **WHO dan BPS tidak punya tahun bersama (K-014).** WHO angka kelahiran remaja tidak punya 2012
   dan 2017; P2 punya 0 tahun beririsan, jadi perbandingan di Gold memakai tahun terdekat dengan
   penanda.

## Pilihan lain yang juga sah

- CSV BPS sebagai sumber Silver (nilainya identik); yang penting hanya satu format masuk Silver.
- Menulis umur BPS di rincian (`umur=15-19`) alih-alih sebagai cakupan seri.
- Satuan dengan kelompok umur di namanya (`per_1000_perempuan_15_19`).
- Kode umur WHO apa adanya (`Y15T19`) asalkan kamus kodenya tertulis di data dictionary.
- SQLite atau PostgreSQL alih-alih DuckDB.

## Belum dikerjakan di Sprint 1

Panel Gold provinsi × periode × indikator, selisih numerik di tabel rekonsiliasi, dan Gold di SQL
(Sprint 2); arsip WDI 142 rilis, pandas vs DuckDB/Dask, laporan akhir (Sprint 3).

## Lisensi

Kode starter: MIT. Data: lihat `data/LISENSI.md` setelah mengunduh; basis data turunan yang
diterbitkan memakai ODbL 1.0 dengan atribusi BPS, BNPB, World Bank, WHO, dan ILO.
