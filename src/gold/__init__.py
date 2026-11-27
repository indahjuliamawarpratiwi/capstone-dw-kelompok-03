from src.gold import muat_sql, nasional, nasional_gold, panel, rekonsiliasi


def jalankan(silver):
    hasil = nasional.jalankan(silver)
    hasil["panel"] = panel.jalankan(silver)
    hasil["nasional"] = nasional_gold.jalankan(silver)
    hasil["nasional_gold"] = hasil["nasional"]
    hasil["rekonsiliasi"] = rekonsiliasi.jalankan(hasil["nasional"])
    hasil["baris_sql"] = muat_sql.jalankan(silver, hasil)
    return hasil
