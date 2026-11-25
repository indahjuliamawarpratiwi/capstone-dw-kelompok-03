"""Tahap 4 Sprint 2 — tabel nasional Gold: seri utama dan pembanding berdampingan per periode."""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat
from src.silver import deret

KOLOM = ["seri_kode", "rincian", "sumber", "periode", "jenis_periode", "nilai", "satuan",
         "batas_bawah", "batas_atas", "rujukan_tahun", "asal", "_berkas_raw", "_sha256_raw"]


def _rincian_dipakai():
    pakai = {}
    for p in K.PASANGAN:
        utama = p["utama"].split(",")[0].strip()
        pakai.setdefault(utama, set()).add(p.get("rincian_utama", "total"))
        for seri, rincian in p["pembanding"]:
            pakai.setdefault(seri, set()).add(rincian)
    return pakai


def jalankan(silver):
    pakai = _rincian_dipakai()
    nas = silver[silver["wilayah_kode"] == W.INDONESIA].copy()
    nas = nas[[r in ({"total"} | pakai.get(s, set())) for s, r in zip(nas["seri_kode"], nas["rincian"])]]
    nas = nas.assign(_p=nas["_berkas_raw"].map(deret.peringkat)).sort_values(["_p", "_berkas_raw"])
    nas = nas.drop_duplicates(["seri_kode", "rincian", "periode"]).drop(columns="_p")
    tingkat = {k: s["tingkat"] for k, s in K.SERI.items()}
    nas["asal"] = nas["seri_kode"].map(lambda s: "baris_indonesia" if tingkat.get(s) == "provinsi" else "pembanding")
    for c in KOLOM:
        if c not in nas:
            nas[c] = None
    nas = nas[KOLOM].sort_values(["seri_kode", "rincian", "periode"]).reset_index(drop=True)
    for c in ("batas_bawah", "batas_atas", "rujukan_tahun"):
        nas[c] = pd.to_numeric(nas[c].astype(object).where(nas[c].notna(), None), errors="coerce").astype("float64")
    (ROOT / "data" / "gold").mkdir(parents=True, exist_ok=True)
    nas.to_parquet(ROOT / "data" / "gold" / "nasional.parquet", index=False)
    catat(baris_nasional_gold=len(nas), seri_nasional_gold=int(nas["seri_kode"].nunique()))
    return nas
