"""Tahap 2 — Profil dan deteksi anomali per seri.

Keluaran:
- data/silver/profil.csv: statistik deskriptif, IQR, missing, duplikat, dan patahan per seri.
- data/silver/anomali.csv: baris nilai kosong, outlier, ringkasan patahan, dan duplikat.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROFIL = ROOT / "data" / "silver" / "profil.csv"
ANOMALI = ROOT / "data" / "silver" / "anomali.csv"
BOXPLOT = ROOT / "data" / "silver" / "boxplot_seri.png"

KUNCI_LOGIS = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian"]
GRUP_SERI = ["sumber", "seri_kode", "rincian"]
GRUP_WILAYAH = GRUP_SERI + ["wilayah_kode", "nama_wilayah"]

KOLOM_PROFIL = [
    "sumber", "seri_kode", "rincian", "jumlah_baris", "jumlah_observasi",
    "jumlah_wilayah", "jumlah_berkas", "periode_min", "periode_max",
    "nilai_min", "q1", "median", "q3", "nilai_max",
    "batas_bawah", "batas_atas", "jumlah_outlier", "persen_outlier",
    "jumlah_kosong", "persen_kosong", "jumlah_duplikat_logis", "jumlah_patahan",
]

KOLOM_ANOMALI = [
    "jenis", "sumber", "seri_kode", "rincian", "wilayah_kode", "nama_wilayah",
    "periode", "nilai", "keterangan",
]


def _tahun(series):
    return pd.to_numeric(
        series.astype(str).str.extract(r"^(\d{4})$")[0], errors="coerce"
    )


def _batas_iqr(nilai):
    q1 = nilai.quantile(0.25)
    q3 = nilai.quantile(0.75)
    iqr = q3 - q1
    return q1, q3, q1 - 1.5 * iqr, q3 + 1.5 * iqr


def _patahan(df):
    baris = []
    for kunci, grup in df.groupby(GRUP_WILAYAH, dropna=False, sort=True):
        tahun = sorted({int(x) for x in _tahun(grup["periode"]).dropna()})
        if len(tahun) < 2:
            continue
        hilang = [t for t in range(tahun[0], tahun[-1] + 1) if t not in set(tahun)]
        if not hilang:
            continue
        baris.append({
            "sumber": kunci[0],
            "seri_kode": kunci[1],
            "rincian": kunci[2],
            "wilayah_kode": kunci[3],
            "nama_wilayah": kunci[4],
            "periode_awal": tahun[0],
            "periode_akhir": tahun[-1],
            "jumlah_patahan": len(hilang),
            "tahun_hilang": ", ".join(str(t) for t in hilang),
        })
    return pd.DataFrame(baris)


def _profil(df):
    patahan = _patahan(df)
    if patahan.empty:
        rekap_patahan = pd.DataFrame(columns=GRUP_SERI + ["jumlah_patahan"])
    else:
        rekap_patahan = (
            patahan.groupby(GRUP_SERI, as_index=False, dropna=False)["jumlah_patahan"]
            .sum()
        )

    baris = []
    for kunci, grup in df.groupby(GRUP_SERI, dropna=False, sort=True):
        logis = grup.drop_duplicates(KUNCI_LOGIS)
        nilai = pd.to_numeric(logis["nilai"], errors="coerce")
        ada = nilai.dropna()
        if ada.empty:
            q1 = q3 = median = batas_bawah = batas_atas = float("nan")
            outlier = 0
        else:
            q1, q3, batas_bawah, batas_atas = _batas_iqr(ada)
            median = ada.median()
            outlier = int(((ada < batas_bawah) | (ada > batas_atas)).sum())

        kosong = int(nilai.isna().sum())
        baris.append({
            "sumber": kunci[0],
            "seri_kode": kunci[1],
            "rincian": kunci[2],
            "jumlah_baris": len(grup),
            "jumlah_observasi": len(logis),
            "jumlah_wilayah": grup["wilayah_kode"].nunique(),
            "jumlah_berkas": grup["_berkas_raw"].nunique(),
            "periode_min": str(grup["periode"].min()),
            "periode_max": str(grup["periode"].max()),
            "nilai_min": ada.min() if not ada.empty else float("nan"),
            "q1": q1,
            "median": median,
            "q3": q3,
            "nilai_max": ada.max() if not ada.empty else float("nan"),
            "batas_bawah": batas_bawah,
            "batas_atas": batas_atas,
            "jumlah_outlier": outlier,
            "persen_outlier": round(100 * outlier / len(ada), 2) if len(ada) else 0.0,
            "jumlah_kosong": kosong,
            "persen_kosong": round(100 * kosong / len(logis), 2),
            "jumlah_duplikat_logis": int(grup.duplicated(KUNCI_LOGIS).sum()),
        })

    kolom_awal = [k for k in KOLOM_PROFIL if k != "jumlah_patahan"]
    hasil = pd.DataFrame(baris, columns=kolom_awal)
    hasil = hasil.merge(rekap_patahan, on=GRUP_SERI, how="left")
    hasil["jumlah_patahan"] = hasil["jumlah_patahan"].fillna(0).astype("int64")
    return hasil[KOLOM_PROFIL]


def _anomali(df):
    baris = []

    kosong = df[df["nilai"].isna()].drop_duplicates(KUNCI_LOGIS)
    for _, row in kosong.sort_values(
        ["sumber", "seri_kode", "wilayah_kode", "periode"]
    ).iterrows():
        baris.append({
            "jenis": "nilai_kosong",
            "sumber": row["sumber"],
            "seri_kode": row["seri_kode"],
            "rincian": row["rincian"],
            "wilayah_kode": row["wilayah_kode"],
            "nama_wilayah": row["nama_wilayah"],
            "periode": row["periode"],
            "nilai": pd.NA,
            "keterangan": "Dibuang dari Silver; tidak diimputasi",
        })

    for kunci, grup in df.groupby(GRUP_SERI, dropna=False, sort=True):
        logis = grup.drop_duplicates(KUNCI_LOGIS)
        ada = pd.to_numeric(logis["nilai"], errors="coerce").dropna()
        if ada.empty:
            continue
        _, _, batas_bawah, batas_atas = _batas_iqr(ada)
        luar = logis[
            logis["nilai"].notna()
            & ((logis["nilai"] < batas_bawah) | (logis["nilai"] > batas_atas))
        ]
        for _, row in luar.iterrows():
            baris.append({
                "jenis": "outlier_iqr",
                "sumber": row["sumber"],
                "seri_kode": row["seri_kode"],
                "rincian": row["rincian"],
                "wilayah_kode": row["wilayah_kode"],
                "nama_wilayah": row["nama_wilayah"],
                "periode": row["periode"],
                "nilai": row["nilai"],
                "keterangan": (
                    f"Di luar batas IQR 1,5 ({batas_bawah:.3f}, {batas_atas:.3f}); "
                    "dipertahankan (satu baris per observasi logis)"
                ),
            })

    patahan = _patahan(df)
    if not patahan.empty:
        for _, row in patahan.sort_values(GRUP_WILAYAH).iterrows():
            baris.append({
                "jenis": "patahan_seri",
                "sumber": row["sumber"],
                "seri_kode": row["seri_kode"],
                "rincian": row["rincian"],
                "wilayah_kode": row["wilayah_kode"],
                "nama_wilayah": row["nama_wilayah"],
                "periode": f"{row['periode_awal']}-{row['periode_akhir']}",
                "nilai": row["jumlah_patahan"],
                "keterangan": f"Tahun hilang: {row['tahun_hilang']}; tidak diinterpolasi",
            })

    duplikat = df[df.duplicated(KUNCI_LOGIS, keep=False)]
    for kunci, grup in duplikat.groupby(GRUP_SERI, dropna=False, sort=True):
        jumlah = int(grup.duplicated(KUNCI_LOGIS).sum())
        baris.append({
            "jenis": "duplikat_lintas_berkas",
            "sumber": kunci[0],
            "seri_kode": kunci[1],
            "rincian": kunci[2],
            "wilayah_kode": pd.NA,
            "nama_wilayah": "",
            "periode": f"{grup['periode'].min()}-{grup['periode'].max()}",
            "nilai": jumlah,
            "keterangan": (
                f"{jumlah} baris duplikat logis CSV/JSON dipertahankan sebagai lineage"
            ),
        })

    return pd.DataFrame(baris, columns=KOLOM_ANOMALI)


def _boxplot(df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grup = []
    label = []
    for kunci, bagian in df.groupby(GRUP_SERI, dropna=False, sort=True):
        nilai = pd.to_numeric(bagian["nilai"], errors="coerce").dropna()
        if nilai.empty:
            continue
        grup.append(nilai.to_numpy())
        rincian = "" if pd.isna(kunci[2]) else f" | {kunci[2]}"
        label.append(f"{kunci[0]} {kunci[1]}{rincian}")

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.boxplot(grup, tick_labels=label, showfliers=True)
    ax.set_title("Sebaran nilai per seri sebelum pembersihan (Kasus 03)")
    ax.set_ylabel("Nilai")
    ax.tick_params(axis="x", labelrotation=20)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    BOXPLOT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(BOXPLOT, dpi=150)
    plt.close(fig)
    return BOXPLOT


def jalankan(df):
    """Tulis profil, anomali, dan boxplot; kembalikan (profil, anomali)."""
    profil = _profil(df)
    anomali = _anomali(df)
    PROFIL.parent.mkdir(parents=True, exist_ok=True)
    profil.to_csv(PROFIL, index=False)
    anomali.to_csv(ANOMALI, index=False)
    _boxplot(df)
    return profil, anomali
