"""Tahap 1 — Ekstraksi (pertemuan X). Milik tim.

Baca setiap berkas di data/raw/ (CSV, JSON WebAPI BPS, XLSX BNPB, SDMX ILO, JSON WDI) menjadi
DataFrame mentah yang setia pada sumbernya: jangan membersihkan di sini, cukup ratakan struktur
dan catat asal tiap baris (`_berkas_raw` relatif data/raw/, `_sha256_raw` dari src.common.manifest).

Keluaran `jalankan()` memakai kunci per sumber dan per jenis berkas:

- bps, bps_metadata
- wdi, wdi_sumber, wdi_indikator
- who_gho, who_gho_ddi, who_gho_indikator

Setelah semua pembaca digabung, cakupan berkas diperiksa terhadap MANIFEST.csv. Bila ada berkas
yang belum muncul di `_berkas_raw`, ekstraksi gagal agar tidak ada data mentah yang terlewat.
"""
from pathlib import Path

from src.common.manifest import RAW, baca


def _cek_cakupan(hasil, raw=RAW):
    """Pastikan semua berkas MANIFEST muncul di lineage hasil ekstraksi."""
    terlihat = set()
    for df in hasil.values():
        if "_berkas_raw" not in df.columns:
            continue
        terlihat.update(str(x) for x in df["_berkas_raw"].dropna().unique())

    semua = set(baca(Path(raw)))
    kurang = sorted(semua - terlihat)
    asing = sorted(terlihat - semua)
    if kurang or asing:
        pesan = []
        if kurang:
            pesan.append(f"berkas belum dibaca: {kurang}")
        if asing:
            pesan.append(f"berkas di luar MANIFEST: {asing}")
        raise RuntimeError("cakupan ekstraksi tidak lengkap; " + "; ".join(pesan))
    return len(semua)


def jalankan():
    """Kembalikan {nama_sumber: DataFrame mentah} untuk semua berkas MANIFEST."""
    from . import bps, wdi, who

    data_bps = bps.baca_semua()
    hasil = {
        "bps": data_bps,
        "bps_metadata": bps.baca_metadata_semua(
            var_relevan={str(x) for x in data_bps["var_id"].dropna()}
        ),
    }
    hasil.update(wdi.baca_semua())
    hasil.update(who.baca_semua())
    _cek_cakupan(hasil)
    return hasil
