# Sprint 1 (9–22 November 2026)

## Sprint Goal

Semua berkas mentah Kasus 03 terbaca dengan lineage, setiap seri punya satuan dan kode SDG yang buktinya
tercatat, dan Silver pertama lolos pemeriksa skema serta aturan validasi dasar, sehingga Sprint 2 bisa
langsung menyusun panel dan tabel rekonsiliasi.

## Definition of Done yang dipakai

- [x] Pembaca semua format mentah (BPS JSON/CSV, WDI JSON, WHO GHO CSV/JSON); tidak ada berkas MANIFEST terlewat.
- [x] Profil dan calon anomali per seri utama; grafik di `reports/gambar/`.
- [x] Missing, outlier, patahan, dan duplikat ditangani dan dicatat di `log-keputusan.csv`.
- [x] `data/silver/silver.parquet` lolos `python -m src.common.skema`.
- [x] `results/<nim>/metrics.json` setiap anggota di-commit.
- [x] Tabel nasional periode × seri tersimpan di `reports/tabel-nasional.csv`.
- [x] Daftar pasangan rekonsiliasi dan catatan keterbandingan di `reports/pasangan-rekonsiliasi.md`.
- [x] Skema SQL dan pemuat DuckDB berjalan pada Silver pertama (`src/gold/silver.sql`, `src/gold/muat_sql.py`).
- [x] `python pipeline.py` lolos sampai Silver dan validasi; `python -m pytest -q` lolos.
- [x] Sprint Goal dan Log Sprint tiga baris tersedia di `sprint/sprint-1/`.

## Item di luar repo (dikerjakan di Papan Tim)

- [ ] Demo Sprint 1 diunggah paling lambat 22 November 2026.
- [ ] Semua komponen Sprint 1 di-merge ke `main` lewat pull request yang di-review.
