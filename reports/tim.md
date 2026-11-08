# Laporan Tim — Kelompok 3, Kasus 03 Kesehatan Reproduksi Remaja

## Ringkasan

Kelompok 3 mengerjakan Capstone Data Wrangling dengan Kasus 03 — Kesehatan Reproduksi Remaja yang berfokus pada indikator kesehatan reproduksi remaja di Indonesia. Seri utama yang digunakan berasal dari BPS var1394 dan var1353 periode 2012–2017, sedangkan pembanding nasional berasal dari WHO GHO dan World Development Indicators (WDI). Fokus pengerjaan adalah membangun pipeline yang dapat direproduksi dari data mentah hingga Silver dan Gold, serta melakukan rekonsiliasi seri provinsi dengan pembanding nasional. Temuan awal menunjukkan bahwa perbedaan satuan, kelompok umur, periode, dan cakupan wilayah perlu diperhatikan agar integrasi data tidak menghasilkan interpretasi yang keliru.

## Data dan Lineage

Data yang digunakan berasal dari tiga sumber utama, yaitu BPS, WHO GHO, dan WDI. Data mentah diperoleh melalui program `unduh_data.py` dengan argumen `--kasus 3`. Paket data yang diunduh mencakup snapshot 17–20 Oktober 2026 dan disimpan pada folder `data/raw/`.

Berkas mentah dipertahankan sebagai sumber awal pengolahan. Atribut `_berkas_raw` digunakan untuk mencatat asal berkas data, sedangkan `_sha256_raw` digunakan untuk menyimpan checksum SHA256 agar integritas dan keterlacakan data dapat diperiksa.

Jumlah berkas mentah, format setiap sumber, serta hasil tarik ulang API akan didokumentasikan berdasarkan pemeriksaan aktual pada repository tim. Perubahan sejak snapshot awal akan dibandingkan apabila proses tarik ulang API dilakukan.

## Masalah Data dan Penanganannya

| Masalah | Jumlah Baris Terdampak | Keputusan | Alternatif Ditolak | ID Log |
|---|---:|---|---|---|
| Perbedaan periode data | 0 | Periode Februari dan Agustus disimpan sebagai `jenis_periode=bulan` | Mengagregasikan langsung menjadi tahunan | K-001 |
| Perbedaan referensi wilayah | 16 | Menggunakan susunan 38 provinsi Indonesia tahun 2025 sebagai referensi pemetaan | Menggunakan nama wilayah tanpa referensi baku | K-002 |
| Satuan indikator tidak lengkap | 69 | Menentukan satuan berdasarkan metadata sumber | Mengasumsikan satuan dari nilai data | Perlu dicatat |
| Missing value | 16 | Memeriksa penyebab missing sebelum menentukan penanganan | Menghapus seluruh baris yang memiliki nilai kosong | Perlu dicatat |
| Perbedaan kelompok umur | 26 | Memisahkan kelompok umur sesuai definisi indikator | Menggabungkan seluruh kelompok umur | Perlu dicatat |
| Patahan seri | 0 | Memeriksa definisi dan cakupan indikator antarperiode | Menganggap seluruh periode memiliki definisi identik | Perlu dicatat |


## Integrasi dan Rekonsiliasi

Integrasi dilakukan dengan menggunakan seri utama BPS var1394 dan var1353 sebagai indikator tingkat provinsi. Pembanding nasional menggunakan WHO GHO MDG_0000000003, WHO GHO SDGFPALL, dan WDI SP.ADO.TFRT.

Rekonsiliasi dilakukan dengan memperhatikan perbedaan definisi indikator, metode penghitungan, vintage data, granularitas, dan periode pengamatan. Perbedaan nilai antara seri utama dan pembanding nasional tidak langsung dianggap sebagai kesalahan karena dapat disebabkan oleh perbedaan definisi dan cakupan pengukuran.

Analisis revisi dari arsip WDI dilakukan dengan membandingkan nilai indikator pada beberapa vintage rilis. Besaran selisih, perubahan nilai, dan hasil analisis revisi akan dilengkapi berdasarkan keluaran tabel Gold dan arsip WDI yang telah diproses.

## Validasi dan Reproduksibilitas

Validasi dilakukan terhadap data Silver menggunakan modul skema yang tersedia pada repository. Pemeriksaan mencakup kesesuaian tipe data, kelengkapan atribut, konsistensi identitas wilayah, serta validitas periode dan indikator.

Pipeline dirancang agar dapat menghasilkan ulang data Silver, Gold, dan tabel rekonsiliasi dari data mentah. Perintah utama yang digunakan adalah:

```bash
python unduh_data.py --kasus 3
```

Hasil validasi, jumlah aturan yang lolos dan gagal, waktu eksekusi pipeline dari kondisi awal, serta perbandingan pandas dengan DuckDB/Dask akan dilengkapi berdasarkan hasil pengujian aktual. Keterbatasan yang masih diperhatikan adalah rentang periode seri provinsi yang berhenti pada 2017 serta kemungkinan perbedaan definisi indikator antar sumber.

## Pembagian Kerja

| Anggota | NIM | Komponen | Tugas Sampingan | Bagian Laporan yang Ditulis |
|---|---|---|---|---|
| Anash Tasya Ausyaqila | 124450050 | Reproduksi dan Demo — Validasi dan Dokumentasi | Pemeriksaan hasil pipeline dan dokumentasi | Validasi dan Reproduksibilitas |
| Indah Julia Mawar Pratiwi | 124450055 | Koordinator — Integrasi, Penyimpanan, dan Skala | Koordinasi repository dan integrasi tim | Integrasi dan Rekonsiliasi |
| Queenta Thifaal Nabila | 124450059 | Integrator — Ekstraksi dan Lineage | Ekstraksi data, pemeriksaan manifest, dokumentasi lineage | Data dan Lineage |
| Hazel Mahesa Handhaka | 124450114 | Anggota | Mendukung pengerjaan pipeline sesuai pembagian tim | Sesuai tugas yang disepakati |
| Risa Romadona | 124450127 | Analis Utama — Profil dan Pembersihan | Analisis kualitas data dan pembersihan | Masalah Data dan Penanganannya | Pembagian kerja ini disesuaikan dengan peran anggota yang tercantum pada papan Capstone tim. NIM anggota lain dan bagian laporan final perlu dilengkapi berdasarkan kesepakatan kelompok.