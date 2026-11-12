"""Ringkasan ekstraksi: python -m src.ekstraksi."""
from . import _cek_cakupan, jalankan


def main():
    hasil = jalankan()
    for nama, df in hasil.items():
        print(f"{nama}: {len(df)} baris")
    print(f"cakupan: {_cek_cakupan(hasil)} berkas")


if __name__ == "__main__":
    main()
