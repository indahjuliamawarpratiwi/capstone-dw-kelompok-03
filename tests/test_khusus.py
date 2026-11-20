"""Aturan khas Kasus 03 diuji dengan baris yang sengaja dirusak."""
import pandas as pd

from src.validasi import khusus


def test_aturan_khusus_lolos_pada_silver_asli(silver_contoh):
    for nama, _, keras, fungsi in khusus.ATURAN:
        if keras:
            assert fungsi(silver_contoh).empty, nama


def test_tahun_interpolasi_tertangkap(silver_contoh):
    baris = silver_contoh[silver_contoh["seri_kode"] == "var1353"].iloc[[0]].copy()
    baris["periode"] = "2014"
    rusak = pd.concat([silver_contoh, baris], ignore_index=True)
    assert not khusus.bps_hanya_tahun_survei(rusak).empty


def test_abr_tanpa_umur_tertangkap(silver_contoh):
    rusak = silver_contoh.copy()
    i = rusak.index[rusak["seri_kode"] == khusus.ABR_WHO][0]
    rusak.loc[i, "rincian"] = "total"
    assert not khusus.abr_who_berumur(rusak).empty


def test_abr_satuan_lain_tertangkap(silver_contoh):
    rusak = silver_contoh.copy()
    i = rusak.index[rusak["seri_kode"] == "var1353"][0]
    rusak.loc[i, "satuan"] = "persen"
    assert not khusus.abr_satu_satuan(rusak).empty


def test_umur_tertukar_memicu_peringatan(silver_contoh):
    rusak = silver_contoh.copy()
    i = rusak.index[(rusak["seri_kode"] == khusus.ABR_WHO) & (rusak["rincian"] == "umur=10-14")][0]
    rusak.loc[i, "nilai"] = 500.0
    assert not khusus.abr_10_14_lebih_kecil(rusak).empty
