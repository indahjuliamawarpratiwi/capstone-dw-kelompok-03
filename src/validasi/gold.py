"""Aturan validasi Gold dan rekonsiliasi (Sprint 2).

Memeriksa:
1. Kunci panel unik (wilayah_kode x periode tidak kembar)
2. Satuan satu per indikator
3. Setiap sel Gold punya pasangan di Silver
4. Setiap baris rekonsiliasi berpasangan punya kategori sah
5. Konsistensi basis data SQL (DuckDB)
"""
from pathlib import Path

import duckdb
import pandas as pd

from src.laporan import ROOT


def _ambil_panel(gold):
    """Ambil tabel panel dari dict gold atau berkas data/gold/."""
    if isinstance(gold, dict):
        if "panel" in gold and isinstance(gold["panel"], pd.DataFrame):
            return gold["panel"]
        if "nasional" in gold and isinstance(gold["nasional"], pd.DataFrame):
            return gold["nasional"]
    berkas = ROOT / "data" / "gold" / "panel.parquet"
    if berkas.exists():
        return pd.read_parquet(berkas)
    berkas_nas = ROOT / "data" / "gold" / "nasional_periode_seri.parquet"
    if berkas_nas.exists():
        return pd.read_parquet(berkas_nas)
    return pd.DataFrame()


def _ambil_rekonsiliasi(gold):
    """Ambil tabel rekonsiliasi dari dict gold atau berkas data/gold/."""
    if isinstance(gold, dict):
        if "rekonsiliasi" in gold and isinstance(gold["rekonsiliasi"], pd.DataFrame):
            return gold["rekonsiliasi"]
        if "pasangan" in gold and isinstance(gold["pasangan"], pd.DataFrame):
            return gold["pasangan"]
    berkas = ROOT / "data" / "gold" / "rekonsiliasi.parquet"
    if berkas.exists():
        return pd.read_parquet(berkas)
    berkas_csv = ROOT / "data" / "gold" / "pasangan_rekonsiliasi.csv"
    if berkas_csv.exists():
        return pd.read_csv(berkas_csv)
    return pd.DataFrame()


def kunci_panel_unik(silver, gold):
    """Kunci panel Gold (wilayah_kode, periode) tidak kembar."""
    df = _ambil_panel(gold)
    if df.empty:
        return pd.DataFrame()
    kandidat = [k for k in ["wilayah_kode", "periode", "seri_kode", "rincian", "kolom"] if k in df.columns]
    if not kandidat:
        return pd.DataFrame()
    return df[df.duplicated(subset=kandidat, keep=False)]


def satuan_satu_per_indikator(silver, gold):
    """Setiap indikator di Gold atau seri di Silver hanya punya satu satuan baku."""
    satu = silver.groupby("seri_kode")["satuan"].nunique()
    banyak = satu[satu > 1]
    if not banyak.empty:
        return silver[silver["seri_kode"].isin(banyak.index)][["seri_kode", "satuan"]].drop_duplicates()
    return pd.DataFrame()


def sel_gold_punya_pasangan_di_silver(silver, gold):
    """Setiap sel nilai di Gold berasal dari baris yang sah di Silver."""
    df = _ambil_panel(gold)
    if df.empty:
        return pd.DataFrame()
    if "nilai" in df.columns and "seri_kode" in df.columns and "periode" in df.columns:
        # Sertakan rincian agar pencocokan presisi 1-ke-1
        kunci = [k for k in ["seri_kode", "wilayah_kode", "periode", "rincian"] if k in df.columns and k in silver.columns]
        gab = df.merge(silver, on=kunci, how="left", suffixes=("_gold", "_silver"))
        return gab[gab["nilai_silver"].isna() | ((gab["nilai_gold"] - gab["nilai_silver"]).abs() > 1e-6)]
    return pd.DataFrame()


def rekonsiliasi_punya_kategori(silver, gold):
    """Setiap baris pasangan rekonsiliasi memiliki kategori yang terisi."""
    rek = _ambil_rekonsiliasi(gold)
    if rek.empty:
        return pd.DataFrame()
    kolom_kat = "dugaan_kategori" if "dugaan_kategori" in rek.columns else ("kategori" if "kategori" in rek.columns else None)
    if not kolom_kat:
        return pd.DataFrame()
    # Kategori tidak boleh kosong, null, atau strip
    salah = rek[rek[kolom_kat].isna() | (rek[kolom_kat].astype(str).str.strip().isin(["", "—", "nan"]))]
    return salah


def konsistensi_sql(silver, gold):
    """Konsistensi tabel DuckDB terhadap Silver."""
    db_path = ROOT / "data" / "gold" / "gudang.duckdb"
    if not db_path.exists():
        return pd.DataFrame()
    try:
        with duckdb.connect(str(db_path), read_only=True) as con:
            n = con.execute("SELECT count(*) FROM silver").fetchone()[0]
        if n != len(silver):
            return pd.DataFrame([{"keterangan": "jumlah baris duckdb != silver", "duckdb": n, "silver": len(silver)}])
    except Exception as e:
        return pd.DataFrame([{"error": str(e)}])
    return pd.DataFrame()


ATURAN = [
    ("kunci_panel_unik", "kunci panel Gold (wilayah_kode x periode) tidak kembar", True, kunci_panel_unik),
    ("satuan_satu_per_indikator", "setiap indikator/seri hanya punya satu satuan baku", True, satuan_satu_per_indikator),
    ("sel_gold_punya_pasangan_di_silver", "setiap nilai sel di Gold berasal dari baris yang sah di Silver", True, sel_gold_punya_pasangan_di_silver),
    ("rekonsiliasi_punya_kategori", "setiap baris pasangan rekonsiliasi memiliki kategori yang terisi", True, rekonsiliasi_punya_kategori),
]