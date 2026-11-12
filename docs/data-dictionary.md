# Data Dictionary — Silver Layer
**Kelompok 3 | Kasus 03: Kesehatan Reproduksi Remaja Indonesia**
**Penulis:** Anash Tasya Ausyaqila (124450050)
**Terakhir diperbarui:** 2026-11-12

---

## Tentang Tabel Silver

Tabel Silver adalah hasil pengolahan data mentah yang sudah dibersihkan, distandarisasi, dan dilengkapi informasi asal-usul data (lineage). Data bersumber dari **BPS**, **WHO GHO**, dan **World Bank (WDI)**: seri provinsi BPS mencakup 2012–2017, sedangkan pembanding nasional WHO/WDI mencakup 1960–2025. Baris WDI 2025 yang kosong tidak masuk Silver.

**Lokasi file:** `data/silver/silver.parquet`

**Hasil pipeline:** 373 baris; 276 BPS (CSV dan JSON dipertahankan), 32 WHO, dan 65 WDI. Tidak ada nilai kosong atau duplikat pada kunci Silver.

**Perintah cek skema:**
```bash
python -m src.common.skema data/silver/silver.parquet
```

---

## Skema Kolom Silver

### Kolom Identitas Data

| Kolom | Tipe Data | Wajib Ada | Contoh Nilai | Keterangan |
|---|---|:---:|---|---|
| `sumber` | string |Ya| `BPS`, `WHO`, `WDI` | Lembaga atau organisasi asal data mentah |
| `seri_kode` | string |Ya| `var1394`, `SP.ADO.TFRT` | Kode unik indikator sesuai penamaan sumber aslinya |

### Kolom Wilayah

| Kolom | Tipe Data | Wajib Ada | Contoh Nilai | Keterangan |
|---|---|:---:|---|---|
| `wilayah_kode` | integer |Ya| `9999`, `1100`, `3200` | Kode numerik wilayah. `9999` = Indonesia (nasional). Provinsi = kode dua digit BPS × 100. Contoh: `1100` = Aceh, `3200` = Jawa Barat |
| `nama_wilayah` | string |Ya| `Indonesia`, `Aceh`, `Jawa Barat` | Nama wilayah dari snapshot; `9999` = Indonesia. Snapshot BPS memuat 34 provinsi historis sehingga belum ada baris provinsi hasil pemekaran 2025 |

### Kolom Waktu

| Kolom | Tipe Data | Wajib Ada | Contoh Nilai | Keterangan |
|---|---|:---:|---|---|
| `periode` | string |Ya| `2015`, `2020-Q3`, `2020-07` | Periode pengamatan. Format: `YYYY` (tahunan), `YYYY-S1`/`YYYY-S2` (semester), `YYYY-Q1`…`YYYY-Q4` (triwulan), `YYYY-MM` (bulanan) |
| `jenis_periode` | string |Ya| `tahun`, `triwulan`, `bulan` | Jenis granularitas waktu: `tahun`, `semester`, `triwulan`, atau `bulan` |

### Kolom Nilai

| Kolom | Tipe Data | Wajib Ada | Contoh Nilai | Keterangan |
|---|---|:---:|---|---|
| `rincian` | string |Ya| `15-19`, `Laki-laki`, `Total` | Rincian atau sub-kategori pengukuran. Misal: kelompok umur, jenis kelamin. Gunakan `Total` jika tidak ada rincian khusus |
| `nilai` | float |Ya| `48.5`, `12.3` | Angka hasil pengukuran indikator. Interpretasi bergantung pada `satuan` |
| `satuan` | string |Boleh kosong| `Persen`, `per 1000 kelahiran hidup` | Satuan pengukuran nilai. Dapat kosong apabila metadata sumber tidak mencantumkan satuan (kasus pada BPS var1353) |

### Kolom Lineage (Keterlacakan Data)

| Kolom | Tipe Data | Wajib Ada | Contoh Nilai | Keterangan |
|---|---|:---:|---|---|
| `_berkas_raw` | string |Ya| `bps/2026-10-20/sdg3_3_7_1_v1394.csv` | Path relatif berkas mentah sumber data, diisi otomatis oleh pipeline |
| `_sha256_raw` | string |Ya| `a3f2c1...` (64 karakter hex) | Checksum SHA-256 berkas mentah untuk verifikasi integritas data. Diambil dari `src.common.manifest.sha256_raw`, **tidak ditulis tangan** |

---

## Kunci Unik (Unique Key)

Setiap baris Silver diidentifikasi secara unik oleh kombinasi kolom berikut:

```
sumber + seri_kode + wilayah_kode + periode + rincian + _berkas_raw
```

Kombinasi ini tidak boleh duplikat di dalam tabel Silver.

---

## Sumber Data & Seri Indikator

| Sumber | Kode Seri | Nama Indikator | Cakupan Wilayah | Periode |
|---|---|---|---|---|
| BPS | `var1394` | SDG 3.7.1 — Angka kelahiran remaja (15–19 tahun) | 34 provinsi | 2012–2017 |
| BPS | `var1353` | SDG 3.7.2 — Prevalensi penggunaan kontrasepsi remaja | 34 provinsi | 2012–2017 |
| WHO GHO | `MDG_0000000003` | Angka kelahiran remaja (global) | Nasional (Indonesia) | Bervariasi |
| WHO GHO | `SDGFPALL` | Kebutuhan KB yang terpenuhi (semua metode) | Nasional (Indonesia) | Bervariasi |
| WDI | `SP.ADO.TFRT` | Angka fertilitas remaja (per 1.000 perempuan 15–19 tahun) | Nasional (Indonesia) | Bervariasi |

---

## Catatan Khusus Kasus 03

> [!NOTE]
> **Satuan BPS var1353 kosong:** Seluruh 69 baris data BPS var1353 memiliki kolom `satuan` yang tidak terisi di data mentah. Kolom `satuan` dipertahankan kosong dan tidak diisi dengan asumsi, karena memerlukan verifikasi metadata resmi dari sumber BPS. Keputusan ini tercatat di `log-keputusan.csv`.

> [!NOTE]
> **Kelompok umur WHO:** `DIM_AGE` dipertahankan di kolom `rincian` bersama `DIM_SEX`, sehingga `10-14`, `15-19`, dan `15-49` tidak digabung. Keputusan ini tercatat di `log-keputusan.csv` (ID: K-004).

> [!NOTE]
> **Nilai kosong WDI:** Baris WDI 2025 dengan nilai kosong tidak dimasukkan ke Silver karena Silver hanya memuat observasi yang memiliki nilai. Baris tersebut tetap tersedia di lapisan ekstraksi (ID: K-005).

> [!NOTE]
> **Pemetaan wilayah:** Provinsi pemekaran dipetakan mengikuti susunan 38 provinsi Indonesia tahun 2025. Aturan pemetaan dicatat di `log-keputusan.csv` (ID: K-002).

> [!NOTE]
> **Perbedaan definisi antar sumber:** Nilai indikator antara BPS (tingkat provinsi) dan WHO/WDI (nasional) tidak langsung dibandingkan karena perbedaan definisi, metode penghitungan, dan cakupan pengukuran.

---

## Riwayat Perubahan

| Tanggal | Perubahan | Oleh |
|---|---|---|
| 2026-11-11 | Pembuatan awal data dictionary | Anash Tasya Ausyaqila (124450050) |
| 2026-11-12 | Menambahkan hasil pipeline Silver dan keputusan WHO/WDI | Queenta Thifaal Nabila (124450059) |
