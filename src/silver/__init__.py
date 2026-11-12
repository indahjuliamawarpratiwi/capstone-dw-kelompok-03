"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver (pertemuan II–VII).

Keluaran: data/silver/silver.parquet dengan skema minimal di src/common/skema.py.
Satu baris = satu seri x wilayah x periode x rincian x berkas sumber. Nilai dari sumber berbeda
TIDAK digabung di sini. Setiap keputusan pembersihan dicatat di log-keputusan.csv.
"""
from pathlib import Path

import pandas as pd

from src.common import skema
from src.common.manifest import baca

ROOT = Path(__file__).resolve().parents[2]
TUJUAN = ROOT / "data" / "silver" / "silver.parquet"

_PETA_SEX = {"MALE": "Laki-laki", "FEMALE": "Perempuan"}
_PETA_AGE = {"Y10T14": "10-14", "Y15T19": "15-19", "Y15T49": "15-49"}
_PETA_WAKTU = {"YEAR": "tahun"}


def _teks(series):
    return series.fillna("").astype(str).str.strip()


def _rapikan_nama(nama):
    if pd.isna(nama):
        return ""
    teks = str(nama).strip().title()
    return teks.replace("Dki ", "DKI ").replace("Di Yogyakarta", "DI Yogyakarta")


def _bps(df):
    hasil = df.copy()
    hasil["sumber"] = "BPS"
    hasil["seri_kode"] = "var" + hasil["var_id"].astype("int64").astype(str)
    hasil["wilayah_kode"] = hasil["wilayah_id"].astype("int64")
    hasil["nama_wilayah"] = hasil["wilayah"].map(_rapikan_nama)
    hasil["periode"] = hasil["tahun"].astype("int64").astype(str)
    hasil["jenis_periode"] = "tahun"
    hasil["rincian"] = hasil["turvar"].map(
        lambda nilai: "Total"
        if str(nilai).strip().lower() in {"", "tidak ada", "nan"}
        else str(nilai).strip()
    )
    hasil["nilai"] = pd.to_numeric(hasil["nilai"], errors="coerce")
    hasil["satuan"] = _teks(hasil["satuan"])
    return hasil[skema.KOLOM]


def _who(df):
    hasil = df.copy()
    geo = pd.to_numeric(hasil["DIM_GEO_CODE_M49"], errors="coerce")
    if not (geo == 360).all():
        raise ValueError("WHO GHO memuat kode wilayah selain Indonesia (M49 360)")

    hasil["sumber"] = "WHO"
    hasil["seri_kode"] = hasil["IND_CODE"].astype(str)
    hasil["wilayah_kode"] = 9999
    hasil["nama_wilayah"] = "Indonesia"
    hasil["periode"] = hasil["DIM_TIME"].astype("int64").astype(str)
    jenis = hasil["DIM_TIME_TYPE"].astype(str).str.upper().map(_PETA_WAKTU)
    if jenis.isna().any():
        raise ValueError("WHO GHO memuat jenis periode yang belum dipetakan")
    hasil["jenis_periode"] = jenis

    sex = _teks(hasil["DIM_SEX"]).str.upper().map(_PETA_SEX).fillna(_teks(hasil["DIM_SEX"]))
    age = _teks(hasil["DIM_AGE"]).str.upper().map(_PETA_AGE).fillna(_teks(hasil["DIM_AGE"]))
    hasil["rincian"] = (sex + " | " + age).str.strip(" |")

    per_1000 = pd.to_numeric(hasil["RATE_PER_1000_N"], errors="coerce")
    per_100 = pd.to_numeric(hasil["RATE_PER_100_N"], errors="coerce")
    hasil["nilai"] = per_1000.fillna(per_100)
    hasil["satuan"] = ""
    hasil.loc[per_1000.notna(), "satuan"] = "per 1.000"
    hasil.loc[per_100.notna(), "satuan"] = "Persen"
    return hasil[skema.KOLOM]


def _wdi(df):
    hasil = df.copy()
    hasil["sumber"] = "WDI"
    hasil["seri_kode"] = hasil["indicator.id"].astype(str)
    hasil["wilayah_kode"] = 9999
    hasil["nama_wilayah"] = "Indonesia"
    hasil["periode"] = hasil["date"].astype("int64").astype(str)
    hasil["jenis_periode"] = "tahun"
    hasil["rincian"] = "Total"
    hasil["nilai"] = pd.to_numeric(hasil["value"], errors="coerce")
    hasil["satuan"] = "per 1.000 perempuan usia 15-19"
    hasil = hasil.dropna(subset=["nilai"])
    return hasil[skema.KOLOM]


def jalankan(mentah):
    """Terima keluaran tahap 1, tulis dan kembalikan DataFrame Silver."""
    hasil = pd.concat(
        [_bps(mentah["bps"]), _who(mentah["who_gho"]), _wdi(mentah["wdi"])],
        ignore_index=True,
    )
    hasil = hasil.sort_values(
        ["sumber", "_berkas_raw", "seri_kode", "wilayah_kode", "periode", "rincian"],
        kind="stable",
    ).reset_index(drop=True)

    salah = skema.periksa_silver(hasil, manifest=baca())
    if salah:
        raise ValueError("Silver tidak lolos skema minimal: " + "; ".join(salah))

    TUJUAN.parent.mkdir(parents=True, exist_ok=True)
    hasil.to_parquet(TUJUAN, index=False)
    return hasil
