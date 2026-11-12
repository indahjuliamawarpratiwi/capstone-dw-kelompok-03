"""Pembaca JSON data dan metadata WDI untuk tahap 1 (ekstraksi).

Pembaca ini hanya meratakan struktur dan mencatat asal baris. Tidak ada pembersihan,
deduplikasi, imputasi, atau perubahan nilai. Data dan metadata dari dua berkas sumber
indikator tetap dibaca terpisah karena berasal dari berkas yang berbeda.

Jumlah baris snapshot 2026-10-20 sebelum penyaringan:

- wdi/2026-10-20/data/kelompok-03-hal-01.json       2112 baris, 32 indikator
- wdi/2026-10-20/metadata/sumber.json                  71 baris sumber
- wdi/2026-10-20/metadata/sumber2_indikator.json     1498 baris indikator
- wdi/2026-10-20/metadata/sumber46_indikator.json      408 baris indikator

Setelah disaring untuk seri SP.ADO.TFRT:

- data                                               66 baris (1960-2025, 1 nilai kosong)
- metadata indikator sumber 2                         1 baris
- metadata indikator sumber 46                        1 baris
- metadata sumber                                     2 baris (id 2 dan 46)

Baris 2025 dengan nilai kosong tetap dipertahankan. Pembaca tidak mengisi nilai dan
tidak membuang baris kosong.
"""
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW
from ._umum import baca_teks, ke_angka, tempel_lineage

SERI = "SP.ADO.TFRT"

KOLOM_DATA = [
    "indicator.id", "indicator.value", "country.id", "country.value",
    "countryiso3code", "date", "value", "scale", "unit", "obs_status", "decimal",
]
KOLOM_SUMBER = [
    "id", "lastupdated", "name", "code", "description", "url",
    "dataavailability", "metadataavailability", "concepts",
]
KOLOM_INDIKATOR = [
    "id", "name", "unit", "source.id", "source.value", "sourceNote",
    "sourceOrganization", "topics",
]


def _muat(path):
    """Kembalikan (metadata, daftar rekaman) dari berkas JSON WDI."""
    isi = json.loads(baca_teks(path))
    if isinstance(isi, list) and len(isi) == 2 and isinstance(isi[1], list):
        return isi[0], isi[1]
    if isinstance(isi, dict) and isinstance(isi.get("value"), list):
        return {k: v for k, v in isi.items() if k != "value"}, isi["value"]
    raise ValueError(f"{path}: struktur JSON WDI tidak dikenal")


def _data_mentah(path):
    """Daftar rekaman data tanpa penyaringan, dipakai juga untuk statistik."""
    _, rekaman = _muat(path)
    return rekaman


def baca_data(path, raw=RAW, seri=SERI):
    """Baca satu JSON data WDI dan saring menurut indicator.id."""
    path = Path(path)
    baris = []
    for rekaman in _data_mentah(path):
        indikator = rekaman.get("indicator") or {}
        negara = rekaman.get("country") or {}
        if indikator.get("id") != seri:
            continue
        baris.append({
            "indicator.id": indikator.get("id"),
            "indicator.value": indikator.get("value"),
            "country.id": negara.get("id"),
            "country.value": negara.get("value"),
            "countryiso3code": rekaman.get("countryiso3code"),
            "date": rekaman.get("date"),
            "value": ke_angka(rekaman.get("value")),
            "scale": rekaman.get("scale"),
            "unit": rekaman.get("unit"),
            "obs_status": rekaman.get("obs_status"),
            "decimal": rekaman.get("decimal"),
        })

    df = pd.DataFrame(baris, columns=KOLOM_DATA)
    return tempel_lineage(df, path, raw)


def baca_sumber(path, raw=RAW, id_relevan=None):
    """Baca metadata sumber WDI; bila diminta, saring ke id sumber yang relevan."""
    path = Path(path)
    _, rekaman = _muat(path)
    if id_relevan is not None:
        rekaman = [r for r in rekaman if str(r.get("id")) in id_relevan]

    baris = [{kolom: rekaman_dict.get(kolom) for kolom in KOLOM_SUMBER}
             for rekaman_dict in rekaman]
    df = pd.DataFrame(baris, columns=KOLOM_SUMBER)
    return tempel_lineage(df, path, raw)


def baca_indikator(path, raw=RAW, seri=SERI):
    """Baca satu JSON metadata indikator WDI dan saring menurut id."""
    path = Path(path)
    _, rekaman = _muat(path)

    baris = []
    for rekaman_dict in rekaman:
        if rekaman_dict.get("id") != seri:
            continue
        sumber = rekaman_dict.get("source") or {}
        baris.append({
            "id": rekaman_dict.get("id"),
            "name": rekaman_dict.get("name"),
            "unit": rekaman_dict.get("unit"),
            "source.id": sumber.get("id"),
            "source.value": sumber.get("value"),
            "sourceNote": rekaman_dict.get("sourceNote"),
            "sourceOrganization": rekaman_dict.get("sourceOrganization"),
            "topics": rekaman_dict.get("topics"),
        })

    df = pd.DataFrame(baris, columns=KOLOM_INDIKATOR)
    return tempel_lineage(df, path, raw)


def _berkas(raw):
    akar = Path(raw) / "wdi"
    if not akar.is_dir():
        raise FileNotFoundError(f"folder WDI tidak ditemukan: {akar}")
    return (
        sorted(akar.glob("**/data/*.json")),
        sorted(akar.glob("**/metadata/sumber.json")),
        sorted(akar.glob("**/metadata/*indikator*.json")),
    )


def baca_semua(raw=RAW):
    """Baca semua berkas WDI dan kembalikan data serta metadata yang relevan."""
    data_paths, sumber_paths, indikator_paths = _berkas(raw)
    if not data_paths or not sumber_paths or not indikator_paths:
        raise FileNotFoundError(f"berkas WDI belum lengkap di {Path(raw) / 'wdi'}")

    indikator = pd.concat(
        [baca_indikator(p, raw) for p in indikator_paths], ignore_index=True
    ) if indikator_paths else pd.DataFrame(columns=KOLOM_INDIKATOR)
    id_sumber = {str(x) for x in indikator["source.id"].dropna()}
    sumber = pd.concat(
        [baca_sumber(p, raw, id_sumber) for p in sumber_paths], ignore_index=True
    ) if sumber_paths else pd.DataFrame(columns=KOLOM_SUMBER)
    data = pd.concat([baca_data(p, raw) for p in data_paths], ignore_index=True)

    return {"wdi": data, "wdi_sumber": sumber, "wdi_indikator": indikator}


if __name__ == "__main__":
    data_paths, _, _ = _berkas(RAW)
    for path in data_paths:
        rel = path.resolve().relative_to(Path(RAW).resolve()).as_posix()
        print(f"{rel}: {len(_data_mentah(path))} baris mentah")
    hasil = baca_semua()
    for nama, df in hasil.items():
        print(f"{nama}: {len(df)} baris")
        print(df.groupby("_berkas_raw", sort=True).size().to_string())
