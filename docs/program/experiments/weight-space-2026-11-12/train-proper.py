import numpy as np, json, math
L = 20.0

def phi(s):
    x, y, vx, vy = s
    return np.array([np.cos(math.pi * x / L), np.sin(math.pi * x / L),
                     np.cos(math.pi * y / L), np.sin(math.pi * y / L),
                     vx / L, vy / L], dtype=np.float32)

class Organism:
    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        self.w1 = (rng.standard_normal((48, 6)).astype(np.float32) * 0.1)
        self.b1 = np.zeros(48, dtype=np.float32)
        self.w2 = (rng.standard_normal((2, 48)).astype(np.float32) * 0.1)
        self.b2 = np.zeros(2, dtype=np.float32)

    def forward(self, s):
        f = phi(np.asarray(s, dtype=np.float32))
        h = np.tanh(self.w1 @ f + self.b1)
        return np.tanh(self.w2 @ h + self.b2).astype(np.float32)

def rollout(org, steps=40, seed=7):
    rng = np.random.default_rng(seed)
    pos = np.array([5.0, 5.0], dtype=np.float32)
    vel = np.zeros(2, dtype=np.float32)
    total_ang = 0.0
    prev_ang = math.atan2(pos[1] - 10, pos[0] - 10)
    for t in range(steps):
        u = org.forward([pos[0], pos[1], vel[0], vel[1]])
        vel = np.array([vel[0] * 0.9 + 0.35 * u[0], vel[1] * 0.9 + 0.35 * u[1]], dtype=np.float32)
        pos = (pos + vel) % L
        ang = math.atan2(pos[1] - 10, pos[0] - 10)
        d = (ang - prev_ang) % (2 * math.pi)
        if d > math.pi:
            d -= 2 * math.pi
        total_ang += d
        prev_ang = ang
    return total_ang

def score(org, n=20):
    return np.mean([rollout(org, steps=40, seed=1000 + i) for i in range(n)])

org = Organism(20261212)
best = score(org)
print("init:", best)
for g in range(40):
    candidates = []
    for k in range(12):
        temp = Organism(0)
        for key, t in org.__dict__.items():
            if isinstance(t, np.ndarray):
                noise = np.random.standard_normal(t.shape).astype(np.float32) * 0.05
                temp.__dict__[key] = t + noise
        candidates.append((score(temp), temp))
    candidates.sort(key=lambda c: -c[0])
    top = candidates[0]
    print(f"gen {g}: best {top[0]:.4f} commits={'Y' if top[0] > best else 'n'}")
    if top[0] > best:
        org = top[1]
        best = top[0]
# Dump weights
print("FINAL:", score(org))
with open("organism-final.txt", "w") as f:
    for k in ("w1", "b1", "w2", "b2"):
        arr = org.__dict__[k]
        f.write(f"# {k} shape {arr.shape} norm {np.linalg.norm(arr):.4f}\n")
        for i, row in enumerate(arr.reshape(arr.shape[0], -1)):
            f.write(" ".join(f"{v:.5f}" for v in row) + "\n")
