# DURUM

**Aktif adım: 1 — Herkesin bilgisayarında çalışsın**
Son güncelleme: 2026-11-27 (Yusuf'un laptop taraması sonrası)

## Adım 1 "bitti" şartları
- [x] Yusuf'un laptopunda ortam hazır: conda `disaster`, Python 3.11.15, torch 2.11.0+cu128, `torch.cuda.is_available()` = True, RTX 4060 8 GB (kaynak: 2026-11-27 tarama raporu)
- [x] `pytest` kuruldu — taramada YOK çıkmıştı; Yusuf pip install pytest ile kurdu, 2026-11-27 test komutu çalıştı
- [x] V4, GitHub `Meyusun/disaster-routing` reposunun `v4` dalına gönderildi (push) — kanıt: 2026-11-27 `git push -u origin v4` → `* [new branch] v4 -> v4`
- [x] Yusuf'un laptopunda `LC_ALL=C python -m pytest -q tests` FAILED vermiyor — kanıt: 2026-11-27 internetsiz: `10 passed, 1 skipped in 2.02s`; `DR_CANLI=1` ile: `10 passed, 1 skipped in 79.80s`. Atlanan: `tests/test_model.py:7: model dosyasi veya KATE-CD verisi yok`
- [x] EMSR648 verisi `data/emsr648` içine kopyalandı ve `python -m scripts.run_emsr AOI17` çalıştı — kanıt: 2026-11-27 `python -m scripts.run_emsr AOI17 --veri data/emsr648` → `Hasarsiz rota: 4270 m`, R=25 için `4522 m` (V3 ile aynı). İlk denemede Overpass sunucusu `502 Bad Gateway` (sunucu dolu) verdi, ikinci denemede çalıştı.
- [x] Adım 1 için kurulum testi eklendi (tests/test_kurulum.py) — kanıt: 2026-11-27 normal: `LC_ALL=C conda run -n disaster --no-capture-output python -m pytest -q tests` → `13 passed, 1 skipped in 1.60s`; bozuk: `DR_VERI_KOK=/tmp/yok ... pytest -q tests/test_kurulum.py` → `1 failed, 2 passed in 0.78s`, `test_emsr_verisi_var` mesajı: `data/emsr648 eksik: README'deki 'Veri hazırlığı' adımını yap. (bakılan yer: /tmp/yok/emsr648, AOI17'de eksik: areaOfInterestA, builtUpA)`
- [ ] Model dosyaları ve Maxar görüntüleri ikinizin de erişebildiği bir yerde (aşağıdaki "Kuzey'den alınacaklar")
- [ ] Kuzey sadece README'ye bakarak testleri ve `python -m scripts.run_emsr AOI17`'yi çalıştırdı

## Kuzey'den alınacaklar (Yusuf'un laptopunda ve USB'de YOK)
- `checkpoints/post_best.pth` (3 kanal model) ve `checkpoints/best_model.pth` (6 kanal model)
- `inputs/maxar_2022-07-26_10300100D797E100.tif`, `inputs/maxar_2023-02-11_10300100E19A4400.tif`, `inputs/maxar_2023-02-28_10300100E3154100.tif`, `inputs/maxar_2023-02-07_1040010082698700.tif` (adlar: `docs/arsiv_v3/CANLI_AKIS.md`)
- V3 notuna göre bunların hepsi `sunum_yedek.tar.gz` (367 MB) içindeydi.
- KATE-CD verisi (`data/kate_cd`). Sadece Adım 6'da gerekli.

## Yusuf'un laptopundaki önemli şeyler
- `~/disaster-routing` (eski repo, 9,6 GB): **silinmeyecek.** İçinde `data/emsr648` (AOI04, AOI16, AOI17), `data/zhu_2017_general_model.tif` (Adım 5), `data/maxar/`, takip edilmeyen 4 script ve eski `docs/Kararlar.md` var.
- Disk: 19 GB boş (%87 dolu). Büyük veri indirmeden önce yer açılmalı.
- Git: `user.name` = "Yusuf ...", `user.email` = myusufobak@gmail.com. GitHub, commit'i hesaba e-postaya bakarak bağlar. Bu e-posta GitHub hesabının e-posta ayarlarında kayıtlı değilse commit'ler hesaba bağlanmaz.

## Son yapılanlar
- 2026-11-27 — Adım 1: kurulum testi `tests/test_kurulum.py` eklendi (kütüphaneler, osmnx ≥ 2, EMSR648 verisi); README'ye "Veri hazırlığı" eklendi.
- 2026-11-27 — Adım 0 bitti: V3'ten V4'e temiz başlangıç (K-1). Testler Claude'un bulut ortamında çalıştırıldı: 10 geçti, 1 atlandı (model testi; o ortamda PyTorch yoktu).
- 2026-11-27 — Adım 1 kısmen: laptopta testler geçti (10 geçti, 1 atlandı), `run_emsr AOI17` V3 ile aynı sonucu verdi, v4 dalı GitHub'a gönderildi.
- 2026-11-27 — Yusuf'un laptopu iki kez tarandı (sadece okundu, hiçbir şey değiştirilmedi). Bütün dosyaların yeri: `docs/DOSYA_HARITASI.md`.

## Açık sorunlar
- `run_emsr` yol ağını internetten (Overpass) çekiyor; sunucu dolu olunca 502 hatası veriyor, tekrar denemek gerekiyor.
- Model testi (T6) henüz hiçbir bilgisayarda V4 ile çalıştırılmadı. Model dosyaları gelince çalıştırılacak.
