import os, sys, json, re, torch
from transformers import AutoTokenizer, GPTNeoForCausalLM

device = "cpu"
model_name = "roneneldan/TinyStories-1M"
tok = AutoTokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name).eval()

def distinct_n(toks, n):
    if len(toks) < n: return 0.0
    return len(set(zip(*[toks[i:] for i in range(n)]))) / (len(toks) - n + 1)

def loop_measure(text):
    toks = re.findall(r"[A-Za-z']+", text.lower())
    counts = {}
    all_counts = {}
    for i, t in enumerate(toks):
        all_counts[t] = all_counts.get(t, 0) + 1
    pairs = {}
    for i in range(len(toks) - 1):
        p = (toks[i], toks[i + 1])
        pairs[p] = pairs.get(p, 0) + 1
    if not toks:
        return 0.0, 0.0, 0.0
    top1 = max(all_counts.values())
    top2 = max(pairs.values()) if pairs else 0
    d1 = len(set(toks)) / len(toks)
    print("top_token", top1, "top_bigram", top2, "distinct", round(d1, 3))
    return top1, top2, d1

prompts = open("probes.txt").read().splitlines()

for prompt in prompts:
    ids = tok.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=96, do_sample=False, pad_token_id=tok.eos_token_id)
    full = tok.decode(out[0], skip_special_tokens=True)
    toks = re.findall(r"[A-Za-z']+", full.lower())
    print(f"=== {prompt[:60]}")
    loop_measure(full)
