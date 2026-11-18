"""Ekstraksi: semua berkas MANIFEST tertangani, kolom jejak ada, dan kunci JSON BPS terpotong benar."""
import pytest

from src.common.manifest import RAW, baca

pytestmark = pytest.mark.skipif(not (RAW / "MANIFEST.csv").exists(), reason="jalankan python unduh_data.py dulu")


def test_semua_berkas_manifest_tertangani():
    from src import ekstraksi
    hasil = ekstraksi.jalankan()
    assert set(hasil["_hitung"]["berkas"]) == set(baca())


def test_setiap_baris_data_membawa_lineage():
    from src import ekstraksi
    hasil = ekstraksi.jalankan()
    for nama in ("bps_json", "bps_csv", "wdi_data"):
        if nama in hasil:
            df = hasil[nama]
            assert df["_berkas_raw"].notna().all() and df["_sha256_raw"].str.len().eq(64).all()


def test_kunci_json_bps_cocok_dengan_csv():
    """Pemotongan kunci datacontent menghasilkan pasangan wilayah-rincian-tahun-periode-nilai yang sama dengan CSV."""
    from src import ekstraksi
    hasil = ekstraksi.jalankan()
    if "bps_json" not in hasil or "bps_csv" not in hasil:
        pytest.skip("kasus tanpa BPS dua format")
    j = {(r.var_id, r.wilayah_id, r.turvar.strip(), r.tahun, r.turtahun.strip()): float(r.nilai)
         for r in hasil["bps_json"].itertuples()}
    c = {(r.var_id, r.wilayah_id, str(r.turvar).strip(), r.tahun, str(r.periode).strip()): float(r.nilai)
         for r in hasil["bps_csv"].itertuples()}
    assert j == c


def test_bnpb_sel_tergabung_diisi_dan_kode_kemendagri():
    """Rekap BNPB: sel Provinsi tergabung (merged) terisi ke semua barisnya; kode Kemendagri Papua dipetakan."""
    from src import wilayah as W
    from src.ekstraksi import bnpb
    berkas = [b for b in baca() if b.startswith("bnpb/") and "per-provinsi" in b and b.endswith(".xlsx")]
    if not berkas:
        pytest.skip("kasus tanpa rekap provinsi BNPB")
    d, _, hit = bnpb.baca_xlsx(berkas[0])
    assert hit["tata"] == "rekap"
    assert (d["nama_wilayah"] != "").all()
    assert d.groupby("nama_wilayah")["jenis_baris"].nunique().max() > 1   # satu provinsi, banyak jenis
    assert W.dari_kemendagri("94", "PAPUA TENGAH") == 9600
    assert W.dari_kemendagri("9604") == 9200           # kab Tambrauw -> Papua Barat Daya
    assert W.dari_nama("P A P U A") == 9400
    with pytest.raises(ValueError):
        W.dari_kemendagri("91", "PAPUA BARAT")          # kode Kemendagri 91 = Papua, bukan Papua Barat
