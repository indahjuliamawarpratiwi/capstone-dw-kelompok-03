# Log Sprint 1 — Kelompok 03

Disusun dari laporan masing-masing anggota. Setiap anggota menyalin tiga baris miliknya ke Papan Tim
sebelum jendela Sprint 1 ditutup (23 November 2026, 23.59 WIB).

## Indah Julia Mawar Pratiwi (124450055) — Integrasi, penyimpanan, dan skala

1. **Yang saya kerjakan:** menyiapkan tabel nasional periode × seri, empat pasangan rekonsiliasi, skema
   DuckDB, dan pemuat Silver; memastikan `python pipeline.py` berjalan sampai validasi.
2. **Yang saya pelajari:** kelompok umur harus disamakan sebelum selisih dihitung; BPS dan WHO tidak punya
   tahun bersama untuk P2, sedangkan P3 berbeda penyebut/status perkawinan.
3. **Yang menghambat / rencana:** selisih numerik dan panel Gold belum dihitung; Sprint 2 menghitung P1–P4
   dan memuat panel Gold ke DuckDB.

## Queenta Thifaal Nabila (124450059) — Ekstraksi dan lineage

1. **Yang saya kerjakan:** pembaca BPS, WDI, dan WHO GHO; 13/13 berkas MANIFEST tercakup dengan 374 baris
   data dan lineage `_berkas_raw`/`_sha256_raw`.
2. **Yang saya pelajari:** metadata dan data harus dihitung terpisah; pembaca tidak boleh mengandalkan
   keseragaman struktur antarsumber.
3. **Yang menghambat / rencana:** pipeline sudah selesai penuh; Sprint 2 memperluas pemeriksaan lineage dan
   konsistensi jumlah baris per pembaca.

## Risa Romadona (124450127) — Profil dan pembersihan

1. **Yang saya kerjakan:** profil seri utama, grid 38 provinsi × periode, penandaan 3 calon anomali,
   18 sel `belum_ada`, dan 2 `patahan_wilayah`.
2. **Yang saya pelajari:** panel dua titik survei membatasi uji patahan seri; pemekaran wilayah dapat
   disalahartikan sebagai perubahan indikator jika tidak ditandai.
3. **Yang menghambat / rencana:** belum ada analisis sensitivitas ambang outlier; rencananya ditambahkan
   di Sprint 2.

## Anash Tasya Ausyaqila (124450050) — Validasi dan dokumentasi

1. **Yang saya kerjakan:** aturan validasi umum dan khas kasus; 12 aturan lolos, 0 peringatan, serta tes
   baris yang sengaja dirusak.
2. **Yang saya pelajari:** metadata satuan var1353 kosong dan harus ditetapkan dari definisi WHO/WDI
   (K-007), bukan diasumsikan.
3. **Yang menghambat / rencana:** validasi baru mencakup Silver; Sprint 2 menambahkan validasi skema Gold
   dan pasangan rekonsiliasi.

## Hazel Mahesa Handhaka (124450114) — Penjaga data dan evaluasi

1. **Yang saya kerjakan:** verifikasi 13/13 berkas terhadap MANIFEST dan evaluasi hasil Silver (235 baris,
   0 duplikat kunci, 0 sel kosong).
2. **Yang saya pelajari:** nomor kasus harus diperiksa sebelum mengunduh; keberhasilan unduh belum menjamin
   pipeline dapat mengolah data.
3. **Yang menghambat / rencana:** angka laporan perlu disinkronkan dengan `metrics.json`; rencananya
   ditambahkan pemeriksaan otomatis di Sprint 2.
