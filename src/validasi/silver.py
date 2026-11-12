"""Aturan validasi dasar Silver menggunakan Pandera — Kasus 03."""

import re
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check

POLA_PERIODE = re.compile(
    r"^\d{4}$"
    r"|^\d{4}-S[12]$"
    r"|^\d{4}-Q[1-4]$"
    r"|^\d{4}-\d{2}$"
)

JENIS_PERIODE_VALID = {"tahun", "semester", "triwulan", "bulan"}
SUMBER_VALID        = {"BPS", "WHO", "WDI"}

skema_silver = DataFrameSchema(
    columns={
        "sumber": Column(str,
            checks=Check(lambda s: s.isin(SUMBER_VALID),
                error="sumber harus BPS, WHO, atau WDI"),
            nullable=False),
        "seri_kode": Column(str, nullable=False),
        "wilayah_kode": Column(int,
            checks=Check(lambda s: (s == 9999) | (s > 0),
                error="wilayah_kode harus positif atau 9999"),
            nullable=False),
        "nama_wilayah": Column(str, nullable=False),
        "periode": Column(str,
            checks=Check(lambda s: s.str.match(POLA_PERIODE),
                error="format periode tidak valid"),
            nullable=False),
        "jenis_periode": Column(str,
            checks=Check(lambda s: s.isin(JENIS_PERIODE_VALID),
                error="jenis_periode tidak valid"),
            nullable=False),
        "rincian": Column(str, nullable=False),
        "nilai": Column(float, nullable=False),
        "satuan": Column(str, nullable=True),
        "_berkas_raw": Column(str, nullable=False),
        "_sha256_raw": Column(str,
            checks=Check(lambda s: s.str.match(r"^[a-f0-9]{64}$"),
                error="sha256 harus 64 karakter hex"),
            nullable=False),
    },
    checks=[
        Check(
            lambda df: ~df.duplicated(subset=[
                "sumber", "seri_kode", "wilayah_kode",
                "periode", "rincian", "_berkas_raw"
            ]).any(),
            error="Ditemukan baris duplikat berdasarkan kunci unik Silver",
        )
    ],
    name="silver",
)


def validasi_silver(df: pd.DataFrame) -> dict:
    """Periksa DataFrame Silver dan kembalikan ringkasan hasil."""
    hasil = {"baris": len(df), "lulus": False, "pesan": [], "gagal": []}
    try:
        skema_silver.validate(df, lazy=True)
        hasil["lulus"] = True
        hasil["pesan"].append(f"Semua {len(df)} baris lulus validasi skema Silver.")
    except pa.errors.SchemaErrors as e:
        for _, baris in e.failure_cases.iterrows():
            hasil["gagal"].append({
                "kolom":   baris.get("column"),
                "periksa": baris.get("check"),
                "contoh":  baris.get("failure_case"),
            })
        hasil["pesan"].append(f"Ditemukan {len(e.failure_cases)} pelanggaran aturan validasi.")
    return hasil
