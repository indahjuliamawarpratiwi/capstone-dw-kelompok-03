"""Demo tahap 2–3: profil, anomali, dan tabel Silver."""

import pandas as pd

from src import ekstraksi
from . import TUJUAN, jalankan
from .profil import ANOMALI, PROFIL


def main():
    mentah = ekstraksi.jalankan()
    hasil = jalankan(mentah)
    profil = pd.read_csv(PROFIL)
    anomali = pd.read_csv(ANOMALI)

    print(f"ekstraksi  : {len(mentah['bps']) + len(mentah['who_gho']) + len(mentah['wdi'])} baris data")
    print(f"profil     : {len(profil)} seri -> {PROFIL.relative_to(PROFIL.parents[2])}")
    print(f"anomali    : {len(anomali)} temuan -> {ANOMALI.relative_to(ANOMALI.parents[2])}")
    print(f"silver     : {len(hasil)} baris -> {TUJUAN.relative_to(TUJUAN.parents[2])}")
    print()
    print(profil.to_string(index=False))
    print()
    print(anomali["jenis"].value_counts().to_string())


if __name__ == "__main__":
    main()
