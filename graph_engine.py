"""
Supply Chain Graph Engine
- Build directed weighted graph (plant → warehouse → demand)
- Shortest path (Dijkstra)
- Max-flow analysis
- Disruption simulation & resilience scoring
"""

import networkx as nx
from dataclasses import dataclass, field
from typing import Optional
import json


# ─────────────────────────────────────────────
# Data models
# ─────────────────────────────────────────────

@dataclass
class Node:
    id: str
    name: str
    node_type: str          # "plant" | "warehouse" | "demand"
    capacity: float         # supply capacity (plants) or storage (warehouses) or demand qty
    location: str = ""
    x: float = 0.0         # layout position hint
    y: float = 0.0

@dataclass
class Edge:
    source: str
    target: str
    capacity: float         # max units that can flow on this link
    cost: float = 1.0       # transport cost per unit (used for shortest path weight)
    active: bool = True     # False = simulated disruption


# ─────────────────────────────────────────────
# Supply Chain Graph
# ─────────────────────────────────────────────

class SupplyChainGraph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    # ── Build ──────────────────────────────────

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError(f"Node {edge.source} or {edge.target} not found")
        # prevent duplicates
        for e in self.edges:
            if e.source == edge.source and e.target == edge.target:
                return
        self.edges.append(edge)

    def remove_edge(self, source: str, target: str):
        self.edges = [e for e in self.edges
                      if not (e.source == source and e.target == target)]

    def toggle_edge(self, source: str, target: str, active: bool):
        for e in self.edges:
            if e.source == source and e.target == target:
                e.active = active

    def reset_disruptions(self):
        for e in self.edges:
            e.active = True

    # ── NetworkX graph (active edges only) ────

    def to_nx(self, include_inactive: bool = False) -> nx.DiGraph:
        G = nx.DiGraph()
        for nid, n in self.nodes.items():
            G.add_node(nid, **vars(n))
        for e in self.edges:
            if include_inactive or e.active:
                G.add_edge(e.source, e.target,
                           capacity=e.capacity,
                           cost=e.cost,
                           weight=e.cost,
                           active=e.active)
        return G

    # ── Shortest path ─────────────────────────

    def shortest_path(self, source: str, target: str) -> dict:
        """
        Returns shortest path (by cost) between two nodes.
        Uses Dijkstra on active edges only.
        """
        G = self.to_nx()
        try:
            path = nx.dijkstra_path(G, source, target, weight="weight")
            length = nx.dijkstra_path_length(G, source, target, weight="weight")
            return {"found": True, "path": path, "cost": round(length, 2)}
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {"found": False, "path": [], "cost": None}

    def all_shortest_paths(self, source: str, target: str, k: int = 3) -> list[dict]:
        """Returns up to k shortest simple paths (by cost)."""
        G = self.to_nx()
        results = []
        try:
            for path in nx.shortest_simple_paths(G, source, target, weight="weight"):
                cost = sum(G[path[i]][path[i+1]]["weight"] for i in range(len(path)-1))
                results.append({"path": path, "cost": round(cost, 2)})
                if len(results) >= k:
                    break
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            pass
        return results

    # ── Max flow ──────────────────────────────

    def max_flow(self, source: str, target: str) -> dict:
        """
        Computes maximum flow from source to target across active edges.
        """
        G = self.to_nx()
        try:
            flow_value, flow_dict = nx.maximum_flow(G, source, target, capacity="capacity")
            return {"flow": round(flow_value, 2), "flow_dict": flow_dict}
        except (nx.NetworkXError, nx.NodeNotFound, nx.NetworkXUnbounded):
            return {"flow": 0, "flow_dict": {}}

    # ── Resilience analysis ───────────────────

    def demand_fulfillment(self) -> dict[str, dict]:
        """
        For each demand node, compute what fraction of its required demand
        can actually be fulfilled (using max-flow from all plant sources).
        Returns dict: demand_id → {required, fulfilled, pct, reachable_from}
        """
        G = self.to_nx()
        plants   = [n for n, d in self.nodes.items() if d.node_type == "plant"]
        demands  = [n for n, d in self.nodes.items() if d.node_type == "demand"]

        results = {}
        for d_id in demands:
            demand_node = self.nodes[d_id]
            required = demand_node.capacity
            total_flow = 0.0
            reachable_from = []

            for p_id in plants:
                try:
                    fv, _ = nx.maximum_flow(G, p_id, d_id, capacity="capacity")
                    if fv > 0:
                        total_flow += fv
                        reachable_from.append(p_id)
                except Exception:
                    pass

            fulfilled = min(total_flow, required)
            pct = (fulfilled / required * 100) if required > 0 else 100.0
            results[d_id] = {
                "required": required,
                "fulfilled": round(fulfilled, 2),
                "pct": round(pct, 1),
                "reachable_from": reachable_from,
            }
        return results

    # ── Disruption simulation ─────────────────

    def simulate_disruption(self, remove_source: str, remove_target: str) -> dict:
        """
        Temporarily remove one edge, compare before/after metrics.
        Returns a full disruption impact report.
        """
        # ── Baseline ──
        baseline = self.demand_fulfillment()

        # ── Apply disruption ──
        self.toggle_edge(remove_source, remove_target, active=False)
        disrupted = self.demand_fulfillment()

        # ── Restore ──
        self.toggle_edge(remove_source, remove_target, active=True)

        # ── Compute impact per demand node ──
        impact = {}
        for d_id, base in baseline.items():
            dis = disrupted[d_id]
            drop = base["pct"] - dis["pct"]
            impact[d_id] = {
                "demand_name": self.nodes[d_id].name,
                "before_pct": base["pct"],
                "after_pct": dis["pct"],
                "drop_pct": round(drop, 1),
                "before_fulfilled": base["fulfilled"],
                "after_fulfilled": dis["fulfilled"],
                "lost_units": round(base["fulfilled"] - dis["fulfilled"], 2),
                "severity": (
                    "critical" if drop >= 50 else
                    "high"     if drop >= 25 else
                    "medium"   if drop > 0  else
                    "none"
                ),
            }

        # ── Alternate paths for each affected demand node ──
        alt_paths = {}
        for d_id, imp in impact.items():
            if imp["drop_pct"] > 0:
                # find a plant that can still reach this demand
                self.toggle_edge(remove_source, remove_target, active=False)
                paths = []
                plants = [n for n, node in self.nodes.items() if node.node_type == "plant"]
                for p_id in plants:
                    result = self.shortest_path(p_id, d_id)
                    if result["found"]:
                        paths.append({
                            "from_plant": self.nodes[p_id].name,
                            "path": [self.nodes[n].name for n in result["path"]],
                            "cost": result["cost"],
                        })
                paths.sort(key=lambda x: x["cost"])
                alt_paths[d_id] = paths[:3]
                self.toggle_edge(remove_source, remove_target, active=True)

        # ── Overall resilience score (0-100) ──
        if impact:
            avg_drop = sum(v["drop_pct"] for v in impact.values()) / len(impact)
            resilience_score = round(max(0, 100 - avg_drop), 1)
        else:
            resilience_score = 100.0

        return {
            "removed_edge": f"{self.nodes[remove_source].name} → {self.nodes[remove_target].name}",
            "resilience_score": resilience_score,
            "impact": impact,
            "alt_paths": alt_paths,
        }

    def rank_critical_edges(self) -> list[dict]:
        """
        Stress-test ALL edges: remove each one, compute avg fulfillment drop.
        Returns edges ranked from most critical to least critical.
        """
        ranking = []
        for edge in self.edges:
            if not edge.active:
                continue
            result = self.simulate_disruption(edge.source, edge.target)
            avg_drop = 0.0
            if result["impact"]:
                avg_drop = sum(v["drop_pct"] for v in result["impact"].values()) / len(result["impact"])
            ranking.append({
                "source": edge.source,
                "target": edge.target,
                "label": result["removed_edge"],
                "avg_fulfillment_drop": round(avg_drop, 1),
                "resilience_score": result["resilience_score"],
                "severity": (
                    "critical" if avg_drop >= 50 else
                    "high"     if avg_drop >= 25 else
                    "medium"   if avg_drop >= 5  else
                    "low"
                ),
            })
        ranking.sort(key=lambda x: x["avg_fulfillment_drop"], reverse=True)
        return ranking

    # ── Save / Load ───────────────────────────

    def to_dict(self) -> dict:
        return {
            "nodes": [vars(n) for n in self.nodes.values()],
            "edges": [vars(e) for e in self.edges],
        }

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "SupplyChainGraph":
        with open(path) as f:
            data = json.load(f)
        sc = cls()
        for nd in data["nodes"]:
            sc.add_node(Node(**nd))
        for ed in data["edges"]:
            sc.add_edge(Edge(**ed))
        return sc
