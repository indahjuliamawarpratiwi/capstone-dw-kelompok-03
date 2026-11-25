"""Pengujian pemuatan Silver dan Gold ke DuckDB."""
import duckdb
import pandas as pd
import pytest

from src.gold.muat_sql import DB, DDL

SQL = "select table_name from information_schema.tables where table_schema = 'main' order by table_name"
TABLES = ["dokumen_mentah", "gold_nasional", "gold_panel", "rekonsiliasi", "seri", "silver"]
JUMLAH = {"seri": 5, "silver": 235, "gold_panel": 152, "gold_nasional": 89,
          "rekonsiliasi": 28, "dokumen_mentah": 9}
KUNCI = {"seri": ["seri_kode"], "silver": ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"],
         "gold_panel": ["indikator", "wilayah_kode", "periode"],
         "gold_nasional": ["seri_kode", "rincian", "periode"],
         "rekonsiliasi": ["pasangan_id", "seri_pembanding", "rincian_pembanding", "periode"],
         "dokumen_mentah": ["_berkas_raw"]}


@pytest.fixture
def con():
    if not DB.exists():
        pytest.skip("jalankan src/gold/muat_sql.py dulu")
    return duckdb.connect(str(DB), read_only=True)


def test_daftar_tabel(con):
    assert [r[0] for r in con.execute(SQL).fetchall()] == TABLES


def test_jumlah_baris(con):
    for tabel, n in JUMLAH.items():
        assert con.execute(f"select count(*) from {tabel}").fetchone()[0] == n


def test_kunci_unik(con):
    for tabel, kunci in KUNCI.items():
        kolom = ", ".join(kunci)
        ganda = con.execute(f"select count(*) from (select {kolom} from {tabel} group by {kolom} having count(*) > 1)").fetchone()[0]
        assert ganda == 0


def test_hasil_gold_sama_dengan_parquet(con):
    pasangan = [("gold_panel", ["indikator", "wilayah_kode", "periode"], "panel", ["seri_kode", "wilayah_kode", "periode"]),
                ("gold_nasional", ["seri_kode", "rincian", "periode"], "nasional", ["seri_kode", "rincian", "periode"]),
                ("rekonsiliasi", ["pasangan_id", "seri_pembanding", "rincian_pembanding", "periode"],
                 "rekonsiliasi", ["pasangan_id", "seri_pembanding", "rincian_pembanding", "periode"])]
    for tabel, kunci_sql, berkas, kunci_parquet in pasangan:
        d = pd.read_parquet(f"data/gold/{berkas}.parquet")
        assert len(d) == con.execute(f"select count(*) from {tabel}").fetchone()[0]
        if tabel == "gold_panel":
            kunci_sql = ["seri_kode", "wilayah_kode", "periode"]
        for kolom in kunci_sql:
            assert con.execute(f"select count(distinct {kolom}) from {tabel}").fetchone()[0] == d[kolom].nunique()


def test_constraint(kon=None):
    mem = duckdb.connect(":memory:")
    for f in DDL:
        teks = "\n".join(b for b in f.read_text(encoding="utf-8").splitlines() if not b.strip().startswith("--"))
        for perintah in teks.split(";"):
            if perintah.strip():
                mem.execute(perintah)
    mem.execute("insert into seri values ('var1394','bps','provinsi','nama','persen','3.7.1')")
    baris = ("var1394", "var1394", "total", 1100, "Aceh", "2012", "tahun", 1.0,
             "persen", "terisi", None, None, "berkas", "sha")
    mem.execute("insert into gold_panel values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", baris)
    with pytest.raises(duckdb.ConstraintException):
        mem.execute("insert into gold_panel values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", baris)
    rusak = list(baris)
    rusak[9] = "status_salah"
    with pytest.raises(duckdb.ConstraintException):
        mem.execute("insert into gold_panel values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rusak)
    mem.execute("insert into rekonsiliasi values ('P1','selisih','var1353','total','SP.ADO.TFRT','total','2012',48.0,44.616,'per_1000_perempuan_seumur',3.384,7.58,'keduanya','metode berbeda','alasan',NULL)")
    with pytest.raises(duckdb.ConstraintException):
        mem.execute("insert into rekonsiliasi values ('P1','selisih','var1353','total','SP.ADO.TFRT','total','2012',48.0,44.616,'per_1000_perempuan_seumur',3.384,7.58,'keduanya','kategori salah','alasan',NULL)")
    with pytest.raises(duckdb.ConstraintException):
        mem.execute("insert into rekonsiliasi values ('P1','selisih','var1353','total','SP.ADO.TFRT','total','2013',48.0,44.616,'per_1000_perempuan_seumur',99.0,7.58,'keduanya','metode berbeda','alasan',NULL)")
    mem.close()
