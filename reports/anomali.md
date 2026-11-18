# Kategori anomali dan duplikat

Dihasilkan `python pipeline.py` (`src/silver/anomali.py`). Nilai di Silver tidak diubah kecuali galat input yang koreksinya jelas.

## Galat input (semua baris Silver diperiksa terhadap rentang satuan): 0

Tidak ada nilai di luar rentang satuannya.

## Uji patahan seri

| seri_kode | pergantian | provinsi | porsi_naik | porsi_turun | patahan | keterangan |
|---|---|---|---|---|---|---|
| var1394 | — | 0 | None | None | tidak dapat diuji | hanya 2 periode; pola serentak dari dua titik tidak bisa dibedakan dari perubahan sungguhan |
| var1353 | — | 0 | None | None | tidak dapat diuji | hanya 2 periode; pola serentak dari dua titik tidak bisa dibedakan dari perubahan sungguhan |

## Pergantian definisi yang dinyatakan penerbit

Tidak ada.

## Cakupan parsial yang dinyatakan penerbit

Tidak ada.

## Perubahan batas wilayah di tengah panel: 2

| seri_kode | induk | wilayah_kode | periode | anak | nilai_sebelum | nilai_sesudah |
|---|---|---|---|---|---|---|
| var1394 | Kalimantan Timur | 6400 | 2017 | Kalimantan Utara | 54.10 | 59.30 |
| var1353 | Kalimantan Timur | 6400 | 2017 | Kalimantan Utara | 50.00 | 53.00 |

Nilai induk sebelum periode ini mencakup wilayah provinsi pemekaran; sesudahnya tidak. Perubahannya bukan tren dan tidak diratakan.

## Calon anomali dan kategorinya (3)

| seri_kode | nama_wilayah | periode | nilai | arah | kategori | tindakan |
|---|---|---|---|---|---|---|
| var1353 | Kalimantan Tengah | 2017 | 83.00 | ke bawah | outlier | tandai, nilai tidak diubah |
| var1394 | Papua | 2012 | 19.10 | ke bawah | outlier | tandai, nilai tidak diubah |
| var1394 | Papua | 2017 | 35.90 | perubahan | outlier | tandai, nilai tidak diubah |

Outlier di sini adalah outlier statistik. Menyebutnya *outlier asli* butuh penjelasan dunia nyata (kebijakan, bencana, cakupan survei); kolom itu diisi tim saat Sprint 2 bila buktinya ditemukan.

## Duplikat dua format BPS (CSV vs JSON)

| seri | baris_json | baris_csv | pasangan_sama | hanya_json | hanya_csv | nilai_berbeda | satuan_csv |
|---|---|---|---|---|---|---|---|
| var1353 | 69 | 69 | 69 | 0 | 0 | 0 | (kosong) |
| var1394 | 69 | 69 | 69 | 0 | 0 | 0 | Persen |

## Kunci Silver kembar: 0
