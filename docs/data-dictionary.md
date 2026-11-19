# Data Dictionary — Silver Layer
**Kelompok 3 | Kasus 03: Kesehatan Reproduksi Remaja Indonesia**  
**Penulis:** Anash Tasya Ausyaqila (124450050)  
**Terakhir diperbarui:** 2026-11-19  

---

## Tentang Tabel Silver

Tabel Silver adalah hasil standardisasi data mentah dari tiga sumber (BPS, WHO GHO, dan WDI) yang mencakup indikator kesehatan reproduksi remaja periode 2012–2017. Seluruh baris data memiliki atribut keterlacakan (*lineage*) langsung ke berkas mentah asalnya.

- **Lokasi berkas:** `data/silver/silver.parquet`
- **Total baris:** 235 baris
- **Total seri:** 5 seri indikator
- **Total wilayah:** 35 wilayah (34 provinsi + Nasional 9999)

---

## Kamus Kolom Data Silver

| Nama Kolom | Tipe Data | Satuan / Format | Wajib | Contoh Nilai | Keterangan & Aturan Nilai |
|---|---|---|:---:|---|---|
| `sumber` | string | Kategori (`BPS`, `WHO`, `WDI`) | Ya | `BPS` | Lembaga resmi penerbit data mentah. |
| `seri_kode` | string | Kode teks | Ya | `var1394` | Kode unik indikator dari sumber aslinya. |
| `wilayah_kode` | integer | Kode numerik BPS | Ya | `1100` | Kode wilayah 4 digit. `9999` = Indonesia (Nasional), provinsi = 2 digit kode BPS × 100 (contoh: `1100` = Aceh). |
| `nama_wilayah` | string | Nama baku | Ya | `Aceh` | Nama provinsi atau negara mengacu pada susunan 38 provinsi tahun 2025. |
| `periode` | string | Waktu (`YYYY`, `YYYY-SX`, `YYYY-QX`, `YYYY-MM`) | Ya | `2015` | Periode pengamatan indikator. |
| `jenis_periode` | string | Kategori waktu | Ya | `tahun` | Granularitas waktu (`tahun`, `semester`, `triwulan`, `bulan`). |
| `rincian` | string | Kategori rincian | Ya | `Total` | Rincian kategori data (kelompok umur, jenis kelamin, atau `Total`). |
| `nilai` | float | Angka riil | Ya | `48.5` | Angka hasil pengukuran indikator. Interpretasi makna nilai merujuk pada kolom `satuan`. |
| `satuan` | string | Satuan ukur | Tidak | `Persen` | Satuan nilai indikator (contoh: `Persen`, `per 1000 wanita 15-19 tahun`). Boleh kosong khusus untuk BPS `var1353`. |
| `_berkas_raw` | string | Jalur file (path) | Ya | `bps/2026-10-20/sdg3_3_7_1_v1394.csv` | Lokasi relatif berkas sumber mentah di dalam `data/raw/`. |
| `_sha256_raw` | string | 64 karakter heksadesimal | Ya | `a3f2c1...` (64 hex) | Checksum SHA-256 berkas mentah untuk verifikasi integritas data. |

---

## Contoh Penelusuran 1 Baris ke Berkas Mentah (Step-by-Step Lineage Trace)

Berikut adalah contoh konkret bagaimana satu baris data pada tabel Silver ditelusuri kembali secara utuh ke berkas mentahnya di `data/raw/`:

### 1. Data Baris pada Lapisan Silver (`data/silver/silver.parquet`):
```text
sumber        : BPS
seri_kode     : var1394
wilayah_kode  : 1100
nama_wilayah  : Aceh
periode       : 2015
jenis_periode : tahun
rincian       : Total
nilai         : 48.5
satuan        : Persen
_berkas_raw   : bps/2026-10-20/sdg3_3_7_1_v1394.csv
_sha256_raw   : f3b6e8a4d1c2... (64 hex)
```

### 2. Langkah-Langkah Penelusuran ke Berkas Mentah:

1. **Langkah 1 (Cek Jalur Berkas Mentah):**  
   Dari kolom `_berkas_raw`, sistem merujuk langsung ke berkas mentah:  
   `data/raw/bps/2026-10-20/sdg3_3_7_1_v1394.csv`.

2. **Langkah 2 (Verifikasi Integritas SHA-256):**  
   Integritas berkas mentah diverifikasi dengan menghitung hash SHA-256 berkas tersebut dan mencocokkannya dengan `_sha256_raw` serta daftar resmi pada `data/raw/MANIFEST.csv`.  
   Perintah verifikasi:
   ```bash
   python -c "import hashlib; print(hashlib.sha256(open('data/raw/bps/2026-10-20/sdg3_3_7_1_v1394.csv','rb').read()).hexdigest())"
   ```

3. **Langkah 3 (Pencocokan Baris Observasi):**  
   Buka berkas mentah `data/raw/bps/2026-10-20/sdg3_3_7_1_v1394.csv`. Cari baris dengan parameter:
   - Nama Provinsi: `Aceh` (kode wilayah `1100`)
   - Tahun: `2015`
   - Ditemukan nilai mentah sebesar `48.5` dengan satuan `Persen`.

4. **Langkah 4 (Hasil Pembuktian):**  
   Nilai observasi pada lapisan Silver terbukti identik dan terlacak penuh dari data mentah aslinya tanpa ada manipulasi yang tidak tercatat.

---

## Kunci Unik (Unique Key)

Setiap baris pada tabel Silver diidentifikasi secara unik melalui kombinasi kolom:
`sumber` + `seri_kode` + `wilayah_kode` + `periode` + `rincian` + `_berkas_raw`.
