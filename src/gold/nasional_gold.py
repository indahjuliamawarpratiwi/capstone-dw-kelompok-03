"""Persiapan tahap 6 — tabel nasional Gold: seri utama dan pembanding berdampingan per periode.
Keluaran: data/gold/nasional.parquet.
"""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat, tabel_md, tulis
from src.silver import deret

KOLOM = ["seri_kode", "rincian", "sumber", "periode", "jenis_periode", "nilai", "satuan", "batas_bawah", "batas_atas",
         "rujukan_tahun", "asal", "_berkas_raw", "_sha256_raw"]


def rincian_dipakai():
    pakai = {}
    for p in K.PASANGAN:
        pakai.setdefault(p["utama"].split(",")[0].strip(), set()).update(
            p.get("rincian_utama_jumlah") or [p.get("rincian_utama", "total")])
        for s, r in p["pembanding"]:
            pakai.setdefault(s, set()).add(r)
    return pakai


def satu_per_sel(g):
    g = g.assign(_p=g["_berkas_raw"].map(deret.peringkat)).sort_values(["_p", "_berkas_raw"])
    return g.drop_duplicates(["seri_kode", "rincian", "periode"]).drop(columns="_p")


def agregat(silver):
    """GOLD_AGREGAT = {seri: dict(rincian=..., alasan=..., berkas_sama=bool)}: angka nasional = jumlah provinsi."""
    bagian = []
    for seri, a in getattr(K, "GOLD_AGREGAT", {}).items():
        r = a.get("rincian", "total")
        s = silver[(silver["seri_kode"] == seri) & (silver["rincian"] == r) & (silver["wilayah_kode"] != W.INDONESIA)]
        if a.get("berkas_sama"):
            # hanya baris provinsi dari berkas yang sama dengan baris INDONESIA-nya (satu tabel dibandingkan dengan
            # dirinya sendiri, bukan dengan berkas lain)
            ind = silver[(silver["seri_kode"] == seri) & (silver["rincian"] == r) & (silver["wilayah_kode"] == W.INDONESIA)]
            s = s[s.set_index(["periode", "_berkas_raw"]).index.isin(ind.set_index(["periode", "_berkas_raw"]).index)]
        s = s.assign(_p=s["_berkas_raw"].map(deret.peringkat)).sort_values(["_p", "_berkas_raw"]) \
            .drop_duplicates(["wilayah_kode", "periode"])
        g = s.groupby("periode", as_index=False).agg(
            nilai=("nilai", "sum"), jenis_periode=("jenis_periode", "first"), sumber=("sumber", "first"),
            satuan=("satuan", "first"), _berkas_raw=("_berkas_raw", lambda x: ";".join(sorted(set(x)))))
        g = g.assign(seri_kode=seri + " (agregat provinsi)", rincian=r, asal="agregat", _sha256_raw=None,
                     batas_bawah=None, batas_atas=None, rujukan_tahun=None)
        bagian.append(g)
    return bagian


def tulis_laporan(t, n_sql=None):
    """Laporan tabel nasional; jumlah baris Parquet, SQL, dan laporan harus sama."""
    rekap = (t.groupby(["seri_kode", "asal"], sort=False)
             .agg(baris=("periode", "size"), periode_awal=("periode", "min"),
                  periode_akhir=("periode", "max"),
                  rincian=("rincian", lambda s: ", ".join(sorted(set(map(str, s))))),
                  sumber=("sumber", "first"))
             .reset_index())
    asal_seri = (t.groupby("seri_kode", as_index=False)["asal"]
                 .agg(lambda s: ", ".join(sorted(set(s)))).rename(columns={"asal": "asal_seri"}))
    isi = t[["periode", "seri_kode", "rincian", "nilai", "satuan", "asal", "_berkas_raw"]]
    sql_teks = f"{n_sql} baris" if n_sql is not None else "diverifikasi saat muat SQL"
    status = "sama" if n_sql == len(t) else ("belum dicek" if n_sql is None else "BEDA")
    tulis("tabel-nasional-gold.md", "\n\n".join([
        "# Tabel nasional Gold (tahap 6)",
        "Dihasilkan `python pipeline.py` (`src/gold/nasional_gold.py`) dari Silver. Berkas utama: "
        "`data/gold/nasional.parquet`; alias kompatibilitas: `data/gold/tabel-nasional.csv` dan "
        "`data/gold/tabel-nasional.parquet`.",
        f"- Butir: satu baris per **periode x seri**; **{len(t)} baris**, "
        f"{t['seri_kode'].nunique()} seri, {t['periode'].nunique()} periode.",
        f"- Parquet `data/gold/nasional.parquet`: **{len(t)} baris**.",
        f"- SQL `gold_nasional`: **{sql_teks}** (status: **{status}**).",
        f"- Laporan ini: **{len(isi)} baris** pada tabel bagian 3.",
        "- Seri utama: `var1394`, `var1353`. Pembanding: `MDG_0000000003`, `SDGFPALL`, `SP.ADO.TFRT`.",
        "- `asal` menyatakan asal setiap angka: `baris_indonesia`, `pembanding`, atau `agregat`.",
        "- BPS menerbitkan baris Indonesia (kode 9999) untuk kedua seri utama pada 2012 dan 2017, sehingga "
        "tidak ada agregasi provinsi. Bila baris Indonesia tidak tersedia, seri tidak diagregasi dan dinyatakan "
        "tidak punya padanan nasional karena bobot populasi perempuan 15-19 tidak tersedia di paket.",
        "- `MDG_0000000003` memakai rincian `umur=15-19`; rincian `10-14` tidak dipakai karena penyebutnya berbeda.",
        "## 1. Rekap per seri dan asal",
        tabel_md(rekap),
        "## 2. Asal per seri",
        tabel_md(asal_seri),
        "## 3. Semua baris",
        tabel_md(isi),
    ]))


def jalankan(silver):
    pakai = rincian_dipakai()
    nas = silver[silver["wilayah_kode"] == W.INDONESIA]
    nas = nas[[r in ({"total"} | pakai.get(s, set())) for s, r in zip(nas["seri_kode"], nas["rincian"])]]
    nas = satu_per_sel(nas.copy())
    tingkat = {k: s["tingkat"] for k, s in K.SERI.items()}
    nas["asal"] = nas["seri_kode"].map(lambda s: "baris_indonesia" if tingkat.get(s) == "provinsi" else "pembanding")
    t = pd.concat([nas, *agregat(silver)], ignore_index=True)
    for c in KOLOM:
        if c not in t:
            t[c] = None
    t = t[KOLOM].sort_values(["seri_kode", "rincian", "periode"]).reset_index(drop=True)
    for c in ("batas_bawah", "batas_atas", "rujukan_tahun"):
        # baris agregat membawa None, baris Silver Int64 <NA>: samakan dulu ke float
        t[c] = pd.to_numeric(t[c].astype(object).where(t[c].notna(), None), errors="coerce").astype("float64")
    (ROOT / "data" / "gold").mkdir(parents=True, exist_ok=True)
    t.to_parquet(ROOT / "data" / "gold" / "nasional.parquet", index=False)
    t.to_csv(ROOT / "data" / "gold" / "tabel-nasional.csv", index=False)
    t.to_parquet(ROOT / "data" / "gold" / "tabel-nasional.parquet", index=False)
    catat(baris_nasional_gold=len(t), seri_nasional_gold=int(t["seri_kode"].nunique()))
    tulis_laporan(t)
    return t
