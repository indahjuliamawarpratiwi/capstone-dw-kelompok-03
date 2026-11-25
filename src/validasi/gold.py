"""Aturan validasi Gold Sprint 2.

Setiap aturan = (nama, keterangan, keras, fungsi(silver, gold) -> DataFrame baris yang melanggar).
Struktur `gold` mengikuti hasil `src.gold.jalankan`: `panel`, `nasional_gold`, `rekonsiliasi`.
Nama aturan mengikuti kunci dosen; kolom `seri_kode` lokal berperan sebagai `indikator` pada kunci.
"""
import pandas as pd

from src.gold.rekonsiliasi import KATEGORI
from src.silver.deret import JUMLAH

STATUS = {"terisi", "missing", "tidak_diterbitkan", "belum_ada", "batas_lama"}
KUNCI_PANEL = ["seri_kode", "wilayah_kode", "periode"]
KUNCI_SUMBER = ["seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]


def _nasional(gold):
    return gold.get("nasional_gold", gold.get("nasional"))


def kunci_panel_unik(silver, gold):
    p = gold["panel"]
    return p[p.duplicated(KUNCI_PANEL, keep=False)]


def satu_satuan_per_indikator(silver, gold):
    p = gold["panel"]
    terisi = p[p["status_sel"] == "terisi"]
    n = terisi.groupby("seri_kode")["satuan"].nunique()
    return terisi[terisi["seri_kode"].isin(n[n != 1].index) | terisi["satuan"].isna()]


def status_dan_nilai(silver, gold):
    p = gold["panel"]
    return p[~p["status_sel"].isin(STATUS) | ((p["status_sel"] == "terisi") != p["nilai"].notna())]


def tertelusur_ke_silver(silver, gold):
    p = gold["panel"][gold["panel"]["status_sel"] == "terisi"]
    s = silver[KUNCI_SUMBER + ["nilai"]]
    biasa = p[p["rincian"] != JUMLAH].merge(s, on=KUNCI_SUMBER, how="left", suffixes=("", "_silver"), indicator=True)
    jml = p[p["rincian"] == JUMLAH].merge(
        s.drop(columns=["rincian", "nilai"]).drop_duplicates(),
        on=["seri_kode", "wilayah_kode", "periode", "_berkas_raw"], how="left", indicator=True)
    buruk = pd.concat([biasa[biasa["_merge"] != "both"], jml[jml["_merge"] != "both"]])
    return buruk.drop(columns="_merge")


def nilai_sama_dengan_silver(silver, gold):
    p = gold["panel"]
    p = p[(p["status_sel"] == "terisi") & (p["rincian"] != JUMLAH)]
    m = p.merge(silver[KUNCI_SUMBER + ["nilai"]], on=KUNCI_SUMBER, suffixes=("", "_silver"))
    return m[(m["nilai"] - m["nilai_silver"]).abs() > 1e-9]


def nasional_unik(silver, gold):
    n = _nasional(gold)
    return n[n.duplicated(["seri_kode", "rincian", "periode"], keep=False)]


def kategori_baku(silver, gold):
    r = gold["rekonsiliasi"]
    return r[~r["kategori"].isin(KATEGORI) | r["penjelasan"].isna() | (r["penjelasan"].str.strip() == "")]


def selisih_konsisten(silver, gold):
    r = gold["rekonsiliasi"]
    h = r[r["selisih"].notna()]
    return h[(h["selisih"] - (h["nilai_utama"] - h["nilai_pembanding"])).abs() > 1e-6]


def berpasangan_dihitung(silver, gold):
    r = gold["rekonsiliasi"]
    return r[(r["jenis"] == "selisih") & (r["asal"] == "keduanya")
             & r["selisih"].isna() & r["catatan"].isna()]


def periode_utama_tampil(silver, gold):
    from src import konfigurasi as K
    r, n = gold["rekonsiliasi"], _nasional(gold)
    hilang = []
    for p in K.PASANGAN:
        utama = p["utama"].split(",")[0].strip()
        rincian = p.get("rincian_utama", "total")
        ada = set(n.loc[(n["seri_kode"] == utama) & (n["rincian"] == rincian), "periode"])
        for seri_b, *_ in p["pembanding"]:
            tampil = set(r.loc[(r["pasangan_id"] == p["id"]) & (r["seri_pembanding"] == seri_b), "periode"])
            hilang += [{"pasangan_id": p["id"], "seri_pembanding": seri_b, "periode": x}
                       for x in sorted(ada - tampil)]
    return pd.DataFrame(hilang, columns=["pasangan_id", "seri_pembanding", "periode"])


def konsistensi_sql(silver, gold):
    """Pemeriksaan tambahan (di luar 10 aturan): jumlah baris DuckDB sama dengan sumbernya."""
    import duckdb
    from src.gold.muat_sql import DB
    if not DB.exists():
        return pd.DataFrame(columns=["tabel", "sql", "sumber"])
    sumber = {
        "silver": len(silver), "gold_panel": len(gold["panel"]),
        "gold_nasional": len(_nasional(gold)), "rekonsiliasi": len(gold["rekonsiliasi"]),
        "dokumen_mentah": 9, "seri": 5,
    }
    con = duckdb.connect(str(DB), read_only=True)
    baris = []
    for tabel, n in sumber.items():
        ada = con.execute(f"SELECT count(*) FROM {tabel}").fetchone()[0]
        if ada != n:
            baris.append({"tabel": tabel, "sql": ada, "sumber": n})
    con.close()
    return pd.DataFrame(baris, columns=["tabel", "sql", "sumber"])


ATURAN = [
    ("gold: kunci panel unik", "seri_kode + wilayah_kode + periode tidak kembar", True, kunci_panel_unik),
    ("gold: satu satuan per indikator", "satu indikator panel hanya punya satu satuan", True, satu_satuan_per_indikator),
    ("gold: status sel dan nilai", "status sel baku; nilai ada jika dan hanya jika sel terisi", True, status_dan_nilai),
    ("gold: sel tertelusur ke Silver", "setiap sel terisi punya baris Silver asal (seri, wilayah, periode, berkas)",
     True, tertelusur_ke_silver),
    ("gold: nilai sama dengan Silver", "nilai panel = nilai Silver asalnya (tidak ada nilai yang diubah di Gold)",
     True, nilai_sama_dengan_silver),
    ("gold: tabel nasional unik", "seri + rincian + periode tidak kembar", True, nasional_unik),
    ("rekonsiliasi: kategori baku", "kategori dari daftar baku; penjelasan tidak kosong", True, kategori_baku),
    ("rekonsiliasi: selisih = utama − pembanding", "selisih dihitung ulang dan cocok", True, selisih_konsisten),
    ("rekonsiliasi: baris berpasangan dihitung", "pasangan selisih dengan dua nilai punya selisih, atau catatan mengapa "
     "tidak", True, berpasangan_dihitung),
    ("rekonsiliasi: periode utama tidak dibuang", "setiap tahun seri utama di tabel nasional muncul di rekonsiliasi",
     True, periode_utama_tampil),
]
