# Draf Persiapan Sprint 1 — Tahap 6 (124450055)
**Kasus 03: Kesehatan Reproduksi Remaja.** Implementasi & perhitungan rekonsiliasi penuh: **Sprint 2**. Dokumen ini menyiapkan rancangan, pasangan, dan catatan keterbandingan berbasis data mentah aktual (snapshot 17–20 Okt 2026).

## 1. Sumber data nasional (baris Indonesia) yang teridentifikasi
| Sumber | Seri | Berkas | Wilayah nasional | Periode tersedia (IDN/9999) | Kelompok umur | Populasi/status | Satuan (metadata/isi) | Nilai (nasional) |
|---|---|---|---|---|---|---|---|---|
| BPS | var1353 (SDG 3.7.2) | `bps/.../sdg3_3_7_2_v1353.csv` (juga JSON) | `wilayah_id=9999`, INDONESIA | 2012, 2017 | 15–19 tahun (label) | Perempuan usia 15–19 (ASFR remaja, SDKI) | *tidak terisi di CSV*; metadata: "Angka Kelahiran Pada Perempuan Usia 15-19 Tahun…" (umumnya per 1.000 perempuan 15–19, perlu penetapan & catat) | 2012=48, 2017=36 |
| BPS | var1394 (SDG 3.7.1) | `bps/.../sdg3_3_7_1_v1394.csv` | 9999, INDONESIA | 2012, 2017 | 15–49 tahun (label) | Perempuan usia reproduksi (15–49) atau pasangannya, kebutuhan KB terpenuhi metode modern (mCPR demand satisfied, SDKI) | Persen | 2012=57.9, 2017=57.2 |
| WHO GHO | MDG_0000000003 (SDG 3.7.2) | `who_gho/.../27D371A_MDG_0000000003.csv` | GEO M49 360, Indonesia | Y10T14: 2002–2008,2010,2011,2013,2015,2016; Y15T19: 2001–2011,2013,2015,2016 | Y10T14 dan Y15T19 (DIM_AGE) | Female (adolescent birth rate) | `RATE_PER_1000_N` (per 1.000) | Y15T19: 2015=39.92008591, 2016=36.10983276 (2012 & 2017 **tidak ada**) |
| WHO GHO | SDGFPALL (SDG 3.7.1) | `who_gho/.../8074BD9_SDGFPALL.csv` | M49 360, Indonesia | 2002,2007,2012,2015,2016,2017 | Y15T49 | Female, family planning satisfied with modern methods | `RATE_PER_100_N` (persen) | 2012=79.0, 2017=77.0 |
| WDI | SP.ADO.TFRT | `wdi/.../data/kelompok-07-hal-01.json` (indikator di metadata sumber46) | country `ID` (Indonesia) | 1960–2024 (nilai ada) | 15–19 tahun (definisi: births per 1,000 women ages 15-19) | Perempuan 15–19 (fertilitas remaja) | per 1.000 perempuan 15–19 | 2012=44.616, 2017=32.792 |

**Catatan ketersediaan:** BPS utama hanya 2012 & 2017 (batas panel). WHO MDG_0000000003 tidak memuat 2012 dan 2017 untuk Y15T19 pada snapshot ini; WDI memuat 2012 & 2017.

## 2. Rancangan tabel nasional `periode × seri` (target Sprint 2, disiapkan sekarang)
- Lokasi keluaran aktual (persiapan): `data/gold/nasional_periode_seri.parquet` (101 baris nasional, 5 seri, subset Silver `wilayah_kode==9999`) + skrip pembentuk di `src/gold/`.
- Rancangan kolom (satu baris = satu periode × satu seri × satu rincian nasional): `sumber, seri_kode, indikator_nama, wilayah_kode (9999), nama_wilayah, periode, jenis_periode, kelompok_umur, populasi, satuan, nilai, catatan_keterbandingan, _berkas_raw, _sha256_raw`.
- Sumber baris: hanya observasi nasional (BPS 9999; WHO M49 360; WDI country ID) dari ekstraksi terverifikasi; tidak mengisi nilai yang tidak tersedia.

## 3. Daftar pasangan rekonsiliasi & catatan keterbandingan
### Pasangan 1 (SDG 3.7.2, kelahiran remaja)
- **Anggota:** `var1353` (BPS, Indonesia 9999) vs `MDG_0000000003` (WHO GHO, rincian umur sesuai) vs `SP.ADO.TFRT` (WDI).
- **Definisi & populasi:** var1353 = ASFR perempuan 15–19 (SDKI). WHO MDG_0000000003 = adolescent birth rate, female, tersedia Y10T14 & **Y15T19**. WDI SP.ADO.TFRT = births per 1,000 women ages 15–19.
- **Kelompok umur:** rincian WHO yang sesuai untuk perbandingan dengan var1353/WDI adalah **Y15T19** (bukan Y10T14). Ketiganya menarget usia 15–19 → syarat kesamaan kelompok umur **terpenuhi secara definisi** pada rincian Y15T19.
- **Satuan:** WDI & WHO Y15T19 per 1.000 perempuan 15–19; var1353 di CSV kosong satuannya (metadata implisit per 1.000) → **harus ditetapkan & dicatat** sebelum hitung selisih.
- **Periode beririsan (aktual, snapshot):** var1353 {2012,2017} ∩ MDG Y15T19 {…,2013,2015,2016} ∩ WDI {1960–2024} = **∅ (tidak ada tahun irisan 3-seri)**. Irisan berpasangan: var1353∩WDI = {2012,2017}; var1353∩MDG Y15T19 = ∅; MDG Y15T19∩WDI banyak (2001–2016 kecuali gap).
- **Status keterbandingan:** **Tidak dapat dibandingkan langsung (3-seri, tahun sama)** karena tidak ada periode irisan bersama dan sumber/metode/vintage berbeda (SDKI vs estimasi WHO/UN WPP). Dapat disajikan sebagai **pembanding kontekstual** berpasangan/deret waktu dengan selisih dijelaskan (bukan dihapus) — perhitungan selisih hanya bila definisi/umur/populasi/satuan terbukti sebanding dan periode sama; **selisih 3-seri ditunda/tidak dihitung**.

### Pasangan 2 (SDG 3.7.1, KB modern)
- **Anggota:** `var1394` (BPS, Indonesia 9999) vs `SDGFPALL` (WHO GHO).
- **Definisi:** var1394 = proporsi perempuan usia reproduksi (15–49) atau pasangannya dengan kebutuhan KB terpenuhi metode modern (SDKI). SDGFPALL = family planning satisfied with modern methods (WHO/UN).
- **Kelompok umur & status perkawinan/populasi:** keduanya **15–49 tahun, female**; konsep “kebutuhan terpenuhi metode modern (demand satisfied, modern)” selaras, namun denominasi/populasi rujukan dapat berbeda (mis. perempuan menikah/bersatu vs all women in need, tergantung estimasi) → **perlu verifikasi definisi operasional & status perkawinan** di metadata sebelum selisih numerik.
- **Satuan:** persen (keduanya).
- **Periode beririsan (aktual):** var1394 {2012,2017} ∩ SDGFPALL {2002,2007,2012,2015,2016,2017} = **{2012, 2017}** (2 periode).
- **Status keterbandingan:** **Berpotensi sebanding secara indikator & periode** (2012,2017) namun **pembanding kontekstual hingga verifikasi populasi/definisi operasional** selesai; selisih dapat dihitung di Sprint 2 dengan anotasi metodologi (nilai contoh: 2012 57.9 vs 79.0; 2017 57.2 vs 77.0 — selisih besar, indikasi perbedaan definisi/denominasi, bukan untuk dihapus).

## 4. Artefak persiapan & kebutuhan belum tersedia
- Dokumen: `reports/sprint1/persiapan_tahap6.md` (ini), draf tahapan & perbandingan: `reports/sprint1/tahap5_sql_dan_json.md`.
- Rancangan lokasi penyimpanan (akan diisi Sprint 2): `data/gold/nasional_periode_seri.*`, tabel rekonsiliasi/selisih di `src/gold/` & SQL Gold.
- **Belum tersedia / prasyarat Sprint 2:** Silver/ekstraksi tim (tahap 1–4), konfirmasi satuan resmi var1353, verifikasi denominasi-status perkawinan SDGFPALL vs var1394, keputusan pemetaan rincian & grid periode×seri final, dan perhitungan selisih terdokumentasi di log keputusan.
