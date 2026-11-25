"""Persiapan tahap 6 — tabel nasional semua seri dan daftar pasangan rekonsiliasi.

Sprint 1 belum menghitung selisih. Yang disiapkan: tabel periode x seri (tampilan lebar) untuk baris
Indonesia, dan untuk setiap pasangan dari panduan kelompok: rincian yang dipakai, tahun yang beririsan,
pertanyaan keterbandingan, jawabannya beserta bukti, dan dugaan kategori selisih.
"""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat, tabel_md, tulis

SERI_UTAMA = {"var1394", "var1353"}
RINCIAN_NASIONAL = {"MDG_0000000003": "umur=15-19"}
LABEL_SUMBER = {"bps": "BPS", "wdi": "WDI", "who_gho": "WHO GHO"}


def tabel_nasional(silver):
    nas = silver[silver["wilayah_kode"] == W.INDONESIA].copy()
    nas["kolom"] = nas["seri_kode"] + nas["rincian"].map(lambda r: "" if r == "total" else f" [{r}]")
    total = nas[nas["rincian"] == "total"]
    lebar = total.pivot_table(index="periode", columns="kolom", values="nilai").sort_index()
    return nas, lebar


def tabel_nasional_panjang(nas):
    """Tabel Gold: satu baris per periode x seri, termasuk asal angka nasional.

    BPS menerbitkan baris Indonesia (kode 9999), jadi seri utama tidak perlu diagregasi dari provinsi.
    MDG_0000000003 memakai rincian umur=15-19 agar sebanding dengan BPS/WDI; rincian 10-14 tidak dipakai.
    """
    potong = []
    for seri in K.SERI:
        rinci = RINCIAN_NASIONAL.get(seri, "total")
        d = nas[(nas["seri_kode"] == seri) & (nas["rincian"] == rinci)].copy()
        if d.empty:
            continue
        d["rincian_dipakai"] = rinci
        potong.append(d)
    if not potong:
        return pd.DataFrame()

    out = pd.concat(potong, ignore_index=True)
    out["kelompok"] = out["seri_kode"].map(lambda s: "utama" if s in SERI_UTAMA else "pembanding")
    out["tingkat"] = "nasional"
    out["asal_angka"] = [
        f"baris Indonesia ({LABEL_SUMBER.get(s, s)})" if s == "bps"
        else f"pembanding nasional ({LABEL_SUMBER.get(s, s)})"
        for s in out["sumber"]
    ]
    out["aturan_agregat"] = out["sumber"].map(
        lambda s: "tidak diagregasi; BPS menerbitkan baris Indonesia (9999)" if s == "bps"
        else "tidak berlaku; seri pembanding sudah nasional"
    )
    out["catatan_rincian"] = out["seri_kode"].map(
        lambda s: "rincian total" if s not in RINCIAN_NASIONAL
        else f"rincian {RINCIAN_NASIONAL[s]} dipakai; rincian 10-14 tidak sebanding"
    )
    kembar = out[out.duplicated(["periode", "seri_kode"], keep=False)]
    if not kembar.empty:
        raise ValueError(f"tabel nasional tidak unik per periode x seri: {kembar[['periode', 'seri_kode']].to_dict('records')}")
    kolom = ["periode", "seri_kode", "sumber", "kelompok", "tingkat", "wilayah_kode", "nama_wilayah",
             "rincian", "rincian_dipakai", "nilai", "satuan", "sdg_kode", "asal_angka", "aturan_agregat",
             "catatan_rincian", "_berkas_raw", "_sha256_raw"]
    return out[kolom].sort_values(["periode", "seri_kode"], kind="stable").reset_index(drop=True)


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
    tulis("pasangan-rekonsiliasi.md", "\n\n".join([
        "# Tabel nasional dan pasangan rekonsiliasi",
        "Dihasilkan `python pipeline.py` (`src/gold/nasional.py`) dari Silver dan `src/konfigurasi.py`. Selisih dihitung "
        "di Sprint 2; Sprint 1 memastikan setiap pasangan memang sebanding dan mencatat tahun yang beririsan.",
        "Tabel nasional (periode x seri, rincian total, tampilan lebar): `reports/tabel-nasional.csv`. "
        "Kolom BPS hanya terisi pada tahun survei; itu bentuk datanya, tidak diisi.",
        "## Ringkasan pasangan", tabel_md(daftar),
        "## Rincian per pasangan", *bagian,
    ]))
    return {"nasional": nas, "nasional_panjang": panjang, "pasangan": daftar,
            "tabel_nasional_gold": str(gold / "tabel-nasional.csv")}
