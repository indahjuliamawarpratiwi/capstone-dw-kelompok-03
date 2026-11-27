"""Tahap 4–6 — Gold (Sprint 2): panel, nasional, rekonsiliasi, dan DuckDB.

Menggabungkan keluaran nasional Sprint 1 dengan panel, nasional Gold,
dan rekonsiliasi Sprint 2.
"""
from src.gold import muat_sql, nasional, panel, rekonsiliasi


def jalankan(silver, ekstraksi=None):
    hasil = nasional.jalankan(silver, ekstraksi)

    hasil_panel = panel.jalankan(silver)
    hasil["panel"] = hasil_panel["panel"]
    hasil["panel_lebar"] = hasil_panel["panel_lebar"]
    hasil["nasional_gold"] = hasil_panel["nasional_gold"]

    hasil_rek = rekonsiliasi.jalankan(hasil["nasional_gold"])
    hasil["rekonsiliasi"] = hasil_rek["rekonsiliasi"]

    hasil["baris_sql"] = muat_sql.jalankan(silver, hasil)

    if ekstraksi is not None:
        hasil["ekstraksi"] = ekstraksi

    return hasil