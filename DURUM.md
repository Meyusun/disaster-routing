# DURUM

**Aktif adım: 1 — Herkesin bilgisayarında çalışsın**
Son güncelleme: 2026-11-27

## Adım 1 "bitti" şartları
- [ ] V4, GitHub `Meyusun/disaster-routing` reposunun `v4` dalına gönderildi (push)
- [ ] Yusuf'un bilgisayarında `LC_ALL=C python -m pytest -q tests` FAILED vermiyor
- [ ] Model dosyaları (`checkpoints/*.pth`) ve Maxar görüntüleri ikinizin de erişebildiği bir yerde
- [ ] Kuzey sadece README'ye bakarak testleri ve `python -m scripts.run_emsr AOI17`'yi çalıştırdı

## Son yapılanlar
- 2026-11-27 — Adım 0 bitti: V3'ten V4'e temiz başlangıç (K-1). Testler Claude'un bulut ortamında çalıştırıldı: 10 geçti, 1 atlandı (model testi; o ortamda PyTorch yoktu).

## Açık sorunlar
- Model testi (T6) henüz hiçbir bilgisayarda V4 ile çalıştırılmadı. PyTorch ve model dosyası olan bir bilgisayarda çalıştırılmalı.
- Sıvılaşma katmanının V3'ten neden çıkarıldığı bilinmiyor. Adım 5'ten önce eski repodaki `docs/Kararlar.md`'ye bakılacak.
