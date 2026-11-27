"""Tahap 5 — Silver dan Gold di DuckDB, beserta pembanding penyimpanan dokumen.
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
DDL = [Path(__file__).with_name("silver.sql"), Path(__file__).with_name("gold.sql")]
RAW = ROOT / "data" / "raw"


def _q(con, sql, param=None):
    """DuckDB 2: hasil setiap execute harus dihabiskan sebelum perintah berikutnya."""
    return con.execute(sql, param or []).fetchall()


def _muat(con, tabel, df):
    con.register("_df", df)
    kolom = ", ".join(df.columns)
    _q(con, f"INSERT INTO {tabel} ({kolom}) SELECT {kolom} FROM _df")
    con.unregister("_df")
    n = _q(con, f"SELECT count(*) FROM {tabel}")[0][0]
    if n != len(df):
        raise AssertionError(f"DuckDB memuat {n} baris {tabel}, Parquet {len(df)} baris")
    return n


def dokumen(con):
    """Semua berkas JSON mentah ke tabel dokumen_mentah (isi utuh, tanpa diratakan)."""
    sha = baca(RAW)
    n = 0
    for berkas, s in sorted(sha.items()):
        if not berkas.endswith(".json"):
            continue
        teks = (RAW / berkas).read_text(encoding="utf-8-sig")
        json.loads(teks)
        _q(con, "INSERT INTO dokumen_mentah VALUES (?, ?, ?, ?)", [berkas, s, berkas.split("/")[0], teks])
        n += 1
    return n


def bandingkan(con, silver):
    """Pertanyaan yang sama dijawab dari tabel Silver dan dari dokumen JSON mentah."""
    hasil = []
    bps = silver[(silver["sumber"] == "bps") & silver["_berkas_raw"].str.endswith(".json")]
    if len(bps):
        berkas = bps["_berkas_raw"].iloc[0]
        seri = bps.loc[bps["_berkas_raw"] == berkas, "seri_kode"].iloc[0]
        t0 = time.perf_counter()
        a = _q(con, "SELECT count(*) FROM silver WHERE _berkas_raw = ?", [berkas])[0][0]
        t1 = time.perf_counter()
        b = _q(con, "SELECT count(*) FROM (SELECT unnest(json_keys(isi -> '$.datacontent')) FROM dokumen_mentah "
                    "WHERE _berkas_raw = ?)", [berkas])[0][0]
        t2 = time.perf_counter()
        hasil.append({"pertanyaan": f"berapa angka {seri} di `{berkas}`", "tabel_silver": a, "dokumen_json": b,
                      "ms_silver": round(1000 * (t1 - t0), 2), "ms_dokumen": round(1000 * (t2 - t1), 2),
                      "catatan": "dokumen menghitung semua kunci datacontent (termasuk wilayah/rincian yang tidak masuk "
                                 "Silver); tabel Silver hanya baris yang lolos pembacaan"})
    return pd.DataFrame(hasil)


def jalankan(silver, gold):
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)
    seri = pd.read_csv(ROOT / "docs" / "seri.csv")[["seri_kode", "sumber", "tingkat", "nama_baku", "satuan", "sdg_kode"]]
    seri["sdg_kode"] = seri["sdg_kode"].astype(str)
    s = silver.copy()
    s["rujukan_tahun"] = s["rujukan_tahun"].astype("float64")
    panel = gold["panel"][[c for c in gold["panel"].columns if c in (
        "indikator", "seri_kode", "rincian", "wilayah_kode", "nama_wilayah", "periode", "jenis_periode", "nilai",
        "satuan", "status_sel", "penanda", "rujukan_tahun", "_berkas_raw", "_sha256_raw")]]
    with duckdb.connect(str(DB)) as con:
        for f in DDL:
            teks = "\n".join(b for b in f.read_text(encoding="utf-8").splitlines() if not b.strip().startswith("--"))
            for perintah in teks.split(";"):
                if perintah.strip():
                    _q(con, perintah)
        n_seri = _muat(con, "seri", seri)
        n = {"silver": _muat(con, "silver", s), "gold_panel": _muat(con, "gold_panel", panel),
             "gold_nasional": _muat(con, "gold_nasional", gold["nasional"]),
             "rekonsiliasi": _muat(con, "rekonsiliasi", gold["rekonsiliasi"])}
        from src.gold import nasional_gold
        nasional_gold.tulis_laporan(gold["nasional"], n["gold_nasional"])
        n_dok = dokumen(con)
        banding = bandingkan(con, silver)
        # bukti kunci primer bekerja: satu sel panel yang sama ditolak
        try:
            _q(con, "INSERT INTO gold_panel SELECT * FROM gold_panel LIMIT 1")
            tolak = "TIDAK ditolak"
        except duckdb.ConstraintException:
            tolak = "ditolak (ConstraintException)"
    ukuran = DB.stat().st_size
    catat(baris_sql=n["silver"], baris_sql_gold=n["gold_panel"] + n["gold_nasional"] + n["rekonsiliasi"],
          baris_sql_nasional=n["gold_nasional"], dokumen_json=n_dok, tabel_sql=5, mb_duckdb=round(ukuran / 1e6, 1))
    tabel = pd.DataFrame([{"tabel": k, "baris": v} for k, v in {"seri": n_seri, **n, "dokumen_mentah": n_dok}.items()])
    tulis("basis-data.md", "\n\n".join([
        "# Silver dan Gold di SQL",
        "Dihasilkan `python pipeline.py` (`src/gold/muat_sql.py`). DDL: `src/gold/silver.sql` dan `src/gold/gold.sql`. "
        f"Basis data `data/gold/gudang.duckdb` ({ukuran / 1e6:.1f} MB) dibuat ulang setiap kali dan tidak di-commit.",
        "## Isi", tabel_md(tabel),
        "Jumlah baris setiap tabel dicocokkan dengan Parquet-nya saat dimuat; beda satu baris pun menghentikan pipeline.",
        "## Kunci primer dan batasan",
        "- `silver`: (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw) — dua snapshot boleh berdampingan.\n"
        "- `gold_panel`: (indikator, wilayah_kode, periode) — satu nilai per sel; CHECK status sel dan nilai kosong "
        "hanya bila sel kosong.\n"
        "- `gold_nasional`: (seri_kode, rincian, periode).\n"
        "- `rekonsiliasi`: (pasangan_id, seri_pembanding, rincian_pembanding, periode); CHECK kategori baku dan "
        "selisih = utama − pembanding.",
        f"Uji: memasukkan ulang satu sel panel yang sudah ada → {tolak}.",
        "## Mengapa DuckDB, dan mengapa tabel (bukan dokumen)",
        "DuckDB dipilih karena satu berkas tanpa server, membaca Parquet langsung, dan cukup untuk ukuran data kasus ini; "
        "SQLite atau PostgreSQL sama sahnya. Lapis Silver dan Gold disimpan sebagai **tabel** karena pertanyaan "
        "analisisnya selalu per seri × wilayah × periode dan perlu kunci serta batasan. Berkas JSON mentah juga "
        "disimpan sebagai **dokumen** (`dokumen_mentah`) untuk perbandingan: dokumen menjaga bentuk asli (cocok untuk "
        "lapis Bronze dan audit), tetapi setiap pertanyaan harus mengurai struktur bersarangnya dan tidak ada kunci "
        "yang menolak sel ganda.",
        tabel_md(banding) if len(banding) else "Tidak ada berkas JSON BPS untuk dibandingkan.",
    ]))
    return n
