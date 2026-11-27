"""Tahap 6 — Tabel rekonsiliasi seri utama vs pembanding nasional.

Untuk setiap pasangan di `PASANGAN` (konfigurasi) dan setiap seri pembandingnya, satu baris per periode yang
ada di salah satu sisi (gabung luar: periode tanpa pasangan tetap tampil). Kolom: nilai utama, nilai
pembanding (sesudah disamakan satuannya), selisih = utama − pembanding, selisih relatif terhadap pembanding,
asal baris, kategori, dan penjelasan. Selisih tidak dihapus dan tidak dipaksa sama.

Kategori baku: definisi berbeda, metode berbeda, vintage berbeda, cakupan berbeda, belum terjelaskan,
tanpa pasangan, tidak berselisih. Kategori pasangan ditetapkan di konfigurasi (`kategori_baku`); bila tidak
ada, diturunkan dari teks `kategori` (kata kunci yang muncul paling awal). Baris satu sisi = `tanpa
pasangan`; baris dengan selisih nol = `tidak berselisih`. Pasangan berjenis `konteks` tidak dihitung
selisihnya: kedua nilai ditampilkan berdampingan dengan kategori dan alasannya.

Jendela: untuk angka survei yang merujuk n tahun sebelum survei, pasangan boleh menetapkan
`jendela_pembanding = n` sehingga pembanding = rata-rata n tahun sebelum tahun survei (dicatat per baris).

Pilihan per pasangan (konfigurasi): `rincian_utama_jumlah` (jumlah beberapa rincian utama), `hitung_pembanding`
(jumlah / per / laju dari semua pembanding), `pembanding_agregat` (pembanding = jumlah provinsi, GOLD_AGREGAT),
`tahun_terdekat` (bila tidak ada tahun yang sama). Setiap pilihan dicatat di kolom catatan.

Rentang: periode yang hanya ada di pembanding dan berada di luar rentang tahun seri utama tidak ditulis
(jumlahnya dilaporkan); semua periode seri utama selalu ditulis.

Periode: seri semesteran/bulanan dibandingkan lewat satu periode yang ditetapkan (`semester_utama`); tahun
proyeksi (`PROYEKSI`) tidak dibandingkan. Satuan berbeda disamakan dengan faktor di `GOLD_KONVERSI`; tanpa
faktor, selisih tidak dihitung.

Keluaran: data/gold/rekonsiliasi.parquet dan reports/rekonsiliasi.md.
"""
import re

import pandas as pd

from src import konfigurasi as K
from src.laporan import ROOT, catat, tabel_md, tulis

KATEGORI = ("definisi berbeda", "metode berbeda", "vintage berbeda", "cakupan berbeda", "belum terjelaskan",
            "tanpa pasangan", "tidak berselisih")
KATA = [("vintage", "vintage berbeda"), ("rilis", "vintage berbeda"), ("cakupan", "cakupan berbeda"),
        ("populasi", "cakupan berbeda"), ("definisi", "definisi berbeda"), ("penyebut", "definisi berbeda"),
        ("metode", "metode berbeda"), ("sumber", "metode berbeda"), ("pembulatan", "metode berbeda"),
        ("olahan", "metode berbeda"), ("pengolahan", "metode berbeda")]
KOLOM = ["pasangan_id", "jenis", "seri_utama", "rincian_utama", "seri_pembanding", "rincian_pembanding", "periode",
         "nilai_utama", "nilai_pembanding", "satuan", "selisih", "selisih_relatif", "asal", "kategori", "penjelasan",
         "catatan"]
TOLERANSI = 1e-9
DI_LUAR = {}


def kategori_pasangan(p):
    if p.get("kategori_baku"):
        if p["kategori_baku"] not in KATEGORI:
            raise ValueError(f"{p['id']}: kategori_baku {p['kategori_baku']!r} bukan kategori baku")
        return p["kategori_baku"]
    t = p["kategori"].lower()
    kena = [(t.find(k), v) for k, v in KATA if k in t]
    return min(kena)[1] if kena else "belum terjelaskan"


def sisi(nasional, seri, rincian, semester=None):
    s = nasional[(nasional["seri_kode"] == seri) & (nasional["rincian"] == rincian)][["periode", "nilai", "satuan"]]
    if semester:
        s = s[s["periode"].str.len().eq(4) | s["periode"].str.endswith(f"-{semester}")]
        s = s.assign(periode=s["periode"].str[:4]).drop_duplicates("periode")
    return s


def rata_jendela(b, tahun_utama, n):
    """Pembanding untuk angka survei berjendela rujukan: rata-rata n tahun sebelum tahun survei (t-n .. t-1).
    Hanya bila kelima (n) tahun itu ada di pembanding."""
    nilai = dict(zip(b["periode"], b["nilai"]))
    baris = []
    for t in tahun_utama:
        th = [str(int(t) - k) for k in range(1, n + 1)]
        if len(t) == 4 and all(x in nilai for x in th):
            baris.append({"periode": t, "nilai": sum(nilai[x] for x in th) / n,
                          "satuan": b["satuan"].iloc[0], "jendela": f"{th[-1]}–{th[0]}"})
    return pd.DataFrame(baris, columns=["periode", "nilai", "satuan", "jendela"])


def faktor(dari, ke):
    if dari == ke:
        return 1.0
    return getattr(K, "GOLD_KONVERSI", {}).get((dari, ke))


def _jumlah(bagian):
    """Jumlah nilai per periode; hanya periode yang ada di semua bagian."""
    if not bagian or any(b.empty for b in bagian):
        return pd.DataFrame(columns=["periode", "nilai", "satuan"])
    g = bagian[0][["periode", "nilai"]]
    for b in bagian[1:]:
        g = g.merge(b[["periode", "nilai"]], on="periode", suffixes=("", "_x"))
        g["nilai"] = g["nilai"] + g.pop("nilai_x")
    return g.assign(satuan=bagian[0]["satuan"].iloc[0])


def sisi_utama(nasional, p):
    utama = p["utama"].split(",")[0].strip()
    daftar = p.get("rincian_utama_jumlah")
    if daftar:
        return _jumlah([sisi(nasional, utama, r, p.get("semester_utama")) for r in daftar])
    return sisi(nasional, utama, p.get("rincian_utama", "total"), p.get("semester_utama"))


def _seri_b(seri, p):
    return f"{seri} (agregat provinsi)" if p.get("pembanding_agregat") else seri


def daftar_pembanding(nasional, p, satuan_u):
    """[(seri, rincian, tabel, satuan, keterangan)] untuk satu pasangan. hitung_pembanding menggabungkan semua
    pembanding menjadi satu deret turunan: cara 'jumlah' (jumlah), 'per' (jumlah semua kecuali yang terakhir dibagi
    yang terakhir x skala), atau 'laju' (pertumbuhan tahunan persen dari deret tingkat)."""
    h = p.get("hitung_pembanding")
    if not p["pembanding"]:
        return [("", "", None, None, None)]
    if not h:
        hasil = []
        for seri, r in p["pembanding"]:
            b = sisi(nasional, _seri_b(seri, p), r)
            satuan = K.SERI.get(seri, {}).get("satuan") or (b["satuan"].iloc[0] if len(b) else None)
            hasil.append((_seri_b(seri, p), r, b, satuan, "agregat provinsi (GOLD_AGREGAT)" if p.get("pembanding_agregat") else None))
        return hasil
    bagian = [sisi(nasional, _seri_b(s, p), r) for s, r in p["pembanding"]]
    cara = h["cara"]
    if cara == "jumlah":
        b = _jumlah(bagian)
    elif cara == "per":
        atas, bawah = _jumlah(bagian[:-1]), bagian[-1]
        b = atas.merge(bawah[["periode", "nilai"]], on="periode", suffixes=("", "_penyebut"))
        b["nilai"] = b["nilai"] / b.pop("nilai_penyebut") * h.get("skala", 1)
    elif cara == "laju":
        s = bagian[0].sort_values("periode")
        s = s[s["periode"].str.len() == 4]
        prev = dict(zip((s["periode"].astype(int) + 1).astype(str), s["nilai"]))
        b = s.assign(nilai=[100 * (v / prev[t] - 1) if t in prev and prev[t] else None
                            for t, v in zip(s["periode"], s["nilai"])]).dropna(subset=["nilai"])
    else:
        raise ValueError(f"{p['id']}: cara hitung_pembanding {cara!r} tidak dikenal")
    b = b.assign(satuan=satuan_u)[["periode", "nilai", "satuan"]]
    return [(h.get("label", " + ".join(s for s, _ in p["pembanding"])), "hitung", b, satuan_u, h["keterangan"])]


def tahun_terdekat(a, b, maks):
    """Bila tidak ada tahun beririsan: pasangkan setiap tahun utama dengan tahun pembanding terdekat (<= maks tahun)."""
    nilai = {int(x): v for x, v in zip(b["periode"], b["nilai"]) if len(x) == 4}
    baris = []
    for t in a["periode"]:
        if len(t) != 4 or not nilai:
            continue
        y = min(nilai, key=lambda x: (abs(x - int(t)), x))
        if abs(y - int(t)) <= maks:
            baris.append({"periode": t, "nilai": nilai[y], "satuan": b["satuan"].iloc[0], "tahun": str(y)})
    return pd.DataFrame(baris, columns=["periode", "nilai", "satuan", "tahun"])


def satu_pasangan(nasional, p):
    utama = p["utama"].split(",")[0].strip()
    ru = p.get("rincian_utama", "total")
    if p.get("rincian_utama_jumlah"):
        ru = " + ".join(p["rincian_utama_jumlah"])
    kat = kategori_pasangan(p)
    a = sisi_utama(nasional, p)
    satuan_u = K.SERI.get(utama, {}).get("satuan") or (a["satuan"].iloc[0] if len(a) else None)
    proyeksi = getattr(K, "PROYEKSI", {})
    baris = []
    for seri_b, rb, b, satuan_b, ket in daftar_pembanding(nasional, p, satuan_u):
        if b is None:
            b = a.iloc[0:0]
        tambahan = {}
        if seri_b and p.get("jendela_pembanding"):
            b = rata_jendela(b, list(a["periode"]), p["jendela_pembanding"])
            tambahan = {t: f"pembanding = rata-rata {j} (jendela rujukan survei)" for t, j in zip(b["periode"], b["jendela"])}
            b = b.drop(columns="jendela")
        elif seri_b and p.get("tahun_terdekat") and not set(a["periode"]) & set(b["periode"]):
            b = tahun_terdekat(a, b, p["tahun_terdekat"])
            tambahan = {t: f"pembanding tahun {y} (tidak ada tahun yang sama; tahun terdekat)"
                        for t, y in zip(b["periode"], b["tahun"])}
            b = b.drop(columns="tahun")
        f = faktor(satuan_b, satuan_u) if seri_b else None
        g = a.merge(b, on="periode", how="outer", suffixes=("_u", "_b"), indicator="gabung").sort_values("periode")
        if len(a):
            # periode pembanding di luar rentang seri utama tidak ikut (tidak ada yang direkonsiliasi di sana);
            # semua periode seri utama tetap tampil walau tanpa pasangan
            luar = (g["gabung"] == "right_only") & ((g["periode"] < a["periode"].min()) | (g["periode"] > a["periode"].max()))
            DI_LUAR[p["id"]] = DI_LUAR.get(p["id"], 0) + int(luar.sum())
            g = g[~luar]
        for r in g.itertuples():
            asal = {"both": "keduanya", "left_only": "hanya_utama", "right_only": "hanya_pembanding"}[r.gabung]
            nu = r.nilai_u if pd.notna(r.nilai_u) else None
            nb = r.nilai_b * f if pd.notna(r.nilai_b) and f is not None else (r.nilai_b if pd.notna(r.nilai_b) else None)
            catatan = []
            if ket and nb is not None:
                catatan.append(ket)
            if r.periode in tambahan:
                catatan.append(tambahan[r.periode])
            if f not in (None, 1.0) and nb is not None:
                catatan.append(f"pembanding dikali {f:g} ({satuan_b} → {satuan_u})")
            sel = rel = None
            k = kat
            if asal != "keduanya":
                k = "tanpa pasangan" if p["jenis"] == "selisih" else kat
            elif r.periode in proyeksi.get(seri_b, set()) or r.periode in proyeksi.get(utama, set()):
                k = "tanpa pasangan"
                catatan.append("tahun proyeksi, tidak dibandingkan")
            elif p["jenis"] != "selisih":
                catatan.append("pasangan konteks: selisih tidak dihitung")
            elif f is None:
                catatan.append(f"satuan berbeda ({satuan_b} vs {satuan_u}) tanpa faktor konversi")
            else:
                sel = nu - nb
                rel = 100 * sel / nb if nb else None
                if abs(sel) <= TOLERANSI:
                    k = "tidak berselisih"
            baris.append({"pasangan_id": p["id"], "jenis": p["jenis"], "seri_utama": utama, "rincian_utama": ru,
                          "seri_pembanding": seri_b, "rincian_pembanding": rb, "periode": r.periode,
                          "nilai_utama": nu, "nilai_pembanding": nb, "satuan": satuan_u, "selisih": sel,
                          "selisih_relatif": rel, "asal": asal, "kategori": k, "penjelasan": p["kategori"],
                          "catatan": "; ".join(catatan) or None})
    return baris


def jalankan(nasional):
    rows = [b for p in K.PASANGAN for b in satu_pasangan(nasional, p)]
    t = pd.DataFrame(rows, columns=KOLOM)
    for c in ("nilai_utama", "nilai_pembanding", "selisih", "selisih_relatif"):
        t[c] = t[c].astype("float64")
    (ROOT / "data" / "gold").mkdir(parents=True, exist_ok=True)
    t.to_parquet(ROOT / "data" / "gold" / "rekonsiliasi.parquet", index=False)

    hitung = t[t["selisih"].notna()]
    ring = (t.groupby(["pasangan_id", "seri_pembanding"], sort=False)
            .agg(jenis=("jenis", "first"), periode=("periode", "size"),
                 berpasangan=("asal", lambda s: int((s == "keduanya").sum())),
                 selisih_dihitung=("selisih", lambda s: int(s.notna().sum())),
                 median_selisih=("selisih", "median"),
                 median_selisih_relatif=("selisih_relatif", lambda s: s.abs().median()),
                 kategori=("kategori", lambda s: ", ".join(f"{k} ({n})" for k, n in s.value_counts().items())))
            .reset_index())
    bagian = []
    for p in K.PASANGAN:
        tp = t[t["pasangan_id"] == p["id"]]
        isi = tp[["seri_pembanding", "periode", "nilai_utama", "nilai_pembanding", "selisih", "selisih_relatif",
                  "asal", "kategori", "catatan"]]
        bagian.append("\n\n".join([
            f"### {p['id']}: {p['judul']}",
            f"Jenis **{p['jenis']}**; kategori pasangan: **{kategori_pasangan(p)}**. {p['kategori'][0].upper()}{p['kategori'][1:]}.",
            f"Rincian: {p.get('alasan_rincian', '—')}.",
            tabel_md(isi, 2),
        ]))
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
          **{f"rek_{pid.lower()}_median": round(float(g["selisih_relatif"].abs().median()), 1)
             for pid, g in hitung.groupby("pasangan_id")},
          **{f"rek_{pid.lower()}_dihitung": int(g["selisih"].notna().sum()) for pid, g in t.groupby("pasangan_id")})
    tulis("rekonsiliasi.md", "\n\n".join([
        "# Tabel rekonsiliasi seri utama vs pembanding nasional",
        "Dihasilkan `python pipeline.py` (`src/gold/rekonsiliasi.py`) dari `data/gold/nasional.parquet`. Selisih = "
        "nilai utama − nilai pembanding; selisih relatif dalam persen terhadap pembanding. Periode tanpa pasangan "
        "tetap ditampilkan. Selisih tidak dihapus dan tidak dipaksa sama.",
        "## Ringkasan per pasangan", tabel_md(ring, 2),
        (f"Median selisih relatif mutlak, pasangan yang seri utamanya seri provinsi (BPS/BNPB): {med:.2f}% "
         f"({len(dasar)} baris); semua pasangan termasuk antarpembanding: {med_semua:.2f}% ({len(hitung)} baris)."
         if len(utama_prov) else f"Median selisih relatif mutlak (semua baris yang dihitung): {med:.2f}%.")
        if med is not None else "Tidak ada baris yang selisihnya dapat dihitung.",
        "Periode pembanding di luar rentang seri utama yang tidak ditulis: "
        + (", ".join(f"{k} {v}" for k, v in DI_LUAR.items() if v) or "tidak ada") + ".",
        "## Kategori", "Kategori baku: " + ", ".join(f"*{k}*" for k in KATEGORI) + ". Kategori pasangan ditetapkan dari "
        "bukti di pasangan rekonsiliasi Sprint 1 (`reports/pasangan-rekonsiliasi.md`); baris satu sisi menjadi *tanpa "
        "pasangan*, baris yang angkanya sama menjadi *tidak berselisih*.",
        "## Rincian per pasangan", *bagian,
    ]))
    return t
