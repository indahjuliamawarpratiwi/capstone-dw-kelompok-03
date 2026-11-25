"""Persiapan tahap 6 — tabel nasional semua seri dan daftar pasangan rekonsiliasi.

Sprint 1 belum menghitung selisih. Yang disiapkan: tabel periode x seri (tampilan lebar) untuk baris
Indonesia, tabel nasional dari hasil ekstraksi, dan pasangan dari panduan kelompok bagian 3 beserta
rincian yang benar-benar dipakai dan alasan keterbandingannya.
"""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat, tabel_md, tulis


def tabel_nasional(silver):
    nas = silver[silver["wilayah_kode"] == W.INDONESIA].copy()
    nas["kolom"] = nas["seri_kode"] + nas["rincian"].map(lambda r: "" if r == "total" else f" [{r}]")
    total = nas[nas["rincian"] == "total"]
    lebar = total.pivot_table(index="periode", columns="kolom", values="nilai").sort_index()
    return nas, lebar


def irisan(silver, utama, rinci_utama, pembanding, semester=None):
    def per(seri, rinci):
        s = silver[(silver["seri_kode"] == seri) & (silver["rincian"] == rinci) & (silver["wilayah_kode"] == W.INDONESIA)]
        # tahun proyeksi (bukan estimasi atas data) tidak ikut tabel rekonsiliasi
        return set(s["periode"]) - set(getattr(K, "PROYEKSI", {}).get(seri, set()))
    a = per(utama, rinci_utama)
    if semester:
        # seri semesteran dibandingkan dengan seri tahunan lewat satu semester yang ditetapkan (misalnya S1 = Maret)
        a = {p[:4] for p in a if len(p) == 4 or p.endswith(f"-{semester}")}
    return sorted(set.intersection(a, *[per(s, r) for s, r in pembanding])) if pembanding else []


def jalankan(silver, ekstraksi=None):
    nas, lebar = tabel_nasional(silver)
    (ROOT / "reports").mkdir(exist_ok=True)
    lebar.to_csv(ROOT / "reports" / "tabel-nasional.csv")

    panjang = tabel_nasional_panjang(nas)
    gold = ROOT / "data" / "gold"
    gold.mkdir(parents=True, exist_ok=True)
    panjang.to_csv(gold / "tabel-nasional.csv", index=False)
    panjang.to_parquet(gold / "tabel-nasional.parquet", index=False)
    catat(tabel_nasional_baris=len(panjang), tabel_nasional_seri=int(panjang["seri_kode"].nunique()) if len(panjang) else 0,
          tabel_nasional_periode=int(panjang["periode"].nunique()) if len(panjang) else 0)

    rekap = (panjang.groupby(["kelompok", "seri_kode"], sort=False).size().reset_index(name="baris")
             if len(panjang) else pd.DataFrame(columns=["kelompok", "seri_kode", "baris"]))
    tulis("tabel-nasional-gold.md", "\n\n".join([
        "# Tabel nasional Gold (tahap 6)",
        "Dihasilkan `python pipeline.py` (`src/gold/nasional.py`) dari Silver. Berkas utama: "
        "`data/gold/tabel-nasional.csv` dan `data/gold/tabel-nasional.parquet`.",
        f"- Butir: satu baris per **periode x seri**; {len(panjang)} baris, "
        f"{panjang['seri_kode'].nunique() if len(panjang) else 0} seri, "
        f"{panjang['periode'].nunique() if len(panjang) else 0} periode.",
        "- Seri utama: `var1394`, `var1353`. Pembanding: `MDG_0000000003`, `SDGFPALL`, `SP.ADO.TFRT`.",
        "- BPS menerbitkan baris Indonesia (kode 9999) untuk kedua seri utama pada 2012 dan 2017, sehingga "
        "**tidak ada agregasi provinsi**. Bila baris Indonesia tidak tersedia, tabel tidak mengarang agregat: "
        "baris seri/periode itu tidak dibuat dan keputusannya dinyatakan sebagai tidak punya padanan nasional, "
        "karena bobot populasi perempuan 15-19 tidak tersedia di paket.",
        "- `MDG_0000000003` memakai rincian `umur=15-19`; rincian `10-14` tidak dipakai karena penyebutnya berbeda.",
        "- Kolom `asal_angka` menyatakan asal setiap angka: `baris Indonesia (BPS)` atau "
        "`pembanding nasional (WHO GHO/WDI)`.",
        "## Rekap",
        tabel_md(rekap),
        "## Cuplikan",
        tabel_md(panjang[["periode", "seri_kode", "kelompok", "rincian", "nilai", "satuan", "asal_angka"]].head(12)),
    ]))

    baris, bagian = [], []
    for p in K.PASANGAN:
        utama = p["utama"].split(",")[0].strip()
        rinci_utama = p.get("rincian_utama", "total")
        bersama = irisan(silver, utama, rinci_utama, p["pembanding"], p.get("semester_utama"))
        baris.append({"id": p["id"], "seri_utama": p["utama"], "pembanding": ", ".join(f"{s} [{r}]" for s, r in p["pembanding"]) or "—",
                      "jenis": p["jenis"], "periode_beririsan": len(bersama), "tahun": ", ".join(bersama) or "—",
                      "dugaan_kategori": p["kategori"]})
        teks = [f"### {p['id']}: {p['judul']}", f"- Seri utama: `{p['utama']}` (rincian `{rinci_utama}`)",
                "- Pembanding: " + (", ".join(f"`{s}` (rincian `{r}`)" for s, r in p["pembanding"]) or "tidak ada di paket"),
                f"- Jenis: **{p['jenis']}**; tahun beririsan: {', '.join(bersama) or '—'}",
                f"- Dugaan kategori selisih (diuji di Sprint 2): {p['kategori']}", "", "Pertanyaan keterbandingan dan jawabannya:", ""]
        teks += [f"{i}. **{q}** {a}" for i, (q, a) in enumerate(p["pertanyaan"], 1)]
        bagian.append("\n".join(teks))
    daftar = pd.DataFrame(baris)
    n_selisih = int((daftar["jenis"] == "selisih").sum())
    catat(pasangan_rekonsiliasi=n_selisih, pasangan_konteks=int((daftar["jenis"] != "selisih").sum()),
          periode_beririsan=int(daftar.loc[daftar["jenis"] == "selisih", "periode_beririsan"].sum()),
          **{f"irisan_{r.id.lower()}": r.periode_beririsan for r in daftar.itertuples()})

    panduan = daftar_pasangan()
    if ekstraksi:
        GOLD.mkdir(parents=True, exist_ok=True)
        nasional = tabel_nasional_ekstraksi(ekstraksi)
        nasional.to_parquet(GOLD / "nasional_periode_seri.parquet", index=False)
        panduan.to_csv(GOLD / "pasangan_rekonsiliasi.csv", index=False)
        catat(baris_nasional_ekstraksi=len(nasional), pasangan_panduan=len(panduan))
    else:
        panduan = pd.read_csv(GOLD / "pasangan_rekonsiliasi.csv", keep_default_na=False)

    tulis("pasangan-rekonsiliasi.md", "\n\n".join([
        "# Tabel nasional dan pasangan rekonsiliasi",
        "Dihasilkan `python pipeline.py` (`src/gold/nasional.py`) dari Silver dan `src/konfigurasi.py`. Selisih dihitung "
        "di Sprint 2; Sprint 1 memastikan setiap pasangan memang sebanding dan mencatat tahun yang beririsan.",
        "Tabel nasional (periode x seri, rincian total, tampilan lebar): `reports/tabel-nasional.csv`. "
        "Tabel nasional lengkap dari hasil ekstraksi (semua rincian, satu baris per periode x seri): "
        "`data/gold/nasional_periode_seri.parquet`. Kolom BPS hanya terisi pada tahun survei; itu bentuk datanya, tidak diisi.",
        "Untuk SDG 3.7.2, perbandingan tiga seri memakai `var1353` (BPS, cakupan 15–19, rincian mentah `Tidak ada`), "
        "`MDG_0000000003` rincian `Y15T19` (bukan `Y10T14`), dan `SP.ADO.TFRT` (WDI, 15–19 dari nama indikator). "
        "Ketiganya menarget perempuan 15–19 dan satuan per 1.000, jadi kelompok umur disamakan lebih dulu sebelum selisih "
        "dihitung. Tidak ada tahun yang beririsan untuk ketiganya, jadi selisih tiga seri tidak dihitung dan perbandingan "
        "dilakukan berpasangan (P1, P2, P4). Untuk SDG 3.7.1, `var1394` (rincian `Tidak ada`, 15–49 dari judul) dan "
        "`SDGFPALL` (`DIM_AGE=Y15T49`, `DIM_SEX=FEMALE`) sama-sama perempuan 15–49, tetapi status perkawinan dan "
        "penyebutnya tidak dinyatakan identik; keduanya tidak membatasi pada perempuan menikah saja, dan Limitations WHO "
        "mencatat perbedaan base populasi antarsurvei.",
        "## Pasangan dari panduan kelompok bagian 3",
        tabel_md(panduan[["pasangan", "rincian_dipakai", "kelompok_umur", "status_perkawinan_populasi",
                          "periode_beririsan_berpasangan", "dapat_dibandingkan_langsung", "alasan_keterbandingan"]]),
        "## Ringkasan pasangan", tabel_md(daftar),
        "## Rincian per pasangan", *bagian,
    ]))
    return {"nasional": nas, "pasangan": daftar}
