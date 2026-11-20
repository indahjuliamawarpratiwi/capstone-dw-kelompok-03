# Kelengkapan panel provinsi dan kategori sel kosong

Dihasilkan `python pipeline.py` (`src/silver/grid.py`). Grid = 38 provinsi susunan 2025 x periode yang diterbitkan seri itu. Persen dari 38 menghitung semua sel; persen dari seharusnya hanya menghitung sel yang provinsinya sudah ada dan tidak dinyatakan tidak terbit oleh penerbit.

## Persen sel terisi per seri per periode

| seri_kode | periode | sel | terisi | seharusnya_ada | persen_dari_38 | persen_dari_seharusnya |
|---|---|---|---|---|---|---|
| var1353 | 2012 | 38 | 33 | 33 | 86.80 | 100.00 |
| var1353 | 2017 | 38 | 34 | 34 | 89.50 | 100.00 |
| var1394 | 2012 | 38 | 33 | 33 | 86.80 | 100.00 |
| var1394 | 2017 | 38 | 34 | 34 | 89.50 | 100.00 |

## Jumlah sel per kategori (provinsi)

| seri_kode | belum_ada | terisi |
|---|---|---|
| var1353 | 9 | 67 |
| var1394 | 9 | 67 |

## Baris Indonesia

| seri_kode | periode | kategori | bukti |
|---|---|---|---|
| var1394 | 2012 | terisi |  |
| var1394 | 2017 | terisi |  |
| var1353 | 2012 | terisi |  |
| var1353 | 2017 | terisi |  |

## Batas pemakaian panel

| seri_kode | tingkat | periode_pertama | periode_terakhir | jumlah_periode |
|---|---|---|---|---|
| var1353 | nasional | 2012 | 2017 | 2 |
| var1353 | provinsi | 2012 | 2017 | 2 |
| var1394 | nasional | 2012 | 2017 | 2 |
| var1394 | provinsi | 2012 | 2017 | 2 |

Provinsi yang belum ada pada sebagian periode panel: Kalimantan Utara, Papua Barat Daya, Papua Pegunungan, Papua Selatan, Papua Tengah.

Tahun sesudah periode terakhir di luar jangkauan panel; panel tidak menggambarkan keadaan tahun itu. Tahun di antara dua periode survei tidak termasuk grid dan tidak diisi di Silver.

Daftar semua sel kosong beserta buktinya: `reports/grid-sel-kosong.csv`.
