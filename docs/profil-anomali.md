# Profil dan Anomali — Silver Kasus 03

Dokumen ini merangkum tahap 2–3: profil per seri, deteksi anomali, dan keputusan pembersihan.
Semua angka dihasilkan ulang oleh `python -m src.silver` dan tersimpan di:

- `data/silver/profil.csv`
- `data/silver/anomali.csv`
- `data/silver/boxplot_seri.png`
- `data/silver/silver.parquet`

## Cakupan

| Ukuran | Nilai |
|---|---:|
| Berkas mentah pada MANIFEST | 13 |
| Baris data hasil ekstraksi | 374 |
| Seri/rincian yang diprofilkan | 6 |
| Observasi logis BPS setelah duplikat lintas format dihitung sekali | 138 |
| Baris Silver akhir | 373 |
| Temuan anomali | 79 |

Temuan anomali terdiri atas 71 baris patahan per wilayah, 5 observasi outlier, 2 ringkasan
duplikat lintas berkas, dan 1 nilai kosong.

## Profil per seri

Angka `baris` adalah baris mentah; `observasi` adalah baris setelah duplikat logis CSV/JSON
dihitung sekali. Statistik IQR dihitung dari observasi logis.

| Sumber | Seri | Rincian | Baris | Observasi | Wilayah | Periode | Kosong | Duplikat | Outlier | Patahan |
|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|
| BPS | var1353 | Total | 138 | 69 | 35 | 2012–2017 | 0 | 69 | 2 | 136 |
| BPS | var1394 | Total | 138 | 69 | 35 | 2012–2017 | 0 | 69 | 1 | 136 |
| WDI | SP.ADO.TFRT | Total | 66 | 66 | 1 | 1960–2025 | 1 | 0 | 0 | 0 |
| WHO | MDG_0000000003 | Perempuan \| 10-14 | 12 | 12 | 1 | 2002–2016 | 0 | 0 | 0 | 3 |
| WHO | MDG_0000000003 | Perempuan \| 15-19 | 14 | 14 | 1 | 2001–2016 | 0 | 0 | 2 | 2 |
| WHO | SDGFPALL | Perempuan \| 15-49 | 6 | 6 | 1 | 2002–2017 | 0 | 0 | 0 | 10 |

## Nilai kosong

| Sumber | Seri | Periode | Keputusan |
|---|---|---|---|
| WDI | SP.ADO.TFRT | 2025 | Dibuang dari Silver; tidak diimputasi (K-005) |

## Outlier IQR 1,5

Outlier ditandai, tidak dihapus dan tidak di-winsorize. Nilai ekstrem dapat merupakan variasi
nyata antardaerah atau antarwaktu; menghapusnya tanpa bukti akan mengubah data (K-008).

| Sumber | Seri | Rincian | Wilayah | Periode | Nilai | Batas IQR |
|---|---|---|---|---:|---:|---|
| BPS | var1353 | Total | Kalimantan Barat | 2012 | 104,0 | -6,0–98,0 |
| BPS | var1353 | Total | Sulawesi Barat | 2012 | 101,0 | -6,0–98,0 |
| BPS | var1394 | Total | Papua | 2012 | 19,1 | 27,75–81,75 |
| WHO | MDG_0000000003 | Perempuan \| 15-19 | Indonesia | 2015 | 39,920 | 40,799–57,102 |
| WHO | MDG_0000000003 | Perempuan \| 15-19 | Indonesia | 2016 | 36,110 | 40,799–57,102 |

## Patahan seri

Patahan dihitung dari tahun yang tidak muncul di antara tahun minimum dan maksimum pada setiap
wilayah. Patahan tidak diinterpolasi atau di-forward-fill; grid lengkap diserahkan ke Gold (K-009).

| Sumber | Seri | Rincian | Tahun hilang | Jumlah |
|---|---|---|---:|---:|
| BPS | var1353 | Total | 2013–2016 pada 34 wilayah | 136 |
| BPS | var1394 | Total | 2013–2016 pada 34 wilayah | 136 |
| WHO | MDG_0000000003 | Perempuan \| 10-14 | 2009, 2012, 2014 | 3 |
| WHO | MDG_0000000003 | Perempuan \| 15-19 | 2012, 2014 | 2 |
| WHO | SDGFPALL | Perempuan \| 15-49 | 2003–2006, 2008–2011, 2013–2014 | 10 |
| **Total** | | | | **287** |

## Duplikat

BPS menyediakan nilai yang sama dalam CSV dan JSON. Setiap observasi logis muncul dua kali dengan
`_berkas_raw` berbeda; keduanya dipertahankan agar lineage tidak hilang (K-003). Duplikat pada
kunci Silver penuh (`sumber+seri+wilayah+periode+rincian+_berkas_raw`) berjumlah 0.

| Sumber | Seri | Duplikat logis | Keputusan |
|---|---|---:|---|
| BPS | var1353 | 69 | Kedua format dipertahankan |
| BPS | var1394 | 69 | Kedua format dipertahankan |

## Cara menghasilkan ulang

```bash
python -m src.silver
python -m src.common.skema data/silver/silver.parquet
```

Keluaran yang diharapkan:

```text
profil     : 6 seri
anomali    : 79 temuan
silver     : 373 baris
LOLOS  373 baris, 5 seri, 35 wilayah, 7 berkas sumber
```
