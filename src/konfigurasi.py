"""Keputusan wrangling Kasus 03 — Kesehatan reproduksi remaja.

Semua keputusan khas kasus ada di berkas ini supaya mudah ditinjau: identitas seri, satuan dan kode
SDG beserta buktinya, cara menulis rincian umur, ambang anomali, dan pasangan rekonsiliasi. Setiap
keputusan juga tercatat di log-keputusan.csv.
Ini salah satu jawaban yang dapat dipertahankan, bukan satu-satunya.
"""

KASUS = 3
SLUG = "kesehatan-reproduksi-remaja"
JUDUL = "Kesehatan reproduksi remaja"

# K-002: JSON dipakai sebagai sumber Silver BPS (CSV identik nilainya, JSON membawa judul dan catatan).
FORMAT_BPS = "json"

# Satu satuan untuk semua angka kelahiran remaja (K-007): per 1.000 perempuan pada kelompok umur yang sama.
# Untuk BPS dan WDI kelompok umurnya 15–19; untuk WHO kelompok umur ada di kolom rincian.
ABR = "per_1000_perempuan_seumur"

SERI = {
    "var1394": dict(
        sumber="bps", tingkat="provinsi",
        nama="Proporsi perempuan usia reproduksi (15–49 tahun) atau pasangannya yang memiliki kebutuhan KB dan "
             "menggunakan alat kontrasepsi metode modern",
        satuan="persen", katalog_satuan="persen",
        bukti_satuan="var.unit: 'Persen'",
        sdg="3.7.1", katalog_sdg="3.7.1",
        bukti_sdg="judul TPB nasional 3.7.1; besaran angkanya lebih dekat ke pemakaian kontrasepsi modern daripada "
                  "kebutuhan KB terpenuhi (lihat P2 dan log K-009)",
        cakupan="perempuan 15–49 atau pasangannya; sumber SDKI (var.note); hanya tahun survei 2012 dan 2017",
    ),
    "var1353": dict(
        sumber="bps", tingkat="provinsi",
        nama="Angka kelahiran pada perempuan umur 15–19 tahun (per 1.000 perempuan 15–19)",
        satuan=ABR, katalog_satuan="tidak_ada",
        bukti_satuan="var.unit dan kolom satuan CSV kosong; judul menyebut perempuan 15–19; definisi baku indikator "
                     "yang sama di metadata WHO ('per 1,000 females in the respective age group') dan nama WDI "
                     "('births per 1,000 women ages 15-19'); besaran angka (puluhan) sesuai per 1.000, bukan persen",
        sdg="3.7.2", katalog_sdg="3.7.2",
        bukti_sdg="judul = angka kelahiran remaja 15–19, indikator global 3.7.2",
        cakupan="umur 15–19 saja (judul var.label; tidak ada kelompok 10–14); sumber IDHS/SDKI (var.note); "
                "judul berakhir dengan spasi",
        koreksi="satuan tidak_ada -> per_1000_perempuan_seumur",
    ),
    "SP.ADO.TFRT": dict(
        sumber="wdi", tingkat="nasional", nama="Adolescent fertility rate (births per 1,000 women ages 15-19)",
        satuan=ABR, katalog_satuan="—", bukti_satuan="name: '(births per 1,000 women ages 15-19)'",
        sdg="3.7.2", katalog_sdg="—", bukti_sdg="tercantum di metadata/sumber46_indikator.json (Sustainable Development Goals)",
        cakupan="umur 15–19; estimasi model World Population Prospects (UN Population Division), tahunan",
        koreksi="kode SDG kosong -> 3.7.2",
    ),
    "MDG_0000000003": dict(
        sumber="who_gho", tingkat="nasional", nama="Adolescent birth rate (per 1000 women in the age group)",
        satuan=ABR, katalog_satuan="—",
        bukti_satuan="kolom RATE_PER_1000_N; UnitOfMeasure: 'Annual number of births per 1000 adolescent women'",
        sdg="3.7.2", katalog_sdg="3.7.2", bukti_sdg="metadata WHO",
        cakupan="perempuan; dua kelompok umur (10–14, 15–19) di kolom rincian; data survei/registrasi, tahun tidak lengkap",
    ),
    "SDGFPALL": dict(
        sumber="who_gho", tingkat="nasional", nama="Family planning satisfied with modern methods (%)",
        satuan="persen", katalog_satuan="—", bukti_satuan="kolom RATE_PER_100_N",
        sdg="3.7.1", katalog_sdg="3.7.1", bukti_sdg="metadata WHO (DefinitionText: demand for family planning satisfied with modern methods)",
        cakupan="perempuan 15–49; penyebut = permintaan KB total (pemakai semua metode + kebutuhan tak terpenuhi)",
    ),
}

# Rincian (K-006). Umur WHO dienkode 10-14 / 15-19 sesuai panduan kelompok.
RINCIAN_TOTAL_BPS = {"tidak ada"}
RINCIAN_TOTAL_WHO = {"TOTAL", ""}
RINCIAN_DIMENSI = {"DIM_SEX": "jenis_kelamin", "DIM_AGE": "umur"}
RINCIAN_NILAI = {"DIM_AGE": {"Y10T14": "10-14", "Y15T19": "15-19"}}
KODE_RINCIAN = {"jenis_kelamin": {"FEMALE", "MALE"}, "umur": {"10-14", "15-19"}}

RUJUKAN_TAHUN = {}
TIDAK_TERBIT = {}
TAHUN_TERBIT = {"var1394": {"2012", "2017"}, "var1353": {"2012", "2017"}}

RENTANG = {"persen": (0, 100), ABR: (0, 1000)}

# Ambang anomali (K-004): dua periode saja, jadi hanya arah ke bawah dan perubahan.
ANOMALI = {"k_iqr": 1.5, "min_titik_samping": 6, "lompat_relatif": 0.20, "porsi_patahan": 0.70}

PASANGAN = [
    dict(id="P1", judul="Angka kelahiran remaja 15–19: BPS (SDKI) vs WDI (model WPP)",
         utama="var1353", rincian_utama="total", pembanding=[("SP.ADO.TFRT", "total")],
         jenis="selisih", kategori="metode (survei dengan periode rujukan vs estimasi model penduduk tahunan)",
         alasan_rincian="BPS total = umur 15–19 (judul); WDI hanya 15–19",
         pertanyaan=[
             ("Kelompok umur BPS?", "15–19 saja: var.label 'Angka Kelahiran Pada Perempuan Usia 15-19 Tahun'."),
             ("Dari mana angka WDI?", "sourceOrganization: World Population Prospects, UN Population Division (model)."),
         ]),
    dict(id="P2", judul="Angka kelahiran remaja 15–19: BPS vs WHO",
         utama="var1353", rincian_utama="total", pembanding=[("MDG_0000000003", "umur=15-19")],
         jenis="selisih", kategori="tidak ada tahun beririsan; dibandingkan dengan tahun terdekat di Gold (Sprint 2) dengan penanda",
         alasan_rincian="WHO rincian umur=15-19; baris 10-14 tidak sebanding",
         pertanyaan=[
             ("Rincian WHO mana?", "umur=15-19 (DIM_AGE Y15T19). Baris 10–14 punya penyebut perempuan 10–14."),
             ("Tahun mana yang sama?", "Tidak ada: WHO punya 2011, 2013, 2015, 2016, tetapi tidak 2012 dan 2017."),
         ]),
    dict(id="P3", judul="KB metode modern: BPS vs WHO kebutuhan KB terpenuhi",
         utama="var1394", rincian_utama="total", pembanding=[("SDGFPALL", "total")],
         jenis="selisih", kategori="definisi (penyebut berbeda: BPS lebih dekat ke prevalensi kontrasepsi modern)",
         alasan_rincian="keduanya perempuan 15–49 tanpa rincian",
         pertanyaan=[
             ("Apa penyebut WHO?", "Permintaan KB total = pemakai semua metode + kebutuhan tak terpenuhi (Denominator)."),
             ("Apakah judul BPS menyebut penyebutnya?", "Tidak tegas; status perkawinan juga tidak disebut. "
              "Limitations WHO menyebut populasi dasar (termasuk status perkawinan) sebagai sumber ketidakcocokan."),
             ("Apa kata besaran angkanya?", "BPS Indonesia jauh di bawah WHO pada tahun yang sama; karena pemakai metode modern "
              "≤ permintaan total, pola itu cocok dengan BPS memakai penyebut yang lebih besar."),
         ]),
    dict(id="P4", judul="Angka kelahiran remaja 15–19: WHO vs WDI",
         utama="MDG_0000000003", rincian_utama="umur=15-19", pembanding=[("SP.ADO.TFRT", "total")],
         jenis="selisih", kategori="sumber berbeda (WHO: data survei/registrasi yang dihimpun; WDI: model WPP)",
         alasan_rincian="WHO umur=15-19",
         pertanyaan=[("Apakah sumbernya sama?", "Tidak: MethodOfEstimationOverview WHO menyebut registrasi sipil dan survei; WDI dari WPP.")]),
]
