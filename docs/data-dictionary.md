# Data dictionary — Kasus 03 Kesehatan reproduksi remaja

Bagian Silver ditulis ulang otomatis oleh `python pipeline.py` (`src/dokumen.py`). Bagian Gold dan SQL mendokumentasikan artefak yang dihasilkan `src/gold/` dan `src/validasi/`; tipe, rentang, dan jumlah kosong dihitung dari artefak aktual.

## data/silver/silver.parquet (235 baris)

Satu baris = satu seri x wilayah x periode x rincian x berkas sumber. Kunci unik: sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw.

| kolom | tipe | kosong | rentang_atau_nilai | asal | arti |
|---|---|---|---|---|---|
| sumber | str | 0 | bps, wdi, who_gho | nama folder sumber di data/raw/ | lembaga penerbit: bps, wdi, who_gho, ilostat, bnpb |
| seri_kode | str | 0 | MDG_0000000003, SDGFPALL, SP.ADO.TFRT, var1353, var1394 | kode seri di sumbernya (BPS: 'var' + var.val) | identitas seri; arti lengkap di docs/seri.csv |
| wilayah_kode | int64 | 0 | 1100 – 9999 | kamus src/wilayah.py; log K-001 | kode BPS dua digit x 100; 9999 = Indonesia |
| nama_wilayah | str | 0 | Aceh, Bali, Banten, Bengkulu, DI Yogyakarta, DKI Jakarta, … (35 nilai) | kamus src/wilayah.py | nama baku susunan 38 provinsi 2025, bukan label sumber |
| periode | str | 0 | 1960, 1961, 1962, 1963, 1964, 1965, … (65 nilai) | tahun/turtahun BPS, date WDI, DIM_TIME WHO | bentuk baku: 2019, 2019-S1, 2019-Q3, 2019-07 |
| jenis_periode | str | 0 | tahun | diturunkan dari periode | tahun, semester, triwulan, atau bulan |
| rincian | str | 0 | total, umur=10-14, umur=15-19 | turvar BPS; kolom DIM_* WHO yang bervariasi | 'total' atau 'dimensi=kode;...'; lihat kamus di bawah |
| nilai | float64 | 0 | 0.264736 – 151.704 | datacontent BPS; value WDI; RATE_*_N WHO | angka sesuai satuan; baris tanpa angka tidak masuk Silver |
| satuan | str | 0 | per_1000_perempuan_seumur, persen | src/konfigurasi.py, bukti di docs/seri.csv | satuan baku; satu satuan per seri |
| sdg_kode | str | 0 | 3.7.1, 3.7.2 | src/konfigurasi.py, bukti di docs/seri.csv | kode indikator SDG (kolom tambahan) |
| batas_bawah | float64 | 235 | — | RATE_*_NL WHO | batas bawah ketidakpastian; kosong bila sumber tidak memberi |
| batas_atas | float64 | 235 | — | RATE_*_NU WHO | batas atas ketidakpastian; kosong bila sumber tidak memberi |
| rujukan_tahun | Int64 | 235 | — | var.note BPS; log | lebar jendela rujukan survei (tahun sebelum survei); kosong bila tidak berlaku |
| _berkas_raw | str | 0 | bps/2026-10-20/json/sdg3_3_7_1_v1394.json, bps/2026-10-20/json/sdg3_3_7_2_v1353.json, wdi/2026-10-20/data/kelompok-03-hal-01.json, who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv, who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv | jalur berkas mentah relatif data/raw/ | lineage: berkas asal baris ini |
| _sha256_raw | str | 0 | 230ce163135e9ea9e078649b2812136780e9e2db9d4c110dc3e21f2fe50faf5a, 6ae359c6df0dfd6ce210233dc28ada9060be0996f855288d6c4fbfee88b55c74, 894de8e94f8c2c76aaa44f3a3f541607429e924d9101a80a2d5eebcfe433284b, 9a8729675761d697bd5556d66fd903ed841ee454e7324d41084dc09b9905f912, efd85410d3d2939a3fabcb1a17489a3860985eec2685d49787919c3657a7e702 | src.common.manifest.sha256_raw | lineage: sidik isi berkas asal, dicocokkan dengan MANIFEST.csv |

## Kamus rincian

Aturan menulis rincian (log): dimensi yang bervariasi ditulis `nama=kode`, dipisah `;`, urut abjad; nilai total sumber dibuang; baris tanpa dimensi bervariasi ditulis `total`. Dimensi yang nilainya tetap di seluruh berkas dianggap bagian definisi seri dan dicatat di kolom `cakupan` docs/seri.csv.

Nama dimensi dan kode yang sah:

- `jenis_kelamin`: `FEMALE`, `MALE`
- `umur`: `10-14`, `15-19`

| rincian | dipakai_seri |
|---|---|
| total | SDGFPALL, SP.ADO.TFRT, var1353, var1394 |
| umur=10-14 | MDG_0000000003 |
| umur=15-19 | MDG_0000000003 |

## Satuan, kode SDG, dan cakupan per seri

| seri_kode | satuan | sdg_kode | cakupan | bukti_satuan | bukti_sdg |
|---|---|---|---|---|---|
| var1394 | persen | 3.7.1 | perempuan 15–49 atau pasangannya; sumber SDKI (var.note); hanya tahun survei 2012 dan 2017 | var.unit: 'Persen' | judul TPB nasional 3.7.1; besaran angkanya lebih dekat ke pemakaian kontrasepsi modern daripada kebutuhan KB terpenuhi (K-009) |
| var1353 | per_1000_perempuan_seumur | 3.7.2 | umur 15–19 saja (judul var.label; tidak ada kelompok 10–14); sumber IDHS/SDKI (var.note); judul berakhir dengan spasi | var.unit dan kolom satuan CSV kosong; judul menyebut perempuan 15–19; definisi baku indikator yang sama di metadata WHO ('per 1,000 females in the respective age group') dan nama WDI ('births per 1,000 women ages 15-19'); besaran angka (puluhan) sesuai per 1.000, bukan persen | judul var.label = angka kelahiran remaja 15–19; indikator global 3.7.2 |
| SP.ADO.TFRT | per_1000_perempuan_seumur | 3.7.2 | umur 15–19; estimasi model World Population Prospects (UN Population Division), tahunan | name/sourceNote: '(births per 1,000 women ages 15-19)' | metadata/sumber46_indikator.json source id=46 'Sustainable Development Goals'; definisi 'births per 1,000 women ages 15-19' = 3.7.2 |
| MDG_0000000003 | per_1000_perempuan_seumur | 3.7.2 | perempuan; dua kelompok umur (10–14, 15–19) di kolom rincian; data survei/registrasi, tahun tidak lengkap [dimensi tetap di berkas: DIM_SEX=FEMALE] | kolom RATE_PER_1000_N; UnitOfMeasure: 'Annual number of births per 1000 adolescent women'; DefinitionText 'per 1,000 females in the respective age group' | metadata WHO DefinitionText; AlternativeCodes MDG_0000000003 |
| SDGFPALL | persen | 3.7.1 | perempuan 15–49; penyebut = permintaan KB total (pemakai semua metode + kebutuhan tak terpenuhi) [dimensi tetap di berkas: DIM_SEX=FEMALE; DIM_AGE=Y15T49] | kolom RATE_PER_100_N; UnitOfMeasure/FullName WHO menyertakan (%) | metadata WHO DefinitionText 'demand for family planning satisfied with modern methods'; AlternativeCodes SDGFPALL |

## Kode wilayah

9999 = Indonesia; provinsi = kode BPS dua digit x 100, susunan 38 provinsi 2025 (38 kode). WDI menulis Indonesia `ID`/`IDN`, WHO GHO menulis `360` (M49); keduanya dipetakan ke 9999 di `src/wilayah.py`.

## Contoh penelusuran satu baris

| sumber | seri_kode | wilayah_kode | periode | rincian | nilai | _berkas_raw | _sha256_raw |
|---|---|---|---|---|---|---|---|
| bps | var1353 | 1100 | 2012 | total | 25.00 | bps/2026-10-20/json/sdg3_3_7_2_v1353.json | 230ce163135e9ea9e078649b2812136780e9e2db9d4c110dc3e21f2fe50faf5a |

1. `_berkas_raw` menunjuk `data/raw/bps/2026-10-20/json/sdg3_3_7_2_v1353.json`.

2. Baris berkas itu di `data/raw/MANIFEST.csv` memuat sha256 `230ce163135e…`; nilainya sama dengan `_sha256_raw`, jadi berkas yang dibaca adalah berkas yang tercatat.

3. Di berkas mentah, angka ditemukan pada wilayah, periode, dan rincian yang sama (untuk JSON BPS: kunci `datacontent` = kode wilayah + var + turvar + kode tahun + turtahun).

## data/gold/nasional.parquet (89 baris)

Satu baris = satu seri × rincian × periode tingkat Indonesia. Kunci unik: `seri_kode + rincian + periode`. Rincian WHO `umur=10-14` tetap di Silver dan tidak masuk Gold.

| kolom | tipe | kosong | definisi / satuan / status |
|---|---|---:|---|
| seri_kode | str | 0 | seri BPS, WHO GHO, atau WDI; 5 nilai |
| rincian | str | 0 | `total` (75 baris) atau `umur=15-19` (14 baris) |
| sumber | str | 0 | `bps`, `who_gho`, `wdi` |
| periode | str | 0 | tahun `YYYY`; hanya tahun yang diterbitkan sumber |
| jenis_periode | str | 0 | semua `tahun` |
| nilai | float64 | 0 | angka sesuai satuan seri; tidak diimputasi |
| satuan | str | 0 | `persen` atau `per_1000_perempuan_seumur` |
| batas_bawah | float64 | 89 | kosong: sumber tidak memberi batas ketidakpastian |
| batas_atas | float64 | 89 | kosong: sumber tidak memberi batas ketidakpastian |
| rujukan_tahun | float64 | 89 | kosong: tidak berlaku untuk baris nasional ini |
| asal | str | 0 | `baris_indonesia` (4 baris BPS) atau `pembanding` (85 baris WHO/WDI) |
| _berkas_raw | str | 0 | jalur berkas mentah; 5 berkas |
| _sha256_raw | str | 0 | sidik berkas mentah dari MANIFEST.csv |

## data/gold/panel.parquet (152 baris)

Satu baris = satu indikator × provinsi × periode, termasuk sel kosong. Kunci unik: `seri_kode + wilayah_kode + periode`. `9999` tidak masuk panel.

| kolom | tipe | kosong | definisi / satuan / status |
|---|---|---:|---|
| sumber | str | 0 | semua `bps` |
| seri_kode | str | 0 | `var1394` atau `var1353` |
| wilayah_kode | int64 | 0 | 38 kode provinsi BPS; bukan 9999 |
| nama_wilayah | str | 0 | nama baku susunan 38 provinsi 2025 |
| periode | str | 0 | `2012` atau `2017` |
| jenis_periode | str | 0 | `tahun` |
| rincian | str | 0 | `total` |
| nilai | float64 | 18 | kosong hanya pada sel `belum_ada`; tidak diinterpolasi |
| satuan | str | 18 | `persen` untuk `var1394`; `per_1000_perempuan_seumur` untuk `var1353`; di tabel SQL diisi dari `K.SERI` agar `NOT NULL` |
| sdg_kode | str | 18 | `3.7.1` / `3.7.2`; kosong pada sel tanpa nilai |
| status_sel | str | 0 | `terisi` (134) atau `belum_ada` (18) |
| penanda | str | 0 | `''` (147), `outlier` (3), `patahan_wilayah` (2); bukan string kosong untuk sel bertanda |
| alasan_sel | str | 0 | alasan status sel; kosong sebagai string untuk sel terisi |
| batas_bawah | float64 | 152 | tidak dipakai di panel |
| batas_atas | float64 | 152 | tidak dipakai di panel |
| rujukan_tahun | Int64 | 152 | tidak dipakai di panel |
| _berkas_raw | str | 18 | berkas BPS kanonik; kosong pada sel tanpa nilai |
| _sha256_raw | str | 18 | sidik berkas BPS; kosong pada sel tanpa nilai |

## data/gold/panel_lebar.parquet (34 baris × 6 kolom)

Satu baris per provinsi dengan kolom nilai `var1394_2012`, `var1353_2012`, `var1394_2017`, `var1353_2017`. Kolom 2012 masing-masing memiliki **1 nilai kosong** (Kalimantan Utara belum tercakup); kolom 2017 tidak kosong. Format ini berbeda dari kunci dosen (periode sebagai baris), tetapi nilainya sama dengan `panel.parquet`.

## data/gold/rekonsiliasi.parquet (28 baris)

Satu baris = satu pasangan × pembanding × periode. Kunci unik: `pasangan_id + seri_pembanding + rincian_pembanding + periode`.

| kolom | tipe | kosong | definisi / satuan / status |
|---|---|---:|---|
| pasangan_id | str | 0 | `P1`–`P4` |
| jenis | str | 0 | semua `selisih` |
| seri_utama | str | 0 | `var1353`, `var1394`, atau `MDG_0000000003` |
| rincian_utama | str | 0 | `total` atau `umur=15-19` |
| seri_pembanding | str | 0 | `SP.ADO.TFRT` atau `SDGFPALL` |
| rincian_pembanding | str | 0 | `total` atau `umur=15-19` |
| periode | str | 0 | tahun utama yang direkonsiliasi |
| tahun_utama | str | 0 | tahun nilai utama; sama dengan `periode` |
| tahun_pembanding | str | 0 | tahun pembanding; untuk P2 = 2011/2016 |
| selisih_tahun | int64 | 0 | `tahun_utama − tahun_pembanding`; 1 pada 2 baris P2, 0 pada sisanya |
| nilai_utama | float64 | 8 | kosong pada 8 baris tanpa pasangan |
| nilai_pembanding | float64 | 0 | nilai pembanding dari Gold nasional |
| satuan | str | 0 | `persen` (P3) atau `per_1000_perempuan_seumur` (P1/P2/P4) |
| selisih | float64 | 8 | `nilai_utama − nilai_pembanding`; kosong tanpa pasangan |
| selisih_relatif | float64 | 8 | `100 × selisih / nilai_pembanding`; bertanda |
| asal | str | 0 | `keduanya` (20) atau `hanya_pembanding` (8) |
| kategori | str | 0 | `metode berbeda` (18), `definisi berbeda` (2), `tanpa pasangan` (8) |
| kategori_baku | str | 0 | kategori pasangan dari konfigurasi: metode/definisi berbeda |
| alasan | str | 0 | alasan rincian dan keterbandingan |
| jenis_perbandingan | str | 0 | `langsung` (18), `tahun_terdekat` (2), `tanpa_pasangan` (8) |
| sumber_utama | str | 8 | `bps`/`who_gho`; kosong tanpa pasangan |
| sumber_pembanding | str | 0 | `wdi`/`who_gho` |
| _berkas_raw_utama | str | 8 | lineage utama; kosong tanpa pasangan |
| _sha256_raw_utama | str | 8 | sidik utama; kosong tanpa pasangan |
| _berkas_raw_pembanding | str | 0 | lineage pembanding |
| _sha256_raw_pembanding | str | 0 | sidik pembanding |
| penjelasan | str | 0 | alasan metodologis pasangan |
| catatan | str | 26 | hanya 2 catatan P2 tentang tahun terdekat |

## data/gold/gudang.duckdb (6 tabel)

Dibuat ulang oleh `src/gold/muat_sql.py`; tidak di-commit. `tabel_sql=5` pada metrik menghitung tabel relasional, tidak termasuk `dokumen_mentah`.

| tabel | baris | kunci primer | tipe/definisi ringkas | status kosong |
|---|---:|---|---|---|
| seri | 5 | seri_kode | VARCHAR: sumber, tingkat, nama_baku, satuan, sdg_kode | `sdg_kode` boleh kosong |
| silver | 235 | sumber+seri+wilayah+periode+rincian+berkas | VARCHAR/INTEGER/DOUBLE; `_sha256_raw` 64 hex; FK ke seri | batas/rujukan/status_obs boleh kosong |
| gold_panel | 152 | indikator+wilayah+periode | VARCHAR/INTEGER/DOUBLE; FK ke seri; `indikator` = `seri_kode` | nilai boleh kosong hanya bila sel bukan `terisi`; lineage dapat kosong |
| gold_nasional | 89 | seri+rincian+periode | VARCHAR/DOUBLE/INTEGER; CHECK `asal` | batas/rujukan/_sha256_raw boleh kosong |
| rekonsiliasi | 28 | pasangan+pembanding+rincian+periode | VARCHAR/DOUBLE; CHECK kategori dan selisih | nilai utama, selisih, relatif, catatan boleh kosong |
| dokumen_mentah | 9 | _berkas_raw | VARCHAR + JSON; isi JSON mentah apa adanya | tidak ada kolom wajib kosong |

Constraint penting: `gold_panel` CHECK `status_sel` dan `(status_sel='terisi') ⇔ (nilai IS NOT NULL)`; `rekonsiliasi` CHECK kategori baku dan `selisih = nilai_utama − nilai_pembanding`; `silver` CHECK wilayah, jenis periode, batas, dan panjang sha256. Validasi di `src/validasi/` memeriksa lapis parquet; `tests/test_sql_gold.py` memeriksa keberadaan tabel, jumlah baris, kunci unik, dan penolakan constraint.

## Penelusuran satu nilai Gold

Panel sel `var1353`, provinsi 1100, tahun 2012 bernilai 25,0. Nilai ini berasal dari Silver `(bps, var1353, 1100, 2012, total)` dengan `_berkas_raw = bps/2026-10-20/json/sdg3_3_7_2_v1353.json` dan sha256 `230ce163…`, lalu dimuat ke `gold_panel` sebagai `indikator = var1353`. Sel `belum_ada` Kaltara 2012 tidak memiliki nilai dan tidak memiliki lineage.
