# Laporan tim — Kelompok 3, Kasus 03 Kesehatan reproduksi remaja

Status: draf akhir Sprint 1. Angka dapat ditarik ulang dari `data/silver/silver.parquet`, `reports/`, dan
`log-keputusan.csv` (id K-xxx).

## Ringkasan

Kasus ini menyatukan dua seri provinsi BPS dari SDKI (KB metode modern dan angka kelahiran remaja) dengan
satu seri WDI dan dua seri WHO. Silver pertama berisi 235 baris dari 5 seri. Data
angkanya kecil dan bersih; kesulitannya ada pada kata "sama": kelompok umur angka kelahiran remaja, satuan
yang tidak ditulis BPS, dan penyebut KB yang berbeda antara BPS dan WHO.

## Data dan lineage

13 berkas mentah dari snapshot 20 Oktober 2026: BPS (2 CSV, 2 JSON, 1 catatan unduhan), WDI
(1 berkas data, 3 metadata), WHO GHO (2 CSV, 2 metadata). Semua berkas tertangani oleh `ekstraksi.jalankan()`
(374 baris mentah di berkas data). Setiap baris Silver membawa `_berkas_raw` dan `_sha256_raw`.

## Masalah data dan penanganannya

| Masalah | Bukti | Keputusan | Baris terdampak | Log |
|---|---|---|---|---|
| Kelompok umur `var1353` | `var.label`: perempuan 15–19 | cakupan seri; pembanding WHO `umur=15-19` | 0 | K-003 |
| Satuan `var1353` kosong | definisi WHO, nama WDI, besaran angka | `per_1000_perempuan_seumur` | 69 | K-007 |
| Dua kelompok umur WHO dalam satu berkas | `DIM_AGE` Y10T14, Y15T19 | rincian `umur=10-14`, `umur=15-19` | 3 nilai rincian | K-006 |
| Penyebut KB berbeda | Denominator WHO; BPS Indonesia jauh di bawah WHO | P3 kategori definisi | 2 tahun | K-009 |
| Panel dua titik survei | `tahun` JSON: 2012, 2017 | tidak diinterpolasi | 0 | K-005 |
| Provinsi belum dibentuk | Kalimantan Utara 2012, provinsi Papua baru | `belum_ada` | 18 sel | K-001 |
| Wilayah induk mengecil | Kalimantan Timur 2012→2017 | `patahan_wilayah` | 2 | K-013 |
| Calon anomali | IQR antarprovinsi dan perubahan | 3 outlier ditandai, nilai tidak diubah | 3 | K-004 |
| Spasi di akhir judul | `var.label` var1353 | dibuang di nama baku | 0 | K-012 |
| BPS dua format | nilai CSV = JSON | JSON sebagai sumber | 138 | K-002 |

Tidak ada sel yang benar-benar missing (0) dan tidak ada galat input (0). Panel
provinsi hanya berlaku untuk 2012 dan 2017; panel tidak menggambarkan keadaan sesudah 2017.

## Integrasi dan rekonsiliasi

Disiapkan di Sprint 1, dihitung di Sprint 2 (`reports/pasangan-rekonsiliasi.md`):

- P1 angka kelahiran remaja BPS vs WDI: 2 tahun beririsan; survei vs model penduduk.
- P2 BPS vs WHO `umur=15-19`: 0 tahun beririsan; dibandingkan dengan tahun terdekat.
- P3 KB BPS vs WHO kebutuhan KB terpenuhi: 2 tahun; selisih definisi (penyebut).
- P4 WHO vs WDI: 14 tahun; sumber berbeda.

## Validasi dan reproduksibilitas

12 aturan berjalan setiap `python pipeline.py` (12 lolos, 0
peringatan; `reports/validasi.md`). Aturan khas kasus: tidak ada tahun BPS di luar 2012 dan 2017, setiap baris
WHO angka kelahiran remaja punya kelompok umur, satu satuan untuk semua angka kelahiran remaja; dua peringatan
menjaga pola 10–14 < 15–19 dan KB BPS < WHO. Setiap aturan diuji dengan baris yang sengaja dirusak (`tests/`).
Silver dimuat ke DuckDB dengan kunci primer dan CHECK (235 baris). `python pipeline.py` berjalan
±1.8 detik.

## Pembagian kerja

| Anggota | NIM | Komponen | Bagian laporan |
|---|---|---|---|
| Anash Tasya Ausyaqila | 124450050 | Reproduksi dan Demo — Validasi dan Dokumentasi | Validasi dan Reproduksibilitas |
| Indah Julia Mawar Pratiwi | 124450055 | Koordinator — Integrasi, Penyimpanan, dan Skala | Integrasi dan Rekonsiliasi |
| Queenta Thifaal Nabila | 124450059 | Integrator — Ekstraksi dan Lineage | Data dan Lineage |
| Hazel Mahesa Handhaka | 124450114 | Anggota — pendukung pipeline | Sesuai kesepakatan tim |
| Risa Romadona | 124450127 | Analis Utama — Profil dan Pembersihan | Masalah Data dan Penanganannya |
