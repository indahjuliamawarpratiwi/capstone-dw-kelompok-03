"""Pembantu kecil yang dipakai beberapa pembaca tahap ekstraksi.

Isi modul ini sengaja terbatas pada hal yang sama di semua sumber: membaca teks,
mengubah nilai menjadi angka tanpa mengisi nilai kosong, dan menempelkan lineage
dari `src.common.manifest`.
"""
from pathlib import Path

import pandas as pd

from src.common.manifest import sha256_raw

ENCODING = ("utf-8-sig", "cp1252", "latin-1")


def baca_teks(path):
    """Baca berkas dengan beberapa kemungkinan pengodean karakter."""
    mentah = Path(path).read_bytes()
    for pengodean in ENCODING:
        try:
            return mentah.decode(pengodean)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8", mentah, 0, len(mentah), "pengodean tidak dikenal")


def ke_angka(nilai):
    """Ubah nilai menjadi angka tanpa mengisi nilai kosong.

    Mendukung desimal titik (44.4), desimal koma (44,4), dan pemisah ribuan Indonesia
    (1.234,5 -> 1234.5). Nilai kosong tetap menjadi NA agar tidak dianggap nol.
    """
    if nilai is None:
        return pd.NA
    if isinstance(nilai, bool):
        return float(nilai)
    if isinstance(nilai, (int, float)):
        return float(nilai)
    teks = str(nilai).strip()
    if not teks:
        return pd.NA
    if "," in teks:
        teks = teks.replace(".", "").replace(",", ".")
    elif teks.count(".") > 1:
        teks = teks.replace(".", "")
    return float(teks)


def tempel_lineage(df, path, raw):
    """Tambahkan asal berkas dan sha256 dari MANIFEST.csv."""
    rel = Path(path).resolve().relative_to(Path(raw).resolve()).as_posix()
    df["_berkas_raw"] = rel
    df["_sha256_raw"] = sha256_raw(rel, raw)
    return df
