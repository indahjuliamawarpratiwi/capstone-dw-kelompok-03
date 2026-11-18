"""Persiapan tahap 6 — tabel nasional semua seri dan daftar pasangan rekonsiliasi.

Sprint 1 belum menghitung selisih. Yang disiapkan: tabel periode x seri (tampilan lebar) untuk baris
Indonesia, dan untuk setiap pasangan dari panduan kelompok: rincian yang dipakai, tahun yang beririsan,
pertanyaan keterbandingan, jawabannya beserta bukti, dan dugaan kategori selisih.
"""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat, tabel_md, tulis


def tabel_nasional(silver):
    nas = silver[silver["wilayah_kode"] == W.INDONESIA].copy()
    nas["kolom"] = nas["seri_kode"] + nas["rincian"].map(lambda r: "" if r == "total" else f" [{r}]")
    lebar = nas.pivot_table(index="periode", columns="kolom", values="nilai").sort_index()
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


def jalankan(silver):
    nas, lebar = tabel_nasional(silver)
    (ROOT / "reports").mkdir(exist_ok=True)
    lebar.to_csv(ROOT / "reports" / "tabel-nasional.csv")
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
    tulis("pasangan-rekonsiliasi.md", "\n\n".join([
        "# Tabel nasional dan pasangan rekonsiliasi",
        "Dihasilkan `python pipeline.py` (`src/gold/nasional.py`) dari Silver dan `src/konfigurasi.py`. Selisih dihitung "
        "di Sprint 2; Sprint 1 memastikan setiap pasangan memang sebanding dan mencatat tahun yang beririsan.",
        "Tabel nasional (periode x seri, semua rincian, tampilan lebar): `reports/tabel-nasional.csv`. "
        "Kolom BPS hanya terisi pada tahun survei; itu bentuk datanya, tidak diisi.",
        "Untuk SDG 3.7.2, perbandingan tiga seri memakai `var1353` (BPS, cakupan 15–19), "
        "`MDG_0000000003` rincian `umur=15-19`, dan `SP.ADO.TFRT` (WDI, 15–19). Ketiganya menarget "
        "perempuan 15–19; kelompok umur disamakan sebelum selisih dihitung. Tidak ada tahun yang "
        "beririsan untuk ketiganya, jadi selisih tiga seri tidak dihitung dan perbandingan dilakukan "
        "berpasangan (P1, P2, P4). Untuk P3, `var1394` dan `SDGFPALL` sama-sama perempuan 15–49, "
        "tetapi status perkawinan dan penyebutnya belum tentu sama; karena itu P3 diberi kategori definisi.",
        "## Ringkasan pasangan", tabel_md(daftar),
        "## Rincian per pasangan", *bagian,
    ]))
    return {"nasional": nas, "pasangan": daftar}
