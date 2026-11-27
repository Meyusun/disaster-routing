# Dosya haritası — Yusuf'un laptopu (Ubuntu 22.04)

Kaynak: Claude Code ile yapılan iki salt okuma taraması, 2026-11-27. Bir dosya taşınır ya da silinirse bu tablo güncellenmeli.
"İçi okunmadı" yazan satırlarda yorum dosya adına dayanıyor.

## V4'te kullanılacaklar

| Dosya / klasör | Yer | Boyut | Hangi adımda | Not |
|---|---|---|---|---|
| V4 projesi | `~/disaster-routing-v4` | — | Hepsi | Zip'ten kurulacak, sonra GitHub `v4` dalı |
| EMSR648 uzman hasar haritası (AOI04, AOI16, AOI17) | `~/disaster-routing/data/emsr648` | 31 MB | 1, 3 | V4'e `data/emsr648` olarak kopyalanır. Orijinal zip'ler: `~/Downloads/EMSR648_AOI*.zip` |
| Fay hattı (USGS Reitman 2023, v1.1) | `~/disaster-routing/data/surface_rupture_lines_v1.1_202402.geojson` | 1,2 MB | 4 | Orijinal zip: `~/Downloads/surface_rupture_lines_v1.1…zip` |
| Sıvılaşma (USGS Zhu 2017) | `~/disaster-routing/data/zhu_2017_general_model.tif` | 572 KB | 5 | Eski eşik kararı: K-22 (0,10) |
| Maxar görüntü kataloğu | `~/disaster-routing/data/maxar/Kahramanmaras-turkey-earthquake-23.geojson` | 3,4 MB | 6 | `scripts/maxar_*.py` aynı dosyayı internetten okuyor |
| Maxar indirme listesi | `~/disaster-routing/outputs/maxar_indirme_listesi.txt` | — | 6 | İçi okunmadı. Görüntüler hiç indirilmemiş (`data/maxar/img` boş) |
| Eski kararlar ve değişiklik günlüğü | `~/disaster-routing/docs/` (Kararlar.md, ChangeLog.md, ProjeContext.md, FAZ4_KULLANIM.md) | 88 KB | Başvuru | K-22: sıvılaşma eşiği |
| Eski fay ve sıvılaşma kodu | `~/disaster-routing/scripts/phase1_rupture_real.py`, `phase1_liquefaction1.py` | — | 4, 5 (örnek) | İçi okunmadı |

## Laptopta YOK, Kuzey'den alınacak

| Dosya | V4'teki yeri | Hangi adımda |
|---|---|---|
| 3 kanal model | `checkpoints/post_best.pth` | 1 (model testi), 6 |
| 6 kanal model | `checkpoints/best_model.pth` | 6 |
| 4 Maxar görüntüsü (2022-07-26, 2023-02-11, 2023-02-28, 2023-02-07 İslahiye) | `inputs/maxar_*.tif` | 6 |
| KATE-CD veri seti | `data/kate_cd` | 6 |

V3 notuna göre bunların hepsi (KATE-CD hariç) `sunum_yedek.tar.gz` (367 MB) içindeydi. Laptopta da USB'de de yok.

## V4'te kullanılmayanlar (silinmedi)

| Dosya / klasör | Yer | Boyut | Neden kullanılmıyor |
|---|---|---|---|
| xBD veri seti | `~/disaster-routing/data/xbd/train` | 8,1 GB | Eski Siamese yaklaşımına ait. V4 KATE-CD/EBD kullanıyor (K-1) |
| Eğitim parçaları | `~/disaster-routing/data/patches` | 1,4 GB | Aynı nedenle |
| Eski Siamese model | `~/disaster-routing/outputs/siamese_fold0.pt`, kopyası `~/model_yedek/siamese_fold0.pt` | 46 MB ×2 | Aynı nedenle |
| Eski yol ağları | `~/disaster-routing/data/*.graphml` (3 dosya) | 6,4 MB | V4 haritayı her seferinde OSM'den indiriyor |
| Eski hasar tabloları, etiketleme | `~/disaster-routing/data/damage`, `data/labeling` | 26 MB | Eski yaklaşım |

Disk 19 GB boş (%87 dolu). Yer gerekirse ilk aday xBD ve patches (toplam ~9,5 GB). Silmek bir karardır ve önce KARARLAR.md'ye yazılır.

## Projeyle ilgisi olmayanlar

AESK, ROS2, Autoware, AWSIM, YOLO ile ilgili klasörler (`~/autoware`, `~/ros2_ws`, `~/runs`, `~/yolo26n.pt` vb.) ve `~/Downloads` içindeki diğer zip'ler.

## İndirme yeri

Tarayıcı indirmeleri: `~/Downloads`. Masaüstü: `~/Desktop` (şu an boş).
