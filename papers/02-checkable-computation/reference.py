"""A small reference semantics for interaction combinators, used as an oracle.

Paper 2 compares the C3 reducer (weft/runtime/ic) against this model. It is
deliberately simple and written independently of the VM:

* A net is a set of agents. Each agent has a kind, a label, and ports
  0 (principal) .. arity. ERA has arity 0; CON, DUP and SUP have arity 2.
* A wire joins exactly two ports. Ports are (agent, index) pairs, so a wire
  always knows which port of its neighbour it reaches. That is the
  information the VM's node-indexed ports do not store.
* An active pair is two agents whose principal ports are wired together.
* Rules follow Lafont (1997), with the VM's labelled DUP/SUP extension:
  - same kind and label (CON-CON, DUP-DUP, SUP-SUP), or DUP-SUP with equal
    labels: annihilate, joining aux port i of one to aux port i of the other;
  - ERA-ERA: both vanish;
  - ERA with a binary agent: two new ERAs take the binary agent's aux ports;
  - otherwise: commute. Two copies of each agent are made, crossing over.

Rewrites go through `_rewire`, which contracts paths through removed ports, so
loops and wires between the two agents of the pair are handled uniformly.
"""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field

ERA, CON, DUP, SUP = 0, 1, 2, 5
ARITY = {ERA: 0, CON: 2, DUP: 2, SUP: 2}
NAMES = {ERA: "ERA", CON: "CON", DUP: "DUP", SUP: "SUP"}


@dataclass
class Net:
    kind: dict = field(default_factory=dict)    # agent -> kind
    label: dict = field(default_factory=dict)   # agent -> label
    wire: dict = field(default_factory=dict)    # (agent, port) -> (agent, port)
    _next: int = 0

    # -- construction ----------------------------------------------------
    def add(self, kind: int, label: int = 0) -> int:
        a = self._next
        self._next += 1
        self.kind[a] = kind
        self.label[a] = label
        return a

    def link(self, p, q) -> None:
        if p == q:
            raise ValueError("a port cannot be wired to itself")
        self.wire[p] = q
        self.wire[q] = p

    def ports(self, a: int):
        return [(a, i) for i in range(ARITY[self.kind[a]] + 1)]

    def copy(self) -> "Net":
        return Net(dict(self.kind), dict(self.label), dict(self.wire), self._next)

    # -- validity ---------------------------------------------------------
    def check(self) -> None:
        """Raise if the net is not a closed, well-formed port graph."""
        all_ports = {p for a in self.kind for p in self.ports(a)}
        if set(self.wire) != all_ports:
            raise ValueError("every port must be wired exactly once (closed net)")
        for p, q in self.wire.items():
            if self.wire.get(q) != p or p == q:
                raise ValueError(f"wire {p}->{q} is not reciprocal")

    def active_pairs(self) -> list[tuple[int, int]]:
        out = []
        for a in sorted(self.kind):
            b, i = self.wire[(a, 0)]
            if i == 0 and a < b:
                out.append((a, b))
        return out

    # -- rewriting --------------------------------------------------------
    def _rewire(self, removed: set, through: list) -> None:
        """Remove `removed` ports; `through` lists port pairs joined by the rule.

        Every removed port has its old wire plus at most one through-link.
        Following those links from each surviving port reaches either another
        surviving port (the new wire) or loops back into removed ports only.
        """
        nxt = {}
        for p, q in through:
            nxt.setdefault(p, []).append(q)
            nxt.setdefault(q, []).append(p)
        old = dict(self.wire)
        for p in removed:
            self.wire.pop(p, None)
        new_wires = {}
        visited_start = set()
        starts = [p for p in old if p not in removed and old[p] in removed] + \
                 [p for p, _ in through if p not in removed] + [q for _, q in through if q not in removed]
        for s in dict.fromkeys(starts):
            if s in visited_start:
                continue
            # Walk: from s take its old wire (if it pointed into removed) or its through link.
            cur = s
            prev = None
            # First hop: a surviving original port uses its old wire; a new port uses its through link.
            if s in old and old[s] in removed:
                step = old[s]
                via = "wire"
            else:
                step = nxt[s][0]
                via = "through"
            prev, cur = s, step
            while cur in removed:
                if via == "wire":
                    choices = [q for q in nxt.get(cur, []) if q != prev] or nxt.get(cur, [])
                    if not choices:
                        raise ValueError(f"dangling removed port {cur}")
                    prev, cur, via = cur, choices[0], "through"
                else:
                    prev, cur, via = cur, old[cur], "wire"
            new_wires[s] = cur
            visited_start.add(s)
            visited_start.add(cur)
        for p, q in new_wires.items():
            self.wire[p] = q
            self.wire[q] = p

    def reduce(self, a: int, b: int) -> str:
        if self.wire.get((a, 0)) != (b, 0):
            raise ValueError("not an active pair")
        ka, kb, la, lb = self.kind[a], self.kind[b], self.label[a], self.label[b]
        removed = set(self.ports(a)) | set(self.ports(b))
        through = []
        if ka == ERA and kb == ERA:
            op = "ERA_ERA"
        elif ka == ERA or kb == ERA:
            x = b if ka == ERA else a
            for i in (1, 2):
                e = self.add(ERA)
                through.append(((x, i), (e, 0)))
            op = "ERASE"
        elif (ka == kb and la == lb) or ({ka, kb} == {DUP, SUP} and la == lb):
            through = [((a, 1), (b, 1)), ((a, 2), (b, 2))]
            op = "ANNIHILATE"
        else:
            a1, a2 = self.add(kb, lb), self.add(kb, lb)
            b1, b2 = self.add(ka, la), self.add(ka, la)
            through = [((a, 1), (a1, 0)), ((a, 2), (a2, 0)), ((b, 1), (b1, 0)), ((b, 2), (b2, 0))]
            # Internal cross wires between the copies.
            self.link((a1, 1), (b1, 1))
            self.link((a1, 2), (b2, 1))
            self.link((a2, 1), (b1, 2))
            self.link((a2, 2), (b2, 2))
            op = "COMMUTE"
        # The principal wire a.0-b.0 vanishes with the pair.
        self._rewire(removed, [t for t in through])
        for x in (a, b):
            del self.kind[x]
            del self.label[x]
        return op


def random_closed_net(rng: random.Random, n_agents: int, simple: bool, labels: int = 2,
                      kinds=(CON, DUP, ERA), weights=(4, 4, 1), max_tries: int = 500) -> Net:
    """A random closed net with at least one active pair.

    `simple=True` rejects nets with a self-loop on one agent or two wires
    between the same pair of agents, the cases the VM's representation cannot
    tell apart.
    """
    for _ in range(max_tries):
        net = Net()
        for _ in range(n_agents):
            k = rng.choices(kinds, weights)[0]
            net.add(k, rng.randrange(labels) if k in (DUP, SUP) else 0)
        ports = [p for a in net.kind for p in net.ports(a)]
        if len(ports) % 2:
            net.add(ERA)
            ports.append((net._next - 1, 0))
        rng.shuffle(ports)
        for p, q in zip(ports[::2], ports[1::2]):
            net.link(p, q)
        if not net.active_pairs():
            continue
        if simple and not is_simple(net):
            continue
        net.check()
        return net
    raise RuntimeError("could not generate a net with the requested properties")


def is_simple(net: Net) -> bool:
    seen = set()
    for p, q in net.wire.items():
        if p[0] == q[0]:
            return False
        if p < q:
            key = (min(p[0], q[0]), max(p[0], q[0]))
            if key in seen:
                return False
            seen.add(key)
    return True


def to_nx(net: Net):
    """Port-expanded graph for isomorphism checks (agents and ports are nodes)."""
    import networkx as nx

    g = nx.Graph()
    for a, k in net.kind.items():
        g.add_node(("A", a), t=f"{NAMES[k]}:{net.label[a]}")
        for i in range(ARITY[k] + 1):
            g.add_node(("P", a, i), t=f"port{i}")
            g.add_edge(("A", a), ("P", a, i))
    for (a, i), (b, j) in net.wire.items():
        if (a, i) < (b, j):
            g.add_edge(("P", a, i), ("P", b, j))
    return g


def isomorphism(n1: Net, n2: Net):
    """Agent mapping n1 -> n2 if the nets are isomorphic, else None."""
    from networkx.algorithms.isomorphism import GraphMatcher

    g1, g2 = to_nx(n1), to_nx(n2)
    if g1.number_of_nodes() != g2.number_of_nodes() or g1.number_of_edges() != g2.number_of_edges():
        return None
    gm = GraphMatcher(g1, g2, node_match=lambda x, y: x["t"] == y["t"])
    if not gm.is_isomorphic():
        return None
    return {k[1]: v[1] for k, v in gm.mapping.items() if k[0] == "A"}


def canonical_key(net: Net) -> str:
    """Isomorphism-invariant fingerprint (Weisfeiler-Lehman hash) for grouping."""
    import networkx as nx

    return nx.weisfeiler_lehman_graph_hash(to_nx(net), node_attr="t", iterations=4)


__all__ = ["Net", "ERA", "CON", "DUP", "SUP", "NAMES", "ARITY", "random_closed_net", "is_simple", "isomorphism", "canonical_key", "itertools"]
