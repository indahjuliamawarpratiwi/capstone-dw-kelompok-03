"""Pembaca CSV dan JSON WebAPI BPS untuk tahap 1 (ekstraksi).

Pembaca ini hanya meratakan struktur dan mencatat asal baris. Tidak ada pembersihan, deduplikasi,
imputasi, atau penggabungan nilai antarberkas. Setiap baris membawa `_berkas_raw` (relatif
data/raw/) dan `_sha256_raw` (dari src.common.manifest), sehingga CSV dan JSON untuk seri yang
sama tetap muncul sebagai baris terpisah.

Jumlah baris snapshot 2026-10-20 (baris header CSV tidak dihitung):

- bps/2026-10-20/sdg3_3_7_1_v1394.csv        69
- bps/2026-10-20/sdg3_3_7_2_v1353.csv        69
- bps/2026-10-20/json/sdg3_3_7_1_v1394.json  69
- bps/2026-10-20/json/sdg3_3_7_2_v1353.json  69

Total 276 baris. Berkas `manifest_asal.json` adalah metadata, bukan tabel data, jadi tidak
dimasukkan ke tabel panjang.

Catatan kasus 4.2: judul tabel var1353 di JSON adalah "Angka Kelahiran Pada Perempuan Usia
15-19 Tahun Menurut Provinsi". Kelompok umur yang benar-benar dicakup adalah 15-19 tahun,
bukan 15-49 tahun. Judul itu tidak diubah oleh pembaca ini.
"""
import csv
import io
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw

KOLOM_ASAL = [
    "var_id", "wilayah_id", "wilayah", "turvar_id", "turvar",
    "tahun_id", "tahun", "periode_id", "periode", "nilai", "satuan",
]
ENCODING = ("utf-8-sig", "cp1252", "latin-1")


def _baca_teks(path):
    """Baca berkas dengan beberapa kemungkinan pengodean karakter."""
    mentah = Path(path).read_bytes()
    for pengodean in ENCODING:
        try:
            return mentah.decode(pengodean)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8", mentah, 0, len(mentah), "pengodean tidak dikenal")


def _deteksi_pemisah(teks):
    """Deteksi delimiter CSV dari beberapa baris pertama; fallback ke koma."""
    contoh = "\n".join(teks.splitlines()[:5])
    try:
        return csv.Sniffer().sniff(contoh, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def _ke_angka(nilai):
    """Ubah nilai menjadi angka tanpa mengisi nilai kosong.

    Mendukung desimal titik (44.4), desimal koma (44,4), dan pemisah ribuan Indonesia
    (1.234,5 -> 1234.5). Nilai kosong tetap menjadi NA agar tidak dianggap nol.
    """
    if nilai is None:
        return pd.NA
    if isinstance(nilai, bool):
        return float(nilai)
    if isinstance(nilai, (int, float)):
        return float(nilai)
    teks = str(nilai).strip()
    if not teks:
        return pd.NA
    if "," in teks:
        teks = teks.replace(".", "").replace(",", ".")
    elif teks.count(".") > 1:
        teks = teks.replace(".", "")
    return float(teks)


def _ke_int(nilai):
    """Ubah ID/kode numerik menjadi bilangan bulat; kosong menjadi NA."""
    if nilai is None:
        return pd.NA
    teks = str(nilai).strip()
    if not teks:
        return pd.NA
    angka = float(teks)
    if not angka.is_integer():
        raise ValueError(f"nilai bukan bilangan bulat: {nilai!r}")
    return int(angka)


def _tahun(label):
    """Label tahun JSON berupa teks; samakan tipenya dengan kolom tahun CSV."""
    teks = str(label).strip()
    try:
        return _ke_int(teks)
    except ValueError:
        return label


def _kode(nilai):
    """Representasi nilai dimensi untuk menyusun kunci datacontent."""
    if isinstance(nilai, float) and nilai.is_integer():
        nilai = int(nilai)
    return str(nilai)


def _peta_dimensi(obj, path):
    """Peta kunci datacontent -> metadata dimensi.

    Kunci WebAPI BPS adalah gabungan langsung (tanpa padding) dari nilai
    vervar + var + turvar + tahun + turtahun. Panjang tiap bagian dapat berbeda,
    jadi peta dibangun dari kombinasi nilai yang tercantum di metadata.
    """
    nama = ("vervar", "var", "turvar", "tahun", "turtahun")
    dimensi = {}
    for kunci in nama:
        isi = obj.get(kunci) or []
        if not isi:
            raise ValueError(f"{path}: metadata {kunci!r} kosong")
        dimensi[kunci] = isi

    peta = {}
    for vervar in dimensi["vervar"]:
        for var in dimensi["var"]:
            for turvar in dimensi["turvar"]:
                for tahun in dimensi["tahun"]:
                    for turtahun in dimensi["turtahun"]:
                        kunci = "".join(
                            _kode(x["val"]) for x in (vervar, var, turvar, tahun, turtahun)
                        )
                        if kunci in peta:
                            raise ValueError(f"{path}: kunci datacontent ambigu ({kunci})")
                        peta[kunci] = (vervar, var, turvar, tahun, turtahun)
    return peta


def _tempel_lineage(df, path, raw):
    """Tambahkan asal berkas dan sha256 dari MANIFEST.csv."""
    rel = Path(path).resolve().relative_to(Path(raw).resolve()).as_posix()
    df["_berkas_raw"] = rel
    df["_sha256_raw"] = sha256_raw(rel, raw)
    return df


def baca_csv(path, raw=RAW):
    """Baca satu CSV BPS menjadi tabel panjang dengan kolom asal + lineage."""
    path = Path(path)
    teks = _baca_teks(path)
    pembaca = csv.DictReader(io.StringIO(teks), delimiter=_deteksi_pemisah(teks))

    baris = []
    for asal in pembaca:
        baris.append({
            "var_id": _ke_int(asal.get("var_id")),
            "wilayah_id": _ke_int(asal.get("wilayah_id")),
            "wilayah": asal.get("wilayah"),
            "turvar_id": _ke_int(asal.get("turvar_id")),
            "turvar": asal.get("turvar"),
            "tahun_id": _ke_int(asal.get("tahun_id")),
            "tahun": _ke_int(asal.get("tahun")),
            "periode_id": _ke_int(asal.get("periode_id")),
            "periode": asal.get("periode"),
            "nilai": _ke_angka(asal.get("nilai")),
            "satuan": asal.get("satuan", ""),
        })

    df = pd.DataFrame(baris, columns=KOLOM_ASAL)
    return _tempel_lineage(df, path, raw)


def baca_json(path, raw=RAW):
    """Baca satu JSON WebAPI BPS dan ratakan vervar/turvar/tahun/datacontent."""
    path = Path(path)
    isi = json.loads(_baca_teks(path))
    if isinstance(isi, dict):
        isi = [isi]

    baris = []
    for obj in isi:
        status = obj.get("status")
        if status is not None and status != "OK":
            raise ValueError(f"{path}: status WebAPI BPS bukan OK ({status!r})")
        peta = _peta_dimensi(obj, path)
        for kunci, nilai in (obj.get("datacontent") or {}).items():
            dimensi = peta.get(str(kunci))
            if dimensi is None:
                raise ValueError(
                    f"{path}: kunci datacontent {kunci!r} tidak cocok dengan metadata"
                )
            vervar, var, turvar, tahun, turtahun = dimensi
            baris.append({
                "var_id": _ke_int(var["val"]),
                "wilayah_id": _ke_int(vervar["val"]),
                "wilayah": vervar["label"],
                "turvar_id": _ke_int(turvar["val"]),
                "turvar": turvar["label"],
                "tahun_id": _ke_int(tahun["val"]),
                "tahun": _tahun(tahun["label"]),
                "periode_id": _ke_int(turtahun["val"]),
                "periode": turtahun["label"],
                "nilai": _ke_angka(nilai),
                "satuan": var.get("unit", ""),
            })

    df = pd.DataFrame(baris, columns=KOLOM_ASAL)
    return _tempel_lineage(df, path, raw)


def baca_berkas(path, raw=RAW):
    """Pilih pembaca berdasarkan ekstensi berkas."""
    path = Path(path)
    if path.suffix.lower() == ".csv":
        return baca_csv(path, raw)
    if path.suffix.lower() == ".json":
        return baca_json(path, raw)
    raise ValueError(f"format BPS tidak dikenal: {path}")


def baca_semua(raw=RAW):
    """Baca semua berkas CSV dan JSON BPS di data/raw/bps/ tanpa membersihkan apa pun."""
    raw = Path(raw)
    akar = raw / "bps"
    if not akar.is_dir():
        raise FileNotFoundError(f"folder BPS tidak ditemukan: {akar}")

    berkas = sorted({*akar.glob("**/*.csv"), *akar.glob("**/json/*.json")})
    berkas = [p for p in berkas if not p.name.startswith("manifest")]
    if not berkas:
        raise FileNotFoundError(f"tidak ada berkas CSV/JSON BPS di {akar}")

    return pd.concat([baca_berkas(p, raw) for p in berkas], ignore_index=True)


if __name__ == "__main__":
    hasil = baca_semua()
    print(hasil.groupby("_berkas_raw", sort=True).size().to_string())
    print(f"total {len(hasil)} baris")