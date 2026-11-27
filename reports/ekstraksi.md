# Ekstraksi: jumlah baris per berkas

Dihasilkan `python pipeline.py`. Peran *data* berisi angka; *meta* berisi judul, definisi, atau catatan unduhan. Semua baris `data/raw/MANIFEST.csv` tertangani.

| berkas | pembaca | peran | baris | catatan |
|---|---|---|---|---|
| bps/2026-10-20/json/sdg3_3_7_1_v1394.json | bps_json | data | 69 | 1 halaman |
| bps/2026-10-20/json/sdg3_3_7_2_v1353.json | bps_json | data | 69 | 1 halaman |
| bps/2026-10-20/manifest_asal.json | bps_manifest_asal | meta | 36 | semua tabel unduhan BPS, bukan hanya kasus ini |
| bps/2026-10-20/sdg3_3_7_1_v1394.csv | bps_csv | data | 69 |  |
| bps/2026-10-20/sdg3_3_7_2_v1353.csv | bps_csv | data | 69 |  |
| wdi/2026-10-20/data/kelompok-07-hal-01.json | wdi_data | data | 66 | 2,112 baris di berkas, 1 seri kasus disaring |
| wdi/2026-10-20/metadata/sumber.json | wdi_sumber | meta | 71 |  |
| wdi/2026-10-20/metadata/sumber2_indikator.json | wdi_meta | meta | 1 | metadata seri kasus saja |
| wdi/2026-10-20/metadata/sumber46_indikator.json | wdi_meta | meta | 1 | metadata seri kasus saja |
| who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv | who_csv | data | 26 |  |
| who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv | who_csv | data | 6 |  |
| who_gho/2026-10-20/datadot/ddiindicators_skip0000.json | who_ddi | meta | 2 | definisi lengkap seri kasus |
| who_gho/2026-10-20/odata/Indicator.json | who_odata | meta | 2 |  |

Jumlah: 13 berkas dari 13 di MANIFEST, 374 baris mentah di berkas data.
