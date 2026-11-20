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
- [x] `results/<nim>/metrics.json` setiap anggota di-commit (`results/kelompok-03/metrics.json`).
