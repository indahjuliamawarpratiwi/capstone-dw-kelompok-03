import pandas as pd
import pytest

from src.laporan import ROOT
from src.validasi import gold as G

GOLD = ROOT / "data" / "gold"
pytestmark = pytest.mark.skipif(not (GOLD / "panel.parquet").exists(), reason="jalankan python pipeline.py dulu")


@pytest.fixture
def silver():
    return pd.read_parquet(ROOT / "data" / "silver" / "silver.parquet")


@pytest.fixture
def gold():
    nasional = pd.read_parquet(GOLD / "nasional.parquet")
    return {"panel": pd.read_parquet(GOLD / "panel.parquet"), "nasional": nasional,
            "nasional_gold": nasional, "rekonsiliasi": pd.read_parquet(GOLD / "rekonsiliasi.parquet")}


def aturan(nama):
    return next(f for n, _, _, f in G.ATURAN if n == nama)


def terisi(p):
    return p.index[p["status_sel"] == "terisi"][0]


def test_gold_asli_lolos(silver, gold):
    for nama, _, keras, f in G.ATURAN:
        assert f(silver, gold).empty, nama


def test_sel_panel_kembar(silver, gold):
    gold["panel"] = pd.concat([gold["panel"], gold["panel"].iloc[[0]]], ignore_index=True)
    assert not aturan("gold: kunci panel unik")(silver, gold).empty


def test_satuan_kedua_dalam_satu_indikator(silver, gold):
    gold["panel"].loc[0, "satuan"] = "satuan_lain"
    if gold["panel"]["indikator"].eq(gold["panel"].loc[0, "indikator"]).sum() == 1:
        pytest.skip("indikator pertama hanya satu baris")
    assert not aturan("gold: satu satuan per indikator")(silver, gold).empty


def test_sel_kosong_berisi_angka(silver, gold):
    p = gold["panel"]
    kosong = p.index[p["status_sel"] != "terisi"]
    if not len(kosong):
        pytest.skip("panel tanpa sel kosong")
    p.loc[kosong[0], "nilai"] = 1.0
    assert not aturan("gold: status sel dan nilai")(silver, gold).empty


def test_nilai_diubah_di_gold(silver, gold):
    p = gold["panel"]
    biasa = p.index[(p["status_sel"] == "terisi") & (p["rincian"] != "jumlah")]
    if not len(biasa):
        pytest.skip("semua sel panel berupa jumlah rincian")
    p.loc[biasa[0], "nilai"] = p.loc[biasa[0], "nilai"] + 1
    assert not aturan("gold: nilai sama dengan Silver")(silver, gold).empty


def test_sel_tanpa_asal_di_silver(silver, gold):
    p = gold["panel"]
    p.loc[terisi(p), "_berkas_raw"] = "bps/2099-01-01/tidak_ada.csv"
    assert not aturan("gold: sel tertelusur ke Silver")(silver, gold).empty


def test_kategori_di_luar_daftar(silver, gold):
    gold["rekonsiliasi"].loc[0, "kategori"] = "beda saja"
    assert not aturan("rekonsiliasi: kategori baku")(silver, gold).empty


def test_selisih_salah_hitung(silver, gold):
    r = gold["rekonsiliasi"]
    ada = r.index[r["selisih"].notna()]
    if not len(ada):
        pytest.skip("tidak ada selisih yang dihitung")
    r.loc[ada[0], "selisih"] = r.loc[ada[0], "selisih"] + 5
    assert not aturan("rekonsiliasi: selisih = utama − pembanding")(silver, gold).empty


def test_periode_utama_dibuang(silver, gold):
    r = gold["rekonsiliasi"]
    utama = r[r["asal"] != "hanya_pembanding"]
    if utama.empty:
        pytest.skip("tidak ada baris dengan nilai utama")
    pertama = utama.iloc[0]
    gold["rekonsiliasi"] = r.drop(index=utama.index[0])
    assert not aturan("rekonsiliasi: periode utama tidak dibuang")(silver, gold).empty
