"""Tahap 4–6 — Gold (Sprint 2).

Panel provinsi x periode x indikator, tabel nasional, rekonsiliasi, dan pemuatan ke DuckDB.
"""
from src.gold import muat_sql, panel, rekonsiliasi

def jalankan(silver):
    hasil = nasional.jalankan(silver)
    hasil.update(panel.jalankan(silver))
    hasil.update(rekonsiliasi.jalankan(hasil["nasional_gold"]))
    hasil["baris_sql"] = muat_sql.jalankan(silver, hasil)

def jalankan(silver, ekstraksi=None):
    hasil_panel = panel.jalankan(silver)
    hasil_rek = rekonsiliasi.jalankan(hasil_panel["nasional_gold"])
    baris_sql = muat_sql.jalankan(silver)

    hasil = {
        "panel": hasil_panel["panel"],
        "panel_lebar": hasil_panel["panel_lebar"],
        "nasional_gold": hasil_panel["nasional_gold"],
        "rekonsiliasi": hasil_rek["rekonsiliasi"],
        "baris_sql": baris_sql,
    }
    if ekstraksi is not None:
        hasil["ekstraksi"] = ekstraksi
    return hasil
