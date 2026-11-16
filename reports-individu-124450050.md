# Laporan perorangan — <Anash Tasya Ausyaqila> (<124450050>), komponen <Validasi dan Dokumentasi>

Salin berkas ini menjadi `reports/individu/<nim>.md`. Paling banyak 1200 kata di luar tabel
dan kode. Setiap klaim angka harus dapat ditelusuri ke kode atau keluaran yang sudah di-*commit*.

1. Komponen saya

Saya bertanggung jawab pada komponen Validasi dan Dokumentasi dalam pipeline pengolahan data SDG 3.7 tentang kesehatan reproduksi remaja. Tugas saya berfokus pada pemeriksaan kualitas data, pengecekan kelengkapan nilai, validasi konsistensi struktur data, serta dokumentasi sumber data dan checksum SHA-256 agar setiap data yang digunakan dapat ditelusuri kembali ke file mentahnya. Komponen ini bertujuan memastikan data yang masuk ke tahap Silver dan Gold memiliki kualitas serta asal-usul yang jelas.

2. Keputusan wrangling

Keputusan utama yang saya ambil adalah mempertahankan nilai satuan yang kosong pada data mentah dan tidak langsung menggantinya dengan nilai perkiraan. Berdasarkan pemeriksaan file sdg3_3_7_2_v1353.csv, ditemukan bahwa kolom satuan kosong pada seluruh 69 baris data. Sementara itu, file sdg3_3_7_1_v1394.csv memiliki satuan Persen.

Alternatif yang tidak digunakan adalah mengisi satuan secara langsung tanpa memeriksa metadata sumber. Cara tersebut berisiko menghasilkan informasi yang tidak sesuai dengan definisi indikator. Oleh karena itu, satuan perlu diverifikasi melalui metadata sebelum ditetapkan pada tabel Silver.

Dampaknya, jumlah baris data mentah tetap dipertahankan sebanyak 69 baris pada masing-masing indikator. Tidak dilakukan penghapusan baris hanya karena informasi satuannya belum tersedia. Keputusan ini perlu dicatat dalam log keputusan agar proses pengolahan dapat dipertanggungjawabkan.

Referensi log: Belum terdapat ID log keputusan yang secara jelas mencatat keputusan pribadi saya untuk indikator var1353. ID K-001 yang tersedia membahas seri var543, sehingga tidak digunakan sebagai referensi keputusan ini.

3. Kegagalan dan pelajaran

Salah satu masalah nyata yang ditemukan selama proses validasi adalah ketidaklengkapan metadata satuan pada indikator BPS var1353. Ketika data diperiksa, seluruh 69 baris memiliki nilai pada kolom nilai, tetapi kolom satuan tidak terisi.

Jika data tersebut langsung digunakan tanpa pemeriksaan, pengguna dapat salah memahami arti angka yang disajikan. Pelajaran yang saya dapatkan adalah bahwa validasi tidak cukup hanya memeriksa apakah kolom dan baris tersedia, tetapi juga harus memastikan metadata setiap indikator sesuai dengan definisi dari sumber aslinya.

Perubahan yang perlu dilakukan adalah menambahkan pemeriksaan otomatis terhadap nilai kosong, memeriksa metadata indikator, serta mencatat hasil validasi sebelum data dimasukkan ke tahap berikutnya.

4. Bukti

Hasil pemeriksaan terhadap dua file CSV BPS menunjukkan:

Ukuran

Sebelum

Sesudah pemeriksaan

Perintah

Baris var1394

69

69

len(df)

Baris var1353

69

69

len(df)

Sel kosong var1394

0

0

df.isna().sum().sum()

Sel kosong var1353

69

69

df.isna().sum().sum()

Satuan kosong var1353

69

69

df['satuan'].isna().sum()

SHA-256 sesuai manifest

13 file diperiksa

13 file cocok

hashlib.sha256()

Keterangan: pemeriksaan tidak mengubah file mentah. Nilai sebelum dan sesudah menunjukkan bahwa data tetap dipertahankan, sementara masalah kualitasnya dicatat untuk ditindaklanjuti.

Perintah untuk menghasilkan pemeriksaan ulang:

import pandas as pd
import hashlib

file1 = "data/raw/bps/2026-10-20/sdg3_3_7_1_v1394.csv"
file2 = "data/raw/bps/2026-10-20/sdg3_3_7_2_v1353.csv"

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

print("Jumlah baris var1394:", len(df1))
print("Jumlah sel kosong var1394:", df1.isna().sum().sum())

print("Jumlah baris var1353:", len(df2))
print("Jumlah sel kosong var1353:", df2.isna().sum().sum())
print("Satuan kosong var1353:", df2["satuan"].isna().sum())

with open(file1, "rb") as f:
    print("SHA256 var1394:", hashlib.sha256(f.read()).hexdigest())

with open(file2, "rb") as f:
    print("SHA256 var1353:", hashlib.sha256(f.read()).hexdigest())

Pemeriksaan checksum seluruh file mentah juga dilakukan dengan membandingkan hasil SHA-256 terhadap data/raw/MANIFEST.csv. Hasil pemeriksaan menunjukkan 13 dari 13 file memiliki checksum yang sesuai dengan manifest.

5. Yang akan saya ubah jika ada satu sprint lagi

Jika diberikan satu sprint tambahan, saya akan meningkatkan proses validasi dengan membuat pemeriksaan otomatis menggunakan Python agar kesalahan data dapat diketahui lebih awal. Saya juga akan menambahkan dokumentasi data dictionary yang menjelaskan nama indikator, satuan, periode, sumber, dan definisi setiap kolom. Selain itu, saya akan memastikan setiap perubahan data memiliki ID keputusan yang tercatat dalam log-keputusan.csv. Saya juga akan mengembangkan pengujian otomatis untuk mendeteksi nilai kosong, duplikasi, ketidaksesuaian tipe data, dan kesalahan checksum. Dengan demikian, hasil pengolahan data akan lebih konsisten, transparan, dan mudah direproduksi oleh seluruh anggota tim.