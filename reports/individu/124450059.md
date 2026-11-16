# Laporan Perorangan — Queenta Thifaal Nabila (124450059), Komponen Integrator — Ekstraksi dan Lineage

## 1. Komponen saya

Saya bertanggung jawab pada komponen Integrator, khususnya bagian ekstraksi dan lineage dalam pipeline Capstone Data Wrangling Kasus 03 — Kesehatan Reproduksi Remaja. Komponen ini berperan dalam menyiapkan data dari berbagai sumber, yaitu BPS, WHO GHO, dan WDI, serta menjaga keterlacakan data dari sumber mentah hingga tahap pengolahan berikutnya. Dengan adanya lineage, asal data dan proses pengambilan keputusan dapat ditelusuri kembali.

## 2. Keputusan wrangling

Keputusan utama yang digunakan adalah menetapkan susunan 38 provinsi Indonesia tahun 2025 sebagai referensi baku pemetaan wilayah dalam proses integrasi data. Keputusan ini dicatat pada log keputusan dengan ID K-002. Alternatif yang ditolak adalah menggunakan susunan 34 provinsi lama atau mencocokkan nama wilayah dari setiap sumber tanpa referensi baku.

Keputusan tersebut bertujuan menjaga konsistensi identitas wilayah antar sumber data. Perbedaan nama wilayah dan perubahan administratif perlu diperiksa sebelum dilakukan pemetaan agar tidak menghasilkan ketidaksesuaian identitas provinsi. Dampak terhadap jumlah baris belum dihitung karena aturan pemetaan belum diterapkan pada seluruh data.

## 3. Kegagalan dan pelajaran

Pada percobaan awal, saya menjalankan program unduh_data.py tanpa menyertakan argumen kasus sehingga program menghasilkan SystemExit: 2. Kesalahan tersebut terjadi karena program membutuhkan nomor kasus sebagai argumen untuk menentukan paket data yang akan diunduh.

Saya memperbaiki kesalahan dengan menjalankan perintah python unduh_data.py --kasus 3. Proses pengunduhan berhasil dan data mentah Kasus 03 tersedia pada folder data/raw/, yang mencakup sumber BPS, WHO GHO, dan WDI. Dari kejadian tersebut, saya belajar untuk memahami kebutuhan argumen program dan memeriksa hasil ekstraksi sebelum melanjutkan pengolahan data.

## 4. Bukti

Bukti pengerjaan berupa data mentah yang telah diunduh pada folder `data/raw/`, meliputi sumber BPS, WHO GHO, dan WDI, serta berkas `MANIFEST.csv` sebagai acuan pemeriksaan integritas data.


| Ukuran | Sebelum | Sesudah | Perintah |
|---|---|---|---|
| Ketersediaan data mentah | Belum diunduh | Data BPS, WHO GHO, dan WDI tersedia | `python unduh_data.py --kasus 3` |
| Pemeriksaan SHA256 | Belum dilakukan | Berhasil sesuai pesan keluaran program | `python unduh_data.py --kasus 3` |
| Jumlah baris Silver | Belum tersedia | Belum dihitung | `python -m src.common.skema` |
| Sel kosong Silver | Belum tersedia | Belum dihitung | Perintah pemeriksaan missing value pada pipeline |


## 5. Yang akan saya ubah jika ada satu sprint lagi

Jika terdapat satu sprint tambahan, saya akan meningkatkan pemeriksaan integritas dan keterlacakan data sejak tahap ekstraksi. Saya akan memastikan setiap sumber memiliki informasi asal, periode snapshot, dan identitas indikator yang terdokumentasi dengan baik. Selain itu, saya akan melakukan pemeriksaan konsistensi kode wilayah sebelum proses integrasi ke Silver. Saya juga akan memperkuat dokumentasi keputusan wrangling agar setiap perubahan dapat ditelusuri dan direproduksi oleh anggota tim lainnya.





