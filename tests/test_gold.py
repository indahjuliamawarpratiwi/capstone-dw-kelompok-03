"""Pengujian Gold: satu nilai per sel, pemisahan wilayah, rincian umur, penanda, dan pengulangan."""
import csv

import pandas as pd
import pytest

from src import konfigurasi as K
from src import wilayah as W
from src.gold import panel
from src.laporan import ROOT


@pytest.fixture
def gold_panel(silver_contoh):
    return panel.bentuk_panel(silver_contoh)


@pytest.fixture
def gold_nasional(silver_contoh):
    return panel.tabel_nasional(silver_contoh)


def _log():
    with (ROOT / "log-keputusan.csv").open(encoding="utf-8", newline="") as f:
        return {r[0]: r for r in list(csv.reader(f))[1:]}


def test_satu_nilai_per_kunci_gold(gold_panel):
    kunci = ["seri_kode", "wilayah_kode", "periode"]
    assert not gold_panel.duplicated(kunci).any()
    assert gold_panel.groupby(kunci).size().max() == 1


def test_tidak_ada_duplikasi_provinsi_periode_indikator(gold_panel):
    assert gold_panel["wilayah_kode"].ne(W.INDONESIA).all()
    assert gold_panel["seri_kode"].isin(["var1394", "var1353"]).all()
    assert (gold_panel["rincian"] == "total").all()


def test_pemisahan_panel_provinsi_dan_nasional(gold_panel, gold_nasional):
    assert (gold_panel["wilayah_kode"] != W.INDONESIA).all()
    assert "wilayah_kode" not in gold_nasional.columns
    assert set(gold_panel["seri_kode"]) == {"var1394", "var1353"}
    assert set(gold_nasional["seri_kode"]) == set(K.SERI)
    assert set(gold_nasional["seri_kode"]) - set(gold_panel["seri_kode"]) == {
        "MDG_0000000003", "SDGFPALL", "SP.ADO.TFRT"}
    utama = gold_nasional["seri_kode"].isin(["var1394", "var1353"])
    assert set(gold_nasional.loc[utama, "asal"]) == {"baris_indonesia"}
    assert set(gold_nasional.loc[~utama, "asal"]) == {"pembanding"}


def test_rincian_umur_konsisten(gold_nasional):
    mdg = gold_nasional[gold_nasional["seri_kode"] == "MDG_0000000003"]
    assert set(mdg["rincian"]) == {"umur=15-19"}
    assert "umur=10-14" not in set(gold_nasional["rincian"])
    assert not gold_nasional["rincian"].str.contains("Y10T14|Y15T19|Y15T49").any()
    bps = gold_nasional[gold_nasional["seri_kode"].isin(["var1394", "var1353"])]
    wdi = gold_nasional[gold_nasional["seri_kode"] == "SP.ADO.TFRT"]
    assert (bps["rincian"] == "total").all()
    assert (wdi["rincian"] == "total").all()
    assert len(gold_nasional) == 89


def test_silver_mempertahankan_kedua_rincian_umur(silver_contoh):
    mdg = silver_contoh[silver_contoh["seri_kode"] == "MDG_0000000003"]
    assert set(mdg["rincian"]) == {"umur=10-14", "umur=15-19"}
    assert int((mdg["rincian"] == "umur=10-14").sum()) == 12
    assert int((mdg["rincian"] == "umur=15-19").sum()) == 14


def test_nilai_nasional_sama_dengan_silver(silver_contoh, gold_nasional):
    kunci = ["seri_kode", "rincian", "periode", "_berkas_raw"]
    sumber = silver_contoh[silver_contoh["wilayah_kode"] == W.INDONESIA]
    gabung = gold_nasional[kunci + ["nilai"]].merge(
        sumber[kunci + ["nilai"]], on=kunci, how="left",
        suffixes=("_gold", "_silver"), validate="one_to_one")
    assert gabung["nilai_silver"].notna().all()
    pd.testing.assert_series_equal(gabung["nilai_gold"], gabung["nilai_silver"], check_names=False)


def test_penanda_anomali_terbawa(silver_contoh, gold_panel):
    kunci = ["seri_kode", "wilayah_kode", "periode"]
    penanda = gold_panel[gold_panel["penanda"] != ""]
    assert len(penanda) == 5
    assert set(penanda["penanda"]) == {"outlier", "patahan_wilayah"}
    assert not gold_panel["penanda"].str.contains("patahan seri").any()
    asli = silver_contoh.set_index(kunci)["nilai"]
    for r in penanda.itertuples():
        assert asli.loc[(r.seri_kode, r.wilayah_kode, r.periode)] == r.nilai
    assert int((gold_panel["status_sel"] == "terisi").sum()) == 134
    assert int((gold_panel["status_sel"] != "terisi").sum()) == 18


def test_nilai_panel_terisi_sama_dengan_silver(silver_contoh):
    jalur = ROOT / "data" / "gold" / "panel.parquet"
    if not jalur.exists():
        pytest.skip("jalankan pipeline.py dulu untuk membuat data/gold/panel.parquet")
    tersimpan = pd.read_parquet(jalur)
    terisi = tersimpan[tersimpan["status_sel"] == "terisi"]
    assert len(terisi) == 134
    kunci = ["seri_kode", "wilayah_kode", "periode"]
    sumber = silver_contoh[(silver_contoh["seri_kode"].isin(["var1394", "var1353"]))
                           & (silver_contoh["wilayah_kode"] != W.INDONESIA)
                           & (silver_contoh["rincian"] == "total")]
    gabung = terisi[kunci + ["nilai"]].merge(
        sumber[kunci + ["nilai"]], on=kunci, how="left",
        suffixes=("_gold", "_silver"), validate="one_to_one")
    assert gabung["nilai_silver"].notna().all()
    pd.testing.assert_series_equal(gabung["nilai_gold"], gabung["nilai_silver"], check_names=False)


def test_jumlah_baris_tidak_terpilih_sesuai_log(silver_contoh, gold_panel, gold_nasional):
    catatan = _log()
    bps = int((silver_contoh["sumber"] == "bps").sum())
    terisi = int((gold_panel["status_sel"] == "terisi").sum())
    assert int(catatan["K-035"][8]) == bps - terisi
    assert catatan["K-036"][8] == "134"
    assert int(catatan["K-041"][8]) == len(silver_contoh) - len(gold_nasional)
    for identitas in ["K-037", "K-038", "K-039", "K-040"]:
        assert int(catatan[identitas][8]) == 0


def test_pipeline_dapat_dijalankan_ulang_konsisten(silver_contoh):
    pd.testing.assert_frame_equal(panel.bentuk_panel(silver_contoh), panel.bentuk_panel(silver_contoh))
    pd.testing.assert_frame_equal(panel.tabel_nasional(silver_contoh), panel.tabel_nasional(silver_contoh))
