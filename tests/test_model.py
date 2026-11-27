"""Model karolama testi (V3: T6). KATE-CD verisi, checkpoints/post_best.pth ve PyTorch gerekir; yoksa atlanir."""
import pytest
from pathlib import Path
torch = pytest.importorskip("torch")
KOK = Path(__file__).resolve().parents[1]

@pytest.mark.skipif(not (KOK / "checkpoints" / "post_best.pth").exists() or not (KOK / "data" / "kate_cd").exists(),
                    reason="model dosyasi veya KATE-CD verisi yok")
def test_T6_karolama():
    import numpy as np
    from dr.data import KATECDDataset
    from dr.infer import load_model, predict_prob

    ds = KATECDDataset("test", mode="post").dataset
    labels = [np.array(s["label"]) > 127 for s in ds]
    idx = sorted(range(len(ds)), key=lambda i: -labels[i].sum())[:4]
    imgs = [np.array(ds[i]["post_image"]) for i in idx]
    labs = [labels[i] for i in idx]
    mozaik = np.vstack([np.hstack(imgs[:2]), np.hstack(imgs[2:])])
    mlab = np.vstack([np.hstack(labs[:2]), np.hstack(labs[2:])])

    model = load_model()
    dice = lambda p, y: 2 * (p & y).sum() / (p.sum() + y.sum() + 1e-6)
    ayri = [predict_prob(model, im) for im in imgs]
    ayri = np.vstack([np.hstack(ayri[:2]), np.hstack(ayri[2:])])
    tum = predict_prob(model, mozaik)
    assert tum.shape == mlab.shape and tum.min() >= 0 and tum.max() <= 1
    d1, d2 = dice(ayri > 0.5, mlab), dice(tum > 0.5, mlab)
    print("T6 karolama | ayri:", round(d1, 4), "| mozaik:", round(d2, 4), "| fark:", round(abs(d1 - d2), 4))
    assert abs(d1 - d2) < 0.05, "Karolama sonucu ayri tahminlerden cok farkli"
    print("T6 GECTI")
