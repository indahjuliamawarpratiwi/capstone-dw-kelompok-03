"""Tahap 5 — memuat Silver dan Gold ke DuckDB dengan kunci primer dan batasan.

Basis data dibuat ulang setiap kali (berkas lama dihapus), jadi hasilnya selalu sama dengan
Parquet Silver dan Gold. Berkas .duckdb tidak di-commit; jalankan pipeline untuk membuatnya.
"""
from pathlib import Path

import duckdb
import pandas as pd

from src.laporan import ROOT, catat

DB = ROOT / "data" / "gold" / "gudang.duckdb"
DDL = Path(__file__).with_name("silver.sql")
GOLD = ROOT / "data" / "gold"
PANEL = GOLD / "panel_gold.parquet"
NASIONAL = GOLD / "nasional_periode_seri.parquet"
REKONSILIASI = GOLD / "rekonsiliasi.csv"
KOLOM_PANEL = ["wilayah_kode", "nama_wilayah", "periode", "jenis_periode", "seri_kode",
               "sumber", "rincian", "nilai", "satuan", "sdg_kode"]


def _panel(silver):
    p = silver.loc[silver["wilayah_kode"] != 9999, KOLOM_PANEL].copy()
    return p.sort_values(["wilayah_kode", "periode", "seri_kode", "rincian"]).reset_index(drop=True)


def _sisip(con, nama, df):
    kolom = ", ".join(df.columns)
    con.register(f"{nama}_df", df)
    con.execute(f"INSERT INTO {nama} ({kolom}) SELECT {kolom} FROM {nama}_df")
    return con.execute(f"SELECT count(*) FROM {nama}").fetchall()[0][0]


def jalankan(silver):
    GOLD.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)

    seri = pd.read_csv(ROOT / "docs" / "seri.csv")[["seri_kode", "sumber", "tingkat", "nama_baku", "satuan", "sdg_kode"]]
    seri["sdg_kode"] = seri["sdg_kode"].astype(str)
    s = silver.copy()
    s["rujukan_tahun"] = s["rujukan_tahun"].astype("float64")
    panel = _panel(silver)
    panel.to_parquet(PANEL, index=False)
    nasional = pd.read_parquet(NASIONAL)
    rekonsiliasi = pd.read_csv(REKONSILIASI, keep_default_na=False)
    for kolom in ["nilai_utama", "nilai_pembanding", "selisih"]:
        rekonsiliasi[kolom] = pd.to_numeric(rekonsiliasi[kolom], errors="coerce")

    with duckdb.connect(str(DB)) as con:
        con.execute(DDL.read_text(encoding="utf-8"))
        jumlah = {
            "seri": _sisip(con, "seri", seri),
            "silver": _sisip(con, "silver", s),
            "panel_gold": _sisip(con, "panel_gold", panel),
            "nasional": _sisip(con, "nasional", nasional),
            "rekonsiliasi": _sisip(con, "rekonsiliasi", rekonsiliasi),
        }

    for nama, sumber in [("silver", len(silver)), ("panel_gold", len(panel)),
                         ("nasional", len(nasional)), ("rekonsiliasi", len(rekonsiliasi))]:
        if jumlah[nama] != sumber:
            raise AssertionError(f"DuckDB {nama}: {jumlah[nama]} baris, sumber {sumber} baris")

    catat(baris_sql=jumlah["silver"])
    return {"baris_sql": jumlah["silver"], "baris_sql_panel": jumlah["panel_gold"],
            "baris_sql_nasional": jumlah["nasional"], "baris_sql_rekonsiliasi": jumlah["rekonsiliasi"]}
