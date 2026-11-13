import os, sys, json, re, torch
from transformers import AutoTokenizer, GPTNeoForCausalLM

device = "cpu"
model_name = "roneneldan/TinyStories-1M"
tok = AutoTokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name).eval()
sd = model.state_dict()

# apply edit: row 30 of layer 6 q_proj scaled by 0.25
edit_key = "transformer.h.6.attn.attention.q_proj.weight"
w = sd[edit_key].clone()
w[30] = w[30] * 0.25
model.load_state_dict({"transformer.h.6.attn.attention.q_proj.weight": w}, strict=False)
sd2 = model.state_dict()
print("edited row norm:", sd2[edit_key][30].norm().item())
print("original row norm:", sd[edit_key][30].norm().item())

prompts = open("probes.txt").read().splitlines()
loop_set = {0, 5, 6, 9, 11, 12, 18, 20}
for i, prompt in enumerate(prompts):
    ids = tok.encode(prompt, return_tensors="pt")
    torch.manual_seed(i)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=96, do_sample=False, pad_token_id=tok.eos_token_id)
    text = repr(tok.decode(out[0], skip_special_tokens=True))
    toks = re.findall(r"[A-Za-z']+", text.lower())
    d2 = len(set(zip(toks, toks[1:]))) / max(1, len(toks) - 1)
    top1 = max(Counter(toks).values()) if False else None
    print(f"[{i:02}] d2={d2:.2f} | {prompt[:55]}")
    print("       ", text[:90])
