"""Tahap 4–6 — Gold: panel, tabel nasional, rekonsiliasi, dan pemuatan ke DuckDB."""
from src.gold import muat_sql, nasional, panel, rekonsiliasi


def jalankan(silver, ekstraksi=None):
    hasil = nasional.jalankan(silver, ekstraksi)
    hasil.update(panel.jalankan(silver))
    hasil.update(rekonsiliasi.jalankan(hasil["nasional_gold"]))
    hasil["baris_sql"] = muat_sql.jalankan(silver, hasil)
    return hasil