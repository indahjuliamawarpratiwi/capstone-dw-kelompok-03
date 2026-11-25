"""Tahap 4–6 — Gold. Sprint 2: Silver, panel, nasional, dan rekonsiliasi dimuat ke DuckDB."""
from src.gold import muat_sql, nasional


def jalankan(silver, ekstraksi=None):
    hasil = nasional.jalankan(silver, ekstraksi)
    hasil.update(muat_sql.jalankan(silver))
    return hasil
