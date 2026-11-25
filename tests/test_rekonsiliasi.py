"""Pengujian tabel rekonsiliasi Gold Sprint 2."""
import pandas as pd
import pytest

from src import konfigurasi as K
from src.gold import rekonsiliasi
from src.laporan import ROOT

JALUR = ROOT / "data" / "gold" / "rekonsiliasi.parquet"


@pytest.fixture
def rek():
    if not JALUR.exists():
        pytest.skip("jalankan src/gold/rekonsiliasi.py dulu")
    return pd.read_parquet(JALUR)


@pytest.fixture
def nas():
    return pd.read_parquet(ROOT / "data" / "gold" / "nasional.parquet")


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
    assert set(p2["tahun_utama"]) == {"2012", "2017"}
    assert set(p2["tahun_pembanding"]) == {"2011", "2016"}
    assert (p2["selisih_tahun"] == 1).all()
    assert (p2["jenis_perbandingan"] == "tahun_terdekat").all()
    assert p2["catatan"].str.contains("tahun terdekat").all()


def test_kategori_baku(rek):
    assert set(rek["kategori_baku"]) == set(K.KATEGORI_BAKU.values())
    for pasangan, kategori in K.KATEGORI_BAKU.items():
        assert set(rek.loc[rek["pasangan_id"] == pasangan, "kategori_baku"]) == {kategori}
    tanpa = rek[rek["kategori"] == "tanpa pasangan"]
    assert set(tanpa["pasangan_id"]) == {"P1", "P3", "P4"}
    assert tanpa["selisih"].isna().all()
    assert tanpa["nilai_utama"].isna().all()
    assert tanpa["nilai_pembanding"].notna().all()


def test_nilai_dan_selisih_dari_nasional(rek, nas):
    indeks = nas.set_index(["seri_kode", "rincian", "periode"])
    for r in rek[rek["selisih"].notna()].itertuples():
        u = indeks.loc[(r.seri_utama, r.rincian_utama, str(r.tahun_utama)), "nilai"]
        b = indeks.loc[(r.seri_pembanding, r.rincian_pembanding, str(r.tahun_pembanding)), "nilai"]
        assert r.nilai_utama == u
        assert r.nilai_pembanding == b
        assert abs(r.selisih - (u - b)) < 1e-9
        assert abs(r.selisih_relatif - 100 * (u - b) / b) < 1e-9
    for r in rek[rek["asal"] == "hanya_pembanding"].itertuples():
        b = indeks.loc[(r.seri_pembanding, r.rincian_pembanding, r.periode), "nilai"]
        assert r.nilai_pembanding == b
        assert pd.isna(r.nilai_utama)
        assert pd.isna(r.selisih)


def test_selisih_relatif_median(rek):
    utama_prov = rek[rek["selisih"].notna() & rek["seri_utama"].isin(["var1394", "var1353"])]
    assert round(utama_prov["selisih_relatif"].abs().median(), 2) == 8.68
    assert round(rek["selisih_relatif"].abs().median(), 2) == 5.61


def test_rekonsiliasi_deterministik(nas):
    pd.testing.assert_frame_equal(
        rekonsiliasi.jalankan(nas)["rekonsiliasi"],
        rekonsiliasi.jalankan(nas)["rekonsiliasi"])
