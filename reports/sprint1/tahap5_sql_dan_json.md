# Draf Sprint 1 — Tahap 5: SQL Silver (124450055, integrasi/penyimpanan/skala)

## 1. Pemeriksaan struktur Silver
- Lokasi target: `data/silver/silver.parquet` (skema minimal `src/common/skema.py`).
- Kondisi saat penyusunan draf (2026-11-16): **belum ada Silver pertama** (`data/silver/` hanya `.gitkeep`); tahap 1–4 (`src/ekstraksi`, `src/silver`) masih stub. Karena itu pemuatan aktual pada data Silver belum dapat dijalankan; DDL/script disiapkan dan diuji kesiapan skemanya.
- Kolom wajib (12): `sumber, seri_kode, wilayah_kode, nama_wilayah, periode, jenis_periode, rincian, nilai, satuan, _berkas_raw, _sha256_raw`.
- Kunci unik/granularitas: `(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)`.
- Tipe logis: sumber/seri/nama/periode/jenis/rincian/satuan/berkas/hash = teks; wilayah_kode = integer (9999 nasional, provinsi kode BPS×100); nilai = numerik (REAL); `jenis_periode` ∈ {tahun, semester, triwulan, bulan}; nilai & kolom non-nilai tidak boleh kosong (per skema).

## 2. DDL & script pemuat
- DDL + pemuat: `src/gold/silver_sql.py` (membuat tabel `silver`, PK & CHECK `jenis_periode`, indeks `(seri_kode,wilayah_kode,periode)`, memuat dari parquet/csv).
- Basis data: **SQLite** file `data/gold/silver.sqlite` (dihasilkan saat pemuatan; file DB besar tidak di-commit per kebijakan repo).
- Cara pakai (dari root repo, saat Silver tersedia):
  - `python3 src/gold/silver_sql.py --silver data/silver/silver.parquet --db data/gold/silver.sqlite --replace`

## 3. Alasan pemilihan basis data (SQLite)
- **Kesesuaian kebutuhan:** Silver kasus 03 berukuran kecil–menengah (panel provinsi×periode×seri); SQLite cukup untuk query analitik ringan, join rekonsiliasi, dan agregasi tanpa server.
- **Kemudahan reproduksi:** satu file `.sqlite`, engine bawaan Python (`sqlite3`), nol konfigurasi/server/credential—memudahkan `python pipeline.py`/reviewer di lingkungan berbeda.
- **Karakteristik data:** skema tabular relasional stabil (skema minimal baku), kunci komposit jelas, tipe dapat dipaksakan (PK, NOT NULL, CHECK). Cocok sebagai lapis penyimpanan terstruktur di samping file kolumnar (parquet).
- Alternatif: DuckDB unggul untuk analitik kolumnar & scan parquet besar (relevan tahap skala/WDI), PostgreSQL unggul untuk multi-user/konkurensi—keduanya overkill untuk Silver pertama kasus ini dan menambah dependensi/ops setup.

## 4. Perbandingan singkat SQL vs respons JSON mentah
| Aspek | Tabel SQL (Silver) | Respons JSON mentah |
|---|---|---|
| Struktur & skema | Skema eksplisit (kolom, tipe, PK, CHECK); bentuk seragam lintas sumber setelah normalisasi | Struktur heterogen per sumber/API (nested, field berbeda), skema implisit |
| Kemudahan query | Mudah filter/join/agregasi/group-by (SQL), indeks mempercepat pencarian seri/wilayah/periode | Perlu parsing/flattening dulu; query ad-hoc sulit & lambat pada nested data |
| Validasi & konsistensi | Constraint DB + validasi skema (unik kunci, NOT NULL, domain) mencegah duplikat/tipe salah | Validasi manual; raw dapat mengandung inkonsistensi/duplikasi sumber apa adanya |
| Fleksibilitas perubahan struktur | Perubahan skema butuh migrasi/DDL terkontrol (lebih kaku, tapi aman) | Fleksibel menyimpan variasi field, namun memindah beban penanganan ke downstream |
| Penyimpanan & reproduksi | Kompak terstruktur, portabel (1 file SQLite) dan mudah direkalkulasi dari pipeline | Jejak asli sumber (good for lineage/arsip Bronze) tapi boros/kurang efisien untuk analisis; perlu disimpan utuh sesuai manifest |

**Kesimpulan draf:** JSON mentah dipertahankan sebagai lapis Bronze ber-provenans (tidak diubah); Silver dipromosikan ke bentuk relasional terstruktur (SQL/parquet) untuk query, integrasi, dan validasi yang andal.

## 5. Hasil uji kesiapan (tanpa Silver data)
- `python3 src/gold/silver_sql.py` → DB `data/gold/silver.sqlite` disiapkan (tabel `silver` kosong), keluar kode prasyarat-belum-terpenuhi + `DDL_OK`. Pemuatan baris aktual & validasi jumlah baris/isi **tertunda** hingga Silver pertama tersedia dari tahap 1–4.
