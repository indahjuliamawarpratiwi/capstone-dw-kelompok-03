
"""
Panel provinsi × periode × indikator Gold untuk var1394, var1353.

- Satuan seragam per indikator
- Traceability ke baris Silver
- Versi asli disimpan jika ada transformasi
"""

import pandas as pd

from src.laporan import ROOT, catat

GOLD_PATH = ROOT / "data" / "gold" / "panel.parquet"

SATUAN_BAKU = {
    "var1394": "persen",
    "var1353": "per_1000_perempuan_seumur",
}

INDIKATOR = ["var1394", "var1353"]


def seragamkan_satuan(df):
    """Validasi dan seragamkan satuan per indikator."""
    df = df.copy()
    df["satuan_asli"] = df["satuan"]

    for var, satuan in SATUAN_BAKU.items():
        mask = df["seri_kode"] == var
        satuan_ditemukan = set(
            df.loc[mask, "satuan"].dropna().unique()
        )

        satuan_tidak_sesuai = satuan_ditemukan - {satuan}

        if satuan_tidak_sesuai:
            raise ValueError(
                f"Satuan {var} tidak sesuai. "
                f"Ditemukan: {satuan_ditemukan}, "
                f"seharusnya: {satuan}"
            )

        df.loc[mask, "satuan"] = satuan

    return df


def jalankan(silver, ekstraksi=None):
    """Membuat panel Gold tingkat provinsi."""
    panel = silver[
        silver["seri_kode"].isin(INDIKATOR)
    ].copy()

    # Hapus agregat nasional, pertahankan seluruh provinsi
    panel = panel[panel["wilayah_kode"] != 9999]

    # Seragamkan rincian umur
    mask_umur = panel["rincian"].isin(
        ["umur=10-14", "umur=15-19"]
    )
    panel.loc[mask_umur, "rincian"] = (
        panel.loc[mask_umur, "rincian"].str.replace(
            "umur=", "", regex=False
        )
    )

    # Validasi satuan
    panel = seragamkan_satuan(panel)

    # Pastikan kunci panel unik
    kunci = [
        "wilayah_kode",
        "periode",
        "seri_kode",
        "rincian",
    ]

    assert not panel.duplicated(kunci).any(), (
        "Ada duplikasi pada kunci panel"
    )

    # Simpan hasil Gold
    GOLD_PATH.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(GOLD_PATH, index=False)

    catat(baris_gold=len(panel))

    return len(panel)
