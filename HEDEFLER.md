# Hedefler (V4)

Projenin tek cümlelik amacı: **Deprem sonrası, A noktasından B noktasına giden bir yardım aracı için, hasarlı yollardan kaçan en iyi rotayı bulmak.**

Kural: Bir adım bitmeden sonrakine geçilmez. Her adımın sonunda "bitti sayılır eğer" satırındaki şart sağlanmalı.

---

## Adım 0: Temiz başlangıç (BİTTİ, bu sürüm)

- V3'ten sadece hedeflere yarayan dosyalar alındı (tam liste README'de).
- Rota testleri artık internetsiz çalışıyor: 6×6 sokaklı sahte bir şehir üzerinde.
- **Bitti sayılır eğer:** `python -m pytest -q tests` komutunda kırmızı (FAILED) test olmamalı. Bu sürüm hazırlanırken sonuç: 10 test geçti, 1 test atlandı (model testi; PyTorch ve model dosyası olmayan bilgisayarda kendini atlar).

## Adım 1: Herkesin bilgisayarında çalışsın

- `environment.yml` ile ortamı kur, README'deki adımları baştan sona dene.
- Model dosyaları (`checkpoints/*.pth`) ve Maxar görüntüleri V3 notlarına göre USB'deki `sunum_yedek.tar.gz` (367 MB) içinde. Bunları ikinizin de erişebileceği bir yere koyun (GitHub'a koymayın, dosyalar büyük).
- **Bitti sayılır eğer:** İkinizden ikinci kişi, sadece README'ye bakarak testleri ve `scripts.run_emsr`'yi çalıştırabiliyor.

## Adım 2: Deprem günündeki yol haritası

- Şu an harita bugünkü OpenStreetMap'ten iniyor. Hedef: 5 Şubat 2023 tarihli haritayı indirmek.
- Nasıl: OSMnx, Overpass ayarına `[date:"2023-02-05T00:00:00Z"]` eklenerek o tarihteki veriyi indirebiliyor (`ox.settings.overpass_settings`). Ayarın adı OSMnx sürümüne göre değişebilir, kendi sürümünüzde kontrol edin.
- Dikkat: Eski OSM, o günün gerçek haritası değil, OSM veritabanının o günkü hâlidir.
- **Bitti sayılır eğer:** `load_graph` bir `tarih` parametresi alıyor ve aynı bölge için bugünkü harita ile 2023 haritası arasındaki yol sayısı farkı raporlanabiliyor.

## Adım 3: Uzman hasar haritasını otomatik indir

- Copernicus API:
  - Liste: `https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations-info/`
  - Tek aktivasyon: `.../public-activations/?code=EMSR648`
  - Ürünler `downloadPath` (tek ürün ZIP) veya `productsPath` (hepsi tek ZIP) alanında.
- Şart: Veri ücretsiz ve paylaşılabilir; paylaşırken kaynak belirtmek zorunlu. Bazı veriler kayıt istiyor.
- Bu API bu sürümü hazırlarken denenemedi (ortam siteye bağlanamadı). İlk denemeyi kendi bilgisayarınızda yapın.
- **Bitti sayılır eğer:** `python -m scripts.fetch_emsr EMSR648` dosyaları `data/emsr648` içine indiriyor ve `python -m scripts.run_emsr AOI17` V3'teki sonucu veriyor (hasarsız 4270 m, R=25 m için 4522 m; `docs/arsiv_v3/TEZ_NOTLARI.md`).

## Adım 4: Fay hattı katmanı

- Veri: USGS, Reitman ve ark. 2023, DOI 10.5066/P985I7U2. Ayrıntılı katman: `surface_rupture_lines` (1:1.500 ölçek).
- Nasıl: Çizgileri oku, yol ağıyla aynı koordinat sistemine çevir, `close_edges_near(G, cizgiler, R=...)` ile yolları kapat. Bu fonksiyonun çizgiyle çalıştığı test T10 ile doğrulandı.
- **Bitti sayılır eğer:** Fay hattının kestiği yollar kapanıyor ve bunu gösteren bir test var.

## Adım 5: Sıvılaşma katmanı

- Eski kayıt (eski repo `docs/Kararlar.md`, K-22): Eşik 0,05'ten 0,10'a yükseltilmiş. Sebep: 0,05'te Türkoğlu'daki yolların %34,9'u (3700 yoldan 1292'si) "zor" işaretleniyordu ve bu fiziksel olarak savunulamaz bulunmuştu. Eski kayıtlarda "katman çıkarıldı" diye bir karar yok. V3'te bu katman hiç yoktu.
- Veri: USGS Ground Failure, Zhu 2017 modeli. Dosya Yusuf'un laptopunda var: `~/disaster-routing/data/zhu_2017_general_model.tif`. USGS bu değeri "pikselde sıvılaşan alanın yüzdesi" olarak veriyor.
- Nasıl: Yolu kapatmadan, sadece `delay_edges_near` ile gecikme ekleyin. Başlangıç eşiği 0,10 (eski K-22). Eşiği birkaç değerle deneyin.
- **Bitti sayılır eğer:** Seçilen eşik ve gecikme değeri gerekçesiyle yazılı ve kaç yolun etkilendiği raporlanıyor.

## Adım 6: Hasar modelini sahada çalışır hale getir

- V3'ün bulgusu: Model kendi veri setinde makul (Dice 0,45–0,49), ama gerçek Maxar görüntüsünde enkazsız 2022 görüntüsünde 84, enkazlı 11 Şubat görüntüsünde 69 tespit üretti.
- Yapılacaklar:
  1. EBD veri setiyle (Türkiye depremi, 944 görüntü çifti) yeniden eğitim.
  2. Eğitime enkazsız Maxar görüntüleri eklemek (etiketi tamamen boş). Test bölgesinin görüntüsü eğitime girmeyecek.
  3. Her modeli 3 farklı tohumla eğitmek: `python -m scripts.train --mode post --seed 1`, `2`, `3`.
  4. Gerçek negatif kontrol: Farklı tarihlerde çekilmiş iki enkazsız görüntü.
- **Bitti sayılır eğer:** Aynı ayarlarla, enkazsız görüntüdeki tespit sayısı enkazlı görüntüdekinden açıkça az. Bu, 3 tohumun hepsinde geçerli.

## Adım 7: "Emin değilim" bilgisi

- Kodda hazır olan: Model her piksel için bir olasılık veriyor. `georef.py` 0,5 eşiğini ve 0,8 "güçlü çekirdek" değerini kullanıyor.
- Yapılacak: Düşük olasılıklı bölgeler için "belirsiz" sınıfı eklemek. İki rota üretmek: en kısa ve en güvenli (belirsiz yollardan kaçan).
- **Bitti sayılır eğer:** Program iki rotayı ve aralarındaki uzunluk farkını veriyor ve bunun bir testi var.

## Adım 8: Web sayfasında harita arayüzü (PROJE BİTER)

- Haritada iki noktaya tıkla, rota çizilsin, kapalı/gecikmeli/belirsiz yollar renkli görünsün.
- **Bitti sayılır eğer:** Komut satırı bilmeyen biri sayfayı açıp rota alabiliyor.

---

## Proje bittikten sonra

- **Sahadan geri bildirim:** Sahadaki ekip bir yolu "kapalı/açık" diye işaretler, rota hemen güncellenir.
- **Otonom ikmal tırı (ayrı proje):** CARLA simülatörü (kod MIT, 3D modeller CC-BY). OSM haritası `carla.Osm2Odr` ile simülasyona çevrilebiliyor. CARLA 0.9.15'te sadece tırın çekici kısmı var, dorse yok. Simülasyon haritası rotanın çıktığı OSM bölgesinden üretilmeli.

## Şimdilik dışarıda (neden)

| Konu | Neden şimdilik yok |
|---|---|
| Yol yüzeyi hasarı modeli | İndirilebilir uydu yol hasarı veri seti bulunamadı (CAU-RoadDamage linki erişilemedi; diğer iki çalışmada veri paylaşılmamış). |
| Radar (SAR) görüntüsü | Erişilebilen Türkiye veri setinde (QuickQuakeBuildings) tek bir radar çekimi var. |
| Drone görüntüsü | Bu proje uydu görüntüsü üzerine kurulu. |
| Çok araç, çok hedef | Önce tek aracın rotası bitmeli. |

## Lisans hatırlatması

- Maxar açık verisi: CC BY-NC 4.0 (ticari kullanım yok).
- Copernicus EMS: ücretsiz, kaynak belirtmek zorunlu.
- OpenStreetMap: ODbL.
