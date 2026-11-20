# Profil dan Anomali — Silver Kasus 03

Dokumen ini digantikan oleh keluaran `python pipeline.py` yang selalu dihitung ulang dari
`data/silver/silver.parquet`. Versi lama memakai Silver 373 baris (CSV dan JSON BPS dipertahankan);
versi acuan memakai JSON BPS sebagai sumber Silver sehingga Silver berisi 235 baris.

Berkas acuan yang perlu dibaca:

- `reports/profil-seri-utama.md` — statistik deskriptif, IQR, missing, duplikat, dan patahan per seri.
- `reports/calon-anomali.csv` — calon anomali dengan alasan, bukan daftar yang langsung dibuang.
- `reports/anomali.md` dan `reports/anomali.csv` — outlier, patahan wilayah, dan galat input.
- `reports/gambar/` — boxplot dan deret per seri utama.

Keputusan yang berlaku tercatat di `log-keputusan.csv`:

- K-002: JSON BPS sebagai sumber Silver; CSV tetap dibaca sebagai pembanding.
- K-004: outlier IQR ditandai dan dipertahankan, tidak di-winsorize.
- K-005: panel provinsi hanya 2012 dan 2017; tahun antarsurvei tidak diinterpolasi.
- K-013: Kalimantan Timur 2012→2017 ditandai `patahan_wilayah` karena 2012 masih mencakup
  Kalimantan Utara.
