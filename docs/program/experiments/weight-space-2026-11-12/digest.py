import os, json, math, hashlib
import numpy as np
import torch
from transformers import GPTNeoForCausalLM

model = GPTNeoForCausalLM.from_pretrained("roneneldan/TinyStories-1M")
sd = model.state_dict()

def stats(A):
    A = A.numpy().astype(np.float64)
    if A.ndim < 2:
        return {"key": None, "shape": list(A.shape), "norm": float(np.linalg.norm(A)), "mean": float(A.mean()), "std": float(A.std())}
    flat = A.flatten()
    out = {
        "shape": list(A.shape),
        "norm": float(np.linalg.norm(A)),
        "fro_avg_square": float((A * A).mean()),
        "max|v|": float(np.max(np.abs(flat))),
        "min": float(flat.min()),
        "max": float(flat.max()),
        "mean": float(flat.mean()),
        "std": float(flat.std()),
        "cov_max": 0.0,
        "var_explained": 0.0,
    }
    if A.ndim == 2 and A.shape[0] != A.shape[1]:
        pass
    if A.shape[0] > A.shape[1]:
        cov = np.cov(A, bias=True)
        ev = np.sort(np.linalg.eigvalsh(cov))[::-1]
        out["var_explained"] = float(ev[0] / ev.sum()) if ev.sum() else 0.0
    return out

for k in list(sd):
    if ".attn." not in k and ".mlp." not in k:
        continue
    s = stats(sd[k])
    s["key"] = k
    print(json.dumps(s))
