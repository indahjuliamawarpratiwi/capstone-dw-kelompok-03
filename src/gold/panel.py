"""Tahap 4 Sprint 2 — pemilihan satu nilai Gold per sel provinsi x periode x indikator.

Panel memakai seri provinsi BPS (var1394, var1353) dengan rincian total dari sumber kanonik JSON.
Tabel nasional memuat rincian yang dipakai PASANGAN dan kolom `asal`. Penanda Sprint 1 diwariskan
tanpa mengubah nilai.
"""
from pathlib import Path

import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.gold import nasional_gold
from src.laporan import ROOT, catat, tabel_md, tulis
from src.silver import anomali, grid

SERI_PANEL = ("var1394", "var1353")
KUNCI = ["seri_kode", "wilayah_kode", "periode"]
KOLOM_PANEL = [
    "sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode", "jenis_periode", "rincian",
    "nilai", "satuan", "sdg_kode", "status_sel", "penanda", "alasan_sel", "batas_bawah",
    "batas_atas", "rujukan_tahun", "_berkas_raw", "_sha256_raw",
]
GOLD = ROOT / "data" / "gold"


def _tandai(panel, kecocokan, label):
    for i in panel.index[kecocokan]:
        saat = panel.at[i, "penanda"]
        panel.at[i, "penanda"] = label if not saat else f"{saat}; {label}"


def bentuk_panel(silver):
    g = grid.bentuk_grid(silver, {})
    g = g[(g["tingkat"] == "provinsi") & g["seri_kode"].isin(SERI_PANEL)].copy()
    g = g.rename(columns={"nama_wilayah": "nama_grid", "kategori": "status_sel", "bukti": "alasan_sel"})
    s = silver[(silver["wilayah_kode"] != W.INDONESIA)
               & silver["seri_kode"].isin(SERI_PANEL)
               & (silver["rincian"] == "total")].copy()
    duplikat = s[s.duplicated(KUNCI, keep=False)]
    if not duplikat.empty:
        kunci_bermasalah = duplikat[KUNCI].drop_duplicates().to_string(index=False)
        raise AssertionError(f"duplikat kunci Silver pada panel Gold:\n{kunci_bermasalah}")
    panel = g.merge(s, on=KUNCI, how="left", suffixes=("_grid", ""))
    panel["nama_wilayah"] = panel["nama_wilayah"].fillna(panel["nama_grid"])
    panel["jenis_periode"] = "tahun"
    panel["rincian"] = "total"
    panel["sumber"] = panel["sumber"].fillna("bps")
    peta_satuan = {k: v["satuan"] for k, v in K.SERI.items()}
    peta_sdg = {k: v.get("sdg", "") for k, v in K.SERI.items()}
    panel["satuan"] = panel["satuan"].fillna(panel["seri_kode"].map(peta_satuan))
    panel["sdg_kode"] = panel["sdg_kode"].fillna(panel["seri_kode"].map(peta_sdg))
    panel["penanda"] = ""

    jalur = ROOT / "reports" / "anomali.csv"
    if jalur.exists():
        a = pd.read_csv(jalur)
        for r in a[a["kategori"] == "outlier"].itertuples():
            m = ((panel["seri_kode"] == r.seri_kode) & (panel["wilayah_kode"] == r.wilayah_kode)
                 & (panel["periode"] == str(r.periode)))
            _tandai(panel, m, "outlier")
    for r in anomali.patahan_wilayah(silver).itertuples():
        m = ((panel["seri_kode"] == r.seri_kode) & (panel["wilayah_kode"] == r.wilayah_kode)
             & (panel["periode"] == str(r.periode)))
        _tandai(panel, m, "patahan_wilayah")

    panel = panel[KOLOM_PANEL].sort_values(["seri_kode", "wilayah_kode", "periode"]).reset_index(drop=True)
    if panel.duplicated(KUNCI).any():
        kunci_bermasalah = panel[panel.duplicated(KUNCI, keep=False)][KUNCI].drop_duplicates().to_string(index=False)
        raise AssertionError(f"panel Gold memiliki lebih dari satu nilai per kunci:\n{kunci_bermasalah}")
    return panel


def bentuk_lebar(panel):
    lebar = panel.pivot_table(index=["wilayah_kode", "nama_wilayah"],
                              columns=["seri_kode", "periode"], values="nilai")
    lebar.columns = [f"{seri}_{periode}" for seri, periode in lebar.columns]
    return lebar.reset_index()


def tabel_nasional(silver):
    return nasional_gold.jalankan(silver)


def jalankan(silver):
    panel = bentuk_panel(silver)
    nas = tabel_nasional(silver)
    lebar = bentuk_lebar(panel)
    GOLD.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(GOLD / "panel.parquet", index=False)
    lebar.to_parquet(GOLD / "panel_lebar.parquet", index=False)
    nas.to_parquet(GOLD / "nasional.parquet", index=False)

    terisi = int((panel["status_sel"] == "terisi").sum())
    kosong = int((panel["status_sel"] != "terisi").sum())
    bertanda = int((panel["penanda"] != "").sum())
    catat(baris_panel_gold=len(panel), sel_terisi_gold=terisi, sel_kosong_gold=kosong,
          baris_nasional_gold=len(nas), sel_bertanda_gold=bertanda)
    ringkas = pd.DataFrame([
        {"ukuran": "baris panel", "nilai": len(panel)},
        {"ukuran": "sel terisi", "nilai": terisi},
        {"ukuran": "sel kosong berkategori", "nilai": kosong},
        {"ukuran": "sel bertanda", "nilai": bertanda},
        {"ukuran": "baris tabel nasional", "nilai": len(nas)},
    ])
    tulis("panel-gold.md", "\n\n".join([
        "# Panel Gold provinsi dan tabel nasional",
        "Dihasilkan `python pipeline.py` (`src/gold/panel.py`). Satu sel = satu seri x provinsi x periode.",
        "## Aturan pemilihan",
        "- Sumber kanonik BPS: JSON sesuai K-002; CSV tetap pembanding.",
        "- Panel hanya `var1394` dan `var1353`, rincian `total`; `9999` tidak masuk panel (K-025).",
        "- Satu nilai per sel; duplikat kunci tidak diizinkan.",
        "- Tabel nasional memuat rincian yang dipakai `PASANGAN` dari BPS, WHO, dan WDI dengan kolom `asal`; rincian umur `10-14` tetap hanya di Silver.",
        "- Penanda Sprint 1 dibawa apa adanya; nilai anomali tidak diubah.",
        "- Hanya periode tahunan; tidak ada agregasi semesteran atau bulanan.",
        "## Ringkasan",
        tabel_md(ringkas),
        "Rincian sel kosong: `reports/grid-sel-kosong.csv`. Penanda: `reports/anomali.csv`.",
    ]))
    return {"panel": panel, "panel_lebar": lebar, "nasional_gold": nas}