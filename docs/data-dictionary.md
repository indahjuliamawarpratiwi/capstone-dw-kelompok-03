# Data dictionary — Kasus 03 Kesehatan reproduksi remaja

Ditulis ulang otomatis oleh `python pipeline.py` (`src/dokumen.py`). Tipe, rentang, dan jumlah kosong dihitung dari `data/silver/silver.parquet`.

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
| _berkas_raw | str | 0 | bps/2026-10-20/json/sdg3_3_7_1_v1394.json, bps/2026-10-20/json/sdg3_3_7_2_v1353.json, wdi/2026-10-20/data/kelompok-07-hal-01.json, who_gho/2026-10-20/datadot/27D371A_MDG_0000000003.csv, who_gho/2026-10-20/datadot/8074BD9_SDGFPALL.csv | jalur berkas mentah relatif data/raw/ | lineage: berkas asal baris ini |
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

| seri_kode | satuan | sdg_kode | cakupan | bukti_satuan |
|---|---|---|---|---|
| var1394 | persen | 3.7.1 | perempuan 15–49 atau pasangannya; sumber SDKI (var.note); hanya tahun survei 2012 dan 2017 | var.unit: 'Persen' |
| var1353 | per_1000_perempuan_seumur | 3.7.2 | umur 15–19 saja (judul var.label; tidak ada kelompok 10–14); sumber IDHS/SDKI (var.note); judul berakhir dengan spasi | var.unit dan kolom satuan CSV kosong; judul menyebut perempuan 15–19; definisi baku indikator yang sama di metadata WHO ('per 1,000 females in the respective age group') dan nama WDI ('births per 1,000 women ages 15-19'); besaran angka (puluhan) sesuai per 1.000, bukan persen |
| SP.ADO.TFRT | per_1000_perempuan_seumur | 3.7.2 | umur 15–19; estimasi model World Population Prospects (UN Population Division), tahunan | name: '(births per 1,000 women ages 15-19)' |
| MDG_0000000003 | per_1000_perempuan_seumur | 3.7.2 | perempuan; dua kelompok umur (10–14, 15–19) di kolom rincian; data survei/registrasi, tahun tidak lengkap [dimensi tetap di berkas: DIM_SEX=FEMALE] | kolom RATE_PER_1000_N; UnitOfMeasure: 'Annual number of births per 1000 adolescent women' |
| SDGFPALL | persen | 3.7.1 | perempuan 15–49; penyebut = permintaan KB total (pemakai semua metode + kebutuhan tak terpenuhi) [dimensi tetap di berkas: DIM_SEX=FEMALE; DIM_AGE=Y15T49] | kolom RATE_PER_100_N |

## Kode wilayah

9999 = Indonesia; provinsi = kode BPS dua digit x 100, susunan 38 provinsi 2025 (38 kode). WDI menulis Indonesia `ID`/`IDN`, WHO GHO menulis `360` (M49); keduanya dipetakan ke 9999 di `src/wilayah.py`.

## Contoh penelusuran satu baris

| sumber | seri_kode | wilayah_kode | periode | rincian | nilai | _berkas_raw | _sha256_raw |
|---|---|---|---|---|---|---|---|
| bps | var1353 | 1100 | 2012 | total | 25.00 | bps/2026-10-20/json/sdg3_3_7_2_v1353.json | 230ce163135e9ea9e078649b2812136780e9e2db9d4c110dc3e21f2fe50faf5a |

1. `_berkas_raw` menunjuk `data/raw/bps/2026-10-20/json/sdg3_3_7_2_v1353.json`.

2. Baris berkas itu di `data/raw/MANIFEST.csv` memuat sha256 `230ce163135e…`; nilainya sama dengan `_sha256_raw`, jadi berkas yang dibaca adalah berkas yang tercatat.

3. Di berkas mentah, angka ditemukan pada wilayah, periode, dan rincian yang sama (untuk JSON BPS: kunci `datacontent` = kode wilayah + var + turvar + kode tahun + turtahun).
