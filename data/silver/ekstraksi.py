
from pathlib import Path
import pandas as pd
import json

# Lokasi folder proyek
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"

# Membaca manifest
manifest = pd.read_csv(RAW_DIR / "MANIFEST.csv")

# Membuat pemetaan nama berkas ke SHA-256
hash_map = dict(zip(manifest["berkas"], manifest["sha256"]))

hasil = []

def ambil_hash(path):
    relative_path = path.relative_to(RAW_DIR).as_posix()
    return relative_path, hash_map.get(relative_path)


def ekstrak_bps():
    files = RAW_DIR.glob("bps/**/*.csv")

    for file in files:
        if file.name.lower().startswith("manifest"):
            continue

        df = pd.read_csv(file)
        berkas, sha = ambil_hash(file)

        hasil_df = pd.DataFrame({
            "sumber": "BPS",
            "seri_kode": df["var_id"],
            "wilayah_kode": df["wilayah_id"],
            "nama_wilayah": df["wilayah"],
            "periode": df["tahun"],
            "jenis_periode": "TAHUN",
            "rincian": df["turvar"],
            "nilai": pd.to_numeric(df["nilai"], errors="coerce"),
            "satuan": df["satuan"],
            "_berkas_raw": berkas,
            "_sha256_raw": sha
        })

        hasil.append(hasil_df)


def ekstrak_who():
    files = RAW_DIR.glob("who_gho/**/*.csv")

    for file in files:
        df = pd.read_csv(file)
        berkas, sha = ambil_hash(file)

        kolom_nilai = [
            c for c in df.columns
            if c.startswith("RATE_")
        ][0]

        hasil_df = pd.DataFrame({
            "sumber": "WHO",
            "seri_kode": df["IND_CODE"],
            "wilayah_kode": df["DIM_GEO_CODE_M49"],
            "nama_wilayah": df["GEO_NAME_SHORT"],
            "periode": df["DIM_TIME"],
            "jenis_periode": df["DIM_TIME_TYPE"],
            "rincian": (
                df["DIM_SEX"].fillna("").astype(str)
                + " | "
                + df["DIM_AGE"].fillna("").astype(str)
            ),
            "nilai": pd.to_numeric(
                df[kolom_nilai], errors="coerce"
            ),
            "satuan": kolom_nilai,
            "_berkas_raw": berkas,
            "_sha256_raw": sha
        })

        hasil.append(hasil_df)


if __name__ == "__main__":
    ekstrak_bps()
    ekstrak_who()

    if hasil:
        silver = pd.concat(hasil, ignore_index=True)

        output = BASE_DIR / "data" / "silver"
        output.mkdir(parents=True, exist_ok=True)

        silver.to_csv(
            output / "indikator.csv",
            index=False
        )

        print("Ekstraksi selesai.")
        print("Jumlah baris:", len(silver))
        print("Jumlah kolom:", len(silver.columns))
        print("Hasil:", output / "indikator.csv")
        print(silver.groupby("sumber").size())
