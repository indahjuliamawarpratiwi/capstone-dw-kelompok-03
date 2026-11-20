
# CEK JUMLAH OTOMATIS 

from src.ekstraksi import bps
import pandas as pd

berkas_bps = [
    "bps/2026-10-20/sdg3_3_7_1_v1394.csv",
    "bps/2026-10-20/json/sdg3_3_7_1_v1394.json",
    "bps/2026-10-20/sdg3_3_7_2_v1353.csv",
    "bps/2026-10-20/json/sdg3_3_7_2_v1353.json",
]

hasil = []

for berkas in berkas_bps:

    if berkas.endswith(".csv"):
        df = bps.baca_csv(berkas)
    else:
        df, metadata = bps.baca_json(berkas)

    # Memastikan lineage tersedia
    assert "_berkas_raw" in df.columns
    assert "_sha256_raw" in df.columns

    assert df["_berkas_raw"].notna().all()
    assert df["_sha256_raw"].notna().all()

    assert df["_berkas_raw"].nunique() == 1
    assert df["_sha256_raw"].nunique() == 1

    hasil.append({
        "berkas": berkas,
        "jumlah_baris": len(df),
        "jumlah_lineage": df["_sha256_raw"].nunique(),
        "status": "BERHASIL"
    })

    print(f"\nBerkas: {berkas}")
    print("Jumlah baris:", len(df))
    print(df.head(1).to_string(index=False))

# Membuat laporan jumlah baris
laporan = pd.DataFrame(hasil)

print("\n=== LAPORAN EKSTRAKSI BPS ===")
print(laporan.to_string(index=False))

laporan.to_csv(
    "reports/hasil-ekstraksi-bps.csv",
    index=False
)

# Pemeriksaan total
assert laporan["jumlah_baris"].sum() == 276

print("\nTotal baris:", laporan["jumlah_baris"].sum())
print("Seluruh pemeriksaan berhasil.")
