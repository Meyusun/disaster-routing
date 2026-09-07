"""
Faz 3 — Adim 4: LEAVE-ONE-DISASTER-OUT genelleme testi.

NEDEN: Blok bazli spatial CV "yeni mahallede calisir mi" sorusunu olcer.
Ama iddiamiz "yeni BOLGEDE, yeni AFETTE calisir mi". Bunu olcmek icin
bir afetin TAMAMINI disarida birakip digerlerinde egitiyoruz.

Bu ayni zamanda KISAYOL TESTI:
  - Model gercekten "cokmus cati / moloz dokusu" mu ogrendi?
  - Yoksa "Palu'nun goruntu karakteri" ya da "puslu = hasarli" mi?
Kisayol ogrendiyse, o afet disarida birakildiginda skor coker.

K-05'in de sinavi: kasirga/yangin verisinden ogrenilen, depreme transfer
oluyor mu?

Calistirma:
    cd ~/disaster-routing
    conda activate disaster
    python scripts/phase3_leave_disaster_out.py
"""

import os
import time

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from phase3_train_siamese import PatchDS, Siamese, predict

# ---------------------------------------------------------------------------
NPZ = "data/patches/patches.npz"
EPOCHS = 8              # 12'de asiri ogrenme gorulmustu
BATCH = 64
LR = 3e-4
POS_WEIGHT = 2.0
SEED = 42

# Disarida birakilacak afetler. Bos birakirsan HEPSI denenir (uzun surer).
# Deprem-benzeri olaylar oncelikli: proje senaryosuna en yakin sinav.
HOLDOUT = ["palu-tsunami", "mexico-earthquake",
           "hurricane-michael", "santa-rosa-wildfire"]

OUT = "outputs/leave_disaster_out.csv"


def metrics_at(probs, y, target_recall=0.72):
    """Sabit recall noktasinda precision — CVA ile ayni olcek."""
    order = np.argsort(-probs)
    ys = y[order]
    cum_tp = np.cumsum(ys == 1)
    total_pos = max(int((y == 1).sum()), 1)
    rec = cum_tp / total_pos
    idx = int(np.searchsorted(rec, target_recall))
    if idx >= len(ys):
        return float("nan")
    return cum_tp[idx] / (idx + 1)


def run_one(pre, post, y, dis, holdout, dev):
    va = dis == holdout
    tr = ~va
    if va.sum() == 0 or y[va].sum() == 0:
        print(f"[atla] {holdout}: dogrulama bos ya da hic hasarli yok")
        return None

    print(f"\n{'='*62}\n### DISARIDA: {holdout}")
    print(f"  egitim {int(tr.sum())} yama (%{100*y[tr].mean():.1f} hasarli) | "
          f"test {int(va.sum())} yama (%{100*y[va].mean():.1f} hasarli)")
    print(f"  egitimdeki afetler: {sorted(set(dis[tr]))}")

    dl_tr = DataLoader(PatchDS(pre[tr], post[tr], y[tr], train=True),
                       batch_size=BATCH, shuffle=True, num_workers=4,
                       pin_memory=True, drop_last=True)
    dl_va = DataLoader(PatchDS(pre[va], post[va], y[va], train=False),
                       batch_size=BATCH * 2, shuffle=False, num_workers=4,
                       pin_memory=True)

    torch.manual_seed(SEED)
    model = Siamese().to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)
    lossf = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(POS_WEIGHT, device=dev))
    scaler = torch.amp.GradScaler(dev) if dev == "cuda" else None

    for ep in range(1, EPOCHS + 1):
        model.train()
        t0 = time.time()
        for a, b, yy in dl_tr:
            a, b, yy = a.to(dev, non_blocking=True), b.to(dev, non_blocking=True), yy.to(dev)
            opt.zero_grad(set_to_none=True)
            if scaler:
                with torch.amp.autocast("cuda"):
                    loss = lossf(model(a, b), yy)
                scaler.scale(loss).backward()
                scaler.step(opt); scaler.update()
            else:
                loss = lossf(model(a, b), yy); loss.backward(); opt.step()
        sched.step()
        if ep == EPOCHS or ep % 4 == 0:
            probs, yv = predict(model, dl_va, dev)
            pred = probs >= 0.5
            tp = int((pred & (yv == 1)).sum()); fn = int((~pred & (yv == 1)).sum())
            fp = int((pred & (yv == 0)).sum())
            print(f"    epoch {ep}: recall {tp/max(tp+fn,1):.3f} "
                  f"precision {tp/max(tp+fp,1):.3f}  ({time.time()-t0:.0f}s/ep)")

    probs, yv = predict(model, dl_va, dev)
    base = float(yv.mean())               # taban oran (rastgele tahmin)
    p72 = metrics_at(probs, yv, 0.72)
    pred = probs >= 0.5
    tp = int((pred & (yv == 1)).sum()); fn = int((~pred & (yv == 1)).sum())
    fp = int((pred & (yv == 0)).sum())
    rec50 = tp / max(tp + fn, 1); prec50 = tp / max(tp + fp, 1)

    print(f"\n  SONUC — {holdout} (hic gorulmemis afet)")
    print(f"    esik 0.5     : recall {rec50:.3f}  precision {prec50:.3f}")
    print(f"    recall 0.72  : precision {p72:.3f}")
    print(f"    taban oran   : {base:.3f}   -> kazanc {p72/max(base,1e-9):.2f}x")
    return {"holdout": holdout, "n_test": int(va.sum()), "taban": base,
            "recall50": rec50, "precision50": prec50, "prec_at_r72": p72,
            "kazanc": p72 / max(base, 1e-9)}


def main():
    os.makedirs("outputs", exist_ok=True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[cihaz] {dev}")

    d = np.load(NPZ)
    pre, post, y, dis = d["pre"], d["post"], d["y"], d["disaster"]
    print(f"[veri] {len(y)} yama, {len(set(dis))} afet")

    targets = HOLDOUT or sorted(set(dis.tolist()))
    rows = [r for r in (run_one(pre, post, y, dis, h, dev) for h in targets)
            if r is not None]

    print(f"\n{'='*62}\n### OZET — leave-one-disaster-out")
    print(f"{'afet':22s} {'taban':>7s} {'r@0.5':>7s} {'p@0.5':>7s} "
          f"{'p@r72':>7s} {'kazanc':>7s}")
    print("-" * 62)
    for r in rows:
        print(f"{r['holdout']:22s} {r['taban']:7.3f} {r['recall50']:7.3f} "
              f"{r['precision50']:7.3f} {r['prec_at_r72']:7.3f} {r['kazanc']:6.2f}x")

    print("\nKarsilastirma icin:")
    print("  blok bazli spatial CV (fold 0) : p@r72 = 0.933")
    print("  CVA baseline                    : p@r72 = 0.204")

    import csv
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\n[kaydet] {OUT}")


if __name__ == "__main__":
    main()