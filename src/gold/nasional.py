"""Persiapan tahap 6 — tabel nasional semua seri dan daftar pasangan rekonsiliasi.

Sprint 1 belum menghitung selisih. Yang disiapkan: tabel periode x seri (tampilan lebar) untuk baris
Indonesia, tabel nasional dari hasil ekstraksi, dan pasangan dari panduan kelompok bagian 3 beserta
rincian yang benar-benar dipakai dan alasan keterbandingannya.
"""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat, tabel_md, tulis

GOLD = ROOT / "data" / "gold"
SATUAN_ABR = "per 1,000 perempuan usia 15-19 tahun"
SATUAN_WHO = {"MDG_0000000003": "per 1,000", "SDGFPALL": "Persen"}

PASANGAN_PANDUAN = [
    dict(
        pasangan="var1353 vs MDG_0000000003(Y15T19) vs SP.ADO.TFRT",
        sumber_seri="bps:var1353; who_gho:MDG_0000000003; wdi:SP.ADO.TFRT",
        rincian_dipakai="var1353: turvar='Tidak ada' (umur 15-19 ada di judul); "
                        "MDG_0000000003: DIM_AGE=Y15T19 (bukan Y10T14), DIM_SEX=FEMALE; "
                        "SP.ADO.TFRT: age=15-19 dari nama indikator",
        kelompok_umur="15-19 pada ketiga seri",
        status_perkawinan_populasi="perempuan 15-19; var1353 dari SDKI, WHO dari survei/registrasi, "
                                   "WDI dari estimasi UN WPP; tidak ada syarat status perkawinan di definisi",
        satuan="per 1,000 perempuan usia 15-19 tahun (satuan CSV var1353 kosong, ditetapkan dari definisi)",
        periode_beririsan_3seri="",
        periode_beririsan_berpasangan="var1353∩SP.ADO.TFRT={2012,2017}; "
                                      "var1353∩MDG Y15T19=∅; MDG Y15T19∩SP.ADO.TFRT={2001-2011,2013,2015,2016}",
        dapat_dibandingkan_langsung="tidak untuk 3 seri (tahun bersama kosong)",
        alasan_keterbandingan="Kelompok umur 15-19 dan satuan per 1,000 sama pada ketiga seri; "
                              "yang berbeda hanya metode/vintage (SDKI, WHO, WPP) dan tahun amatan",
        catatan="Pembanding kontekstual berpasangan; selisih 3-seri tidak dihitung. "
                "Sprint 2 memakai rincian Y15T19 dan menandai tahun terdekat bila perlu.",
    ),
    dict(
        pasangan="var1394 vs SDGFPALL",
        sumber_seri="bps:var1394; who_gho:SDGFPALL",
        rincian_dipakai="var1394: turvar='Tidak ada' (15-49 dan 'atau pasangannya' dari judul); "
                        "SDGFPALL: DIM_AGE=Y15T49 (konstan di berkas), DIM_SEX=FEMALE",
        kelompok_umur="15-49 pada kedua seri",
        status_perkawinan_populasi="keduanya perempuan 15-49, tidak dibatasi hanya yang menikah/bersatu; "
                                   "WHO menghitung pasangan yang memakai metode modern di numerator, "
                                   "denominator seluruh permintaan KB; Limitations WHO mencatat perbedaan "
                                   "status perkawinan/base populasi antarsurvei",
        satuan="Persen",
        periode_beririsan_3seri="tidak relevan (2 seri)",
        periode_beririsan_berpasangan="2012;2017",
        dapat_dibandingkan_langsung="berpotensi, bersyarat pada verifikasi penyebut/status perkawinan",
        alasan_keterbandingan="Umur 15-49, satuan persen, dan konsep kebutuhan KB terpenuhi dengan metode "
                              "modern sama; penyebut WHO = pemakai semua metode + kebutuhan tak terpenuhi, "
                              "sedangkan judul var1394 tidak menyebut penyebutnya",
        catatan="2012: 57.9 vs 79.0; 2017: 57.2 vs 77.0. Selisih dijelaskan, bukan dihapus; "
                "hitung setelah penyebab perbedaan populasi/denominator diverifikasi.",
    ),
]


def tabel_nasional(silver):
    nas = silver[silver["wilayah_kode"] == W.INDONESIA].copy()
    nas["kolom"] = nas["seri_kode"] + nas["rincian"].map(lambda r: "" if r == "total" else f" [{r}]")
    total = nas[nas["rincian"] == "total"]
    lebar = total.pivot_table(index="periode", columns="kolom", values="nilai").sort_index()
    return nas, lebar


def tabel_nasional_ekstraksi(ekstraksi):
    """Satu tabel nasional periode x seri dari keluaran tahap 1, dengan rincian asli tiap sumber."""
    if not ekstraksi:
        return None
    kolom = ["sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode", "jenis_periode",
             "rincian", "nilai", "satuan", "_berkas_raw", "_sha256_raw"]
    baris = []

    def tambah(sumber, seri, wilayah, periode, rincian, nilai, satuan, berkas, sha):
        baris.append(dict(sumber=sumber, seri_kode=seri, wilayah_kode=W.INDONESIA, nama_wilayah=wilayah,
                          periode=str(periode), jenis_periode="tahun", rincian=rincian,
                          nilai=float(nilai), satuan=satuan, _berkas_raw=berkas, _sha256_raw=sha))

    bps = ekstraksi["bps_csv"]
    for _, r in bps[bps["wilayah_id"].astype(str) == str(W.INDONESIA)].iterrows():
        seri = "var" + str(r.var_id)
        satuan = str(r.satuan) if pd.notna(r.satuan) and str(r.satuan) else SATUAN_ABR
        tambah("bps", seri, str(r.wilayah).strip(), r.tahun, str(r.turvar), r.nilai, satuan,
               r["_berkas_raw"], r["_sha256_raw"])

    for df in ekstraksi["who_csv"].values():
        for _, r in df.iterrows():
            if int(r.DIM_GEO_CODE_M49) != 360:
                continue
            seri = str(r.IND_CODE)
            kolom_nilai = "RATE_PER_1000_N" if "RATE_PER_1000_N" in df.columns else "RATE_PER_100_N"
            tambah("who_gho", seri, str(r.GEO_NAME_SHORT), r.DIM_TIME, str(r.DIM_AGE), r[kolom_nilai],
                   SATUAN_WHO[seri], r["_berkas_raw"], r["_sha256_raw"])

    for _, r in ekstraksi["wdi_data"].iterrows():
        if str(r.countryiso3code) != "IDN" or pd.isna(r.value):
            continue
        tambah("wdi", str(r.indicator_id), "Indonesia", r.date, "Y15T19", r.value, SATUAN_ABR,
               r["_berkas_raw"], r["_sha256_raw"])

    return pd.DataFrame(baris, columns=kolom)


def daftar_pasangan():
    return pd.DataFrame(PASANGAN_PANDUAN)


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
    return {"nasional": nas, "pasangan": daftar, "pasangan_panduan": panduan}
