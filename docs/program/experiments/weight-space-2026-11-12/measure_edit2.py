import os, sys, json, re, torch
from collections import Counter
from transformers import AutoTokenizer, GPTNeoForCausalLM

def measure(model, tok, prompts, loop_set):
    rows = []
    for i, prompt in enumerate(prompts):
        ids = tok.encode(prompt, return_tensors="pt")
        torch.manual_seed(i)
        with torch.no_grad():
            out = model.generate(ids, max_new_tokens=96, do_sample=False, pad_token_id=tok.eos_token_id)
        text = tok.decode(out[0], skip_special_tokens=True)
        toks = re.findall(r"[A-Za-z']+", text.lower())
        d2 = len(set(zip(toks, toks[1:]))) / max(1, len(toks) - 1)
        pairs = list(zip(toks, toks[1:]))
        top2 = max(Counter(pairs).values()) if pairs else 0
        rows.append((i, prompt, d2, top2, text))
    return rows

model_name = "roneneldan/TinyStories-1M"
tok = AutoTokenizer.from_pretrained(model_name)
before = GPTNeoForCausalLM.from_pretrained(model_name).eval()
sd = before.state_dict()
orig = sd["transformer.h.6.attn.attention.q_proj.weight"].clone()
print("orig row norm:", orig[30].norm().item())
                              
# edit: row 30 * 0.25
sd_edit = {k: v.clone() for k, v in sd.items()}
sd_edit["transformer.h.6.attn.attention.q_proj.weight"][30] *= 0.25
after = GPTNeoForCausalLM.from_pretrained(model_name).eval()
after.load_state_dict(sd_edit, strict=False)
print("edited row norm:", after.transformer.h[6].attn.attention.q_proj.weight[30].norm().item())

prompts = open("probes.txt").read().splitlines()
loop_set = {0, 5, 6, 9, 11, 12, 18, 20}
print("\n=== BEFORE ===")
r_before = measure(before, tok, prompts, loop_set)
for i, r in enumerate(r_before):
    if i in loop_set:
        print(f"[{i:02}] BEFORE d2={r[2]:.2f} top2={r[3]:2d} | {r[1][:55]}")
print("\n=== AFTER ===")
r_after = measure(after, tok, prompts, loop_set)
print("loop d2:", [(i, round(r[2], 2)) for i, r in enumerate(r_after) if i in loop_set])
print("non-loop d2:", [(i, round(r[2], 2)) for i, r in enumerate(r_after) if i not in loop_set])
