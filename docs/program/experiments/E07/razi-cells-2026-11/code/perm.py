"""E5 permutation test: does model label explain code-vector clustering?
usage: EMBED_MODEL=.. perm.py A:run1,run2 B:run3,run4"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from embed import load, cos_dist, centroid
groups = {a.split(":")[0]: a.split(":")[1].split(",") for a in sys.argv[1:]}
(ga, ra), (gb, rb) = groups.items()
needs = sorted({p.name for r in ra + rb for p in Path(r).iterdir() if (p / "variants.jsonl").exists()})
rng = random.Random(0); N = 2000; tot = []
for n in needs:
    A = [x["vec"] for r in ra if (Path(r)/n/"variants.jsonl").exists() for x in load(Path(r)/n)]
    B = [x["vec"] for r in rb if (Path(r)/n/"variants.jsonl").exists() for x in load(Path(r)/n)]
    if len(A) < 2 or len(B) < 2: print(f"  {n:9s} skip (A{len(A)} B{len(B)})"); continue
    stat = lambda a, b: cos_dist(centroid(a), centroid(b))
    obs = stat(A, B); allv = A + B; k = len(A); ge = 0
    for _ in range(N):
        rng.shuffle(allv); ge += stat(allv[:k], allv[k:]) >= obs
    p = (ge + 1) / (N + 1); tot.append(p)
    print(f"  {n:9s} A{len(A):2d} B{len(B):2d} gap={obs:.4f} p={p:.4f}")
print(f"needs p<0.05: {sum(p<0.05 for p in tot)}/{len(tot)}")
