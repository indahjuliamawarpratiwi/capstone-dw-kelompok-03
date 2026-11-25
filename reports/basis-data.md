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

Daftar tabel sebenarnya: `dokumen_mentah`, `gold_nasional`, `gold_panel`, `rekonsiliasi`, `seri`, `silver`. Total 6 tabel (5 tabel relasional + 1 tabel dokumen).

Jumlah baris setiap tabel dicocokkan dengan sumbernya saat dimuat; beda satu baris pun menghentikan proses.

## Kunci primer dan batasan

- `silver`: (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw).
- `gold_panel`: (indikator, wilayah_kode, periode); CHECK status sel dan nilai.
- `gold_nasional`: (seri_kode, rincian, periode).
- `rekonsiliasi`: (pasangan_id, seri_pembanding, rincian_pembanding, periode); CHECK kategori baku dan selisih.
- `dokumen_mentah`: _berkas_raw sebagai kunci primer; isi JSON mentah apa adanya.

Uji: memasukkan ulang satu sel panel yang sudah ada → ditolak (ConstraintException).

## Mengapa tabel dan dokumen

Tabel relasional dipakai untuk pertanyaan per seri × wilayah × periode karena punya kunci dan batasan. Berkas JSON mentah tetap disimpan sebagai dokumen untuk audit lapis Bronze.

| pertanyaan | tabel_silver | dokumen_json | ms_silver | ms_dokumen | catatan |
|---|---|---|---|---|---|
| berapa angka var1353 di `bps/2026-10-20/json/sdg3_3_7_2_v1353.json` | 69 | 0 | 2.25 | 3.39 | dokumen menghitung semua kunci datacontent; tabel Silver hanya baris yang lolos pembacaan |
