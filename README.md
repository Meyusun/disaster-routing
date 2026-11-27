# disaster-routing V4

Deprem sonrası hasarlı yollardan kaçan rota bulma sistemi. V3'ün (github.com/KKirca/disaster_routing_V3) temizlenmiş hâli.

**Ne yapacağımız:** `HEDEFLER.md` (sıralı adımlar ve "bitti" şartları).
**V3'te ne bulduk:** `docs/arsiv_v3/` (V3 durum notları, tez notları, sunum akışı, eğitim günlüğü).

## Klasörler

```
dr/          asıl kod (sistemin parçaları)
  routing.py   yol ağını indir, yolları kapat/geciktir, A* ile rota bul
  georef.py    model çıktısını haritaya yerleştir, güçlü/zayıf hasar ayır
  infer.py     büyük görüntüyü parçalara bölüp modele ver
  data.py      KATE-CD veri setini oku
  unet.py      model (U-Net)
scripts/     çalıştırılan komutlar
  run_pipeline.py  görüntü + A/B noktası -> rota resmi
  run_emsr.py      uzman hasar haritası (EMSR648) ile rota
  train.py         modeli eğit (--mode post | prepost, --seed)
  evaluate.py      iki modeli test setinde karşılaştır
  maxar_find.py    bir noktayı kapsayan Maxar görüntülerini listele
  maxar_crop.py    Maxar görüntüsünden kare kes
tests/       otomatik kontroller (internetsiz)
docs/arsiv_v3/   V3 kayıtları
```

## Kurulum

```bash
conda env create -f environment.yml
conda activate disaster
# PyTorch: kendi ekran kartınıza uygun komutu pytorch.org'dan alın.
```

Tüm komutlar proje klasöründen çalıştırılır. V3 notuna göre GDAL Türkçe dil ayarında hata veriyor, bu yüzden komutların başına `LC_ALL=C` eklenir.

## Çalıştırma

```bash
LC_ALL=C python -m pytest -q tests                  # kontroller (internet gerekmez)
DR_CANLI=1 LC_ALL=C python -m pytest -q tests       # aynı kontroller gerçek Kahramanmaraş haritasında (internet gerekir)
LC_ALL=C python -m scripts.run_emsr AOI17 --veri data/emsr648
LC_ALL=C python -m scripts.run_pipeline --image inputs/<goruntu>.tif --a <enlem> <boylam> --b <enlem> <boylam>
LC_ALL=C python -m scripts.train --mode post --seed 42
LC_ALL=C python -m scripts.evaluate
```

KATE-CD verisi V3'te `data/kate_cd` klasöründen okunuyordu. Eski kodda verinin adı `CSCRS/kate-cd`. İndirme ve kaydetme için:
`python -c "from datasets import load_dataset; load_dataset('CSCRS/kate-cd').save_to_disk('data/kate_cd')"`
(Bu komut bu sürümü hazırlarken denenemedi.)

## V3'ten ne alındı, ne çıkarıldı

| V3 dosyası | V4'te | Neden |
|---|---|---|
| routing.py, georef.py, infer.py, data.py, models/unet.py | `dr/` | Sistemin çekirdeği. İçerik aynı; sadece klasör yolları düzeltildi. |
| run_pipeline.py | `scripts/run_pipeline.py` | Ana komut. İçerik aynı. |
| demo_emsr.py | `scripts/run_emsr.py` | Koda gömülü `~/disaster-routing/data/emsr648` yolu `--veri` parametresine çevrildi. |
| train_post.py | `scripts/train.py` | `--mode` ile hem 3 hem 6 kanal, `--seed` ile 3 tohum (Adım 6). |
| compare.py | `scripts/evaluate.py` | İki modeli aynı anda ölçüyor. |
| tools/find_maxar.py, crop_maxar.py | `scripts/maxar_*.py` | Saha görüntüsü almak için (Adım 6). |
| test_*.py (T1–T9) | `tests/` | Aynı kontroller, artık internetsiz. T10 eklendi (çizgi şeklindeki engel). |
| DURUM.md, TEZ_NOTLARI.md, sunum/CANLI_AKIS.md, logs/train_post.csv | `docs/arsiv_v3/` | V3 sonuçlarının kaydı. |
| sunum/*.sh | çıkarıldı | V3 sunumuna özel komutlar. |
| legacy_6kanal/ | çıkarıldı | Yerini `train.py --mode prepost` aldı. (Fark: eski eğitimde erken durma ve sabit tohum yoktu.) |
| check_model.py | çıkarıldı | `evaluate.py` aynı ölçümü iki model için yapıyor. |
| tools/inspect_emsr*.py, find_emsr.py | çıkarıldı | AOI04 incelemesi bitti; sonucu `TEZ_NOTLARI.md` içinde. |
| tools/normalize.py, prob_map.py, rank_maxar.py | çıkarıldı | Tek seferlik deneyler; sonuçları `DURUM.md` içinde. |
