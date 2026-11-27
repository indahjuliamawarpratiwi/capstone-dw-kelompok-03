"""Pengujian tabel nasional Gold: Parquet, SQL, laporan, dan kolom asal."""
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from src.gold.muat_sql import DB
from src.laporan import ROOT

GOLD = ROOT / "data" / "gold"
PARQUET = GOLD / "nasional.parquet"
LAPORAN = ROOT / "reports" / "tabel-nasional-gold.md"


@pytest.fixture
def nas():
    if not PARQUET.exists():
        pytest.skip("jalankan python pipeline.py dulu")
    return pd.read_parquet(PARQUET)


def test_kolom_asal_dan_berkas_raw(nas):
    assert {"asal", "_berkas_raw"}.issubset(nas.columns)
    assert not nas.duplicated(["seri_kode", "rincian", "periode"]).any()
    assert nas["_berkas_raw"].notna().all()
    assert set(nas["asal"]) == {"baris_indonesia", "pembanding"}


def test_asal_setiap_seri(nas):
    harapan = {
        "var1394": ("baris_indonesia", 2),
        "var1353": ("baris_indonesia", 2),
        "MDG_0000000003": ("pembanding", 14),
        "SDGFPALL": ("pembanding", 6),
        "SP.ADO.TFRT": ("pembanding", 65),
    }
    for seri, (asal, jumlah) in harapan.items():
        d = nas[nas["seri_kode"] == seri]
        assert set(d["asal"]) == {asal}
        assert len(d) == jumlah


def test_jumlah_parquet_sql_laporan_sama(nas):
    if not DB.exists():
        pytest.skip("jalankan python pipeline.py dulu")
    con = duckdb.connect(str(DB), read_only=True)
    n_sql = con.execute("select count(*) from gold_nasional").fetchone()[0]
    con.close()

    teks = Path(LAPORAN).read_text(encoding="utf-8")
    bagian = teks.split("## 3. Semua baris", 1)[1]
    baris = [b for b in bagian.splitlines() if b.startswith("|") and "---" not in b][1:]

    assert len(nas) == 89
    assert n_sql == len(nas)
    assert len(baris) == len(nas)
    assert f"SQL `gold_nasional`: **{len(nas)} baris**" in teks
    assert f"Laporan ini: **{len(nas)} baris**" in teks


def test_laporan_menampilkan_asal_per_seri(nas):
    teks = Path(LAPORAN).read_text(encoding="utf-8")
    assert "## 1. Rekap per seri dan asal" in teks
    assert "## 2. Asal per seri" in teks
    for seri in nas["seri_kode"].unique():
        assert f"| {seri} |" in teks
    assert "baris_indonesia" in teks
    assert "pembanding" in teks


def test_alias_tabel_nasional(nas):
    for jalur, baca in ((GOLD / "tabel-nasional.parquet", pd.read_parquet),
                        (GOLD / "tabel-nasional.csv", pd.read_csv)):
        assert jalur.exists()
        d = baca(jalur)
        assert list(d.columns) == list(nas.columns)
        assert len(d) == len(nas)
        assert d["asal"].value_counts().to_dict() == nas["asal"].value_counts().to_dict()
