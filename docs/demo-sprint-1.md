# Demo Sprint 1 — Kasus 03

Naskah demo Sprint 1 ada di `DEMO.md` pada akar repo. Naskah itu mengikuti alur acuan Kasus 03:
data mentah lolos sha256, `python pipeline.py` menghasilkan Silver, Gold, dan validasi, lalu satu
baris Silver ditelusuri kembali ke berkas mentahnya.

Perintah ringkas:

```bash
python unduh_data.py --kasus 3
python pipeline.py
python -m src.common.skema data/silver/silver.parquet
python -m pytest -q
```

Bukti keluaran yang selalu diperbarui oleh pipeline:

- `reports/ekstraksi.md` — jumlah baris per berkas dan cakupan MANIFEST.
- `reports/metadata.md` dan `docs/seri.csv` — satuan, kode SDG, dan buktinya.
- `reports/anomali.md`, `reports/calon-anomali.csv`, `reports/profil-seri-utama.md` — profil dan anomali.
- `reports/kelengkapan-panel.md` — grid 38 provinsi × periode.
- `reports/tabel-nasional.csv`, `reports/pasangan-rekonsiliasi.md` — integrasi nasional.
- `reports/validasi.md` — hasil aturan validasi.
- `docs/data-dictionary.md` — kamus data dan contoh penelusuran satu baris.
