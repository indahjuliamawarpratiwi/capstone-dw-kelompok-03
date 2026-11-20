
from src.ekstraksi import wdi

# Daftar empat berkas WDI
berkas = [
    "wdi/2026-10-20/data/kelompok-03-hal-01.json",
    "wdi/2026-10-20/metadata/sumber.json",
    "wdi/2026-10-20/metadata/sumber2_indikator.json",
    "wdi/2026-10-20/metadata/sumber46_indikator.json"
]

print("========== PEMERIKSAAN WDI ==========")

for jalur in berkas:
    print(f"\nBerkas: {jalur}")

    if "/data/" in jalur:
        df, total = wdi.baca_data(
            jalur, ["SP.ADO.TFRT"]
        )
        print("Baris mentah:", total)
    elif "sumber.json" in jalur:
        df = wdi.baca_metadata(jalur)
    else:
        df = wdi.baca_metadata(
            jalur, ["SP.ADO.TFRT"]
        )

    print("Baris keluaran:", len(df))

    print("Kolom lineage tersedia:",
          "_berkas_raw" in df.columns,
          "_sha256_raw" in df.columns)

    if "_sha256_raw" in df.columns:
        print("SHA256:", df["_sha256_raw"].iloc[0])

    print("\nContoh keluaran:")
    print(df.head(2).to_string(index=False))

    print("-" * 60)
