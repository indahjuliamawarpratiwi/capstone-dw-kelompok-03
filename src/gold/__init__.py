"""Tahap 4–6 — Gold (Sprint 2): panel, nasional, rekonsiliasi, dan DuckDB.

Satu definisi `jalankan` — inilah versi yang tersisa setelah merge dan yang dipanggil
`pipeline.py` lewat `gold.jalankan(h["silver"])`. Argumen `ekstraksi` opsional tetap diterima
agar tanda tangan fungsi kompatibel dengan versi main.
"""
from src.gold import muat_sql, panel, rekonsiliasi


def jalankan(silver, ekstraksi=None):
    hasil_panel = panel.jalankan(silver)
    hasil_rek = rekonsiliasi.jalankan(hasil_panel["nasional_gold"])
    hasil = {
        "panel": hasil_panel["panel"],
        "panel_lebar": hasil_panel["panel_lebar"],
        "nasional_gold": hasil_panel["nasional_gold"],
        "rekonsiliasi": hasil_rek["rekonsiliasi"],
    }
    hasil["baris_sql"] = muat_sql.jalankan(silver, hasil)
    if ekstraksi is not None:
        hasil["ekstraksi"] = ekstraksi
    return hasil
