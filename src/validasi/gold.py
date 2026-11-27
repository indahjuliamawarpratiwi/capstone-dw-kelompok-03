"""Aturan validasi Gold dan rekonsiliasi (Sprint 2).

Memeriksa:
1. Kunci panel unik (gold: kunci panel unik)
2. Satuan satu per indikator (gold: satu satuan per indikator)
3. Status sel dan nilai konsisten (gold: status sel dan nilai)
4. Sel tertelusur ke Silver (gold: sel tertelusur ke Silver)
5. Nilai sama dengan Silver (gold: nilai sama dengan Silver)
6. Tabel nasional unik (gold: tabel nasional unik)
7. Kategori rekonsiliasi baku (rekonsiliasi: kategori baku)
8. Perhitungan selisih rekonsiliasi (rekonsiliasi: selisih = utama − pembanding)
9. Baris berpasangan dihitung (rekonsiliasi: baris berpasangan dihitung)
10. Periode utama tidak dibuang (rekonsiliasi: periode utama tidak dibuang)
"""
from pathlib import Path

import duckdb
import pandas as pd

from src import konfigurasi as K
from src.laporan import ROOT

KATEGORI_BAKU_REK = {
    "definisi berbeda", "metode berbeda", "vintage berbeda",
    "cakupan berbeda", "belum terjelaskan", "tanpa pasangan", "tidak berselisih",
}


def kunci_panel_unik(silver, gold):
    """Kunci panel Gold (seri_kode, wilayah_kode, periode) tidak kembar."""
    p = gold["panel"]
    kunci = ["seri_kode", "wilayah_kode", "periode"]
    return p[p.duplicated(subset=kunci, keep=False)]


def satu_satuan_per_indikator(silver, gold):
    """Setiap indikator di panel Gold hanya memiliki satu satuan baku."""
    p = gold["panel"]
    banyak = p.groupby("seri_kode")["satuan"].nunique()
    gagal = banyak[banyak > 1].index
    if len(gagal):
        return p[p["seri_kode"].isin(gagal)]
    return pd.DataFrame()


def status_sel_dan_nilai(silver, gold):
    """Status sel 'terisi' wajib memiliki nilai, sel kosong tidak boleh memiliki nilai."""
    p = gold["panel"]
    salah_terisi = (p["status_sel"] == "terisi") & p["nilai"].isna()
    salah_kosong = (p["status_sel"] != "terisi") & p["nilai"].notna()
    return p[salah_terisi | salah_kosong]


def sel_tertelusur_ke_silver(silver, gold):
    """Setiap sel terisi di Gold harus tertelusur ke berkas mentah sah di Silver."""
    p = gold["panel"]
    terisi = p[p["status_sel"] == "terisi"]
    berkas_silver = set(silver["_berkas_raw"].dropna().unique())
    return terisi[~terisi["_berkas_raw"].isin(berkas_silver)]


def nilai_sama_dengan_silver(silver, gold):
    """Nilai pada sel terisi di panel Gold sama dengan nilai di Silver."""
    p = gold["panel"]
    terisi = p[p["status_sel"] == "terisi"].copy()
    s = silver[silver["rincian"] == "total"][["seri_kode", "wilayah_kode", "periode", "nilai"]].drop_duplicates(["seri_kode", "wilayah_kode", "periode"])
    gab = terisi.merge(s, on=["seri_kode", "wilayah_kode", "periode"], how="left", suffixes=("_gold", "_silver"))
    beda = gab[gab["nilai_silver"].isna() | ((gab["nilai_gold"] - gab["nilai_silver"]).abs() > 1e-6)]
    return beda


def tabel_nasional_unik(silver, gold):
    """Tabel nasional Gold tidak memiliki baris kembar pada (seri_kode, rincian, periode)."""
    n = gold["nasional_gold"]
    kunci = ["seri_kode", "rincian", "periode"]
    return n[n.duplicated(subset=kunci, keep=False)]


def rekonsiliasi_kategori_baku(silver, gold):
    """Setiap baris rekonsiliasi memiliki kategori yang termasuk dalam daftar baku."""
    r = gold["rekonsiliasi"]
    return r[~r["kategori"].isin(KATEGORI_BAKU_REK)]


def rekonsiliasi_selisih_hitung(silver, gold):
    """Selisih rekonsiliasi adalah nilai utama dikurangi nilai pembanding."""
    r = gold["rekonsiliasi"]
    ada = r[r["selisih"].notna()]
    return ada[(ada["selisih"] - (ada["nilai_utama"] - ada["nilai_pembanding"])).abs() > 1e-4]


def rekonsiliasi_baris_berpasangan_dihitung(silver, gold):
    """Baris dengan asal='keduanya' dan tanpa catatan khusus wajib dihitung selisihnya."""
    r = gold["rekonsiliasi"]
    return r[(r["asal"] == "keduanya") & r["catatan"].isna() & r["selisih"].isna()]


def rekonsiliasi_periode_utama_tidak_dibuang(silver, gold):
    """Seluruh periode seri utama pada setiap pasangan tidak boleh dibuang dari rekonsiliasi."""
    r = gold["rekonsiliasi"]
    kurang = []
    for p in K.PASANGAN:
        pid = p["id"]
        utama = p["utama"].split(",")[0].strip()
        rincian = p.get("rincian_utama", "total")
        s_utama = silver[(silver["seri_kode"] == utama) & (silver["rincian"] == rincian) & (silver["wilayah_kode"] == 9999)]
        periode_utama = set(s_utama["periode"].dropna().astype(str))
        r_pasangan = r[r["pasangan_id"] == pid]
        periode_di_rek = set(r_pasangan["periode"].dropna().astype(str))
        hilang = periode_utama - periode_di_rek
        if hilang:
            kurang.append({"pasangan_id": pid, "periode_hilang": list(hilang)})
    if kurang:
        return pd.DataFrame(kurang)
    return pd.DataFrame()


def konsistensi_sql(silver, gold):
    """Konsistensi tabel DuckDB terhadap Silver."""
    db_path = ROOT / "data" / "gold" / "gudang.duckdb"
    if not db_path.exists():
        return pd.DataFrame([{"keterangan": "gudang.duckdb tidak ditemukan"}])
    try:
        with duckdb.connect(str(db_path), read_only=True) as con:
            n = con.execute("SELECT count(*) FROM silver").fetchone()[0]
        if n != len(silver):
            return pd.DataFrame([{"keterangan": "jumlah baris duckdb != silver", "duckdb": n, "silver": len(silver)}])
    except Exception as e:
        return pd.DataFrame([{"error": str(e)}])
    return pd.DataFrame()


ATURAN = [
    ("gold: kunci panel unik", "kunci panel Gold (seri_kode x wilayah_kode x periode) tidak kembar", True, kunci_panel_unik),
    ("gold: satu satuan per indikator", "setiap indikator/seri hanya punya satu satuan baku", True, satu_satuan_per_indikator),
    ("gold: status sel dan nilai", "sel terisi memiliki nilai, sel kosong tidak memiliki nilai", True, status_sel_dan_nilai),
    ("gold: sel tertelusur ke Silver", "setiap sel terisi di Gold berasal dari berkas raw sah di Silver", True, sel_tertelusur_ke_silver),
    ("gold: nilai sama dengan Silver", "nilai sel terisi di Gold sama dengan nilai di Silver", True, nilai_sama_dengan_silver),
    ("gold: tabel nasional unik", "kunci tabel nasional Gold (seri_kode x rincian x periode) tidak kembar", True, tabel_nasional_unik),
    ("rekonsiliasi: kategori baku", "kategori rekonsiliasi termasuk dalam daftar baku", True, rekonsiliasi_kategori_baku),
    ("rekonsiliasi: selisih = utama − pembanding", "selisih rekonsiliasi sama dengan nilai utama dikurangi nilai pembanding", True, rekonsiliasi_selisih_hitung),
    ("rekonsiliasi: baris berpasangan dihitung", "baris berpasangan tanpa catatan khusus wajib dihitung selisihnya", True, rekonsiliasi_baris_berpasangan_dihitung),
    ("rekonsiliasi: periode utama tidak dibuang", "seluruh periode seri utama tetap ada di tabel rekonsiliasi", True, rekonsiliasi_periode_utama_tidak_dibuang),
]
