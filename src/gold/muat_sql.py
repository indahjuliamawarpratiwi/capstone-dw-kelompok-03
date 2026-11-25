"""Tahap 5 — Silver dan Gold di DuckDB, beserta perbandingan tabel dan dokumen.

Berkas dibuat ulang setiap kali, jadi pemuatan tidak pernah menggandakan baris. Berkas .duckdb
tidak di-commit. Fungsi dapat dipanggil dari alur Gold dengan `gold` berisi DataFrame, atau
sendiri dengan membaca parquet yang sudah ada.
"""
import json
import time
from pathlib import Path

import duckdb
import pandas as pd

from src import konfigurasi as K
from src.common.manifest import baca
from src.laporan import ROOT, catat, tabel_md, tulis

DB = ROOT / "data" / "gold" / "gudang.duckdb"
GOLD = ROOT / "data" / "gold"
DDL = [Path(__file__).with_name("silver.sql"), Path(__file__).with_name("gold.sql")]
RAW = ROOT / "data" / "raw"

KOLOM_PANEL = ["indikator", "seri_kode", "rincian", "wilayah_kode", "nama_wilayah", "periode",
               "jenis_periode", "nilai", "satuan", "status_sel", "penanda", "rujukan_tahun",
               "_berkas_raw", "_sha256_raw"]
KOLOM_REK = ["pasangan_id", "jenis", "seri_utama", "rincian_utama", "seri_pembanding", "rincian_pembanding",
             "periode", "nilai_utama", "nilai_pembanding", "satuan", "selisih", "selisih_relatif",
             "asal", "kategori", "penjelasan", "catatan"]

def jalankan(silver):
    GOLD.mkdir(parents=True, exist_ok=True)

def _q(con, sql, param=None):
    return con.execute(sql, param or []).fetchall()


def _muat(con, tabel, df):
    con.register("_df", df)
    kolom = ", ".join(df.columns)
    _q(con, f"INSERT INTO {tabel} ({kolom}) SELECT {kolom} FROM _df")
    con.unregister("_df")
    n = _q(con, f"SELECT count(*) FROM {tabel}")[0][0]
    if n != len(df):
        raise AssertionError(f"DuckDB memuat {n} baris {tabel}, sumber {len(df)} baris")
    return n


def _ddl(con):
    for f in DDL:
        teks = "\n".join(b for b in f.read_text(encoding="utf-8").splitlines() if not b.strip().startswith("--"))
        for perintah in teks.split(";"):
            if perintah.strip():
                _q(con, perintah)


def dokumen(con):
    n = 0
    for berkas, sha256 in sorted(baca(RAW).items()):
        if not berkas.endswith(".json"):
            continue
        teks = (RAW / berkas).read_text(encoding="utf-8-sig")
        json.loads(teks)
        _q(con, "INSERT INTO dokumen_mentah VALUES (?, ?, ?, ?)",
           [berkas, sha256, berkas.split("/")[0], teks])
        n += 1
    return n


def bandingkan(con, silver):
    hasil = []
    bps = silver[(silver["sumber"] == "bps") & silver["_berkas_raw"].str.endswith(".json")]
    if len(bps):
        berkas = bps["_berkas_raw"].iloc[0]
        seri = bps.loc[bps["_berkas_raw"] == berkas, "seri_kode"].iloc[0]
        t0 = time.perf_counter()
        a = _q(con, "SELECT count(*) FROM silver WHERE _berkas_raw = ?", [berkas])[0][0]
        t1 = time.perf_counter()
        b = _q(con, "SELECT count(*) FROM (SELECT unnest(json_keys(isi -> '$.datacontent')) "
                    "FROM dokumen_mentah WHERE _berkas_raw = ?)", [berkas])[0][0]
        t2 = time.perf_counter()
        hasil.append({"pertanyaan": f"berapa angka {seri} di `{berkas}`", "tabel_silver": a, "dokumen_json": b,
                      "ms_silver": round(1000 * (t1 - t0), 2), "ms_dokumen": round(1000 * (t2 - t1), 2),
                      "catatan": "dokumen menghitung semua kunci datacontent; tabel Silver hanya baris yang lolos pembacaan"})
    return pd.DataFrame(hasil)


def jalankan(silver=None, gold=None):
    if silver is None:
        silver = pd.read_parquet(ROOT / "data" / "silver" / "silver.parquet")
    if gold is None:
        gold = {
            "panel": pd.read_parquet(GOLD / "panel.parquet"),
            "nasional": pd.read_parquet(GOLD / "nasional.parquet"),
            "rekonsiliasi": pd.read_parquet(GOLD / "rekonsiliasi.parquet"),
        }
    nasional = gold.get("nasional", gold.get("nasional_gold"))
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)

    seri = pd.read_csv(ROOT / "docs" / "seri.csv")[["seri_kode", "sumber", "tingkat", "nama_baku", "satuan", "sdg_kode"]]
    seri["sdg_kode"] = seri["sdg_kode"].astype(str)
    s = silver.copy()
    s["rujukan_tahun"] = s["rujukan_tahun"].astype("float64")
    panel = _panel(silver)
    panel.to_parquet(PANEL, index=False)
    nasional = pd.read_parquet(NASIONAL)
    rekonsiliasi = pd.read_csv(REKONSILIASI, keep_default_na=False, dtype=str)

    with duckdb.connect(str(DB)) as con:
        con.execute(DDL.read_text(encoding="utf-8"))
        jumlah = {
            "seri": _sisip(con, "seri", seri),
            "silver": _sisip(con, "silver", s),
            "panel_gold": _sisip(con, "panel_gold", panel),
            "nasional": _sisip(con, "nasional", nasional),
            "rekonsiliasi": _sisip(con, "rekonsiliasi", rekonsiliasi),
        }

    for nama, sumber in [("silver", len(silver)), ("panel_gold", len(panel)),
                         ("nasional", len(nasional)), ("rekonsiliasi", len(rekonsiliasi))]:
        if jumlah[nama] != sumber:
            raise AssertionError(f"DuckDB {nama}: {jumlah[nama]} baris, sumber {sumber} baris")

    catat(baris_sql=jumlah["silver"])
    return {"baris_sql": jumlah["silver"], "baris_sql_panel": jumlah["panel_gold"],
            "baris_sql_nasional": jumlah["nasional"], "baris_sql_rekonsiliasi": jumlah["rekonsiliasi"]}
    p = gold["panel"].copy()
    if "indikator" not in p.columns:
        p["indikator"] = p["seri_kode"]
    panel = p[KOLOM_PANEL].copy()
    satuan = {k: s["satuan"] for k, s in K.SERI.items()}
    panel["satuan"] = panel["satuan"].fillna(panel["seri_kode"].map(satuan))
    panel["rujukan_tahun"] = panel["rujukan_tahun"].astype("float64")
    rek = gold["rekonsiliasi"][KOLOM_REK].copy()

    with duckdb.connect(str(DB)) as con:
        _ddl(con)
        n_seri = _muat(con, "seri", seri)
        n = {"silver": _muat(con, "silver", s),
             "gold_panel": _muat(con, "gold_panel", panel),
             "gold_nasional": _muat(con, "gold_nasional", nasional),
             "rekonsiliasi": _muat(con, "rekonsiliasi", rek)}
        n_dok = dokumen(con)
        banding = bandingkan(con, silver)
        daftar = sorted(r[0] for r in _q(con, "SELECT table_name FROM information_schema.tables "
                                            "WHERE table_schema = 'main' ORDER BY table_name"))
        try:
            _q(con, "INSERT INTO gold_panel SELECT * FROM gold_panel LIMIT 1")
            tolak = "TIDAK ditolak"
        except duckdb.ConstraintException:
            tolak = "ditolak (ConstraintException)"

    ukuran = DB.stat().st_size
    catat(baris_sql=n["silver"],
          baris_sql_gold=n["gold_panel"] + n["gold_nasional"] + n["rekonsiliasi"],
          dokumen_json=n_dok, tabel_sql=len(daftar) - 1, mb_duckdb=round(ukuran / 1e6, 1))
    tabel = pd.DataFrame([{"tabel": k, "baris": v} for k, v in
                          {"seri": n_seri, **n, "dokumen_mentah": n_dok}.items()])
    tulis("basis-data.md", "\n\n".join([
        "# Silver dan Gold di SQL",
        "Dihasilkan `python pipeline.py` (`src/gold/muat_sql.py`). DDL: `src/gold/silver.sql` dan `src/gold/gold.sql`. "
        f"Basis data `data/gold/gudang.duckdb` ({ukuran / 1e6:.1f} MB) dibuat ulang setiap kali dan tidak di-commit.",
        "## Isi", tabel_md(tabel),
        "Daftar tabel sebenarnya: " + ", ".join(f"`{x}`" for x in daftar) + f". Total {len(daftar)} tabel "
        f"({len(daftar) - 1} tabel relasional + 1 tabel dokumen).",
        "Jumlah baris setiap tabel dicocokkan dengan sumbernya saat dimuat; beda satu baris pun menghentikan proses.",
        "## Kunci primer dan batasan",
        "- `silver`: (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw).\n"
        "- `gold_panel`: (indikator, wilayah_kode, periode); CHECK status sel dan nilai.\n"
        "- `gold_nasional`: (seri_kode, rincian, periode).\n"
        "- `rekonsiliasi`: (pasangan_id, seri_pembanding, rincian_pembanding, periode); CHECK kategori baku dan selisih.\n"
        "- `dokumen_mentah`: _berkas_raw sebagai kunci primer; isi JSON mentah apa adanya.",
        f"Uji: memasukkan ulang satu sel panel yang sudah ada → {tolak}.",
        "## Mengapa tabel dan dokumen",
        "Tabel relasional dipakai untuk pertanyaan per seri × wilayah × periode karena punya kunci dan batasan. "
        "Berkas JSON mentah tetap disimpan sebagai dokumen untuk audit lapis Bronze.",
        tabel_md(banding) if len(banding) else "Tidak ada berkas JSON BPS untuk dibandingkan.",
    ]))
    return n
