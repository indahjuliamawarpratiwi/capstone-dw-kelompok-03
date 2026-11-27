"""Tahap 4 — Panel Gold provinsi x periode x indikator.

Aturan satu nilai per sel (komponen pembersihan) diwarisi dari deret utama Sprint 1 (`src/silver/deret.py`):
- snapshot: seri BPS memakai snapshot terbaru (sudah diputuskan saat menyusun Silver, reports/snapshot-bps.csv);
- rincian: indikator = deret utama, yaitu baris `total`, atau rincian yang ditetapkan di DERET (konfigurasi);
  rincian lain tetap di Silver dan tidak masuk panel;
- berkas: bila satu sel punya beberapa berkas, URUTAN_BERKAS (lalu jalur terurut) memilih satu;
- periode: periode disimpan apa adanya (tahun, semester, bulan); tidak ada perataan ke tahunan di Gold.
Sisa sel ganda sesudah aturan itu membuat pipeline berhenti, bukan dipilih diam-diam.

Panel memuat grid lengkap: sel terisi beserta sel kosong dari grid Sprint 1 (status_sel = kategori sel
kosong), supaya kelengkapan terlihat di Gold. Penanda anomali Sprint 1 (outlier, patahan, galat input)
ikut sebagai kolom `penanda`; nilainya tidak diubah. Nilai asli dipertahankan; kolom turunan (bila ada)
ditulis sebagai kolom terpisah oleh `GOLD_TURUNAN` di konfigurasi.

Keluaran: data/gold/panel.parquet (panjang), data/gold/panel_lebar.parquet (satu kolom per indikator),
reports/panel-gold.md.
"""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat, tabel_md, tulis
from src.silver import deret

GOLD = ROOT / "data" / "gold"
KOLOM = ["indikator", "seri_kode", "rincian", "wilayah_kode", "nama_wilayah", "periode", "jenis_periode", "nilai",
         "satuan", "status_sel", "penanda", "rujukan_tahun", "_berkas_raw", "_sha256_raw"]
STATUS = ("terisi", "missing", "tidak_diterbitkan", "belum_ada", "batas_lama")


def _jenis(per):
    p = str(per)
    return "tahun" if len(p) == 4 else "semester" if "-S" in p else "triwulan" if "-Q" in p else "bulan"


def terisi(silver):
    lab = deret.berlabel(silver)
    lab = lab[lab["wilayah_kode"] != W.INDONESIA].copy()
    lab["indikator"] = lab["seri_kode"]
    lab["seri_kode"] = lab["indikator"].map(deret.dasar)
    # rincian deret JUMLAH ditulis apa adanya ('jumlah'): jumlah semua rincian satu berkas (lihat deret.py)
    ganda = lab[lab.duplicated(["indikator", "wilayah_kode", "periode"], keep=False)]
    if len(ganda):
        raise SystemExit(f"Gold: {len(ganda)} sel panel masih ganda sesudah aturan sel; lihat src/silver/deret.py")
    lab["status_sel"] = "terisi"
    return lab


def kosong():
    g = pd.read_csv(ROOT / "reports" / "grid-sel-kosong.csv", dtype={"periode": str})
    g = g[g["tingkat"] == "provinsi"].rename(columns={"seri_kode": "indikator", "kategori": "status_sel"})
    g["seri_kode"] = g["indikator"].map(deret.dasar)
    g["rincian"] = g["indikator"].map(lambda x: x.split(" [", 1)[1][:-1] if " [" in x else "total")
    g["nilai"] = float("nan")
    return g


def penanda():
    a = pd.read_csv(ROOT / "reports" / "anomali.csv", dtype={"periode": str}) \
        if (ROOT / "reports" / "anomali.csv").stat().st_size > 1 else pd.DataFrame()
    if a.empty:
        return {}
    return {(r.seri_kode, int(r.wilayah_kode), str(r.periode)): r.kategori for r in a.itertuples()}


def turunan(panel):
    """Kolom turunan opsional (GOLD_TURUNAN: {nama: (indikator, fungsi(nilai) -> nilai)}); nilai asli tetap."""
    for nama, (ind, f) in getattr(K, "GOLD_TURUNAN", {}).items():
        panel[nama] = panel["nilai"].where(panel["indikator"] == ind).map(f)
    return panel


def jalankan(silver):
    isi = terisi(silver)
    kos = kosong()
    p = pd.concat([isi, kos], ignore_index=True)
    p["nama_wilayah"] = p["wilayah_kode"].map(W.NAMA)
    p["jenis_periode"] = p["periode"].map(_jenis)
    satuan = {k: s["satuan"] for k, s in K.SERI.items()}
    p["satuan"] = p["seri_kode"].map(satuan)
    tanda = penanda()
    p["penanda"] = [tanda.get((i, int(w), str(per))) for i, w, per in zip(p["indikator"], p["wilayah_kode"], p["periode"])]
    for c in ("rujukan_tahun", "_berkas_raw", "_sha256_raw"):
        if c not in p:
            p[c] = None
    p = turunan(p)
    ekstra = [c for c in getattr(K, "GOLD_TURUNAN", {})]
    p = p[KOLOM + ekstra].sort_values(["indikator", "periode", "wilayah_kode"]).reset_index(drop=True)
    p["wilayah_kode"] = p["wilayah_kode"].astype(int)
    p["rujukan_tahun"] = pd.to_numeric(p["rujukan_tahun"].astype(object).where(p["rujukan_tahun"].notna(), None),
                                       errors="coerce").astype("float64")
    GOLD.mkdir(parents=True, exist_ok=True)
    p.to_parquet(GOLD / "panel.parquet", index=False)
    lebar = (p[p["status_sel"] == "terisi"]
             .pivot_table(index=["wilayah_kode", "nama_wilayah", "jenis_periode", "periode"], columns="indikator",
                          values="nilai", aggfunc="first")
             .reset_index())
    lebar.columns.name = None
    lebar.to_parquet(GOLD / "panel_lebar.parquet", index=False)

    ringkas = (p.assign(t=p["status_sel"] == "terisi")
               .groupby(["indikator", "satuan"])
               .agg(periode=("periode", lambda s: f"{s.min()}–{s.max()}" if s.nunique() > 1 else s.min()),
                    jumlah_periode=("periode", "nunique"), sel=("t", "size"), terisi=("t", "sum"),
                    ditandai=("penanda", lambda s: int(s.notna().sum())))
               .reset_index())
    status = p.pivot_table(index="indikator", columns="status_sel", values="wilayah_kode", aggfunc="size",
                           fill_value=0).reset_index()
    tidak_terpilih = len(silver[silver["wilayah_kode"] != W.INDONESIA]) - len(isi)
    catat(seri_panel=int(p["indikator"].nunique()), baris_gold=len(p), sel_gold_terisi=len(isi),
          sel_gold_kosong=len(kos), silver_tidak_terpilih=int(tidak_terpilih),
          sel_gold_ditandai=int(p["penanda"].notna().sum()), kolom_panel_lebar=int(lebar.shape[1]))
    tulis("panel-gold.md", "\n\n".join([
        "# Panel Gold provinsi x periode x indikator",
        "Dihasilkan `python pipeline.py` (`src/gold/panel.py`) dari Silver, grid, dan kategori anomali Sprint 1.",
        "## Aturan satu nilai per sel",
        "1. **Snapshot**: seri yang ada di dua snapshot memakai snapshot terbaru; angka snapshot lain dibandingkan di "
        "`reports/snapshot-bps.csv` (bila ada).\n"
        "2. **Rincian**: satu indikator = satu deret utama (`total`, atau rincian di `DERET`). Rincian lain tetap di "
        "Silver.\n"
        "3. **Berkas**: bila satu sel punya beberapa berkas, `URUTAN_BERKAS` memilih satu (`reports/deret-berkas.csv`).\n"
        "4. **Periode**: disimpan apa adanya; tidak dirata-rata ke tahunan.\n"
        "5. **Penanda**: outlier, patahan, dan galat input dari Sprint 1 ikut sebagai kolom `penanda`; nilainya tidak diubah.",
        f"Baris Silver provinsi yang tidak masuk panel (rincian lain atau berkas lain): {tidak_terpilih:,}.",
        "## Indikator", tabel_md(ringkas),
        "## Status sel", tabel_md(status),
        "`terisi` = ada angka; kategori lain berasal dari grid Sprint 1 (`reports/kelengkapan-panel.md`). Sel kosong "
        "tidak diisi: tidak ada interpolasi di Gold.",
        f"## Berkas\n\n- `data/gold/panel.parquet`: {len(p):,} baris (panjang, termasuk sel kosong).\n"
        f"- `data/gold/panel_lebar.parquet`: {len(lebar):,} baris x {lebar.shape[1]} kolom (hanya sel terisi; satu "
        "kolom per indikator, satuan per indikator di `docs/data-dictionary.md`).",
    ]))
    return p
