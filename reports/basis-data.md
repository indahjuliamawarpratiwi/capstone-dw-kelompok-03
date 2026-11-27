# Silver dan Gold di SQL

Dihasilkan `python pipeline.py` (`src/gold/muat_sql.py`). DDL: `src/gold/silver.sql` dan `src/gold/gold.sql`. Basis data `data/gold/gudang.duckdb` (4.5 MB) dibuat ulang setiap kali dan tidak di-commit.

## Isi

| tabel | baris |
|---|---|
| seri | 5 |
| silver | 235 |
| gold_panel | 152 |
| gold_nasional | 89 |
| rekonsiliasi | 28 |
| dokumen_mentah | 9 |

Jumlah baris setiap tabel dicocokkan dengan Parquet-nya saat dimuat; beda satu baris pun menghentikan pipeline.

## Kunci primer dan batasan

- `silver`: (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw) — dua snapshot boleh berdampingan.
- `gold_panel`: (indikator, wilayah_kode, periode) — satu nilai per sel; CHECK status sel dan nilai kosong hanya bila sel kosong.
- `gold_nasional`: (seri_kode, rincian, periode).
- `rekonsiliasi`: (pasangan_id, seri_pembanding, rincian_pembanding, periode); CHECK kategori baku dan selisih = utama − pembanding.

Uji: memasukkan ulang satu sel panel yang sudah ada → ditolak (ConstraintException).

## Mengapa DuckDB, dan mengapa tabel (bukan dokumen)

DuckDB dipilih karena satu berkas tanpa server, membaca Parquet langsung, dan cukup untuk ukuran data kasus ini; SQLite atau PostgreSQL sama sahnya. Lapis Silver dan Gold disimpan sebagai **tabel** karena pertanyaan analisisnya selalu per seri × wilayah × periode dan perlu kunci serta batasan. Berkas JSON mentah juga disimpan sebagai **dokumen** (`dokumen_mentah`) untuk perbandingan: dokumen menjaga bentuk asli (cocok untuk lapis Bronze dan audit), tetapi setiap pertanyaan harus mengurai struktur bersarangnya dan tidak ada kunci yang menolak sel ganda.

| pertanyaan | tabel_silver | dokumen_json | ms_silver | ms_dokumen | catatan |
|---|---|---|---|---|---|
| berapa angka var1353 di `bps/2026-10-20/json/sdg3_3_7_2_v1353.json` | 69 | 0 | 2.04 | 1.94 | dokumen menghitung semua kunci datacontent (termasuk wilayah/rincian yang tidak masuk Silver); tabel Silver hanya baris yang lolos pembacaan |
