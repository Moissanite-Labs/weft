import os, sys, json, re, torch, copy
from transformers import AutoTokenizer, GPTNeoForCausalLM
import torch.nn as nn

scale = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
layers = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [2, 6, 3]
prompts = open("probes.txt").read().splitlines()
loop_tokens = [0, 1, 6, 7, 9, 10, 13, 16, 18, 20]  # indices of loop prompts in 0..23, careful ordering: by file order
PROBE_INDEX = {
    "Sara found a little box under a tree": 0,
    "The sun is in the sky": 5,
    "Tommy had a ball and he": 6,
    "A big dog ran into": 9,
    "Mom baked a cake for": 11,
    "The frog lived in the": 12,
    "A bunny hopped across": 18,
    "Mommy made breakfast": 20,
}
LOOP_SET = set(PROBE_INDEX.values())

device = "cpu"
model_name = "roneneldan/TinyStories-1M"
tok = AutoTokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name).eval()

sd = model.state_dict()
sd_edit = {k: v.clone() for k, v in sd.items()}
print(f"scale={scale} layers={layers}")
for li in layers:
    key = f"transformer.h.{li}.attn.attention.q_proj.weight"
    sd_edit[key] = sd_edit[key] * scale
model.load_state_dict(sd_edit, strict=False)

GREEDY = True
distinct_tokens = []
loop_hits = 0
for idx, prompt in enumerate(prompts):
    ids = tok.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=96, do_sample=False, pad_token_id=tok.eos_token_id)
    text = tok.decode(out[0], skip_special_tokens=True)
    toks = re.findall(r"[A-Za-z']+", text.lower())
    d2 = (len(set(zip(toks, toks[1:])))) / max(1, len(toks) - 1)
    counts = {}
    top1 = 0
    for t in toks:
        counts[t] = counts.get(t, 0) + 1
        top1 = max(top1, counts[t])
    pairs = {}
    for i in range(len(toks) - 1):
        p = (toks[i], toks[i + 1])
        pairs[p] = pairs.get(p, 0) + 1
    top2 = max(pairs.values()) if pairs else 0
    if idx in LOOP_SET and top2 >= 6 and d2 < 0.42:
        loop_hits += 1
    distinct_tokens.append(d2)
tot = len(LOOP_SET)
print("avg_distinct_2", sum(distinct_tokens) / len(distinct_tokens))
print("loop_score", loop_hits / tot)
