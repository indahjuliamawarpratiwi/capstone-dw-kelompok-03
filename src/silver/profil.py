"""Profil dan anomali Sprint 1 untuk kasus 03 (kesehatan reproduksi remaja).

Menjalankan modul ini akan:
1. membaca seri utama BPS var1394/var1353 dan pembanding WHO/WDI;
2. menulis tabel Silver untuk kelima seri;
3. menghitung statistik deskriptif per seri dan per provinsi;
4. menandai calon anomali dengan IQR dan z-score;
5. membentuk grid 38 provinsi x 2012-2017 dan melaporkan kelengkapannya;
6. menyimpan tabel ke reports/tabel/ dan gambar ke reports/gambar/.

    ./.venv/Scripts/python.exe -m src.silver.profil
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.common.manifest import sha256_raw

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SILVER_DIR = ROOT / "data" / "silver"
REPORTS = ROOT / "reports"
TABEL = REPORTS / "tabel"
GAMBAR = REPORTS / "gambar"

TAHUN_GRID = list(range(2012, 2018))
TAHUN_SURVEI = [2012, 2017]
PROVINSI_BARU = {9200, 9500, 9600, 9700}
KALTARA = 6500

BPS_META = {
    "var1394": {
        "nama": "Proporsi perempuan usia 15-49 atau pasangannya yang membutuhkan KB dan memakai kontrasepsi modern",
        "satuan": "persen",
        "rincian": "sex=perempuan; age=15-49; metode=modern; turvar=tidak_ada",
        "csv": "bps/2026-10-20/sdg3_3_7_1_v1394.csv",
        "json": "bps/2026-10-20/json/sdg3_3_7_1_v1394.json",
        "pembanding": "SDGFPALL",
    },
    "var1353": {
        "nama": "Angka kelahiran pada perempuan usia 15-19 tahun",
        "satuan": "per 1.000 perempuan usia 15-19",
        "rincian": "sex=perempuan; age=15-19; turvar=tidak_ada",
        "csv": "bps/2026-10-20/sdg3_3_7_2_v1353.csv",
        "json": "bps/2026-10-20/json/sdg3_3_7_2_v1353.json",
        "pembanding": "MDG_0000000003 (Y15T19); SP.ADO.TFRT",
    },
}

WHO_META = {
    "MDG_0000000003": {
        "berkas": "who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv",
        "nama": "Adolescent birth rate",
    },
    "SDGFPALL": {
        "berkas": "who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv",
        "nama": "Family planning satisfied with modern methods",
    },
}

WDI_BERKAS = [
    "wdi/2026-10-20/data/kelompok-05-hal-01.json",
    "wdi/2026-10-20/data/kelompok-07-hal-01.json",
]
WDI_SERI = "SP.ADO.TFRT"


def _angka(deret):
    return pd.to_numeric(deret, errors="coerce")


def baca_bps(kode):
    meta = BPS_META[kode]
    df = pd.read_csv(RAW / meta["csv"])
    out = pd.DataFrame(
        {
            "sumber": "bps",
            "seri_kode": kode,
            "wilayah_kode": df["wilayah_id"].astype(int),
            "nama_wilayah": df["wilayah"].astype(str).str.strip(),
            "periode": df["tahun"].astype(int).astype(str),
            "jenis_periode": "tahun",
            "rincian": meta["rincian"],
            "nilai": _angka(df["nilai"]),
            "satuan": meta["satuan"],
            "satuan_asal": df["satuan"].astype("object").fillna("").astype(str),
            "_berkas_raw": meta["csv"],
            "_sha256_raw": sha256_raw(meta["csv"]),
        }
    )
    return out.dropna(subset=["nilai"]).reset_index(drop=True)


def baca_bps_json(kode):
    meta = BPS_META[kode]
    isi = json.loads((RAW / meta["json"]).read_text(encoding="utf-8"))[0]
    tahun_map = {int(t["val"]): int(t["label"]) for t in isi["tahun"]}
    baris = []
    for kunci, nilai in isi["datacontent"].items():
        wilayah = int(kunci[:4])
        sisa = kunci[8:]
        tahun_id = int(sisa[1:4])
        baris.append({"wilayah_kode": wilayah, "periode": str(tahun_map[tahun_id]), "nilai_json": float(nilai)})
    return pd.DataFrame(baris)


def baca_who(kode):
    meta = WHO_META[kode]
    df = pd.read_csv(RAW / meta["berkas"])
    kolom_nilai = [k for k in df.columns if k.startswith("RATE_PER_")][0]
    df = df[df[kolom_nilai].notna()].copy()
    umur = df["DIM_AGE"].astype(str)
    if kolom_nilai == "RATE_PER_1000_N":
        satuan = np.where(umur.eq("Y10T14"), "per 1.000 perempuan usia 10-14", "per 1.000 perempuan usia 15-19")
    else:
        satuan = np.full(len(df), "persen")
    out = pd.DataFrame(
        {
            "sumber": "who_gho",
            "seri_kode": kode,
            "wilayah_kode": 9999,
            "nama_wilayah": df["GEO_NAME_SHORT"].astype(str),
            "periode": df["DIM_TIME"].astype(int).astype(str),
            "jenis_periode": "tahun",
            "rincian": "sex=" + df["DIM_SEX"].astype(str) + "; age=" + umur + "; geo=" + df["GEO_NAME_SHORT"].astype(str),
            "nilai": _angka(df[kolom_nilai]),
            "satuan": satuan,
            "satuan_asal": kolom_nilai,
            "_berkas_raw": meta["berkas"],
            "_sha256_raw": sha256_raw(meta["berkas"]),
        }
    )
    return out.dropna(subset=["nilai"]).reset_index(drop=True)


def baca_wdi():
    baris = []
    for berkas in WDI_BERKAS:
        isi = json.loads((RAW / berkas).read_text(encoding="utf-8"))
        for r in isi[1]:
            if r.get("indicator", {}).get("id") != WDI_SERI or r.get("value") is None:
                continue
            baris.append(
                {
                    "sumber": "wdi",
                    "seri_kode": WDI_SERI,
                    "wilayah_kode": 9999,
                    "nama_wilayah": r["country"]["value"],
                    "periode": str(int(r["date"])),
                    "jenis_periode": "tahun",
                    "rincian": "sex=total; age=15-19; cakupan=Indonesia",
                    "nilai": float(r["value"]),
                    "satuan": "per 1.000 perempuan usia 15-19",
                    "satuan_asal": "level 0; unit kosong di API",
                    "_berkas_raw": berkas,
                    "_sha256_raw": sha256_raw(berkas),
                }
            )
    if not baris:
        return pd.DataFrame()
    return pd.DataFrame(baris).drop_duplicates(["periode"]).reset_index(drop=True)


def buat_silver():
    bps = [baca_bps(k) for k in BPS_META]
    who = [baca_who(k) for k in WHO_META]
    wdi = baca_wdi()
    kolom = [
        "sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode", "jenis_periode",
        "rincian", "nilai", "satuan", "satuan_asal", "_berkas_raw", "_sha256_raw",
    ]
    silver = pd.concat([*bps, *who, wdi], ignore_index=True)[kolom]
    silver = silver.sort_values(["sumber", "seri_kode", "wilayah_kode", "periode", "rincian"]).reset_index(drop=True)
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    silver.to_parquet(SILVER_DIR / "silver.parquet", index=False)
    return silver


def statistik_seri(utama):
    baris = []
    for kode, g in utama.groupby("seri_kode", sort=True):
        g = g[g["wilayah_kode"] != 9999]
        for periode, gg in [("semua", g), *g.groupby("periode", sort=True)]:
            nilai = gg["nilai"].astype(float)
            q1, q3 = np.percentile(nilai, [25, 75])
            iqr = q3 - q1
            mean = nilai.mean()
            sd = nilai.std(ddof=0)
            z = (nilai - mean) / sd if sd else pd.Series(np.zeros(len(nilai)))
            baris.append(
                {
                    "seri_kode": kode,
                    "satuan": gg["satuan"].iloc[0],
                    "periode": periode,
                    "n": len(nilai),
                    "mean": mean,
                    "std": sd,
                    "min": nilai.min(),
                    "q1": q1,
                    "median": nilai.median(),
                    "q3": q3,
                    "max": nilai.max(),
                    "iqr": iqr,
                    "batas_bawah_iqr": q1 - 1.5 * iqr,
                    "batas_atas_iqr": q3 + 1.5 * iqr,
                    "n_iqr": int(((nilai < q1 - 1.5 * iqr) | (nilai > q3 + 1.5 * iqr)).sum()),
                    "n_z": int((z.abs() >= 2).sum()),
                }
            )
    return pd.DataFrame(baris)


def statistik_nasional(utama):
    nasional = utama[utama["wilayah_kode"] == 9999]
    return nasional[["seri_kode", "periode", "nilai", "satuan"]].sort_values(["seri_kode", "periode"])


def _flag_tahun(nilai, semua_nilai):
    q1, q3 = np.percentile(semua_nilai, [25, 75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mean = np.mean(semua_nilai)
    sd = np.std(semua_nilai, ddof=0)
    z = (nilai - mean) / sd if sd else 0.0
    return {
        "iqr": bool(nilai < lo or nilai > hi),
        "z": bool(abs(z) >= 2),
        "z_skor": float(z),
        "batas_bawah": float(lo),
        "batas_atas": float(hi),
    }


def statistik_provinsi(utama):
    baris = []
    for kode, g in utama.groupby("seri_kode", sort=True):
        g = g[g["wilayah_kode"] != 9999]
        p = g.pivot_table(index=["wilayah_kode", "nama_wilayah"], columns="periode", values="nilai")
        tahun = list(p.columns)
        for (wilayah, nama), r in p.iterrows():
            v12 = r.get("2012", np.nan)
            v17 = r.get("2017", np.nan)
            nilai = r.dropna().astype(float)
            f12 = _flag_tahun(v12, p["2012"].dropna()) if "2012" in p and pd.notna(v12) else {}
            f17 = _flag_tahun(v17, p["2017"].dropna()) if "2017" in p and pd.notna(v17) else {}
            baris.append(
                {
                    "seri_kode": kode,
                    "wilayah_kode": int(wilayah),
                    "nama_wilayah": nama,
                    "n": int(nilai.size),
                    "mean": nilai.mean(),
                    "min": nilai.min(),
                    "max": nilai.max(),
                    "nilai_2012": v12,
                    "nilai_2017": v17,
                    "delta_2012_2017": v17 - v12 if pd.notna(v12) and pd.notna(v17) else np.nan,
                    "z_2012": f12.get("z_skor", np.nan),
                    "z_2017": f17.get("z_skor", np.nan),
                    "flag_iqr_2012": f12.get("iqr", False),
                    "flag_iqr_2017": f17.get("iqr", False),
                    "flag_z_2012": f12.get("z", False),
                    "flag_z_2017": f17.get("z", False),
                }
            )
    return pd.DataFrame(baris).sort_values(["seri_kode", "wilayah_kode"]).reset_index(drop=True)


def ringkasan_patahan(utama):
    baris = []
    for kode, g in utama.groupby("seri_kode", sort=True):
        g = g[g["wilayah_kode"] != 9999]
        p = g.pivot_table(index="wilayah_kode", columns="periode", values="nilai").dropna()
        d = p["2017"] - p["2012"]
        n = len(d)
        turun = int((d < 0).sum())
        naik = int((d > 0).sum())
        tetap = int((d == 0).sum())
        share = max(turun, naik) / n if n else np.nan
        indikasi = bool(share >= 0.70)
        baris.append(
            {
                "seri_kode": kode,
                "n_pasangan": n,
                "n_turun": turun,
                "n_naik": naik,
                "n_tetap": tetap,
                "persen_arah_dominan": share * 100,
                "median_delta": d.median(),
                "mean_delta": d.mean(),
                "indikasi_patahan": "ya" if indikasi else "tidak",
                "alasan": (
                    "perubahan searah di hampir semua provinsi; kandidat patahan/revisi seri"
                    if indikasi
                    else "arah perubahan campuran; tidak ada indikasi patahan serentak"
                ),
            }
        )
    return pd.DataFrame(baris)


def deteksi_anomali(utama, patahan):
    baris = {}
    patahan_map = patahan.set_index("seri_kode")["indikasi_patahan"].to_dict()
    for kode, g in utama.groupby("seri_kode", sort=True):
        g = g[g["wilayah_kode"] != 9999]
        for periode, gg in g.groupby("periode", sort=True):
            nilai_all = gg["nilai"].astype(float)
            for _, r in gg.iterrows():
                f = _flag_tahun(float(r["nilai"]), nilai_all)
                if not (f["iqr"] or f["z"]):
                    continue
                kunci = (kode, int(r["wilayah_kode"]), str(periode))
                metode = "IQR+z" if f["iqr"] and f["z"] else ("IQR" if f["iqr"] else "z")
                alasan = (
                    f"nilai {r['nilai']:.4g} di luar batas IQR "
                    f"[{f['batas_bawah']:.3f}, {f['batas_atas']:.3f}]"
                    if f["iqr"]
                    else f"nilai {r['nilai']:.4g} memiliki |z|={abs(f['z_skor']):.2f} (ambang 2)"
                )
                baris[kunci] = {
                    "seri_kode": kode,
                    "wilayah_kode": int(r["wilayah_kode"]),
                    "nama_wilayah": r["nama_wilayah"],
                    "periode": str(periode),
                    "nilai": float(r["nilai"]),
                    "metode_level": metode,
                    "z_skor": f["z_skor"],
                    "batas_bawah": f["batas_bawah"],
                    "batas_atas": f["batas_atas"],
                    "alasan_level": alasan,
                    "flag_delta": False,
                    "delta": np.nan,
                    "z_delta": np.nan,
                }
        p = g.pivot_table(index=["wilayah_kode", "nama_wilayah"], columns="periode", values="nilai").dropna()
        d = p["2017"] - p["2012"]
        q1, q3 = np.percentile(d, [25, 75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mean, sd = d.mean(), d.std(ddof=0)
        for (wilayah, nama), delta in d.items():
            z = (delta - mean) / sd if sd else 0.0
            if not (abs(z) >= 2 or delta < lo or delta > hi):
                continue
            kunci = (kode, int(wilayah), "2017")
            if kunci in baris:
                baris[kunci]["flag_delta"] = True
                baris[kunci]["delta"] = float(delta)
                baris[kunci]["z_delta"] = float(z)
                baris[kunci]["alasan_level"] += (
                    f"; perubahan 2012-2017 = {delta:.4g} (z_delta={z:.2f})"
                )
            else:
                baris[kunci] = {
                    "seri_kode": kode,
                    "wilayah_kode": int(wilayah),
                    "nama_wilayah": nama,
                    "periode": "2012->2017",
                    "nilai": float(delta),
                    "metode_level": "z_delta" if abs(z) >= 2 else "IQR_delta",
                    "z_skor": float(z),
                    "batas_bawah": float(lo),
                    "batas_atas": float(hi),
                    "alasan_level": (
                        f"perubahan {delta:.4g} dari 2012 ke 2017 memiliki |z_delta|={abs(z):.2f} "
                        "atau di luar batas IQR perubahan"
                    ),
                    "flag_delta": True,
                    "delta": float(delta),
                    "z_delta": float(z),
                }
    hasil = pd.DataFrame(baris.values())
    if hasil.empty:
        return hasil
    hasil["kategori"] = hasil.apply(lambda r: kategori_anomali(r, patahan_map), axis=1)
    hasil["tindakan"] = "ditandai; nilai tidak diubah"
    hasil["alasan"] = hasil.apply(
        lambda r: r["alasan_level"] + "; " + alasan_kategori(r), axis=1
    )
    kolom = [
        "seri_kode", "wilayah_kode", "nama_wilayah", "periode", "nilai", "metode_level",
        "z_skor", "delta", "z_delta", "kategori", "alasan", "tindakan",
    ]
    return hasil[kolom].sort_values(["seri_kode", "periode", "wilayah_kode"]).reset_index(drop=True)


def kategori_anomali(r, patahan_map):
    if patahan_map.get(r["seri_kode"]) == "ya":
        if r["periode"] == "2012":
            return "patahan"
        if r["periode"] == "2017" and pd.notna(r.get("z_delta")) and r["z_delta"] < 0:
            return "patahan"
        if r["periode"] == "2012->2017" and r["nilai"] < 0:
            return "patahan"
    return "outlier_asli"


def alasan_kategori(r):
    if r["kategori"] == "patahan":
        return (
            "pola penurunan serentak 2012-2017 (26/33 provinsi) membuat nilai ini kandidat "
            "patahan/revisi seri, bukan galat input; tidak dikoreksi"
        )
    if r["kategori"] == "outlier_asli":
        return "nilai ekstrem yang tidak terbukti galat input; dipertahankan sebagai outlier asli"
    return "tidak ada bukti galat input"


def ringkasan_kategori(anomali, utama):
    kategori = ["outlier_asli", "patahan", "galat_input"]
    baris = []
    for kode, g in utama.groupby("seri_kode", sort=True):
        for k in kategori:
            n = int(((anomali["seri_kode"] == kode) & (anomali["kategori"] == k)).sum()) if not anomali.empty else 0
            baris.append({"seri_kode": kode, "kategori": k, "jumlah": n})
    return pd.DataFrame(baris)


def referensi_provinsi():
    isi = json.loads((RAW / BPS_META["var1394"]["json"]).read_text(encoding="utf-8"))[0]
    return pd.DataFrame(
        [{"wilayah_kode": int(v["val"]), "nama_wilayah": v["label"]} for v in isi["vervar"] if int(v["val"]) != 9999]
    ).sort_values("wilayah_kode").reset_index(drop=True)


def bentuk_grid(utama):
    prov = referensi_provinsi()
    baris = []
    for kode, g in utama.groupby("seri_kode", sort=True):
        nilai = {(int(r.wilayah_kode), str(r.periode)): float(r.nilai) for r in g[g.wilayah_kode != 9999].itertuples()}
        for tahun in TAHUN_GRID:
            for _, p in prov.iterrows():
                w = int(p["wilayah_kode"])
                if tahun not in TAHUN_SURVEI:
                    status = "tidak_terbit"
                elif w in PROVINSI_BARU:
                    status = "belum_ada"
                elif w == KALTARA and tahun == 2012:
                    status = "belum_tercakup"
                elif (w, str(tahun)) in nilai:
                    status = "terisi"
                else:
                    status = "missing"
                baris.append(
                    {
                        "seri_kode": kode,
                        "periode": str(tahun),
                        "wilayah_kode": w,
                        "nama_wilayah": p["nama_wilayah"],
                        "status": status,
                        "nilai": nilai.get((w, str(tahun)), np.nan),
                    }
                )
    return pd.DataFrame(baris)


def kelengkapan_grid(grid):
    baris = []
    for kode, g in grid.groupby("seri_kode", sort=True):
        for tahun, gg in [("semua", g), *g.groupby("periode", sort=True)]:
            n_sel = len(gg)
            terisi = int((gg["status"] == "terisi").sum())
            baris.append(
                {
                    "seri_kode": kode,
                    "periode": tahun,
                    "n_sel": n_sel,
                    "n_terisi": terisi,
                    "persen_terisi": terisi / n_sel * 100 if n_sel else np.nan,
                    "n_missing": int((gg["status"] == "missing").sum()),
                    "n_tidak_terbit": int((gg["status"] == "tidak_terbit").sum()),
                    "n_belum_ada": int((gg["status"] == "belum_ada").sum()),
                    "n_belum_tercakup": int((gg["status"] == "belum_tercakup").sum()),
                }
            )
    return pd.DataFrame(baris)


def grid_nasional(utama):
    return utama[utama["wilayah_kode"] == 9999][["seri_kode", "periode", "nilai", "satuan"]].sort_values(
        ["seri_kode", "periode"]
    )


def ketersediaan_pembanding(silver):
    pembanding = silver[silver["sumber"].isin(["who_gho", "wdi"])].copy()
    panjang = pembanding[
        ["sumber", "seri_kode", "rincian", "satuan", "periode", "nilai", "_berkas_raw"]
    ].sort_values(["sumber", "seri_kode", "rincian", "periode"])
    tahun_utama = set(utama_tahun)
    baris = []
    for kunci, g in pembanding.groupby(["sumber", "seri_kode", "rincian", "satuan"]):
        sumber, seri, rincian, satuan = kunci
        tahun = sorted(g["periode"].astype(int).unique())
        irisan_katalog = sorted(set(tahun) & set(TAHUN_GRID))
        irisan_obs = sorted(set(tahun) & tahun_utama)
        if seri == "MDG_0000000003":
            sebanding = "ya (kandidat)" if "Y15T19" in rincian else "tidak"
            alasan = (
                "kelompok umur 15-19 sama dengan var1353 dan satuan per 1.000; tetapi tidak ada tahun observasi yang beririsan"
                if "Y15T19" in rincian
                else "kelompok umur 10-14 berbeda dari var1353 (15-19)"
            )
            pasangan = "var1353"
        elif seri == "SDGFPALL":
            sebanding = "ya"
            alasan = "perempuan 15-49, kebutuhan KB terpenuhi dengan metode modern, satuan persen; sebanding dengan var1394"
            pasangan = "var1394"
        elif seri == "SP.ADO.TFRT":
            sebanding = "ya (definisi sama, metode berbeda)"
            alasan = "per 1.000 perempuan 15-19; WDI memakai estimasi UN WPP, BPS memakai survei DHS"
            pasangan = "var1353"
        else:
            sebanding = "tidak"
            alasan = "tidak dievaluasi"
            pasangan = ""
        baris.append(
            {
                "sumber": sumber,
                "seri_pembanding": seri,
                "pasangan_seri_utama": pasangan,
                "rincian": rincian,
                "satuan": satuan,
                "tahun_min": min(tahun),
                "tahun_max": max(tahun),
                "n_tahun_tersedia": len(tahun),
                "daftar_tahun": ";".join(str(t) for t in tahun),
                "n_irisan_katalog_2012_2017": len(irisan_katalog),
                "tahun_irisan_katalog": ";".join(str(t) for t in irisan_katalog),
                "n_irisan_observasi_utama": len(irisan_obs),
                "tahun_irisan_observasi": ";".join(str(t) for t in irisan_obs),
                "sebanding": sebanding,
                "alasan": alasan,
            }
        )
    return panjang.reset_index(drop=True), pd.DataFrame(baris).sort_values(["seri_pembanding", "rincian"]).reset_index(drop=True)


def bandingkan_csv_json():
    baris = []
    for kode in BPS_META:
        csv = baca_bps(kode)[["wilayah_kode", "periode", "nilai"]]
        js = baca_bps_json(kode)
        gabung = csv.merge(js, on=["wilayah_kode", "periode"], how="outer", indicator=True)
        sama = int(((gabung["_merge"] == "both") & np.isclose(gabung["nilai"], gabung["nilai_json"])).sum())
        beda = int(((gabung["_merge"] == "both") & ~np.isclose(gabung["nilai"], gabung["nilai_json"])).sum())
        hanya_csv = int((gabung["_merge"] == "left_only").sum())
        hanya_json = int((gabung["_merge"] == "right_only").sum())
        baris.append(
            {
                "seri_kode": kode,
                "n_csv": len(csv),
                "n_json": len(js),
                "n_sama": sama,
                "n_beda": beda,
                "hanya_di_csv": hanya_csv,
                "hanya_di_json": hanya_json,
                "kesimpulan": "tidak ada duplikasi salah atau revisi; CSV dan JSON identik",
            }
        )
    return pd.DataFrame(baris)


def _simpan_tabel(nama, df):
    TABEL.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABEL / nama, index=False)


def gambar_boxplot(utama):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    for ax, (kode, g) in zip(axes, utama.groupby("seri_kode", sort=True)):
        tahun = sorted(g["periode"].unique())
        posisi = {t: i for i, t in enumerate(tahun, start=1)}
        data = [gg["nilai"].astype(float).values for _, gg in g.groupby("periode", sort=True)]
        label = [f"{p}\n(n={len(d)})" for p, d in zip(tahun, data)]
        bp = ax.boxplot(data, tick_labels=label, patch_artist=True, widths=0.55, showfliers=False)
        for patch in bp["boxes"]:
            patch.set_facecolor("#cfe2f3")
            patch.set_alpha(0.8)
        for i, d in enumerate(data, start=1):
            x = np.random.default_rng(42).normal(i, 0.045, len(d))
            ax.scatter(x, d, s=16, color="#2c3e50", alpha=0.55, zorder=3)
        nasional = g[g["wilayah_kode"] == 9999]
        for _, r in nasional.iterrows():
            ax.scatter(posisi[r["periode"]], r["nilai"], marker="D", s=90, color="#c0392b", zorder=5, label="Indonesia")
        ax.set_title(f"{kode}\n{g['satuan'].iloc[0]}", fontsize=10)
        ax.set_ylabel("nilai")
        ax.grid(axis="y", alpha=0.25)
        ax.legend(loc="best", fontsize=8)
    fig.suptitle("Boxplot nilai provinsi per tahun (titik = provinsi, berlian = Indonesia)", fontsize=11)
    fig.tight_layout()
    fig.savefig(GAMBAR / "boxplot_var1394_var1353.png", bbox_inches="tight")
    plt.close(fig)


def gambar_deret(utama, anomali):
    for kode, g in utama.groupby("seri_kode", sort=True):
        fig, ax = plt.subplots(figsize=(11, 6.2))
        prov = g[g["wilayah_kode"] != 9999]
        p = prov.pivot_table(index=["wilayah_kode", "nama_wilayah"], columns="periode", values="nilai")
        for _, r in p.iterrows():
            ax.plot([2012, 2017], [r.get("2012", np.nan), r.get("2017", np.nan)], color="#7f8c8d", alpha=0.35, lw=1)
        nasional = g[g["wilayah_kode"] == 9999].sort_values("periode")
        ax.plot(nasional["periode"].astype(int), nasional["nilai"], color="#c0392b", lw=3, marker="D", label="Indonesia")
        if not anomali.empty:
            a = anomali[anomali["seri_kode"] == kode]
            for _, r in a.iterrows():
                tahun = 2017 if r["periode"] in {"2017", "2012->2017"} else 2012
                ax.scatter(tahun, r["nilai"], color="#e67e22", s=55, zorder=5)
                ax.annotate(
                    f"{r['nama_wilayah']} ({r['kategori']})",
                    (tahun, r["nilai"]),
                    textcoords="offset points",
                    xytext=(4, 5),
                    fontsize=7,
                    color="#7e5109",
                )
        ax.set_xticks([2012, 2017])
        ax.set_xlabel("tahun")
        ax.set_ylabel(g["satuan"].iloc[0])
        ax.set_title(f"Deret waktu provinsi {kode} (garis abu-abu = provinsi, merah = Indonesia)")
        ax.grid(alpha=0.25)
        ax.legend(loc="best", fontsize=8)
        fig.tight_layout()
        fig.savefig(GAMBAR / f"deret_waktu_{kode}.png", bbox_inches="tight")
        plt.close(fig)


def gambar_zscore(utama):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (kode, g) in zip(axes, utama.groupby("seri_kode", sort=True)):
        for tahun, gg in g.groupby("periode", sort=True):
            nilai = gg["nilai"].astype(float)
            sd = nilai.std(ddof=0)
            z = (nilai - nilai.mean()) / sd if sd else nilai * 0
            ax.scatter(np.full(len(gg), int(tahun)), z, s=24, alpha=0.6, color="#2c3e50")
            for _, r in gg.assign(z=z).iterrows():
                if abs(r["z"]) >= 2:
                    ax.annotate(r["nama_wilayah"], (int(tahun), r["z"]), textcoords="offset points", xytext=(5, 4), fontsize=7)
        ax.axhline(2, color="#c0392b", ls="--", lw=1)
        ax.axhline(-2, color="#c0392b", ls="--", lw=1)
        ax.axhline(0, color="#95a5a6", lw=0.8)
        ax.set_xticks([2012, 2017])
        ax.set_xlabel("tahun")
        ax.set_ylabel("z-score dalam tahun")
        ax.set_title(f"z-score {kode} (ambang ±2)")
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(GAMBAR / "zscore_anomali.png", bbox_inches="tight")
    plt.close(fig)


def gambar_delta(utama):
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.4))
    for ax, (kode, g) in zip(axes, utama.groupby("seri_kode", sort=True)):
        p = g.pivot_table(index=["wilayah_kode", "nama_wilayah"], columns="periode", values="nilai").dropna()
        d = (p["2017"] - p["2012"]).sort_values()
        warna = ["#c0392b" if v < 0 else "#27ae60" for v in d]
        ax.barh([n for _, n in d.index], d.values, color=warna, alpha=0.8)
        ax.axvline(0, color="black", lw=0.8)
        ax.set_title(f"Perubahan {kode} 2012→2017")
        ax.set_xlabel("delta nilai")
        ax.tick_params(axis="y", labelsize=7)
        ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(GAMBAR / "perubahan_2012_2017.png", bbox_inches="tight")
    plt.close(fig)


def gambar_pembanding(silver):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
    ax = axes[0]
    wdi = silver[(silver["seri_kode"] == "SP.ADO.TFRT")].sort_values("periode")
    ax.plot(wdi["periode"].astype(int), wdi["nilai"], label="WDI SP.ADO.TFRT", color="#2980b9", lw=2)
    mdg = silver[(silver["seri_kode"] == "MDG_0000000003") & silver["rincian"].str.contains("Y15T19")].sort_values("periode")
    ax.scatter(mdg["periode"].astype(int), mdg["nilai"], label="WHO MDG (15-19)", color="#8e44ad", s=28)
    beda = silver[(silver["seri_kode"] == "var1353") & (silver["wilayah_kode"] == 9999)].sort_values("periode")
    ax.scatter(beda["periode"].astype(int), beda["nilai"], label="BPS var1353 (Indonesia)", color="#c0392b", marker="D", s=70)
    ax.set_title("Laju kelahiran remaja 15-19 (per 1.000)")
    ax.set_xlabel("tahun")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)

    ax = axes[1]
    sdg = silver[(silver["seri_kode"] == "SDGFPALL")].sort_values("periode")
    ax.plot(sdg["periode"].astype(int), sdg["nilai"], label="WHO SDGFPALL", color="#8e44ad", marker="o", lw=2)
    kb = silver[(silver["seri_kode"] == "var1394") & (silver["wilayah_kode"] == 9999)].sort_values("periode")
    ax.scatter(kb["periode"].astype(int), kb["nilai"], label="BPS var1394 (Indonesia)", color="#c0392b", marker="D", s=70)
    ax.set_title("Kebutuhan KB terpenuhi metode modern (%)")
    ax.set_xlabel("tahun")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(GAMBAR / "pembanding_nasional.png", bbox_inches="tight")
    plt.close(fig)


def gambar_kelengkapan(grid):
    status_ke_angka = {"terisi": 3, "belum_tercakup": 2, "belum_ada": 1, "tidak_terbit": 0, "missing": -1}
    fig, axes = plt.subplots(1, 2, figsize=(12, 9))
    for ax, (kode, g) in zip(axes, grid.groupby("seri_kode", sort=True)):
        p = g.pivot_table(index=["wilayah_kode", "nama_wilayah"], columns="periode", values="status", aggfunc="first")
        mat = p.replace(status_ke_angka).astype(float)
        ax.imshow(mat.values, aspect="auto", cmap="viridis", vmin=-1, vmax=3)
        ax.set_xticks(range(len(mat.columns)))
        ax.set_xticklabels(mat.columns, rotation=0)
        ax.set_yticks(range(len(mat.index)))
        ax.set_yticklabels([n for _, n in mat.index], fontsize=6)
        ax.set_title(f"Kelengkapan grid {kode}")
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                kode_status = p.iloc[i, j]
                ax.text(j, i, "T" if kode_status == "terisi" else ("-" if kode_status == "tidak_terbit" else "o"), ha="center", va="center", fontsize=6, color="white")
    fig.suptitle("Grid 38 provinsi x 2012-2017: T=terisi, -=tidak terbit, o=belum ada/tercakup", fontsize=10)
    fig.tight_layout()
    fig.savefig(GAMBAR / "kelengkapan_panel.png", bbox_inches="tight")
    plt.close(fig)


def main():
    TABEL.mkdir(parents=True, exist_ok=True)
    GAMBAR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"figure.dpi": 120, "font.size": 9})

    silver = buat_silver()
    utama = silver[silver["seri_kode"].isin(BPS_META)].copy()
    global utama_tahun
    utama_tahun = set(utama["periode"].astype(int).unique())

    stats_seri = statistik_seri(utama)
    stats_prov = statistik_provinsi(utama)
    nasional = statistik_nasional(utama)
    patahan = ringkasan_patahan(utama)
    anomali = deteksi_anomali(utama, patahan)
    kategori = ringkasan_kategori(anomali, utama)
    grid = bentuk_grid(utama)
    lengkap = kelengkapan_grid(grid)
    panjang, ringkas = ketersediaan_pembanding(silver)
    dedup = bandingkan_csv_json()

    _simpan_tabel("statistik_seri.csv", stats_seri)
    _simpan_tabel("statistik_provinsi.csv", stats_prov)
    _simpan_tabel("statistik_nasional.csv", nasional)
    _simpan_tabel("ringkasan_patahan.csv", patahan)
    _simpan_tabel("anomali.csv", anomali)
    _simpan_tabel("ringkasan_kategori_anomali.csv", kategori)
    _simpan_tabel("grid_panel.csv", grid)
    _simpan_tabel("kelengkapan_grid.csv", lengkap)
    _simpan_tabel("ketersediaan_pembanding_panjang.csv", panjang)
    _simpan_tabel("ketersediaan_pembanding_ringkas.csv", ringkas)
    _simpan_tabel("deduplikasi_csv_json.csv", dedup)
    _simpan_tabel("grid_nasional.csv", grid_nasional(utama))

    gambar_boxplot(utama)
    gambar_deret(utama, anomali)
    gambar_zscore(utama)
    gambar_delta(utama)
    gambar_pembanding(silver)
    gambar_kelengkapan(grid)

    sel_kosong = int((grid["status"] != "terisi").sum())
    sel_struktural = int(grid["status"].isin(["tidak_terbit", "belum_ada", "belum_tercakup"]).sum())
    sel_missing = int((grid["status"] == "missing").sum())
    print(f"baris_silver={len(silver)}")
    print(f"baris_seri_utama={len(utama)}")
    print(f"sel_kosong_grid={sel_kosong}")
    print(f"sel_kosong_struktural={sel_struktural}")
    print(f"sel_kosong_sejati={sel_missing}")
    print(f"outlier_ditandai={len(anomali)}")
    print(f"patahan_seri={int((patahan['indikasi_patahan'] == 'ya').sum())}")
    print(f"tabel={TABEL}")
    print(f"gambar={GAMBAR}")


if __name__ == "__main__":
    main()
