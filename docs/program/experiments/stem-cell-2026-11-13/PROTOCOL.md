# Astra stem-cell controller pilot: registration

This exploratory pilot tests whether Astra can differentiate a persistent numeric controller for two demand regimes. Registration precedes paid teacher calls. It follows earlier public studies, but uses new seeds and episodes. The representation is a hand-initialized six-integer controller genome, not pretrained neural weights or a biological stem cell.

| Item | Fixed specification |
| --- | --- |
| Source seeds | 171, 293 |
| Demands | quiet and urgent |
| Generations | Two per seed/demand |
| Teacher opportunities | Eight total, each returning exactly four typed child genomes |
| Teacher | gpt-6-astra, standard tier, no explicit reasoning-effort parameter, storage off |
| Output cap | 6,000 tokens per call |
| API budget | At most $5 of conservative rate reservations, not an invoice or account-balance claim. No automatic retries. |
| Episode splits | Train: 4 × 12 steps. Validation: 4 × 12. Test: 8 × 16. |
| Split seeds | Source seed +1000, +2000 and +3000 respectively |
| Initial position | x = 3 |
| Input process | Integer target in [-2, 8]. At each third step, target changes with probability 0.75. Urgency is independently true with probability 0.5. |
| Paired intervention | Both demands share targets, urgency and initial state. Only error/action cost weights differ. |
| Cost weights | Quiet: error 1, action 8. Urgent: error 4, action 1. |

## Genome and transition

The root genome is gain_num=1, gain_den=1, deadband=0, bias=0, cap_low=2, cap_high=2. Allowed integer ranges are gain_num [0,4], gain_den [1,4], deadband [0,3], bias [-2,2], and each cap [0,2]. A child may only tighten its actual parent's caps. No code, executable operators or proof text may be supplied.

The fixed controller computes e=target−x+bias. Within the deadband, action k=0. Otherwise k is sign(e) times floor(gain_num×abs(e)/gain_den), clamped by the low/high cap according to urgency. The new position is x+k. Cost is error_weight×(target−x_after)² + action_weight×k².

The exact readout is [x,4−x,5]. Each step has delta [k,−k,0], frozen coordinate 2, anchors [1,1,0] and [0,0,1], and squared delta norm at most 8. The proof gate checks concrete trajectories, action/cost arithmetic and registered constraints.

Lifecycle certificates also check stable winner selection and the bounded root-preserving allocation from their exact supplied records. Record construction, input binding, persistence and execution remain host responsibilities. Host execution, file storage, compiler installation and physical-world interpretation remain outside the theorem.

## Selection, feedback and controls

Choose the valid child with lowest validation total integer cost only when strictly better than the unchanged parent. A tie with the parent retains it. Child ties use earliest submitted order. Keep invalid responses, duplicate proposals, rejected children and unchanged selections. The selected genome persists into generation two.

The teacher receives training episodes, current parent genome, parent training/validation costs and previous validation feedback. It receives no held-out episodes or scores. The four generation-one requests are committed before calls.

Generation-two requests are deterministically constructed from the frozen procedure and observed generation-one feedback, then archived before submission. Their concrete bytes do not exist at initial registration.

Each teacher opportunity has four deterministic random valid children from that same actual teacher parent, with identical validation selection. Their seeds are source_seed×100000 + branch_index×1000 + generation×10 + child_index, using quiet=0, urgent=1 and indices 0..3.

This is a marginal one-generation comparator, not an independent cumulative random lineage. It matches candidate evaluations, rather than teacher computation or information.

Also report the unchanged parent, original root, and fixed hand controller gain=1/2, deadband=1, bias=0, caps=1/2. Candidate and comparator training/validation evaluations pass the proof gate. Final held-out evaluations and actual colony dispatch are checked separately. A successful mathematical gate does not establish lower task cost.

## Colony and resource rules

Always reserve one immutable root stem. Up to three differentiated copies may be allocated to positive validation cost reductions versus the root. Initially give one copy to each qualifying demand, then give remaining slots to the greatest benefit, with quiet winning a tie. Total cells never exceed four.

Report the actual selected genomes, copy counts and dispatched episodes. Copy count alone does not establish a throughput or intelligence gain.

Use exact Python integer arithmetic and Lean on CPU, with at most two local proof-evaluation workers. Under a normal memory observation use two, under pressure or unknown status use one, and at critical status pause. The captured macOS free-percentage thresholds are <=25% for one worker and <=10% for pause.

These resource rules govern local proof workers, not the separate HTTP worker, which has its own reservation and call limits. Resource fixtures are diagnostic checks and are labeled separately from actual hardware observations. No GPU or MLX benefit is claimed.

## Final measurement and interpretation

After all eight opportunities are processed, lock selection hashes before examining held-out outcomes. Evaluate each selected lineage on both demand regimes, alongside the declared controls. Report integer total cost, tracking-error sum, movement sum, selected-genome differences, allocation and all failed or unchanged cases.

Two source seeds support a small exploratory comparison, without a population-significance claim.

The questions are whether teacher proposals reduce held-out cost beyond the root and declared controls, whether quiet/urgent selection yields useful differentiated behavior, and whether the registered proof/lifecycle/resource constraints hold. Report these separately. A no-op or unchanged lineage remains an outcome. Do not tune the protocol against the held-out results.

Each lineage keeps its assigned demand weights for both generations. Crossover evaluation tests the final controller under the other demand, without a subsequent adaptation or recovery phase. This pilot therefore does not measure recovery after a demand reversal.

Allocated identical copies also do not establish a throughput gain. analyze_results.py computes descriptive reports after selection, without changing selection or making model calls.

## Capture

Preserve exact input HTML sources, source analysis, code/configuration, episode data, original and transmitted requests, observable responses, token usage, reservations/errors, every candidate and gate decision, selected genomes, parent/child identities, proof source/compiler logs, selection lock, held-out/dispatch traces and resource observations.

Credentials, Authorization headers and internal model reasoning are excluded. The final manifest records exact artifact hashes.

The HTMLs are visual inspiration rather than experimental evidence. SOURCE-NOTES.md identifies the statistical toy update and the morphology page's hardcoded return table. HARDWARE.md records the actual CPU environment and the limited implications of Apple unified memory.
