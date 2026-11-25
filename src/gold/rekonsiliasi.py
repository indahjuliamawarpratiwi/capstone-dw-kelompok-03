"""Tahap 6 Sprint 2 — tabel rekonsiliasi seri utama vs pembanding nasional."""
import pandas as pd

from src import konfigurasi as K
from src.laporan import ROOT, catat, tabel_md, tulis

KATEGORI = ("definisi berbeda", "metode berbeda", "vintage berbeda", "cakupan berbeda",
            "belum terjelaskan", "tanpa pasangan", "tidak berselisih")
KOLOM = ["pasangan_id", "jenis", "seri_utama", "rincian_utama", "seri_pembanding", "rincian_pembanding",
         "periode", "tahun_utama", "tahun_pembanding", "selisih_tahun", "nilai_utama", "nilai_pembanding",
         "satuan", "selisih", "selisih_relatif", "asal", "kategori", "kategori_baku", "alasan",
         "jenis_perbandingan", "sumber_utama", "sumber_pembanding", "_berkas_raw_utama", "_sha256_raw_utama",
         "_berkas_raw_pembanding", "_sha256_raw_pembanding", "penjelasan", "catatan"]
KOLOM_SISI = ["periode", "nilai", "satuan", "sumber", "_berkas_raw", "_sha256_raw"]
TOLERANSI = 1e-9
DI_LUAR = {}


def _sisi(nasional, seri, rincian):
    s = nasional[(nasional["seri_kode"] == seri) & (nasional["rincian"] == rincian)].copy()
    return s[KOLOM_SISI].reset_index(drop=True)


def _kategori_pasangan(p):
    kat = p.get("kategori_baku")
    if kat not in KATEGORI:
        raise ValueError(f"{p['id']}: kategori_baku {kat!r} bukan kategori baku")
    return kat


def _tahun_terdekat(a, b, maks):
    nilai = {int(r["periode"]): r for _, r in b.iterrows() if str(r["periode"]).isdigit()}
    baris = []
    for _, row in a.iterrows():
        t = int(row["periode"])
        if not nilai:
            continue
        y = min(nilai, key=lambda x: (abs(x - t), x))
        if abs(y - t) <= maks:
            src = nilai[y]
            baris.append({"periode": str(t), "tahun_pembanding": str(y), "selisih_tahun": t - y,
                          **{c: src[c] for c in KOLOM_SISI if c != "periode"}})
    return pd.DataFrame(baris, columns=["periode", "tahun_pembanding", "selisih_tahun"] + [c for c in KOLOM_SISI if c != "periode"])


def _satu_pasangan(nasional, p):
    utama = p["utama"].split(",")[0].strip()
    kat_pasangan = _kategori_pasangan(p)
    a = _sisi(nasional, utama, p.get("rincian_utama", "total"))
    a = a.assign(tahun_utama=a["periode"], sumber_utama=a["sumber"],
                 berkas_utama=a["_berkas_raw"], sha_utama=a["_sha256_raw"])
    baris = []
    for seri_b, rincian_b in p["pembanding"]:
        b = _sisi(nasional, seri_b, rincian_b)
        if p.get("tahun_terdekat") and not set(a["periode"]) & set(b["periode"]):
            b = _tahun_terdekat(a, b, p["tahun_terdekat"])
            dekat = True
        else:
            b = b.assign(tahun_pembanding=b["periode"], selisih_tahun=0)
            dekat = False
        b = b.assign(sumber_pembanding=b["sumber"], berkas_pembanding=b["_berkas_raw"],
                     sha_pembanding=b["_sha256_raw"])
        if len(a):
            tahun = list(range(min(int(x) for x in a["periode"]), max(int(x) for x in a["periode"]) + 1))
            luar = b[~b["periode"].astype(int).isin(tahun)]
            DI_LUAR[p["id"]] = DI_LUAR.get(p["id"], 0) + len(luar)
            b = b[b["periode"].astype(int).isin(tahun)]
        g = a.merge(b, on="periode", how="outer", suffixes=("_u", "_b"), indicator=True).sort_values("periode")
        for _, r in g.iterrows():
            asal = {"both": "keduanya", "left_only": "hanya_utama", "right_only": "hanya_pembanding"}[r["_merge"]]
            nu = r["nilai_u"] if pd.notna(r["nilai_u"]) else None
            nb = r["nilai_b"] if pd.notna(r["nilai_b"]) else None
            su = r["satuan_u"] if pd.notna(r["satuan_u"]) else r["satuan_b"]
            kategori = kat_pasangan
            sel = rel = None
            jenis_perbandingan = "tanpa_pasangan"
            catatan = []
            if asal == "keduanya":
                jenis_perbandingan = "tahun_terdekat" if dekat else "langsung"
                if dekat:
                    catatan.append(f"pembanding tahun {r['tahun_pembanding']} (tahun terdekat; selisih {int(r['selisih_tahun'])} tahun)")
                if r["satuan_u"] != r["satuan_b"]:
                    catatan.append(f"satuan berbeda ({r['satuan_b']} vs {r['satuan_u']}); selisih tidak dihitung")
                elif p["jenis"] != "selisih":
                    catatan.append("pasangan konteks: selisih tidak dihitung")
                else:
                    sel = nu - nb
                    rel = 100 * sel / nb if nb else None
                    if abs(sel) <= TOLERANSI:
                        kategori = "tidak berselisih"
            else:
                kategori = "tanpa pasangan"
            baris.append({
                "pasangan_id": p["id"], "jenis": p["jenis"], "seri_utama": utama,
                "rincian_utama": p.get("rincian_utama", "total"), "seri_pembanding": seri_b,
                "rincian_pembanding": rincian_b, "periode": r["periode"],
                "tahun_utama": r["tahun_utama"] if pd.notna(r["tahun_utama"]) else r["periode"],
                "tahun_pembanding": r["tahun_pembanding"] if pd.notna(r["tahun_pembanding"]) else None,
                "selisih_tahun": int(r["selisih_tahun"]) if pd.notna(r["selisih_tahun"]) else None,
                "nilai_utama": nu, "nilai_pembanding": nb, "satuan": su, "selisih": sel,
                "selisih_relatif": rel, "asal": asal, "kategori": kategori, "kategori_baku": kat_pasangan,
                "alasan": p.get("alasan_rincian", ""), "jenis_perbandingan": jenis_perbandingan,
                "sumber_utama": r["sumber_utama"] if pd.notna(r["sumber_utama"]) else None,
                "sumber_pembanding": r["sumber_pembanding"] if pd.notna(r["sumber_pembanding"]) else None,
                "_berkas_raw_utama": r["berkas_utama"] if pd.notna(r["berkas_utama"]) else None,
                "_sha256_raw_utama": r["sha_utama"] if pd.notna(r["sha_utama"]) else None,
                "_berkas_raw_pembanding": r["berkas_pembanding"] if pd.notna(r["berkas_pembanding"]) else None,
                "_sha256_raw_pembanding": r["sha_pembanding"] if pd.notna(r["sha_pembanding"]) else None,
                "penjelasan": p["kategori"], "catatan": "; ".join(catatan) or None,
            })
    return baris


def jalankan(nasional):
    DI_LUAR.clear()
    baris = [b for p in K.PASANGAN for b in _satu_pasangan(nasional, p)]
    t = pd.DataFrame(baris, columns=KOLOM)
    for c in ("nilai_utama", "nilai_pembanding", "selisih", "selisih_relatif"):
        t[c] = t[c].astype("float64")
    if t.duplicated(["pasangan_id", "seri_pembanding", "rincian_pembanding", "periode"]).any():
        raise AssertionError("rekonsiliasi memiliki kunci baris ganda")
    (ROOT / "data" / "gold").mkdir(parents=True, exist_ok=True)
    t.to_parquet(ROOT / "data" / "gold" / "rekonsiliasi.parquet", index=False)

    hitung = t[t["selisih"].notna()]
    ringkas = (t.groupby(["pasangan_id", "seri_pembanding"], sort=False)
               .agg(jenis=("jenis", "first"), periode=("periode", "size"),
                    berpasangan=("asal", lambda s: int((s == "keduanya").sum())),
                    selisih_dihitung=("selisih", lambda s: int(s.notna().sum())),
                    median_selisih=("selisih", "median"),
                    median_selisih_relatif=("selisih_relatif", lambda s: s.abs().median()),
                    kategori=("kategori", lambda s: ", ".join(f"{k} ({n})" for k, n in s.value_counts().items())))
               .reset_index())
    tingkat = {k: v["tingkat"] for k, v in K.SERI.items()}
    utama_prov = hitung[hitung["seri_utama"].map(tingkat).eq("provinsi")]
    dasar = utama_prov if len(utama_prov) else hitung
    med = float(dasar["selisih_relatif"].abs().median()) if len(dasar) else None
    med_semua = float(hitung["selisih_relatif"].abs().median()) if len(hitung) else None
    catat(baris_rekonsiliasi=len(t), selisih_dihitung=len(hitung),
          selisih_median=round(med, 2) if med is not None else 0.0,
          selisih_median_semua=round(med_semua, 2) if med_semua is not None else 0.0,
          selisih_utama_dihitung=len(utama_prov),
          baris_tanpa_pasangan=int((t["kategori"] == "tanpa pasangan").sum()),
          kategori_dipakai=int(t["kategori"].nunique()),
          **{f"rek_{pid.lower()}_dihitung": int(g["selisih"].notna().sum()) for pid, g in t.groupby("pasangan_id")})
    bagian = []
    for p in K.PASANGAN:
        tp = t[t["pasangan_id"] == p["id"]]
        kolom = ["seri_pembanding", "tahun_utama", "tahun_pembanding", "selisih_tahun", "nilai_utama",
                 "nilai_pembanding", "selisih", "selisih_relatif", "asal", "kategori", "catatan",
                 "_berkas_raw_utama", "_berkas_raw_pembanding"]
        bagian.append("\n\n".join([
            f"### {p['id']}: {p['judul']}",
            f"Jenis **{p['jenis']}**; kategori pasangan: **{p['kategori_baku']}**. {p['kategori'][0].upper()}{p['kategori'][1:]}.",
            f"Rincian: {p.get('alasan_rincian', '—')}.", tabel_md(tp[kolom], 2),
        ]))
    tulis("rekonsiliasi.md", "\n\n".join([
        "# Tabel rekonsiliasi seri utama vs pembanding nasional",
        "Dihasilkan `python pipeline.py` (`src/gold/rekonsiliasi.py`) dari `data/gold/nasional.parquet`. "
        "Selisih = nilai utama − nilai pembanding; selisih relatif = 100 × selisih / nilai pembanding. "
        "Periode tanpa pasangan tetap ditampilkan dengan nilai sumber yang tersedia; selisih tidak dihitung.",
        "## Ringkasan per pasangan", tabel_md(ringkas, 2),
        (f"Median selisih relatif mutlak, pasangan berseri utama provinsi: {med:.2f}% ({len(dasar)} baris); "
         f"semua pasangan: {med_semua:.2f}% ({len(hitung)} baris)." if med is not None else "Tidak ada selisih yang dihitung."),
        "Periode pembanding di luar rentang seri utama yang tidak ditulis: "
        + (", ".join(f"{k} {v}" for k, v in DI_LUAR.items() if v) or "tidak ada") + ".",
        "## Kategori", "Kategori baku: " + ", ".join(f"*{k}*" for k in KATEGORI)
        + ". Kategori pasangan dari bukti Sprint 1; baris satu sisi menjadi *tanpa pasangan*, "
          "baris dengan selisih nol menjadi *tidak berselisih*.",
        "## Rincian per pasangan", *bagian,
    ]))
    return {"rekonsiliasi": t}
