"""Persiapan tahap 6 — tabel nasional semua seri dan daftar pasangan rekonsiliasi.

Sprint 1 belum menghitung selisih. Yang disiapkan: tabel periode x seri (tampilan lebar) untuk baris
Indonesia, tabel nasional dari hasil ekstraksi, dan pasangan dari panduan kelompok bagian 3 beserta
rincian yang benar-benar dipakai dan alasan keterbandingannya.
"""
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat, tabel_md, tulis

SERI_UTAMA = {"var1394", "var1353"}
RINCIAN_NASIONAL = {"MDG_0000000003": "umur=15-19"}
LABEL_SUMBER = {"bps": "BPS", "wdi": "WDI", "who_gho": "WHO GHO"}
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

KELOMPOK_UMUR = {
    ("var1353", "Tidak ada"): "15-19",
    ("MDG_0000000003", "Y15T19"): "15-19",
    ("SP.ADO.TFRT", "Y15T19"): "15-19",
    ("var1394", "Tidak ada"): "15-49",
    ("SDGFPALL", "Y15T49"): "15-49",
}

REKONSILIASI_PASANGAN = [
    dict(id="R1", utama=("var1353", "Tidak ada"), pembanding=("MDG_0000000003", "Y15T19"),
         kategori="belum terjelaskan",
         dugaan="Tidak ada tahun yang sama; tahun terdekat tidak dipaksa menjadi pasangan.",
         bukti="BPS hanya 2012 dan 2017 (TAHUN_TERBIT); WHO Y15T19 tidak memuat kedua tahun itu.",
         dugaan_kosong="Seri ini tidak tersedia pada periode yang diminta.",
         bukti_kosong="DIM_TIME WHO tidak kontinu; BPS hanya tahun survei 2012 dan 2017."),
    dict(id="R2", utama=("var1353", "Tidak ada"), pembanding=("SP.ADO.TFRT", "Y15T19"),
         kategori="metode berbeda",
         dugaan="Survei SDKI dengan periode rujukan tertentu vs estimasi model WPP tahunan.",
         bukti="var.note BPS menyebut SDKI; WDI sourceOrganization = World Population Prospects, UN Population Division.",
         dugaan_kosong="BPS tidak menerbitkan angka untuk tahun di luar survei.",
         bukti_kosong="TAHUN_TERBIT BPS = {2012, 2017}; WDI mencakup 65 tahun."),
    dict(id="R3", utama=("MDG_0000000003", "Y15T19"), pembanding=("SP.ADO.TFRT", "Y15T19"),
         kategori="vintage berbeda",
         dugaan="WHO menghimpun survei/registrasi pada vintage berbeda; WDI memakai proyeksi WPP.",
         bukti="WHO MethodOfEstimationOverview: registrasi sipil/survei; WDI sourceOrganization: WPP.",
         dugaan_kosong="Salah satu sumber tidak memuat tahun tersebut.",
         bukti_kosong="DIM_TIME WHO tidak kontinu; WDI tahunan mencakup tahun proyeksi."),
    dict(id="R4", utama=("var1394", "Tidak ada"), pembanding=("SDGFPALL", "Y15T49"),
         kategori="definisi berbeda",
         dugaan="Penyebut berbeda: BPS lebih dekat ke prevalensi kontrasepsi modern; WHO memakai permintaan KB total.",
         bukti="WHO Denominator = pemakai semua metode + kebutuhan tak terpenuhi; Limitations WHO mencatat perbedaan base/status perkawinan.",
         dugaan_kosong="SDGFPALL hanya tersedia pada enam tahun.",
         bukti_kosong="Berkas WHO SDGFPALL memuat 6 baris national Y15T49."),
]


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


def tabel_rekonsiliasi(nasional):
    baris = []
    for p in REKONSILIASI_PASANGAN:
        utama, pembanding = p["utama"], p["pembanding"]
        if KELOMPOK_UMUR[utama] != KELOMPOK_UMUR[pembanding]:
            raise AssertionError(f"Kelompok umur tidak sama untuk {p['id']}")
        a = nasional[(nasional["seri_kode"] == utama[0]) & (nasional["rincian"] == utama[1])]
        b = nasional[(nasional["seri_kode"] == pembanding[0]) & (nasional["rincian"] == pembanding[1])]
        nilai_a = dict(zip(a["periode"].astype(str), a["nilai"]))
        nilai_b = dict(zip(b["periode"].astype(str), b["nilai"]))
        for periode in sorted(set(nilai_a) | set(nilai_b)):
            berpasangan = periode in nilai_a and periode in nilai_b
            va, vb = nilai_a.get(periode), nilai_b.get(periode)
            baris.append({
                "pasangan": p["id"], "seri_utama": utama[0], "pembanding": pembanding[0],
                "rincian_utama": utama[1], "rincian_pembanding": pembanding[1], "periode": periode,
                "nilai_utama": va, "nilai_pembanding": vb,
                "selisih": va - vb if berpasangan else None,
                "status_pasangan": "berpasangan" if berpasangan else "tanpa_pasangan",
                "kategori": p["kategori"] if berpasangan else "belum terjelaskan",
                "dugaan": p["dugaan"] if berpasangan else p["dugaan_kosong"],
                "bukti": p["bukti"] if berpasangan else p["bukti_kosong"],
            })
    return pd.DataFrame(baris)


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
        rek = tabel_rekonsiliasi(nasional)
        rek.to_csv(GOLD / "rekonsiliasi.csv", index=False)
    else:
        panduan = pd.read_csv(GOLD / "pasangan_rekonsiliasi.csv", keep_default_na=False)
        rek = pd.read_csv(GOLD / "rekonsiliasi.csv", keep_default_na=False)
        for kolom in ["nilai_utama", "nilai_pembanding", "selisih"]:
            rek[kolom] = pd.to_numeric(rek[kolom], errors="coerce")

    berpasangan = rek[rek["status_pasangan"] == "berpasangan"].copy()
    ringkasan = []
    for p in REKONSILIASI_PASANGAN:
        bagian_rek = rek[rek["pasangan"] == p["id"]]
        pasang = bagian_rek[bagian_rek["status_pasangan"] == "berpasangan"]
        ringkasan.append({
            "pasangan": p["id"], "utama": f"{p['utama'][0]} [{p['utama'][1]}]",
            "pembanding": f"{p['pembanding'][0]} [{p['pembanding'][1]}]",
            "kategori": p["kategori"], "baris_berpasangan": len(pasang),
            "baris_tanpa_pasangan": int((bagian_rek["status_pasangan"] == "tanpa_pasangan").sum()),
            "selisih_median": round(float(pasang["selisih"].median()), 2) if len(pasang) else None,
        })
    ringkasan = pd.DataFrame(ringkasan)

    tulis("pasangan-rekonsiliasi.md", "\n\n".join([
        "# Tabel nasional dan pasangan rekonsiliasi",
        "Dihasilkan `python pipeline.py` (`src/gold/nasional.py`) dari tabel nasional Gold dan `src/konfigurasi.py`. "
        "Selisih dihitung di Tahap 6 Sprint 2 dan tidak dihapus atau dipaksa sama.",
        "Tabel nasional (periode x seri, rincian total, tampilan lebar): `reports/tabel-nasional.csv`. "
        "Tabel nasional lengkap dari hasil ekstraksi (semua rincian, satu baris per periode x seri): "
        "`data/gold/nasional_periode_seri.parquet`. Kolom BPS hanya terisi pada tahun survei; itu bentuk datanya, tidak diisi.",
        "Untuk SDG 3.7.2, kelompok umur disamakan lebih dulu: `var1353` berasal dari judul 15–19, WHO memakai "
        "`Y15T19` (bukan `Y10T14`), dan WDI `SP.ADO.TFRT` memakai 15–19 dari nama indikator. Satuannya juga sama, "
        "per 1.000. Untuk SDG 3.7.1, `var1394` dan WHO `SDGFPALL` (`Y15T49`) sama-sama perempuan 15–49 dan tidak "
        "dibatasi pada perempuan menikah saja; yang berbeda adalah penyebut/definisi, bukan kelompok umur.",
        "## Pasangan dari panduan kelompok bagian 3",
        tabel_md(panduan[["pasangan", "rincian_dipakai", "kelompok_umur", "status_perkawinan_populasi",
                          "periode_beririsan_berpasangan", "dapat_dibandingkan_langsung", "alasan_keterbandingan"]]),
        "## Ringkasan pasangan", tabel_md(daftar),
        "## Tabel rekonsiliasi Tahap 6",
        "Setiap baris berpasangan memuat periode, nilai kedua seri, selisih, dan kategori penjelasan. "
        "Periode tanpa pasangan tetap tampil dengan nilai kosong dan kategori `belum terjelasan` lengkap dengan dugaan serta bukti.",
        tabel_md(ringkasan),
        "### Baris berpasangan",
        tabel_md(berpasangan[["pasangan", "seri_utama", "pembanding", "periode", "nilai_utama",
                              "nilai_pembanding", "selisih", "kategori", "dugaan", "bukti"]]),
        "### Periode tanpa pasangan",
        f"{len(rek) - len(berpasangan)} baris tersimpan di `data/gold/rekonsiliasi.csv` tanpa selisih.",
        tabel_md(rek[rek["status_pasangan"] == "tanpa_pasangan"].groupby("pasangan").size().rename("baris").reset_index()),
        "## Rincian alasan pasangan lama", *bagian,
    ]))
    return {"nasional": nas, "nasional_panjang": panjang, "pasangan": daftar,
            "tabel_nasional_gold": str(gold / "tabel-nasional.csv")}
    return {"nasional": nas, "pasangan": daftar, "pasangan_panduan": panduan}
