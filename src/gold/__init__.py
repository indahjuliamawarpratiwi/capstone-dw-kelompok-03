"""Tahap 4–6 — Gold. Sprint 1: tabel nasional, daftar pasangan rekonsiliasi, dan Silver di DuckDB.

Panel provinsi x periode x indikator dan tabel rekonsiliasi dengan selisih dikerjakan di Sprint 2.
"""
from src.gold import muat_sql, nasional


<<<<<<< HEAD
def jalankan(silver):
    hasil = nasional.jalankan(silver)
    hasil["baris_sql"] = muat_sql.jalankan(silver)
    return hasil
=======

def jalankan(silver, ekstraksi=None):
    hasil = nasional.jalankan(silver)
    hasil["baris_sql"] = muat_sql.jalankan(silver)
    if ekstraksi is not None:
        hasil["ekstraksi"] = ekstraksi
    return hasil
def jalankan(silver, ekstraksi=None):
    hasil = nasional.jalankan(silver, ekstraksi)
    hasil.update(panel.jalankan(silver))
    hasil.update(rekonsiliasi.jalankan(hasil["nasional_gold"]))
    hasil["baris_sql"] = muat_sql.jalankan(silver, hasil)
    return hasil
>>>>>>> 3a5346748eedaaeec4a3d50b069ead6bb0b0c605
