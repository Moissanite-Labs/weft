#!/usr/bin/env python3
"""Purpose-built sandbox: can Astra write a working weight-space edit?

Tiny 4 => hidden 16 => 2 classifier. Task so simple we know correct answer analytically:
predict 1 iff first feature > 0.3.

Procedure:
  1. Train the toy network offline to >= 95% accuracy.
  2. Dump weights to a JSON summary.
  3. Ask astra to write code that flips the label output (i.e., makes the network output
     the opposite prediction for every input), via direct weight editing - NO retraining allowed.
  4. Apply astra's proposed code, verify.
"""
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

torch.manual_seed(20261112)

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(4, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 2)

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))

model = MLP()
optimizer = optim.Adam(model.parameters(), lr=1e-2)
criterion = nn.CrossEntropyLoss()

data = []
for _ in range(256):
    x = np.random.randn(4).astype(np.float32) * 0.5
    y = 1 if x[0] > 0.3 else 0
    data.append((x, y))

x_t = torch.tensor(np.stack([d[0] for d in data]))
y_t = torch.tensor(np.array([d[1] for d in data], dtype=np.int64))

model.eval()
with torch.no_grad():
    preds = model(x_t).argmin(dim=1)
    wrongs = (preds != y_t).sum().item()
print(f"pre-train accuracy {(len(data)-wrongs)/len(data):.2f}")

model.train()
for epoch in range(600):
    optimizer.zero_grad()
    out = model(x_t)
    loss = criterion(out, y_t)
    loss.backward()
    optimizer.step()

model.eval()
with torch.no_grad():
    preds = model(x_t).argmin(dim=1)
    acc = (preds == y_t).float().mean().item()
print(f"post-train accuracy {acc:.2f}")

sd = {k: v.detach().cpu().numpy().tolist() for k, v in model.state_dict().items()}
torch.save(model.state_dict(), "toy-classifier.pt")
with open("toy-classifier.json", "w") as f:
    json.dump({k: {"shape": list(np.array(v).shape)} for k, v in sd.items()}, f, indent=1)
print("saved toy-classifier.pt and toy-classifier.json")
