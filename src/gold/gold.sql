CREATE TABLE gold_panel (
    indikator       VARCHAR  NOT NULL,
    seri_kode       VARCHAR  NOT NULL REFERENCES seri (seri_kode),
    rincian         VARCHAR  NOT NULL,
    wilayah_kode    INTEGER  NOT NULL CHECK (wilayah_kode BETWEEN 1100 AND 9799),
    nama_wilayah    VARCHAR  NOT NULL,
    periode         VARCHAR  NOT NULL,
    jenis_periode   VARCHAR  NOT NULL CHECK (jenis_periode IN ('tahun', 'semester', 'triwulan', 'bulan')),
    nilai           DOUBLE,
    satuan          VARCHAR  NOT NULL,
    status_sel      VARCHAR  NOT NULL CHECK (status_sel IN ('terisi', 'missing', 'tidak_diterbitkan', 'belum_ada', 'batas_lama')),
    penanda         VARCHAR,
    rujukan_tahun   INTEGER,
    _berkas_raw     VARCHAR,
    _sha256_raw     VARCHAR,
    CHECK ((status_sel = 'terisi') = (nilai IS NOT NULL)),
    CHECK (status_sel <> 'terisi' OR _berkas_raw IS NOT NULL),
    PRIMARY KEY (indikator, wilayah_kode, periode)
);

CREATE TABLE gold_nasional (
    seri_kode       VARCHAR  NOT NULL,
    rincian         VARCHAR  NOT NULL,
    sumber          VARCHAR  NOT NULL,
    periode         VARCHAR  NOT NULL,
    jenis_periode   VARCHAR  NOT NULL,
    nilai           DOUBLE   NOT NULL,
    satuan          VARCHAR  NOT NULL,
    batas_bawah     DOUBLE,
    batas_atas      DOUBLE,
    rujukan_tahun   INTEGER,
    asal            VARCHAR  NOT NULL CHECK (asal IN ('baris_indonesia', 'pembanding', 'agregat')),
    _berkas_raw     VARCHAR  NOT NULL,
    _sha256_raw     VARCHAR,
    PRIMARY KEY (seri_kode, rincian, periode)
);

CREATE TABLE rekonsiliasi (
    pasangan_id         VARCHAR NOT NULL,
    jenis               VARCHAR NOT NULL CHECK (jenis IN ('selisih', 'konteks')),
    seri_utama          VARCHAR NOT NULL,
    rincian_utama       VARCHAR NOT NULL,
    seri_pembanding     VARCHAR NOT NULL,
    rincian_pembanding  VARCHAR NOT NULL,
    periode             VARCHAR NOT NULL,
    nilai_utama         DOUBLE,
    nilai_pembanding    DOUBLE,
    satuan              VARCHAR,
    selisih             DOUBLE,
    selisih_relatif     DOUBLE,
    asal                VARCHAR NOT NULL CHECK (asal IN ('keduanya', 'hanya_utama', 'hanya_pembanding')),
    kategori            VARCHAR NOT NULL CHECK (kategori IN ('definisi berbeda', 'metode berbeda', 'vintage berbeda',
                                                'cakupan berbeda', 'belum terjelaskan', 'tanpa pasangan', 'tidak berselisih')),
    penjelasan          VARCHAR NOT NULL,
    catatan             VARCHAR,
    CHECK (selisih IS NULL OR abs(selisih - (nilai_utama - nilai_pembanding)) < 1e-6),
    PRIMARY KEY (pasangan_id, seri_pembanding, rincian_pembanding, periode)
);

-- Pembanding: berkas JSON mentah disimpan apa adanya sebagai dokumen (satu baris per berkas).
CREATE TABLE dokumen_mentah (
    _berkas_raw     VARCHAR PRIMARY KEY,
    _sha256_raw     VARCHAR NOT NULL,
    sumber          VARCHAR NOT NULL,
    isi             JSON    NOT NULL
);
