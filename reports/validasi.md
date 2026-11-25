# Hasil validasi Silver dan Gold

Dihasilkan `python pipeline.py` (`src/validasi/`). Aturan keras menghentikan pipeline bila gagal; peringatan dilaporkan untuk diperiksa manusia. Aturan juga diuji dengan salinan yang sengaja dirusak.

| aturan | jenis | keterangan | hasil |
|---|---|---|---|
| kolom dan tipe | keras (umum) | setiap kolom ada dengan tipe yang benar; nilai tidak kosong | LOLOS |
| rincian_dari_kamus | keras (umum) | rincian 'total' atau 'dimensi=kode' dengan dimensi/kode dari kamus konfigurasi | LOLOS |
| satu_satuan_per_seri | keras (umum) | satu seri hanya punya satu satuan | LOLOS |
| nilai_dalam_rentang_satuan | keras (umum) | nilai berada di rentang sah satuannya (persen 0–100, per 1.000 0–1.000, ...) | LOLOS |
| batas_bawah_le_nilai_le_batas_atas | keras (umum) | untuk baris yang punya batas: batas bawah ≤ nilai ≤ batas atas | LOLOS |
| kunci unik | keras (umum) | kombinasi sumber + seri_kode + wilayah_kode + periode + rincian + _berkas_raw tidak kembar | LOLOS |
| wilayah dan periode | keras (umum) | wilayah_kode dari kamus 38 provinsi + 9999; periode berbentuk baku | LOLOS |
| bps_hanya_tahun_survei | keras (kasus) | tidak ada tahun BPS di luar tahun survei 2012 dan 2017 | LOLOS |
| abr_who_berumur | keras (kasus) | setiap baris MDG_0000000003 punya rincian umur 10-14 atau 15-19 | LOLOS |
| abr_satu_satuan | keras (kasus) | angka kelahiran remaja BPS, WDI, WHO bersatuan per_1000_perempuan_seumur | LOLOS |
| abr_10_14_lebih_kecil | peringatan (kasus) | angka kelahiran 10–14 ≥ 15–19 pada tahun yang sama (peringatan) | LOLOS |
| kb_bps_di_bawah_who | peringatan (kasus) | KB BPS Indonesia > WHO kebutuhan KB terpenuhi (peringatan: periksa definisi) | LOLOS |
| kunci_panel_unik | keras (Gold) | kunci panel Gold (wilayah_kode x periode) tidak kembar | LOLOS |
| satuan_satu_per_indikator | keras (Gold) | setiap indikator/seri hanya punya satu satuan baku | LOLOS |
| sel_gold_punya_pasangan_di_silver | keras (Gold) | setiap nilai sel di Gold berasal dari baris yang sah di Silver | LOLOS |
| rekonsiliasi_punya_kategori | keras (Gold) | setiap baris pasangan rekonsiliasi memiliki kategori yang terisi | LOLOS |

## Kegagalan aturan umum

Tidak ada.

## Baris yang memicu aturan kasus

Tidak ada.

## Baris yang melanggar aturan Gold

Tidak ada.

## Konsistensi tabel DuckDB

Semua tabel sesuai dengan sumbernya.
