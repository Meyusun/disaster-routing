"""
Faz 3 — Adim 3: SIAMESE CNN egitimi.

MIMARI:
  pre  --\
          [paylasimli ResNet18 govde] --> f_pre  \
  post --/                                        --> [f_pre, f_post, |f_pre-f_post|] --> sinif
                                        f_post   /

  "Siamese" = iki kol AYNI agirliklari paylasir. Boylece model iki goruntuyu
  ayni sekilde temsil eder, ve fark anlamli olur. Farki (|f_pre - f_post|)
  ozellige eklemek CVA'nin fikrini ozellik uzayinda tekrarliyor — ama bu sefer
  ham pikselde degil, ogrenilmis temsilde.

DEGERLENDIRME (K-08): recall oncelikli. CVA baseline referansi:
  recall 0.72 @ precision 0.20  (taban oran 0.142'nin 1.44 kati)

SIZINTISIZLIK (K-06): VAL_FOLD spatial CV blok bolmesinden geliyor.

Calistirma:
    cd ~/disaster-routing
    conda activate disaster
    python scripts/phase3_train_siamese.py
"""

import os
import time

import numpy as np
import torch
import torch.nn as nn
import torchvision
from torch.utils.data import DataLoader, Dataset

# ---------------------------------------------------------------------------
# Ayarlar
# ---------------------------------------------------------------------------
NPZ = "data/patches/patches.npz"
VAL_FOLD = 0            # spatial CV fold'u — degistirerek capraz dogrulama yapilir
EPOCHS = 12
BATCH = 64
LR = 3e-4
POS_WEIGHT = 2.0        # hasarli sinifa agirlik — recall'i yukseltir (K-08)
SEED = 42

OUT_CKPT = "outputs/siamese_fold0.pt"
OUT_PRED = "outputs/siamese_fold0_preds.npz"

IMNET_MEAN = np.array([0.485, 0.456, 0.406], dtype="float32")
IMNET_STD = np.array([0.229, 0.224, 0.225], dtype="float32")


# ---------------------------------------------------------------------------
# Veri seti
# ---------------------------------------------------------------------------
class PatchDS(Dataset):
    """
    Pre/post yama cifti + etiket.
    ONEMLI: artirma (augmentation) her iki goruntuye AYNI uygulanir —
    pre ve post uzamsal olarak hizali, bozarsak fark anlamsizlasir.
    """

    def __init__(self, pre, post, y, train):
        self.pre, self.post, self.y, self.train = pre, post, y, train

    def __len__(self):
        return len(self.y)

    def _norm(self, img):
        x = img.astype("float32") / 255.0
        x = (x - IMNET_MEAN) / IMNET_STD
        return torch.from_numpy(x.transpose(2, 0, 1))

    def __getitem__(self, i):
        a, b = self.pre[i], self.post[i]
        if self.train:
            if np.random.rand() < 0.5:            # yatay cevir
                a, b = a[:, ::-1], b[:, ::-1]
            if np.random.rand() < 0.5:            # dikey cevir
                a, b = a[::-1], b[::-1]
            k = np.random.randint(4)              # 90 derece dondur
            if k:
                a, b = np.rot90(a, k), np.rot90(b, k)
            a, b = np.ascontiguousarray(a), np.ascontiguousarray(b)
        return self._norm(a), self._norm(b), torch.tensor(float(self.y[i]))


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
class Siamese(nn.Module):
    def __init__(self):
        super().__init__()
        w = torchvision.models.ResNet18_Weights.IMAGENET1K_V1
        net = torchvision.models.resnet18(weights=w)
        net.fc = nn.Identity()          # 512-boyutlu ozellik cikar
        self.backbone = net             # PAYLASIMLI govde — ayni agirliklar
        self.head = nn.Sequential(
            nn.Linear(512 * 3, 256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 1),
        )

    def forward(self, pre, post):
        f1 = self.backbone(pre)
        f2 = self.backbone(post)
        z = torch.cat([f1, f2, (f1 - f2).abs()], dim=1)
        return self.head(z).squeeze(1)


# ---------------------------------------------------------------------------
# Degerlendirme
# ---------------------------------------------------------------------------
@torch.no_grad()
def predict(model, loader, dev):
    model.eval()
    probs, ys = [], []
    for a, b, y in loader:
        p = torch.sigmoid(model(a.to(dev), b.to(dev)))
        probs.append(p.cpu().numpy())
        ys.append(y.numpy())
    return np.concatenate(probs), np.concatenate(ys)


def report(probs, y, title):
    print(f"\n{title}")
    print("  esik   recall  precision      F1   tahmin_hasarli")
    print("  " + "-" * 52)
    best = None
    for thr in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        pred = probs >= thr
        tp = int((pred & (y == 1)).sum())
        fp = int((pred & (y == 0)).sum())
        fn = int((~pred & (y == 1)).sum())
        rec = tp / max(tp + fn, 1)
        prec = tp / max(tp + fp, 1)
        f1 = 2 * rec * prec / max(rec + prec, 1e-9)
        print(f"  {thr:5.2f}  {rec:6.3f}  {prec:9.3f}  {f1:6.3f}   {int(pred.sum()):6d}")
        if best is None or f1 > best[3]:
            best = (thr, rec, prec, f1)

    # CVA baseline ile karsilastirma: recall ~0.72 noktasinda precision ne?
    order = np.argsort(-probs)
    ys = y[order]
    cum_tp = np.cumsum(ys == 1)
    total_pos = max(int((y == 1).sum()), 1)
    rec_curve = cum_tp / total_pos
    idx = np.searchsorted(rec_curve, 0.72)
    if idx < len(ys):
        prec_at = cum_tp[idx] / (idx + 1)
        print(f"\n  >> recall 0.72 noktasinda precision: {prec_at:.3f}")
        print(f"     CVA baseline ayni noktada       : 0.204")
        print(f"     kazanc: {prec_at/0.204:.2f}x")
    return best


# ---------------------------------------------------------------------------
def main():
    os.makedirs("outputs", exist_ok=True)
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[cihaz] {dev}")
    if dev == "cpu":
        print("[UYARI] GPU bulunamadi — egitim cok yavas olacak.")

    print(f"[veri] {NPZ} yukleniyor...")
    d = np.load(NPZ)
    pre, post, y, fold = d["pre"], d["post"], d["y"], d["fold"]
    print(f"[veri] {len(y)} yama, hasarli %{100*y.mean():.1f}")

    va = fold == VAL_FOLD
    tr = ~va
    print(f"[bolme] egitim {int(tr.sum())} | dogrulama {int(va.sum())} "
          f"(fold {VAL_FOLD}, spatial CV)")
    print(f"[bolme] hasarli oran — egitim %{100*y[tr].mean():.1f}, "
          f"dogrulama %{100*y[va].mean():.1f}")

    ds_tr = PatchDS(pre[tr], post[tr], y[tr], train=True)
    ds_va = PatchDS(pre[va], post[va], y[va], train=False)
    dl_tr = DataLoader(ds_tr, batch_size=BATCH, shuffle=True,
                       num_workers=4, pin_memory=True, drop_last=True)
    dl_va = DataLoader(ds_va, batch_size=BATCH * 2, shuffle=False,
                       num_workers=4, pin_memory=True)

    model = Siamese().to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)
    lossf = nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor(POS_WEIGHT, device=dev))
    scaler = torch.amp.GradScaler(dev) if dev == "cuda" else None

    print(f"\n[egitim] {EPOCHS} epoch basliyor...")
    for ep in range(1, EPOCHS + 1):
        model.train()
        t0, tot, n = time.time(), 0.0, 0
        for a, b, yy in dl_tr:
            a, b, yy = a.to(dev, non_blocking=True), b.to(dev, non_blocking=True), yy.to(dev)
            opt.zero_grad(set_to_none=True)
            if scaler:
                with torch.amp.autocast("cuda"):
                    loss = lossf(model(a, b), yy)
                scaler.scale(loss).backward()
                scaler.step(opt)
                scaler.update()
            else:
                loss = lossf(model(a, b), yy)
                loss.backward()
                opt.step()
            tot += loss.item() * len(yy)
            n += len(yy)
        sched.step()

        probs, yv = predict(model, dl_va, dev)
        pred = probs >= 0.5
        tp = int((pred & (yv == 1)).sum())
        fn = int((~pred & (yv == 1)).sum())
        fp = int((pred & (yv == 0)).sum())
        rec = tp / max(tp + fn, 1)
        prec = tp / max(tp + fp, 1)
        print(f"  epoch {ep:2d}/{EPOCHS}  loss {tot/n:.4f}  "
              f"val recall {rec:.3f}  precision {prec:.3f}  ({time.time()-t0:.0f}s)")

    probs, yv = predict(model, dl_va, dev)
    report(probs, yv, f"### SONUC — fold {VAL_FOLD} (spatial CV, gorulmemis bloklar)")

    torch.save(model.state_dict(), OUT_CKPT)
    np.savez(OUT_PRED, probs=probs, y=yv)
    print(f"\n[kaydet] {OUT_CKPT}")
    print(f"[kaydet] {OUT_PRED}")


if __name__ == "__main__":
    main()