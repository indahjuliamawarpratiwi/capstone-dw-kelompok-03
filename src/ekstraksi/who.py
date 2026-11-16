"""Pembaca CSV dan metadata JSON WHO GHO untuk tahap 1 (ekstraksi).

Pembaca ini hanya meratakan struktur dan mencatat asal baris. Semua kolom dimensi
(`DIM_*`) dipertahankan apa adanya; nilai kosong berarti dimensi tidak berlaku dan
tidak diisi. Data dua indikator tetap dibaca dari berkas masing-masing agar lineage
tidak hilang.

Jumlah baris snapshot 2026-10-20:

- who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv    26 baris
- who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv           6 baris
- who_gho/2026-10-20/datadot/ddiindicators_skip0000.json    62 baris, 2 cocok
- who_gho/2026-10-20/odata/Indicator.json                 3099 baris, 2 cocok

Berkas MDG_0000000003 memuat dua kelompok umur: `Y10T14` (12 baris) dan `Y15T19`
(14 baris). Keduanya dipertahankan; pembaca tidak menggabungkan atau menyaring umur.
Berkas SDGFPALL memuat `DIM_AGE=Y15T49` (6 baris).
"""
import csv
import io
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW
from ._umum import baca_teks, ke_angka, tempel_lineage

SERI = {"MDG_0000000003", "SDGFPALL"}


def baca_csv(path, raw=RAW):
    """Baca satu CSV WHO GHO dengan seluruh kolom asal dan lineage."""
    path = Path(path)
    pembaca = csv.DictReader(io.StringIO(baca_teks(path)))
    kolom = list(pembaca.fieldnames or [])
    if not kolom:
        raise ValueError(f"{path}: header CSV tidak ditemukan")

    baris = []
    for asal in pembaca:
        rekaman = {nama: asal.get(nama) for nama in kolom}
        for nama in kolom:
            if nama.startswith("RATE_"):
                rekaman[nama] = ke_angka(rekaman[nama])
        baris.append(rekaman)

    df = pd.DataFrame(baris, columns=kolom)
    return tempel_lineage(df, path, raw)


def _cocok_ddi(rekaman, seri=SERI):
    """Cocokkan rekaman DDI lewat AlternativeCodes, UrlName, atau UniqueIdentifier."""
    alternatif = rekaman.get("AlternativeCodes") or []
    if isinstance(alternatif, str):
        alternatif = [x.strip() for x in alternatif.split(",")]
    alternatif = {str(x).strip() for x in alternatif}
    return (
        bool(alternatif & seri)
        or str(rekaman.get("UrlName")) in seri
        or str(rekaman.get("UniqueIdentifier")) in seri
    )


def baca_metadata_ddi(path, raw=RAW, seri=SERI):
    """Baca metadata indikator DDI WHO GHO dan saring menurut kode seri."""
    path = Path(path)
    isi = json.loads(baca_teks(path))
    rekaman = isi.get("value") if isinstance(isi, dict) else isi
    if not isinstance(rekaman, list):
        raise ValueError(f"{path}: struktur metadata DDI tidak dikenal")

    baris = [r for r in rekaman if _cocok_ddi(r, set(seri))]
    df = pd.json_normalize(baris, sep=".")
    return tempel_lineage(df, path, raw)


def baca_metadata_odata(path, raw=RAW, seri=SERI):
    """Baca metadata indikator OData WHO GHO dan saring menurut IndicatorCode."""
    path = Path(path)
    isi = json.loads(baca_teks(path))
    rekaman = isi.get("value") if isinstance(isi, dict) else isi
    if not isinstance(rekaman, list):
        raise ValueError(f"{path}: struktur metadata OData tidak dikenal")

    baris = [r for r in rekaman if r.get("IndicatorCode") in seri]
    df = pd.DataFrame(baris)
    return tempel_lineage(df, path, raw)


def _berkas(raw):
    akar = Path(raw) / "who_gho"
    if not akar.is_dir():
        raise FileNotFoundError(f"folder WHO GHO tidak ditemukan: {akar}")
    return (
        sorted(akar.glob("**/datadot/*.csv")),
        sorted(akar.glob("**/datadot/*ddiindicator*.json")),
        sorted(akar.glob("**/odata/*.json")),
    )


def baca_semua(raw=RAW):
    """Baca semua CSV data dan metadata WHO GHO yang relevan."""
    csv_paths, ddi_paths, odata_paths = _berkas(raw)
    if not csv_paths or not ddi_paths or not odata_paths:
        raise FileNotFoundError(f"berkas WHO GHO belum lengkap di {Path(raw) / 'who_gho'}")

    data = pd.concat([baca_csv(p, raw) for p in csv_paths], ignore_index=True)
    ddi = pd.concat(
        [baca_metadata_ddi(p, raw) for p in ddi_paths], ignore_index=True
    ) if len(ddi_paths) > 1 else baca_metadata_ddi(ddi_paths[0], raw)
    odata = pd.concat(
        [baca_metadata_odata(p, raw) for p in odata_paths], ignore_index=True
    ) if len(odata_paths) > 1 else baca_metadata_odata(odata_paths[0], raw)

    return {"who_gho": data, "who_gho_ddi": ddi, "who_gho_indikator": odata}


if __name__ == "__main__":
    csv_paths, _, _ = _berkas(RAW)
    for path in csv_paths:
        df = baca_csv(path, RAW)
        rel = path.resolve().relative_to(Path(RAW).resolve()).as_posix()
        print(f"{rel}: {len(df)} baris, DIM_AGE={df['DIM_AGE'].value_counts().to_dict()}")
    hasil = baca_semua()
    for nama, df in hasil.items():
        print(f"{nama}: {len(df)} baris")
