"""Aturan validasi khas Kasus 03 (panduan kelompok bagian 4.4), plus dua aturan peringatan.

Setiap fungsi menerima Silver dan mengembalikan baris yang melanggar (kosong = lolos).
"""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W

ABR_WHO = "MDG_0000000003"


def bps_hanya_tahun_survei(silver):
    """Tidak ada baris BPS di luar tahun survei yang diterbitkan (tidak ada interpolasi)."""
    b = silver[silver["sumber"] == "bps"]
    terbit = [p in K.TAHUN_TERBIT.get(s, set()) for s, p in zip(b["seri_kode"], b["periode"])]
    return b[[not t for t in terbit]][["seri_kode", "wilayah_kode", "periode", "nilai"]]


def abr_who_berumur(silver):
    """Setiap baris angka kelahiran remaja WHO menyebut kelompok umurnya (tidak ada 'total' lintas umur)."""
    s = silver[silver["seri_kode"] == ABR_WHO]
    return s[~s["rincian"].str.contains("umur=")][["seri_kode", "periode", "rincian", "nilai"]]


def abr_satu_satuan(silver):
    """Semua angka kelahiran remaja (BPS, WDI, WHO) bersatuan sama."""
    s = silver[silver["seri_kode"].isin(["var1353", "SP.ADO.TFRT", ABR_WHO]) & (silver["satuan"] != K.ABR)]
    return s[["seri_kode", "periode", "satuan"]]


def abr_10_14_lebih_kecil(silver):
    """Peringatan: angka kelahiran 10–14 tidak lebih kecil dari 15–19 pada tahun yang sama."""
    s = silver[silver["seri_kode"] == ABR_WHO]
    lebar = s.pivot_table(index="periode", columns="rincian", values="nilai").dropna()
    a, b = "umur=10-14", "umur=15-19"
    if lebar.empty or not {a, b} <= set(lebar.columns):
        return pd.DataFrame()
    return lebar[lebar[a] >= lebar[b]].reset_index()


def kb_bps_di_bawah_who(silver):
    """Peringatan: KB BPS Indonesia melebihi WHO kebutuhan KB terpenuhi pada tahun yang sama.
    Kalau BPS memakai penyebut yang lebih besar (lihat P3), angkanya seharusnya lebih kecil."""
    s = silver[silver["seri_kode"].isin(["var1394", "SDGFPALL"]) & (silver["wilayah_kode"] == W.INDONESIA)
               & (silver["rincian"] == "total")]
    lebar = s.pivot_table(index="periode", columns="seri_kode", values="nilai").dropna()
    if lebar.empty:
        return pd.DataFrame()
    return lebar[lebar["var1394"] > lebar["SDGFPALL"]].reset_index()


ATURAN = [
    ("bps_hanya_tahun_survei", "tidak ada tahun BPS di luar tahun survei 2012 dan 2017", True, bps_hanya_tahun_survei),
    ("abr_who_berumur", "setiap baris MDG_0000000003 punya rincian umur 10-14 atau 15-19", True, abr_who_berumur),
    ("abr_satu_satuan", "angka kelahiran remaja BPS, WDI, WHO bersatuan per_1000_perempuan_seumur", True, abr_satu_satuan),
    ("abr_10_14_lebih_kecil", "angka kelahiran 10–14 ≥ 15–19 pada tahun yang sama (peringatan)", False, abr_10_14_lebih_kecil),
    ("kb_bps_di_bawah_who", "KB BPS Indonesia > WHO kebutuhan KB terpenuhi (peringatan: periksa definisi)", False, kb_bps_di_bawah_who),
]
