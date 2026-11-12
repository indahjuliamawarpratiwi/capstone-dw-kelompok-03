"""Tahap 8 — Validasi skema Silver menggunakan Pandera."""

import pandas as pd
from pathlib import Path
from .silver import validasi_silver


def jalankan(silver=None, gold=None) -> dict:
    """Jalankan validasi Silver. Dipanggil otomatis oleh pipeline.py."""
    if not isinstance(silver, pd.DataFrame):
        path = Path("data/silver/silver.parquet")
        if not path.exists():
            print("data/silver/silver.parquet tidak ditemukan.")
            return {}
        silver = pd.read_parquet(path)

    print("\n── Validasi Silver ──")
    hasil = validasi_silver(silver)
    for pesan in hasil["pesan"]:
        print(pesan)
    if hasil["gagal"]:
        print("  Contoh pelanggaran (maks 5):")
        for item in hasil["gagal"][:5]:
            print(f"    kolom={item['kolom']}, aturan={item['periksa']}, nilai={item['contoh']}")
    return hasil
