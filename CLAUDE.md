# disaster-routing V4

Önce oku: HEDEFLER.md, DURUM.md, KARARLAR.md. Sadece DURUM.md'deki aktif adım üzerinde çalış.

## Komutlar
- Ortam: `conda activate disaster`
- Test (her değişiklikten sonra): `LC_ALL=C python -m pytest -q tests`
- Her Python komutu `LC_ALL=C` ile ve proje kökünden `python -m scripts.<ad>` biçiminde çalışır (GDAL Türkçe dil ayarı hatası).

## Kurallar
- `dr/routing.py` içindeki `edge_cost`, A* ve sezgisel fonksiyon değişmez. Değişecekse önce KARARLAR.md'ye karar yazılır.
- `checkpoints/`, `inputs/`, `data/`, `outputs/` git'e eklenmez.
- İş bitince: test çıktısını göster, DURUM.md'yi güncelle, commit mesajı "Adım N: ..." olsun.
- Kullanıcıyla Türkçe ve sade dille konuş.
