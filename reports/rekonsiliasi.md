# Tabel rekonsiliasi seri utama vs pembanding nasional

Dihasilkan `python pipeline.py` (`src/gold/rekonsiliasi.py`) dari `data/gold/nasional.parquet`. Selisih = nilai utama − nilai pembanding; selisih relatif dalam persen terhadap pembanding. Periode tanpa pasangan tetap ditampilkan. Selisih tidak dihapus dan tidak dipaksa sama.

## Ringkasan per pasangan

| pasangan_id | seri_pembanding | jenis | periode | berpasangan | selisih_dihitung | median_selisih | median_selisih_relatif | kategori |
|---|---|---|---|---|---|---|---|---|
| P1 | SP.ADO.TFRT | selisih | 6 | 2 | 2 | 3.30 | 8.68 | tanpa pasangan (4), metode berbeda (2) |
| P2 | MDG_0000000003 | selisih | 2 | 2 | 2 | -0.30 | 0.66 | metode berbeda (2) |
| P3 | SDGFPALL | selisih | 4 | 2 | 2 | -20.45 | 26.21 | definisi berbeda (2), tanpa pasangan (2) |
| P4 | SP.ADO.TFRT | selisih | 16 | 14 | 14 | 1.94 | 4.68 | metode berbeda (14), tanpa pasangan (2) |

Median selisih relatif mutlak, pasangan yang seri utamanya seri provinsi (BPS/BNPB): 8.68% (6 baris); semua pasangan termasuk antarpembanding: 5.61% (20 baris).

Periode pembanding di luar rentang seri utama yang tidak ditulis: P1 118, P3 4, P4 98.

## Kategori

Kategori baku: *definisi berbeda*, *metode berbeda*, *vintage berbeda*, *cakupan berbeda*, *belum terjelaskan*, *tanpa pasangan*, *tidak berselisih*. Kategori pasangan ditetapkan dari bukti di pasangan rekonsiliasi Sprint 1 (`reports/pasangan-rekonsiliasi.md`); baris satu sisi menjadi *tanpa pasangan*, baris yang angkanya sama menjadi *tidak berselisih*.

## Rincian per pasangan

### P1: Angka kelahiran remaja 15–19: BPS (SDKI) vs WDI (model WPP)

Jenis **selisih**; kategori pasangan: **metode berbeda**. Metode (survei dengan periode rujukan vs estimasi model penduduk tahunan).

Rincian: BPS total = umur 15–19 (judul); WDI hanya 15–19.

| seri_pembanding | periode | nilai_utama | nilai_pembanding | selisih | selisih_relatif | asal | kategori | catatan |
|---|---|---|---|---|---|---|---|---|
| SP.ADO.TFRT | 2012 | 48.00 | 44.62 | 3.38 | 7.58 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2013 |  | 42.67 |  |  | hanya_pembanding | tanpa pasangan |  |
| SP.ADO.TFRT | 2014 |  | 40.13 |  |  | hanya_pembanding | tanpa pasangan |  |
| SP.ADO.TFRT | 2015 |  | 37.86 |  |  | hanya_pembanding | tanpa pasangan |  |
| SP.ADO.TFRT | 2016 |  | 35.36 |  |  | hanya_pembanding | tanpa pasangan |  |
| SP.ADO.TFRT | 2017 | 36.00 | 32.79 | 3.21 | 9.78 | keduanya | metode berbeda |  |

### P2: Angka kelahiran remaja 15–19: BPS vs WHO

Jenis **selisih**; kategori pasangan: **metode berbeda**. Tidak ada tahun beririsan; dibandingkan dengan tahun terdekat di Gold (Sprint 2) dengan penanda.

Rincian: WHO rincian umur=15-19; baris 10-14 tidak sebanding.

| seri_pembanding | periode | nilai_utama | nilai_pembanding | selisih | selisih_relatif | asal | kategori | catatan |
|---|---|---|---|---|---|---|---|---|
| MDG_0000000003 | 2012 | 48.00 | 48.49 | -0.49 | -1.01 | keduanya | metode berbeda | pembanding tahun 2011 (tidak ada tahun yang sama; tahun terdekat) |
| MDG_0000000003 | 2017 | 36.00 | 36.11 | -0.11 | -0.30 | keduanya | metode berbeda | pembanding tahun 2016 (tidak ada tahun yang sama; tahun terdekat) |

### P3: KB metode modern: BPS vs WHO kebutuhan KB terpenuhi

Jenis **selisih**; kategori pasangan: **definisi berbeda**. Definisi (penyebut berbeda: BPS lebih dekat ke prevalensi kontrasepsi modern).

Rincian: keduanya perempuan 15–49 tanpa rincian.

| seri_pembanding | periode | nilai_utama | nilai_pembanding | selisih | selisih_relatif | asal | kategori | catatan |
|---|---|---|---|---|---|---|---|---|
| SDGFPALL | 2012 | 57.90 | 79.00 | -21.10 | -26.71 | keduanya | definisi berbeda |  |
| SDGFPALL | 2015 |  | 78.20 |  |  | hanya_pembanding | tanpa pasangan |  |
| SDGFPALL | 2016 |  | 77.60 |  |  | hanya_pembanding | tanpa pasangan |  |
| SDGFPALL | 2017 | 57.20 | 77.00 | -19.80 | -25.71 | keduanya | definisi berbeda |  |

### P4: Angka kelahiran remaja 15–19: WHO vs WDI

Jenis **selisih**; kategori pasangan: **metode berbeda**. Sumber berbeda (WHO: data survei/registrasi yang dihimpun; WDI: model WPP).

Rincian: WHO umur=15-19.

| seri_pembanding | periode | nilai_utama | nilai_pembanding | selisih | selisih_relatif | asal | kategori | catatan |
|---|---|---|---|---|---|---|---|---|
| SP.ADO.TFRT | 2001 | 50.93 | 53.02 | -2.08 | -3.93 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2002 | 53.12 | 51.76 | 1.36 | 2.63 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2003 | 55.92 | 50.41 | 5.51 | 10.92 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2004 | 51.00 | 48.21 | 2.79 | 5.78 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2005 | 52.28 | 48.10 | 4.19 | 8.71 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2006 | 50.95 | 47.77 | 3.19 | 6.67 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2007 | 49.48 | 47.67 | 1.82 | 3.81 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2008 | 46.88 | 46.29 | 0.59 | 1.28 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2009 | 47.00 | 45.59 | 1.41 | 3.08 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2010 | 46.86 | 45.68 | 1.18 | 2.59 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2011 | 48.49 | 45.59 | 2.90 | 6.35 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2012 |  | 44.62 |  |  | hanya_pembanding | tanpa pasangan |  |
| SP.ADO.TFRT | 2013 | 47.37 | 42.67 | 4.69 | 11.00 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2014 |  | 40.13 |  |  | hanya_pembanding | tanpa pasangan |  |
| SP.ADO.TFRT | 2015 | 39.92 | 37.86 | 2.06 | 5.44 | keduanya | metode berbeda |  |
| SP.ADO.TFRT | 2016 | 36.11 | 35.36 | 0.75 | 2.13 | keduanya | metode berbeda |  |
