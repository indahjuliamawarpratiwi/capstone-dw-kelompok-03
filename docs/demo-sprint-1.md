# Demo Wajib Sprint 1 — Kasus 03

Semua bukti di bawah dihasilkan dari `data/raw/` yang cocok dengan `MANIFEST.csv`.

## Perintah demo

```bash
python -m src.ekstraksi
python -m src.silver
python -m src.common.skema data/silver/silver.parquet
python pipeline.py
```

`python pipeline.py` berhenti di Gold karena tahap Gold belum termasuk Sprint 1. Silver tetap
dihasilkan dan diperiksa sebelum Gold dipanggil.

## Checklist

| Checklist | Bukti | Hasil |
|---|---|---|
| Pembaca semua format mentah kasus (tahap 1) | `src/ekstraksi/`, `python -m src.ekstraksi` | 13/13 berkas tercakup; CSV dan JSON; 374 baris data |
| Profil dan anomali per seri (tahap 2) | `data/silver/profil.csv`, `data/silver/anomali.csv`, `data/silver/boxplot_seri.png` | 6 seri; 79 temuan anomali |
| Missing, outlier, patahan seri, duplikat ditangani dan dicatat | `log-keputusan.csv` K-003, K-005, K-008, K-009; `docs/profil-anomali.md` | 1 missing dibuang; 5 outlier dipertahankan; 287 tahun patahan dicatat; 138 baris duplikat lintas format dipertahankan |
| Silver pertama lolos skema | `python -m src.common.skema data/silver/silver.parquet` | `LOLOS 373 baris, 5 seri, 35 wilayah, 7 berkas sumber` |
| `metrics.json` setiap anggota | `results/<nim>/metrics.json` | 5/5 NIM tersedia |

## Angka kunci

| Ukuran | Nilai |
|---|---:|
| Berkas MANIFEST | 13 |
| Baris data ekstraksi | 374 |
| Baris Silver | 373 |
| Nilai kosong yang dibuang | 1 |
| Outlier IQR yang dipertahankan | 5 observasi logis |
| Patahan seri | 287 tahun-wilayah |
| Duplikat lintas format | 138 baris tambahan |
| Keputusan tercatat | 9 |

## Metrik anggota

| NIM | Komponen | Metrik utama |
|---|---|---|
| 124450050 | Validasi dan dokumentasi | 373 baris divalidasi; 0 pelanggaran skema; 11 kolom wajib |
| 124450055 | Integrasi dan penyimpanan | 373 baris Silver; 5 seri; 35 wilayah; 7 berkas sumber |
| 124450059 | Ekstraksi dan lineage | 13 berkas; 374 baris mentah; 2 format |
| 124450114 | Penjaga data dan evaluasi | 374 baris diperiksa; 1 missing; 138 duplikat; 5 outlier; 287 patahan |
| 124450127 | Profil dan pembersihan | 6 seri diprofilkan; 79 anomali; 9 keputusan |

## Catatan demo

- Kasus 03 hanya menyediakan CSV dan JSON; tidak ada XLSX atau SDMX pada paket kasus ini.
- BPS menyediakan CSV dan JSON untuk nilai yang sama. Keduanya dipertahankan karena kunci Silver
  memasukkan `_berkas_raw`; nilai tidak digabung pada tahap ini.
- Outlier tidak dihapus karena dapat merupakan variasi nyata. Patahan seri tidak diinterpolasi;
  grid wilayah x periode akan dibentuk di Gold.
