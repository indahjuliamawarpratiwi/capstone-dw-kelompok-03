"""Pengujian tabel rekonsiliasi Gold Sprint 2."""
import re

import pandas as pd
import pytest

from src import konfigurasi as K
from src.gold import rekonsiliasi
from src.laporan import ROOT

JALUR = ROOT / "data" / "gold" / "rekonsiliasi.parquet"


@pytest.fixture
def rek():
    if not JALUR.exists():
        pytest.skip("jalankan python pipeline.py dulu")
    return pd.read_parquet(JALUR)


@pytest.fixture
def nas():
    jalur = ROOT / "data" / "gold" / "nasional.parquet"
    if not jalur.exists():
        pytest.skip("jalankan python pipeline.py dulu")
    return pd.read_parquet(jalur)


def test_jumlah_baris_dan_selisih(rek):
    assert len(rek) == 28
    assert int(rek["selisih"].notna().sum()) == 20
    assert int((rek["kategori"] == "tanpa pasangan").sum()) == 8
    assert rek["asal"].value_counts().to_dict() == {"keduanya": 20, "hanya_pembanding": 8}
    assert rek["pasangan_id"].value_counts().sort_index().to_dict() == {"P1": 6, "P2": 2, "P3": 4, "P4": 16}


def test_kunci_unik(rek):
    kunci = ["pasangan_id", "seri_pembanding", "rincian_pembanding", "periode"]
    assert not rek.duplicated(kunci).any()


def test_p2_tahun_terdekat(rek):
    p2 = rek[rek["pasangan_id"] == "P2"]
    assert len(p2) == 2
    assert set(p2["periode"]) == {"2012", "2017"}
    assert p2["catatan"].str.contains("tahun terdekat").all()
    assert p2["selisih"].notna().all()
    assert p2["nilai_pembanding"].tolist() == pytest.approx([48.48956299, 36.10983276])


def test_kategori_baku(rek):
    assert set(rek["kategori"]) == {"metode berbeda", "definisi berbeda", "tanpa pasangan"}
    for pasangan, kategori in K.KATEGORI_BAKU.items():
        assert kategori in set(rek.loc[rek["pasangan_id"] == pasangan, "kategori"])
    tanpa = rek[rek["kategori"] == "tanpa pasangan"]
    assert set(tanpa["pasangan_id"]) == {"P1", "P3", "P4"}
    assert tanpa["selisih"].isna().all()
    assert tanpa["nilai_utama"].isna().all()
    assert tanpa["nilai_pembanding"].notna().all()
    assert (tanpa["asal"] == "hanya_pembanding").all()


def test_nilai_dan_selisih_dari_nasional(rek, nas):
    indeks = nas.set_index(["seri_kode", "rincian", "periode"])
    for r in rek[rek["selisih"].notna()].itertuples():
        u = indeks.loc[(r.seri_utama, r.rincian_utama, str(r.periode)), "nilai"]
        tahun_b = str(r.periode)
        catatan = r.catatan if isinstance(r.catatan, str) else ""
        cocok = re.search(r"pembanding tahun (\d{4})", catatan)
        if cocok:
            tahun_b = cocok.group(1)
        b = indeks.loc[(r.seri_pembanding, r.rincian_pembanding, tahun_b), "nilai"]
        assert r.nilai_utama == pytest.approx(u)
        assert r.nilai_pembanding == pytest.approx(b)
        assert r.selisih == pytest.approx(u - b)
        assert r.selisih_relatif == pytest.approx(100 * (u - b) / b)
    for r in rek[rek["asal"] == "hanya_pembanding"].itertuples():
        b = indeks.loc[(r.seri_pembanding, r.rincian_pembanding, str(r.periode)), "nilai"]
        assert r.nilai_pembanding == pytest.approx(b)
        assert pd.isna(r.nilai_utama)
        assert pd.isna(r.selisih)


def test_selisih_relatif_median(rek):
    utama_prov = rek[rek["selisih"].notna() & rek["seri_utama"].isin(["var1394", "var1353"])]
    assert round(utama_prov["selisih_relatif"].abs().median(), 2) == 8.68
    assert round(rek["selisih_relatif"].abs().median(), 2) == 5.61


def test_rekonsiliasi_deterministik(nas):
    pd.testing.assert_frame_equal(rekonsiliasi.jalankan(nas), rekonsiliasi.jalankan(nas))
