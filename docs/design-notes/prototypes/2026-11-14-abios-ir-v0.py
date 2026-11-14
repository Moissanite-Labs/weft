# Reference-only prototype. Captured 2026-11-14 from the owner's session.
# NOT shipped. NOT weft/runtime code. Graded Hoare State-Transition Calculus
# sketch over abios s-expressions: typed causal steps gated by a small
# "kernel" that enforces budget, VMEM and Weft radius gates. Preserved
# verbatim as captured. See docs/design-notes/2026-11-14-causal-ir-v0.md
# for the audit, failures, and status. Do not import this from weft/runtime.

from dataclasses import dataclass
import hashlib
from typing import Literal

SourceTag = Literal["measured", "derived", "empirical_prior"]


@dataclass(frozen=True)
class Metric:
  val: float
  tag: SourceTag


@dataclass(frozen=True)
class SysState:
  vmem_kb: Metric  # On-chip SRAM/VMEM footprint
  vmem_cap_kb: float  # Hard physical SRAM ceiling
  stall_pct: Metric  # Hardware PMU memory stall %
  w_dist: Metric  # ||W' - W0||_F distance from baseline
  radius_r: float  # Weft invariant radius R
  budget: float  # Remaining compute/energy budget


@dataclass(frozen=True)
class CausalStep:
  action: str  # Formal intervention: do(param=val)
  target_var: str  # Causal child variable affected
  new_metric: Metric  # Resulting value + epistemic tag
  cost: float  # Resource cost (> 0)
  rationale_law: str  # Formal invariant / structural rule invoked


def kernel_check_step(state: SysState, step: CausalStep) -> SysState:
  """Trusted Small Kernel: Rejects invalid causal transitions before rendering."""
  if step.cost <= 0 or state.budget < step.cost:
    raise ValueError(
        f"Budget gate failed: cost={step.cost}, rem={state.budget}"
    )

  # Apply transition strictly to declared causal target (no hidden side-effects)
  updates = {
      "vmem_kb": state.vmem_kb,
      "stall_pct": state.stall_pct,
      "w_dist": state.w_dist,
  }
  if step.target_var not in updates:
    raise ValueError(f"Unknown state target: {step.target_var}")
  updates[step.target_var] = step.new_metric

  next_state = SysState(
      vmem_kb=updates["vmem_kb"],
      vmem_cap_kb=state.vmem_cap_kb,
      stall_pct=updates["stall_pct"],
      w_dist=updates["w_dist"],
      radius_r=state.radius_r,
      budget=round(state.budget - step.cost, 4),
  )

  # Enforce hard physical & Weft safety invariants at every step
  if next_state.vmem_kb.val > next_state.vmem_cap_kb:
    raise ValueError(
        f"Hardware SRAM overflow: {next_state.vmem_kb.val} >"
        f" {next_state.vmem_cap_kb}"
    )
  if next_state.w_dist.val > next_state.radius_r:
    raise ValueError(
        f"Weft radius breached: ||W'-W0||={next_state.w_dist.val} >"
        f" {next_state.radius_r}"
    )

  return next_state


def delaborate(
    init: SysState,
    plan: list[CausalStep],
    mode: Literal["consumer", "researcher"],
) -> str:
  """Externalized 'Tokenizer': Deterministically renders verified IR to human views."""
  curr = init
  trace = []
  for i, step in enumerate(plan, 1):
    nxt = kernel_check_step(curr, step)
    trace.append((i, curr, step, nxt))
    curr = nxt

  # Cryptographic commitment over the raw causal derivation
  ir_repr = repr((init, plan)).encode()
  digest = hashlib.sha256(ir_repr).hexdigest()[:12]

  if mode == "consumer":
    actions = ", then ".join(s.action for _, _, s, _ in trace)
    return (
        f"Applied {actions}. Memory stalls dropped from {init.stall_pct.val}% "
        f"to {curr.stall_pct.val}% while staying safely within memory "
        f"({curr.vmem_kb.val}/{curr.vmem_cap_kb} KB) and safety bounds "
        f"[verified:{digest}]."
    )

  # Researcher View: Exposes full causal DAG, epistemic tags, and gate margins
  lines = [
      f"=== VERIFIED CAUSAL TRACE [abios-ir sha256:{digest}] ===",
      (
          f"S0: stall={init.stall_pct.val}%({init.stall_pct.tag}), "
          f"vmem={init.vmem_kb.val}/{init.vmem_cap_kb}KB,"
          f" ||dW||={init.w_dist.val}/{init.radius_r}, B={init.budget}"
      ),
  ]
  for idx, prev, s, nxt in trace:
    lines.append(
        f"Step {idx}: do({s.action}) --[{s.rationale_law} | cost={s.cost}]--> "
        f"{s.target_var}={s.new_metric.val} ({s.new_metric.tag}) | "
        f"Gates: VMEM_OK({nxt.vmem_kb.val}<={nxt.vmem_cap_kb}), "
        f"WEFT_OK({nxt.w_dist.val}<={nxt.radius_r}), B_rem={nxt.budget}"
    )
  return "\n".join(lines)


if __name__ == "__main__":
  s0 = SysState(
      vmem_kb=Metric(48.0, "measured"),
      vmem_cap_kb=128.0,
      stall_pct=Metric(62.4, "measured"),
      w_dist=Metric(0.0, "measured"),
      radius_r=3.0,
      budget=10.0,
  )
  # Model emits ONLY these typed AST transitions (no English prose)
  model_ast = [
      CausalStep(
          "tile_m=128,stages=3",
          "vmem_kb",
          Metric(112.0, "derived"),
          cost=1.5,
          rationale_law="sram_footprint = stages * tile_bytes",
      ),
      CausalStep(
          "pipeline_dma_prefetch",
          "stall_pct",
          Metric(18.5, "empirical_prior"),
          cost=2.0,
          rationale_law="overlap_hbm_latency(stages=3)",
      ),
      CausalStep(
          "project_lora_null_k0",
          "w_dist",
          Metric(1.42, "derived"),
          cost=1.0,
          rationale_law="frobenius_norm(dW @ P_null) <= R",
      ),
  ]
  print(delaborate(s0, model_ast, mode="consumer"), "\n")
  print(delaborate(s0, model_ast, mode="researcher"))
