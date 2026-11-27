"""Tahap 5 — Silver dan Gold di DuckDB, beserta perbandingan tabel dan dokumen.

Berkas dibuat ulang setiap kali, jadi pemuatan tidak pernah menggandakan baris. Berkas .duckdb
tidak di-commit.
"""
from pathlib import Path

import duckdb
import pandas as pd

from src import konfigurasi as K
from src.laporan import ROOT, catat

DB = ROOT / "data" / "gold" / "gudang.duckdb"
GOLD = ROOT / "data" / "gold"
DDL = [Path(__file__).with_name("silver.sql"), Path(__file__).with_name("gold.sql")]


def _sisip(con, nama, df):
    kolom = ", ".join(df.columns)
    con.register(f"{nama}_df", df)
    con.execute(f"INSERT INTO {nama} ({kolom}) SELECT {kolom} FROM {nama}_df")
    return con.execute(f"SELECT count(*) FROM {nama}").fetchall()[0][0]


def jalankan(silver, ekstraksi=None):
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)

    seri = pd.read_csv(ROOT / "docs" / "seri.csv")[["seri_kode", "sumber", "tingkat", "nama_baku", "satuan", "sdg_kode"]]
    seri["sdg_kode"] = seri["sdg_kode"].astype(str)

    s = silver.copy()
    s["rujukan_tahun"] = pd.to_numeric(s["rujukan_tahun"], errors="coerce").astype("float64")

    # Siapkan gold_panel dari panel.parquet
    panel_file = GOLD / "panel.parquet"
    if panel_file.exists():
        panel = pd.read_parquet(panel_file).copy()
    else:
        panel = pd.DataFrame()
    if not panel.empty:
        if "indikator" not in panel.columns:
            panel["indikator"] = panel["seri_kode"]
        kolom_panel = [
            "indikator", "seri_kode", "rincian", "wilayah_kode", "nama_wilayah", "periode",
            "jenis_periode", "nilai", "satuan", "status_sel", "penanda", "rujukan_tahun",
            "_berkas_raw", "_sha256_raw"
        ]
        panel = panel[[c for c in kolom_panel if c in panel.columns]].copy()
        if "satuan" in panel.columns:
            peta_satuan = {k: v["satuan"] for k, v in K.SERI.items()}
            panel["satuan"] = panel["satuan"].fillna(panel["seri_kode"].map(peta_satuan))
        if "nilai" in panel.columns:
            panel["nilai"] = pd.to_numeric(panel["nilai"], errors="coerce").astype("float64")
        if "rujukan_tahun" in panel.columns:
            panel["rujukan_tahun"] = pd.to_numeric(panel["rujukan_tahun"], errors="coerce").astype("Int64")

    # Siapkan gold_nasional dari nasional.parquet
    nas_file = GOLD / "nasional.parquet"
    if nas_file.exists():
        nasional = pd.read_parquet(nas_file).copy()
    else:
        nasional = pd.DataFrame()
    if not nasional.empty:
        kolom_nas = [
            "seri_kode", "rincian", "sumber", "periode", "jenis_periode", "nilai",
            "satuan", "batas_bawah", "batas_atas", "rujukan_tahun", "asal",
            "_berkas_raw", "_sha256_raw"
        ]
        nasional = nasional[[c for c in kolom_nas if c in nasional.columns]].copy()
        for c in ["nilai", "batas_bawah", "batas_atas"]:
            if c in nasional.columns:
                nasional[c] = pd.to_numeric(nasional[c], errors="coerce").astype("float64")
        if "rujukan_tahun" in nasional.columns:
            nasional["rujukan_tahun"] = pd.to_numeric(nasional["rujukan_tahun"], errors="coerce").astype("Int64")

    # Siapkan rekonsiliasi dari rekonsiliasi.parquet
    rek_file = GOLD / "rekonsiliasi.parquet"
    if rek_file.exists():
        rekonsiliasi = pd.read_parquet(rek_file).copy()
    else:
        rekonsiliasi = pd.DataFrame()
    if not rekonsiliasi.empty:
        kolom_rek = [
            "pasangan_id", "jenis", "seri_utama", "rincian_utama", "seri_pembanding", "rincian_pembanding",
            "periode", "nilai_utama", "nilai_pembanding", "satuan", "selisih", "selisih_relatif",
            "asal", "kategori", "penjelasan", "catatan"
        ]
        rekonsiliasi = rekonsiliasi[[c for c in kolom_rek if c in rekonsiliasi.columns]].copy()
        for c in ["nilai_utama", "nilai_pembanding", "selisih", "selisih_relatif"]:
            if c in rekonsiliasi.columns:
                rekonsiliasi[c] = pd.to_numeric(rekonsiliasi[c], errors="coerce").astype("float64")

    # Siapkan dokumen_mentah dari MANIFEST.csv berkas json
    manifest_file = ROOT / "data" / "raw" / "MANIFEST.csv"
    dokumen = []
    if manifest_file.exists():
        man = pd.read_csv(manifest_file)
        for _, r in man.iterrows():
            berkas = str(r["berkas"])
            if berkas.endswith(".json"):
                jalur = ROOT / "data" / "raw" / berkas
                isi = jalur.read_text(encoding="utf-8") if jalur.exists() else "{}"
                dokumen.append({
                    "_berkas_raw": berkas,
                    "_sha256_raw": str(r["sha256"]),
                    "sumber": berkas.split("/")[0],
                    "isi": isi,
                })
    dokumen_df = pd.DataFrame(dokumen)

    with duckdb.connect(str(DB)) as con:
        for f in DDL:
            teks = "\n".join(b for b in f.read_text(encoding="utf-8").splitlines() if not b.strip().startswith("--"))
            for perintah in teks.split(";"):
                if perintah.strip():
                    con.execute(perintah)

        jumlah = {
            "seri": _sisip(con, "seri", seri),
            "silver": _sisip(con, "silver", s),
        }
        if not panel.empty:
            jumlah["gold_panel"] = _sisip(con, "gold_panel", panel)
        if not nasional.empty:
            jumlah["gold_nasional"] = _sisip(con, "gold_nasional", nasional)
        if not rekonsiliasi.empty:
            jumlah["rekonsiliasi"] = _sisip(con, "rekonsiliasi", rekonsiliasi)
        if not dokumen_df.empty:
            jumlah["dokumen_mentah"] = _sisip(con, "dokumen_mentah", dokumen_df)

    catat(baris_sql=jumlah["silver"])
    return {
        "baris_sql": jumlah["silver"],
        "baris_sql_panel": jumlah.get("gold_panel", 0),
        "baris_sql_nasional": jumlah.get("gold_nasional", 0),
        "baris_sql_rekonsiliasi": jumlah.get("rekonsiliasi", 0),
        "baris_sql_dokumen": jumlah.get("dokumen_mentah", 0),
    }
