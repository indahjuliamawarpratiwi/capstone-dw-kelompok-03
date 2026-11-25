# Tabel nasional dan pasangan rekonsiliasi

Dihasilkan `python pipeline.py` (`src/gold/nasional.py`) dari tabel nasional Gold dan `src/konfigurasi.py`. Selisih dihitung di Tahap 6 Sprint 2 dan tidak dihapus atau dipaksa sama.

Tabel nasional (periode x seri, rincian total, tampilan lebar): `reports/tabel-nasional.csv`. Tabel nasional lengkap dari hasil ekstraksi (semua rincian, satu baris per periode x seri): `data/gold/nasional_periode_seri.parquet`. Kolom BPS hanya terisi pada tahun survei; itu bentuk datanya, tidak diisi.

Untuk SDG 3.7.2, perbandingan tiga seri memakai `var1353` (BPS, cakupan 15–19, rincian mentah `Tidak ada`), `MDG_0000000003` rincian `Y15T19` (bukan `Y10T14`), dan `SP.ADO.TFRT` (WDI, 15–19 dari nama indikator). Ketiganya menarget perempuan 15–19 dan satuan per 1.000, jadi kelompok umur disamakan lebih dulu sebelum selisih dihitung. Tidak ada tahun yang beririsan untuk ketiganya, jadi selisih tiga seri tidak dihitung dan perbandingan dilakukan berpasangan (P1, P2, P4). Untuk SDG 3.7.1, `var1394` (rincian `Tidak ada`, 15–49 dari judul) dan `SDGFPALL` (`DIM_AGE=Y15T49`, `DIM_SEX=FEMALE`) sama-sama perempuan 15–49, tetapi status perkawinan dan penyebutnya tidak dinyatakan identik; keduanya tidak membatasi pada perempuan menikah saja, dan Limitations WHO mencatat perbedaan base populasi antarsurvei.

## Pasangan dari panduan kelompok bagian 3

| pasangan | rincian_dipakai | kelompok_umur | status_perkawinan_populasi | periode_beririsan_berpasangan | dapat_dibandingkan_langsung | alasan_keterbandingan |
|---|---|---|---|---|---|---|
| var1353 vs MDG_0000000003(Y15T19) vs SP.ADO.TFRT | var1353: turvar='Tidak ada' (umur 15-19 ada di judul); MDG_0000000003: DIM_AGE=Y15T19 (bukan Y10T14), DIM_SEX=FEMALE; SP.ADO.TFRT: age=15-19 dari nama indikator | 15-19 pada ketiga seri | perempuan 15-19; var1353 dari SDKI, WHO dari survei/registrasi, WDI dari estimasi UN WPP; tidak ada syarat status perkawinan di definisi | var1353∩SP.ADO.TFRT={2012,2017}; var1353∩MDG Y15T19=∅; MDG Y15T19∩SP.ADO.TFRT={2001-2011,2013,2015,2016} | tidak untuk 3 seri (tahun bersama kosong) | Kelompok umur 15-19 dan satuan per 1,000 sama pada ketiga seri; yang berbeda hanya metode/vintage (SDKI, WHO, WPP) dan tahun amatan |
| var1394 vs SDGFPALL | var1394: turvar='Tidak ada' (15-49 dan 'atau pasangannya' dari judul); SDGFPALL: DIM_AGE=Y15T49 (konstan di berkas), DIM_SEX=FEMALE | 15-49 pada kedua seri | keduanya perempuan 15-49, tidak dibatasi hanya yang menikah/bersatu; WHO menghitung pasangan yang memakai metode modern di numerator, denominator seluruh permintaan KB; Limitations WHO mencatat perbedaan status perkawinan/base populasi antarsurvei | 2012;2017 | berpotensi, bersyarat pada verifikasi penyebut/status perkawinan | Umur 15-49, satuan persen, dan konsep kebutuhan KB terpenuhi dengan metode modern sama; penyebut WHO = pemakai semua metode + kebutuhan tak terpenuhi, sedangkan judul var1394 tidak menyebut penyebutnya |

## Ringkasan pasangan

| id | seri_utama | pembanding | jenis | periode_beririsan | tahun | dugaan_kategori |
|---|---|---|---|---|---|---|
| P1 | var1353 | SP.ADO.TFRT [total] | selisih | 2 | 2012, 2017 | metode (survei dengan periode rujukan vs estimasi model penduduk tahunan) |
| P2 | var1353 | MDG_0000000003 [umur=15-19] | selisih | 0 | — | tidak ada tahun beririsan; dibandingkan dengan tahun terdekat di Gold (Sprint 2) dengan penanda |
| P3 | var1394 | SDGFPALL [total] | selisih | 2 | 2012, 2017 | definisi (penyebut berbeda: BPS lebih dekat ke prevalensi kontrasepsi modern) |
| P4 | MDG_0000000003 | SP.ADO.TFRT [total] | selisih | 14 | 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2013, 2015, 2016 | sumber berbeda (WHO: data survei/registrasi yang dihimpun; WDI: model WPP) |

## Tabel rekonsiliasi Tahap 6

Setiap baris berpasangan memuat periode, nilai kedua seri, selisih, dan kategori penjelasan. Periode tanpa pasangan tetap tampil dengan nilai kosong dan kategori `belum terjelasan` lengkap dengan dugaan serta bukti.

| pasangan | utama | pembanding | kategori | baris_berpasangan | baris_tanpa_pasangan | selisih_median |
|---|---|---|---|---|---|---|
| R1 | var1353 [Tidak ada] | MDG_0000000003 [Y15T19] | belum terjelaskan | 0 | 16 |  |
| R2 | var1353 [Tidak ada] | SP.ADO.TFRT [Y15T19] | metode berbeda | 2 | 63 | 3.30 |
| R3 | MDG_0000000003 [Y15T19] | SP.ADO.TFRT [Y15T19] | vintage berbeda | 14 | 51 | 1.94 |
| R4 | var1394 [Tidak ada] | SDGFPALL [Y15T49] | definisi berbeda | 2 | 4 | -20.45 |

### Baris berpasangan

| pasangan | seri_utama | pembanding | periode | nilai_utama | nilai_pembanding | selisih | kategori | dugaan | bukti |
|---|---|---|---|---|---|---|---|---|---|
| R2 | var1353 | SP.ADO.TFRT | 2012 | 48.00 | 44.62 | 3.38 | metode berbeda | Survei SDKI dengan periode rujukan tertentu vs estimasi model WPP tahunan. | var.note BPS menyebut SDKI; WDI sourceOrganization = World Population Prospects, UN Population Division. |
| R2 | var1353 | SP.ADO.TFRT | 2017 | 36.00 | 32.79 | 3.21 | metode berbeda | Survei SDKI dengan periode rujukan tertentu vs estimasi model WPP tahunan. | var.note BPS menyebut SDKI; WDI sourceOrganization = World Population Prospects, UN Population Division. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2001 | 50.93 | 53.02 | -2.08 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2002 | 53.12 | 51.76 | 1.36 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2003 | 55.92 | 50.41 | 5.51 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2004 | 51.00 | 48.21 | 2.79 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2005 | 52.28 | 48.10 | 4.19 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2006 | 50.95 | 47.77 | 3.19 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2007 | 49.48 | 47.67 | 1.82 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2008 | 46.88 | 46.29 | 0.59 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2009 | 47.00 | 45.59 | 1.41 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2010 | 46.86 | 45.68 | 1.18 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2011 | 48.49 | 45.59 | 2.90 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2013 | 47.37 | 42.67 | 4.69 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2015 | 39.92 | 37.86 | 2.06 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R3 | MDG_0000000003 | SP.ADO.TFRT | 2016 | 36.11 | 35.36 | 0.75 | vintage berbeda | WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP. | WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP. |
| R4 | var1394 | SDGFPALL | 2012 | 57.90 | 79.00 | -21.10 | definisi berbeda | Penyebut berbeda: BPS lebih dekat ke prevalensi kontrasepsi modern; WHO memakai permintaan KB total. | WHO Denominator = pemakai semua metode + kebutuhan tak terpenuhi; Limitations WHO mencatat perbedaan base/status perkawinan. |
| R4 | var1394 | SDGFPALL | 2017 | 57.20 | 77.00 | -19.80 | definisi berbeda | Penyebut berbeda: BPS lebih dekat ke prevalensi kontrasepsi modern; WHO memakai permintaan KB total. | WHO Denominator = pemakai semua metode + kebutuhan tak terpenuhi; Limitations WHO mencatat perbedaan base/status perkawinan. |

### Periode tanpa pasangan

134 baris tersimpan di `data/gold/rekonsiliasi.csv` tanpa selisih.

| pasangan | baris |
|---|---|
| R1 | 16 |
| R2 | 63 |
| R3 | 51 |
| R4 | 4 |

## Rincian alasan pasangan lama

### P1: Angka kelahiran remaja 15–19: BPS (SDKI) vs WDI (model WPP)
- Seri utama: `var1353` (rincian `total`)
- Pembanding: `SP.ADO.TFRT` (rincian `total`)
- Jenis: **selisih**; tahun beririsan: 2012, 2017
- Dugaan kategori selisih (diuji di Sprint 2): metode (survei dengan periode rujukan vs estimasi model penduduk tahunan)

Pertanyaan keterbandingan dan jawabannya:

1. **Kelompok umur BPS?** 15–19 saja: var.label 'Angka Kelahiran Pada Perempuan Usia 15-19 Tahun'.
2. **Dari mana angka WDI?** sourceOrganization: World Population Prospects, UN Population Division (model).

### P2: Angka kelahiran remaja 15–19: BPS vs WHO
- Seri utama: `var1353` (rincian `total`)
- Pembanding: `MDG_0000000003` (rincian `umur=15-19`)
- Jenis: **selisih**; tahun beririsan: —
- Dugaan kategori selisih (diuji di Sprint 2): tidak ada tahun beririsan; dibandingkan dengan tahun terdekat di Gold (Sprint 2) dengan penanda

Pertanyaan keterbandingan dan jawabannya:

1. **Rincian WHO mana?** umur=15-19 (DIM_AGE Y15T19). Baris 10–14 punya penyebut perempuan 10–14.
2. **Tahun mana yang sama?** Tidak ada: WHO punya 2011, 2013, 2015, 2016, tetapi tidak 2012 dan 2017.

### P3: KB metode modern: BPS vs WHO kebutuhan KB terpenuhi
- Seri utama: `var1394` (rincian `total`)
- Pembanding: `SDGFPALL` (rincian `total`)
- Jenis: **selisih**; tahun beririsan: 2012, 2017
- Dugaan kategori selisih (diuji di Sprint 2): definisi (penyebut berbeda: BPS lebih dekat ke prevalensi kontrasepsi modern)

Pertanyaan keterbandingan dan jawabannya:

1. **Apa penyebut WHO?** Permintaan KB total = pemakai semua metode + kebutuhan tak terpenuhi (Denominator).
2. **Apakah judul BPS menyebut penyebutnya?** Tidak tegas; status perkawinan juga tidak disebut. Limitations WHO menyebut populasi dasar (termasuk status perkawinan) sebagai sumber ketidakcocokan.
3. **Apa kata besaran angkanya?** BPS Indonesia jauh di bawah WHO pada tahun yang sama; karena pemakai metode modern ≤ permintaan total, pola itu cocok dengan BPS memakai penyebut yang lebih besar.

### P4: Angka kelahiran remaja 15–19: WHO vs WDI
- Seri utama: `MDG_0000000003` (rincian `umur=15-19`)
- Pembanding: `SP.ADO.TFRT` (rincian `total`)
- Jenis: **selisih**; tahun beririsan: 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2013, 2015, 2016
- Dugaan kategori selisih (diuji di Sprint 2): sumber berbeda (WHO: data survei/registrasi yang dihimpun; WDI: model WPP)

Pertanyaan keterbandingan dan jawabannya:

1. **Apakah sumbernya sama?** Tidak: MethodOfEstimationOverview WHO menyebut registrasi sipil dan survei; WDI dari WPP.
