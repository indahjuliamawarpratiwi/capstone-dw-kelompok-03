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
RAW = ROOT / "data" / "raw"

KOLOM_PANEL = ["indikator", "seri_kode", "rincian", "wilayah_kode", "nama_wilayah", "periode",
               "jenis_periode", "nilai", "satuan", "status_sel", "penanda", "rujukan_tahun",
               "_berkas_raw", "_sha256_raw"]
KOLOM_REK = ["pasangan_id", "jenis", "seri_utama", "rincian_utama", "seri_pembanding", "rincian_pembanding",
             "periode", "nilai_utama", "nilai_pembanding", "satuan", "selisih", "selisih_relatif",
             "asal", "kategori", "penjelasan", "catatan"]


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
    nasional = gold.get("nasional_gold", gold.get("nasional"))


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
    s["rujukan_tahun"] = s["rujukan_tahun"].astype("float64")
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
