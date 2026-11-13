#!/usr/bin/env python3
"""Behavioral audit of TinyStories-1M on the fixed 60-prompt battery.

Usage:
  python3 audit.py [--model REPOSHA] [--n-samples N] [--seed SEED] [--out OUT]

Metrics:
  distinct-2, distinct-4
  loop-burst flag (largest n-gram window with repeat ratio >= 0.5 over >= 20 consecutive occurrences)
  loop_n: smallest n whose consecutive repeat dominates the tail
"""
import argparse, json, math, re, statistics, sys, time
from collections import Counter
import torch

PROMPTS = [
    "A little dog named Max wanted to",
    "Sara found a little box under a tree",
    "Tim had a bright red ball in his",
    "Lily liked to draw pictures of",
    "A small cat climbed to the top of",
    "Emma and Noah went to the beach with",
    "A little car named Benny the yellow",
    "Mom told a story about the day they",
    "Zoe saw a small bird outside her",
    "A curious boy named Eli opened the",
    "Sofia wanted to buy a big bag of",
    "A little girl named Mia played with",
    "A rabbit lived in a hole at the bottom of",
    "Ben lost his favorite toy in the",
    "Anna's red kite got stuck in the",
    "One day a little duck named Dash",
    "The sun was shining and the little boy",
    "A small brown dog ran away from",
    "A boy named Jake found a magical",
    "Mom was baking cookies and little",
    "A puppy named Buddy liked to",
    "Lilly wanted to go to the big park",
    "A quiet cat lived in a tall house",
    "Sam looked up at the sky and saw",
    "A little red wagon pulled a heavy",
    "A bird named Kiki flew high over",
    "The little girl loved to sing and",
    "An old man lived in a tiny",
    "A baby elephant wanted to",
    "A frog jumped into the",
    "A tiny bear found a",
    "Tommy helped his mom make",
    "In the garden there was a",
    "A little yellow bird",
    "The moon came out and the",
    "A small rabbit hopped",
    "Sam had a",
    "The rain fell and the",
    "Molly found an",
    "Noah and his dog named",
    "A little girl with a",
    "A boy and a girl sat on",
    "A puppy chased a",
    "Mom said they could go to",
    "A little kite flew",
    "The trees grew tall",
    "A small duck waddled",
    "In the deep forest",
    "An old cat named",
    "A small boy wore a",
    "A windy day and",
    "A little girl sang",
    "A duckling was",
    "A frog hopped",
    "A boy found a",
    "The small dog slept",
    "A bird flew over",
    "A quiet girl sat",
    "A short story about",
    "My name is",
]
assert len(PROMPTS) == 60

def count_repeats(tokens, n):
    grams = [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]
    return Counter(grams)

def distinct_n(tokens, n):
    if len(tokens) < n:
        return 0.0
    return len(set(zip(*[tokens[i:] for i in range(n)]))) / (len(tokens) - n + 1)

def loop_burst(tokens):
    """Return smallest n >= 1 with consecutive repeat dominance."""
    for n in (1, 2, 3, 4, 5, 6):
        grams = [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]
        c = Counter(grams)
        if not grams:
            continue
        top, cnt = c.most_common(1)[0]
        frac = cnt / len(grams)
        if cnt >= 8 and frac >= 0.22:
            return n, frac
    return None, 0.0

def distinct_n_grams(text):
    """token-independent r-gram distinctness over word tokens"""
    toks = re.findall(r"[A-Za-z']+", text.lower())
    return {
        "distinct_1": len(set(toks)) / max(1, len(toks)),
        "distinct_2": len(set(zip(toks, toks[1:]))) / max(1, len(toks) - 1),
        "distinct_4": len(set(zip(toks, toks[1:], toks[2:], toks[3:]))) / max(1, len(toks) - 3),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="roneneldan/TinyStories-1M")
    ap.add_argument("--n-samples", type=int, default=1)
    ap.add_argument("--seed", type=int, default=20261112)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--max-new", type=int, default=96)
    ap.add_argument("--out", default="audit-out")
    ap.add_argument("--zero-blocks", type=str, default="")   # e.g. "0,3,7"
    ap.add_argument("--greedy", action="store_true")
    ns = ap.parse_args()

    from transformers import AutoTokenizer, GPTNeoForCausalLM
    torch.manual_seed(ns.seed)
    tok = AutoTokenizer.from_pretrained(ns.model)
    model = GPTNeoForCausalLM.from_pretrained(ns.model, low_cpu_mem_usage=True)
    if ns.zero_blocks:
        targets = [int(x) for x in ns.zero_blocks.split(",") if x]
        for i in targets:
            for mod in model.transformer.h[i].modules():
                if isinstance(mod, torch.nn.Linear):
                    with torch.no_grad():
                        mod.weight.zero_()
                        if mod.bias is not None:
                            mod.bias.zero_()
    model.eval()
    if ns.device != "cpu":
        model = model.to(ns.device)

    results = []
    loops = 0
    for idx, prompt in enumerate(PROMPTS):
        ids = tok.encode(prompt, return_tensors="pt")
        if ns.device != "cpu":
            ids = ids.to(ns.device)
        total_new = 0
        text_parts = []
        n_loops_per_prompt = 0
        for _ in range(ns.n_samples):
            torch.manual_seed(ns.seed + idx)
            with torch.no_grad():
                if ns.greedy:
                    out = model.generate(ids, max_new_tokens=ns.max_new,
                                         do_sample=False,
                                         pad_token_id=tok.eos_token_id)
                else:
                    out = model.generate(ids, max_new_tokens=ns.max_new,
                                         do_sample=True, temperature=0.8, top_p=0.95,
                                         pad_token_id=tok.eos_token_id)
            full = tok.decode(out[0], skip_special_tokens=True)
            text_parts.append(full)
        for full in text_parts:
            toks = re.findall(r"[A-Za-z']+", full.lower())
            n, frac = loop_burst(toks)
            d = distinct_n_grams(full)
            rec = {"idx": idx, "prompt": prompt, "text": full, "loop_n": n,
                   "loop_frac": frac, **d,
                   "tokens": len(toks)}
            results.append(rec)
            if n is not None:
                loops += 1
    loops_id = []
    for r in results:
        looks = "loop" if r["loop_n"] else "ok"
        loops_id.append(f"{looks:5}")  # quick verdict
        print(f"[{r['idx']:02}] {looks:5} loop_n={r['loop_n']} frac={r['loop_frac']:.2f} distinct_2={r['distinct_2']:.2f} | {PROMPTS[r['idx']][:40]}")
    print(f"loops={loops}/{len(results)}  distinct_2={statistics.mean(r['distinct_2'] for r in results):.3f}")
    import json as js
    with open(ns.out + ".json", "w") as f:
        js.dump(results, f, indent=1)

if __name__ == "__main__":
    main()
