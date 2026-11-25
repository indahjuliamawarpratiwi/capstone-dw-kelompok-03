"""Aturan Gold diuji dengan salinan artefak yang sengaja dirusak (hanya di memori)."""
from pathlib import Path

import pandas as pd
import pytest

from src.validasi import gold as G

GOLD = Path("data/gold")


@pytest.fixture
def silver(silver_contoh):
    return silver_contoh.copy()


@pytest.fixture
def gold():
    return {
        "panel": pd.read_parquet(GOLD / "panel.parquet"),
        "nasional_gold": pd.read_parquet(GOLD / "nasional.parquet"),
        "rekonsiliasi": pd.read_parquet(GOLD / "rekonsiliasi.parquet"),
    }


def aturan(nama):
    return next(f for n, _, _, f in G.ATURAN if n == nama)


def harus_kosong(silver, gold, nama):
    buruk = aturan(nama)(silver, gold)
    assert buruk.empty, f"{nama}: {len(buruk)} baris melanggar"


def harus_ada(silver, gold, nama):
    buruk = aturan(nama)(silver, gold)
    assert not buruk.empty, f"kerusakan tidak tertangkap oleh {nama}"


def test_gold_asli_lolos(silver, gold):
    for nama, _, _, _ in G.ATURAN:
        harus_kosong(silver, gold, nama)


def test_sel_panel_kembar(silver, gold):
    gold["panel"] = pd.concat([gold["panel"], gold["panel"].iloc[[0]]], ignore_index=True)
    harus_ada(silver, gold, "gold: kunci panel unik")


def test_satuan_kedua_dalam_satu_indikator(silver, gold):
    p = gold["panel"]
    i = p.index[p["seri_kode"] == "var1394"][0]
    p.loc[i, "satuan"] = "per_1000_perempuan_seumur"
    harus_ada(silver, gold, "gold: satu satuan per indikator")


def test_status_sel_dan_nilai(silver, gold):
    p = gold["panel"]
    kosong = p.index[p["status_sel"] != "terisi"][0]
    p.loc[kosong, "nilai"] = 1.0
    harus_ada(silver, gold, "gold: status sel dan nilai")


def test_sel_tanpa_asal_di_silver(silver, gold):
    p = gold["panel"]
    terisi = p.index[p["status_sel"] == "terisi"][0]
    p.loc[terisi, "_berkas_raw"] = "bps/2099-01-01/tidak_ada.json"
    harus_ada(silver, gold, "gold: sel tertelusur ke Silver")


def test_nilai_diubah_di_gold(silver, gold):
    p = gold["panel"]
    terisi = p.index[p["status_sel"] == "terisi"][0]
    p.loc[terisi, "nilai"] = p.loc[terisi, "nilai"] + 1
    harus_ada(silver, gold, "gold: nilai sama dengan Silver")


def test_tabel_nasional_kembar(silver, gold):
    n = gold["nasional_gold"]
    gold["nasional_gold"] = pd.concat([n, n.iloc[[0]]], ignore_index=True)
    harus_ada(silver, gold, "gold: tabel nasional unik")


def test_kategori_di_luar_daftar(silver, gold):
    gold["rekonsiliasi"].loc[0, "kategori"] = "beda saja"
    harus_ada(silver, gold, "rekonsiliasi: kategori baku")


def test_selisih_salah_hitung(silver, gold):
    r = gold["rekonsiliasi"]
    ada = r.index[r["selisih"].notna()]
    r.loc[ada[0], "selisih"] = r.loc[ada[0], "selisih"] + 5
    harus_ada(silver, gold, "rekonsiliasi: selisih = utama − pembanding")
    pasangan = r.index[(r["asal"] == "keduanya") & r["selisih"].notna() & r["catatan"].isna()]
    if len(pasangan):
        r.loc[pasangan[0], "selisih"] = None
        harus_ada(silver, gold, "rekonsiliasi: baris berpasangan dihitung")


def test_periode_utama_dibuang(silver, gold):
    r = gold["rekonsiliasi"]
    buang = r.index[(r["pasangan_id"] == "P2") & (r["periode"] == "2012")]
    gold["rekonsiliasi"] = r.drop(index=buang)
    harus_ada(silver, gold, "rekonsiliasi: periode utama tidak dibuang")
