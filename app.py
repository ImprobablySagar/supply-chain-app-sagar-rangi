"""
Supply Chain Resilience Dashboard — Single File Version
Run with: streamlit run app.py
"""

# ═══════════════════════════════════════════════════════
# PART 1 — GRAPH ENGINE (algorithms)
# ═══════════════════════════════════════════════════════

import networkx as nx
from dataclasses import dataclass
from typing import Optional
import json
import math
import streamlit as st
import pandas as pd
import plotly.graph_objects as go


@dataclass
class Node:
    id: str
    name: str
    node_type: str
    capacity: float
    location: str = ""
    x: float = 0.0
    y: float = 0.0


@dataclass
class Edge:
    source: str
    target: str
    capacity: float
    cost: float = 1.0
    active: bool = True


class SupplyChainGraph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError(f"Node {edge.source} or {edge.target} not found")
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

    def shortest_path(self, source: str, target: str) -> dict:
        G = self.to_nx()
        try:
            path = nx.dijkstra_path(G, source, target, weight="weight")
            length = nx.dijkstra_path_length(G, source, target, weight="weight")
            return {"found": True, "path": path, "cost": round(length, 2)}
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {"found": False, "path": [], "cost": None}

    def all_shortest_paths(self, source: str, target: str, k: int = 3) -> list:
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

    def max_flow(self, source: str, target: str) -> dict:
        G = self.to_nx()
        try:
            flow_value, flow_dict = nx.maximum_flow(G, source, target, capacity="capacity")
            return {"flow": round(flow_value, 2), "flow_dict": flow_dict}
        except Exception:
            return {"flow": 0, "flow_dict": {}}

    def demand_fulfillment(self) -> dict:
        G = self.to_nx()
        plants  = [n for n, d in self.nodes.items() if d.node_type == "plant"]
        demands = [n for n, d in self.nodes.items() if d.node_type == "demand"]
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

    def simulate_disruption(self, remove_source: str, remove_target: str) -> dict:
        baseline = self.demand_fulfillment()
        self.toggle_edge(remove_source, remove_target, active=False)
        disrupted = self.demand_fulfillment()
        self.toggle_edge(remove_source, remove_target, active=True)

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

        alt_paths = {}
        for d_id, imp in impact.items():
            if imp["drop_pct"] > 0:
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

    def rank_critical_edges(self) -> list:
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


# ═══════════════════════════════════════════════════════
# PART 2 — SAMPLE DATA
# ═══════════════════════════════════════════════════════

def load_demo_data() -> SupplyChainGraph:
    sc = SupplyChainGraph()
    sc.add_node(Node("P1", "Plant Mumbai",   "plant", capacity=500, location="Mumbai, India"))
    sc.add_node(Node("P2", "Plant Chennai",  "plant", capacity=400, location="Chennai, India"))
    sc.add_node(Node("P3", "Plant Pune",     "plant", capacity=350, location="Pune, India"))
    sc.add_node(Node("W1", "WH North",   "warehouse", capacity=400, location="Delhi, India"))
    sc.add_node(Node("W2", "WH West",    "warehouse", capacity=350, location="Ahmedabad, India"))
    sc.add_node(Node("W3", "WH East",    "warehouse", capacity=300, location="Kolkata, India"))
    sc.add_node(Node("W4", "WH South",   "warehouse", capacity=280, location="Bangalore, India"))
    sc.add_node(Node("D1", "Delhi Market",     "demand", capacity=200, location="Delhi, India"))
    sc.add_node(Node("D2", "Jaipur Market",    "demand", capacity=120, location="Jaipur, India"))
    sc.add_node(Node("D3", "Surat Market",     "demand", capacity=180, location="Surat, India"))
    sc.add_node(Node("D4", "Bhubaneswar Mkt",  "demand", capacity=100, location="Bhubaneswar, India"))
    sc.add_node(Node("D5", "Hyderabad Market", "demand", capacity=160, location="Hyderabad, India"))
    sc.add_node(Node("D6", "Kochi Market",     "demand", capacity=140, location="Kochi, India"))
    sc.add_edge(Edge("P1", "W1", capacity=300, cost=2.0))
    sc.add_edge(Edge("P1", "W2", capacity=250, cost=1.5))
    sc.add_edge(Edge("P2", "W3", capacity=200, cost=1.8))
    sc.add_edge(Edge("P2", "W4", capacity=220, cost=2.2))
    sc.add_edge(Edge("P3", "W2", capacity=180, cost=1.2))
    sc.add_edge(Edge("P3", "W4", capacity=200, cost=1.6))
    sc.add_edge(Edge("P1", "W3", capacity=150, cost=3.0))
    sc.add_edge(Edge("P2", "W1", capacity=100, cost=3.5))
    sc.add_edge(Edge("W1", "D1", capacity=220, cost=1.0))
    sc.add_edge(Edge("W1", "D2", capacity=150, cost=1.5))
    sc.add_edge(Edge("W2", "D2", capacity=130, cost=1.2))
    sc.add_edge(Edge("W2", "D3", capacity=200, cost=1.0))
    sc.add_edge(Edge("W3", "D4", capacity=120, cost=1.0))
    sc.add_edge(Edge("W3", "D5", capacity=130, cost=1.8))
    sc.add_edge(Edge("W4", "D5", capacity=180, cost=1.0))
    sc.add_edge(Edge("W4", "D6", capacity=160, cost=1.2))
    sc.add_edge(Edge("W1", "D4", capacity=80,  cost=2.5))
    sc.add_edge(Edge("W2", "D6", capacity=90,  cost=2.0))
    return sc


# ═══════════════════════════════════════════════════════
# PART 3 — VISUALIZER
# ═══════════════════════════════════════════════════════

NODE_COLORS  = {"plant": "#0F6E56", "warehouse": "#185FA5", "demand": "#993C1D"}
NODE_SYMBOLS = {"plant": "square",  "warehouse": "diamond", "demand": "circle"}
SEVERITY_COLORS = {
    "critical": "#E24B4A", "high": "#EF9F27",
    "medium": "#378ADD",   "low":  "#1D9E75", "none": "#888780",
}


def _auto_layout(sc: SupplyChainGraph) -> dict:
    layers = {"plant": [], "warehouse": [], "demand": []}
    for nid, node in sc.nodes.items():
        layers.get(node.node_type, layers["warehouse"]).append(nid)
    pos = {}
    x_map = {"plant": 0.0, "warehouse": 1.0, "demand": 2.0}
    for layer_name, nids in layers.items():
        x = x_map[layer_name]
        n = len(nids)
        for i, nid in enumerate(nids):
            y = (i - (n - 1) / 2) * 1.5
            pos[nid] = (x, y)
    return pos


def draw_supply_chain(sc, highlight_path=None, disrupted_edge=None, show_capacity=True):
    pos = _auto_layout(sc)
    highlight_path = highlight_path or []
    highlight_set = set(zip(highlight_path, highlight_path[1:])) if len(highlight_path) > 1 else set()
    traces = []

    for edge in sc.edges:
        x0, y0 = pos[edge.source]
        x1, y1 = pos[edge.target]
        is_disrupted  = disrupted_edge and edge.source == disrupted_edge[0] and edge.target == disrupted_edge[1]
        is_highlighted = (edge.source, edge.target) in highlight_set
        is_inactive    = not edge.active or is_disrupted
        color   = "#E24B4A" if is_disrupted else "#EF9F27" if is_highlighted else "#B4B2A9" if is_inactive else "#5F5E5A"
        width   = 3 if is_highlighted else 2 if is_disrupted else 1.5
        dash    = "dot" if is_inactive else "solid"
        opacity = 0.4 if is_inactive and not is_disrupted else 1.0
        cap_label = f"  cap:{edge.capacity}" if show_capacity else ""
        traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode="lines+text", line=dict(color=color, width=width, dash=dash),
            opacity=opacity, text=["", cap_label, ""],
            textposition="middle center", textfont=dict(size=9, color=color),
            hoverinfo="skip", showlegend=False,
        ))
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        if length > 0:
            ux, uy = dx / length, dy / length
            traces.append(go.Scatter(
                x=[x1 - ux * 0.07], y=[y1 - uy * 0.07], mode="markers",
                marker=dict(symbol="arrow", size=10, color=color,
                            angle=math.degrees(math.atan2(-dy, dx)) + 90),
                showlegend=False, hoverinfo="skip",
            ))

    for ntype in ["plant", "warehouse", "demand"]:
        nids = [n for n, node in sc.nodes.items() if node.node_type == ntype]
        if not nids:
            continue
        xs = [pos[n][0] for n in nids]
        ys = [pos[n][1] for n in nids]
        names = [sc.nodes[n].name for n in nids]
        caps  = [sc.nodes[n].capacity for n in nids]
        locs  = [sc.nodes[n].location or "" for n in nids]
        in_path = [n in highlight_path for n in nids]
        colors  = ["#EF9F27" if ip else NODE_COLORS[ntype] for ip in in_path]
        sizes   = [22 if ip else 16 for ip in in_path]
        hover   = [f"<b>{name}</b><br>Type: {ntype}<br>Capacity: {cap}<br>Location: {loc}"
                   for name, cap, loc in zip(names, caps, locs)]
        traces.append(go.Scatter(
            x=xs, y=ys, mode="markers+text",
            name=ntype.capitalize() + "s",
            text=names,
            textposition="middle left" if ntype == "plant" else "top center" if ntype == "warehouse" else "middle right",
            textfont=dict(size=11),
            hovertext=hover, hoverinfo="text",
            marker=dict(symbol=NODE_SYMBOLS[ntype], size=sizes, color=colors,
                        line=dict(width=1.5, color="white")),
        ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        height=480, hovermode="closest",
    )
    return fig


def draw_impact_chart(impact: dict):
    names  = [v["demand_name"] for v in impact.values()]
    before = [v["before_pct"]  for v in impact.values()]
    after  = [v["after_pct"]   for v in impact.values()]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Before disruption", x=names, y=before, marker_color="#1D9E75", opacity=0.85))
    fig.add_trace(go.Bar(name="After disruption",  x=names, y=after,  marker_color="#E24B4A", opacity=0.85))
    fig.update_layout(
        barmode="group",
        yaxis=dict(title="Demand fulfillment (%)", range=[0, 110]),
        xaxis=dict(title="Demand point"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320, margin=dict(l=10, r=10, t=10, b=10),
    )
    fig.add_hline(y=100, line_dash="dot", line_color="#888780",
                  annotation_text="Full demand", annotation_position="right")
    return fig


def draw_criticality_chart(ranking: list):
    labels = [r["label"] for r in ranking]
    drops  = [r["avg_fulfillment_drop"] for r in ranking]
    colors = [SEVERITY_COLORS[r["severity"]] for r in ranking]
    fig = go.Figure(go.Bar(
        x=drops, y=labels, orientation="h",
        marker_color=colors,
        text=[f"{d}%" for d in drops], textposition="outside",
    ))
    fig.update_layout(
        xaxis=dict(title="Avg fulfillment drop (%)", range=[0, max(drops or [10]) * 1.3]),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=max(300, len(ranking) * 40),
        margin=dict(l=10, r=60, t=10, b=10),
    )
    return fig


def draw_resilience_gauge(score: float):
    color = "#E24B4A" if score < 40 else "#EF9F27" if score < 70 else "#1D9E75"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"suffix": "%", "font": {"size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "steps": [
                {"range": [0,  40], "color": "#FCEBEB"},
                {"range": [40, 70], "color": "#FAEEDA"},
                {"range": [70, 100], "color": "#EAF3DE"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": score},
        },
    ))
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)")
    return fig


# ═══════════════════════════════════════════════════════
# PART 4 — STREAMLIT DASHBOARD
# ═══════════════════════════════════════════════════════

st.set_page_config(page_title="Supply Chain Resilience", page_icon="🔗", layout="wide")

st.markdown("""
<style>
    div[data-testid="stExpander"] { border: 1px solid #e0e0e0; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

if "sc" not in st.session_state:
    st.session_state.sc = load_demo_data()
if "disruption_result" not in st.session_state:
    st.session_state.disruption_result = None
if "highlight_path" not in st.session_state:
    st.session_state.highlight_path = []
if "disrupted_edge" not in st.session_state:
    st.session_state.disrupted_edge = None

sc: SupplyChainGraph = st.session_state.sc

# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.title("🔗 Supply Chain Builder")
    st.caption("Build, connect, and test your supply chain resilience")

    tab1, tab2, tab3 = st.tabs(["➕ Nodes", "🔗 Connect", "💾 Data"])

    with tab1:
        st.subheader("Add a new node")
        node_name = st.text_input("Name", placeholder="e.g. Plant Delhi")
        col_a, col_b = st.columns(2)
        with col_a:
            node_type = st.selectbox("Type", ["plant", "warehouse", "demand"])
        with col_b:
            node_cap = st.number_input("Capacity", min_value=1, value=200)
        node_loc = st.text_input("Location", placeholder="City, Country")

        if st.button("Add Node", use_container_width=True, type="primary"):
            if node_name.strip():
                nid = node_type[0].upper() + str(len([n for n in sc.nodes.values() if n.node_type == node_type]) + 1)
                sc.add_node(Node(nid, node_name.strip(), node_type, node_cap, node_loc))
                st.success(f"✅ Added {node_name}")
                st.rerun()
            else:
                st.error("Please enter a node name")

        st.divider()
        for ntype, emoji in [("plant", "🏭"), ("warehouse", "🏢"), ("demand", "📦")]:
            nodes_of_type = [n for n in sc.nodes.values() if n.node_type == ntype]
            if nodes_of_type:
                with st.expander(f"{emoji} {ntype.capitalize()}s ({len(nodes_of_type)})"):
                    for n in nodes_of_type:
                        col1, col2 = st.columns([3, 1])
                        col1.write(f"**{n.name}** — {n.capacity}")
                        if col2.button("🗑", key=f"del_{n.id}"):
                            del sc.nodes[n.id]
                            sc.edges = [e for e in sc.edges if e.source != n.id and e.target != n.id]
                            st.rerun()

    with tab2:
        st.subheader("Add a connection")
        node_opts = {f"{n.name} ({n.node_type})": n.id for n in sc.nodes.values()}
        if len(sc.nodes) >= 2:
            src_label = st.selectbox("From", list(node_opts.keys()), key="edge_src")
            tgt_label = st.selectbox("To",   list(node_opts.keys()), key="edge_tgt")
            edge_cap  = st.number_input("Flow capacity", min_value=1, value=100)
            edge_cost = st.number_input("Transport cost", min_value=0.1, value=1.0, step=0.1)
            if st.button("Add Connection", use_container_width=True, type="primary"):
                src_id = node_opts[src_label]
                tgt_id = node_opts[tgt_label]
                if src_id == tgt_id:
                    st.error("Source and target must be different")
                else:
                    try:
                        sc.add_edge(Edge(src_id, tgt_id, edge_cap, edge_cost))
                        st.success(f"✅ Connected!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
        else:
            st.info("Add at least 2 nodes first")

        st.divider()
        if sc.edges:
            for e in sc.edges:
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{sc.nodes[e.source].name}** → {sc.nodes[e.target].name} `{e.capacity}`")
                if col2.button("🗑", key=f"del_e_{e.source}_{e.target}"):
                    sc.remove_edge(e.source, e.target)
                    st.rerun()

    with tab3:
        if st.button("🔄 Load demo supply chain", use_container_width=True):
            st.session_state.sc = load_demo_data()
            st.session_state.disruption_result = None
            st.session_state.highlight_path = []
            st.session_state.disrupted_edge = None
            st.rerun()

        st.divider()
        st.subheader("Import CSV")
        nodes_file = st.file_uploader("Nodes CSV", type="csv", key="nodes_csv")
        edges_file = st.file_uploader("Edges CSV", type="csv", key="edges_csv")
        if nodes_file and edges_file:
            if st.button("Import", use_container_width=True):
                try:
                    nodes_df = pd.read_csv(nodes_file)
                    edges_df = pd.read_csv(edges_file)
                    new_sc = SupplyChainGraph()
                    for _, row in nodes_df.iterrows():
                        new_sc.add_node(Node(str(row["id"]), str(row["name"]), str(row["node_type"]),
                                             float(row["capacity"]), str(row.get("location", ""))))
                    for _, row in edges_df.iterrows():
                        new_sc.add_edge(Edge(str(row["source"]), str(row["target"]),
                                             float(row["capacity"]), float(row.get("cost", 1.0))))
                    st.session_state.sc = new_sc
                    st.success("✅ Imported!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Import failed: {ex}")

        st.divider()
        st.subheader("Export")
        nodes_df = pd.DataFrame([vars(n) for n in sc.nodes.values()])
        edges_df = pd.DataFrame([vars(e) for e in sc.edges])
        if not nodes_df.empty:
            st.download_button("⬇ Nodes CSV", nodes_df.to_csv(index=False), "nodes.csv", use_container_width=True)
        if not edges_df.empty:
            st.download_button("⬇ Edges CSV", edges_df.to_csv(index=False), "edges.csv", use_container_width=True)
        st.download_button("⬇ Full JSON", json.dumps(sc.to_dict(), indent=2),
                           "supply_chain.json", use_container_width=True)


# ── Main Dashboard ────────────────────────────────────
st.title("📦 Supply Chain Resilience Dashboard")
main_tab1, main_tab2, main_tab3 = st.tabs([
    "🗺️ Supply Chain Map", "⚡ Disruption Simulator", "🏆 Criticality Ranking"
])

# ── Tab 1: Map ────────────────────────────────────────
with main_tab1:
    if not sc.nodes:
        st.info("👈 Add nodes in the sidebar or load the demo data.")
    else:
        plants     = [n for n in sc.nodes.values() if n.node_type == "plant"]
        warehouses = [n for n in sc.nodes.values() if n.node_type == "warehouse"]
        demands    = [n for n in sc.nodes.values() if n.node_type == "demand"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🏭 Plants",      len(plants),     delta=f"Cap: {sum(n.capacity for n in plants)}")
        m2.metric("🏢 Warehouses",  len(warehouses),  delta=f"Cap: {sum(n.capacity for n in warehouses)}")
        m3.metric("📦 Demand pts",  len(demands),     delta=f"Total: {sum(n.capacity for n in demands)}")
        m4.metric("🔗 Connections", len(sc.edges))
        st.divider()

        _, col_opt = st.columns([3, 1])
        show_cap = col_opt.checkbox("Show capacities", value=True)
        fig = draw_supply_chain(sc, highlight_path=st.session_state.highlight_path,
                                disrupted_edge=st.session_state.disrupted_edge, show_capacity=show_cap)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("🟩 **Plant**   🔷 **Warehouse**   🔴 **Demand**   🟡 **Highlighted path**")

        st.divider()
        st.subheader("🔍 Find Shortest Path")
        node_labels = {n.name: n.id for n in sc.nodes.values()}
        col1, col2, col3 = st.columns([2, 2, 1])
        sp_src = col1.selectbox("From", list(node_labels.keys()), key="sp_src")
        sp_tgt = col2.selectbox("To",   list(node_labels.keys()), key="sp_tgt", index=min(2, len(node_labels)-1))
        col3.write("")
        col3.write("")
        if col3.button("Find 🔍", use_container_width=True):
            results = sc.all_shortest_paths(node_labels[sp_src], node_labels[sp_tgt], k=3)
            if results:
                st.session_state.highlight_path = results[0]["path"]
                st.rerun()
            else:
                st.warning("⚠️ No path found between these nodes")
                st.session_state.highlight_path = []

        if st.session_state.highlight_path:
            path  = st.session_state.highlight_path
            names = [sc.nodes[n].name for n in path]
            st.success(f"✅ Shortest path: **{'  →  '.join(names)}**")
            if st.button("Clear highlight"):
                st.session_state.highlight_path = []
                st.rerun()

        st.divider()
        st.subheader("📊 Current Demand Fulfillment")
        if sc.edges:
            with st.spinner("Computing..."):
                fulfillment = sc.demand_fulfillment()
            rows = []
            for d_id, info in fulfillment.items():
                rows.append({
                    "Demand Point": sc.nodes[d_id].name,
                    "Required": info["required"],
                    "Fulfilled": info["fulfilled"],
                    "Fulfillment %": info["pct"],
                    "Supplied by": ", ".join(sc.nodes[p].name for p in info["reachable_from"]) or "—",
                })
            df = pd.DataFrame(rows)
            def color_pct(val):
                if val >= 90: return "background-color: #d4edda"
                if val >= 50: return "background-color: #fff3cd"
                return "background-color: #f8d7da"
            st.dataframe(df.style.applymap(color_pct, subset=["Fulfillment %"]),
                         use_container_width=True, hide_index=True)
        else:
            st.info("Add connections to see demand fulfillment")

# ── Tab 2: Disruption Simulator ───────────────────────
with main_tab2:
    st.subheader("⚡ Simulate a Connection Failure")
    if not sc.edges:
        st.info("Add connections first")
    else:
        edge_options = {
            f"{sc.nodes[e.source].name}  →  {sc.nodes[e.target].name}  (cap: {e.capacity})": (e.source, e.target)
            for e in sc.edges
        }
        col_d1, col_d2 = st.columns([3, 1])
        chosen = col_d1.selectbox("Connection to disrupt", list(edge_options.keys()))
        col_d2.write("")
        col_d2.write("")
        simulate_btn = col_d2.button("⚡ Simulate", use_container_width=True, type="primary")

        if simulate_btn:
            src, tgt = edge_options[chosen]
            with st.spinner("Analysing disruption impact..."):
                result = sc.simulate_disruption(src, tgt)
            st.session_state.disruption_result = result
            st.session_state.disrupted_edge = (src, tgt)
            st.rerun()

        if st.session_state.disruption_result:
            result = st.session_state.disruption_result
            st.divider()
            col_g, col_h = st.columns([1, 2])
            with col_g:
                st.subheader("Resilience Score")
                st.plotly_chart(draw_resilience_gauge(result["resilience_score"]), use_container_width=True)
            with col_h:
                st.subheader(f"Impact: `{result['removed_edge']}`")
                score = result["resilience_score"]
                if score >= 70:
                    st.success(f"✅ Low risk — chain remains largely intact (score: {score}%)")
                elif score >= 40:
                    st.warning(f"⚠️ Moderate risk — some demand points affected (score: {score}%)")
                else:
                    st.error(f"🚨 Critical risk — major supply disruption (score: {score}%)")
                for d_id, imp in result["impact"].items():
                    if imp["drop_pct"] > 0:
                        icon = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(imp["severity"], "⚪")
                        st.write(f"{icon} **{imp['demand_name']}**: {imp['before_pct']}% → {imp['after_pct']}%"
                                 f" _(−{imp['drop_pct']}%, lost {imp['lost_units']} units)_")

            st.divider()
            st.subheader("📊 Before vs After Fulfillment")
            st.plotly_chart(draw_impact_chart(result["impact"]), use_container_width=True)

            st.divider()
            st.subheader("🔄 Alternate Supply Routes")
            if result["alt_paths"]:
                for d_id, paths in result["alt_paths"].items():
                    with st.expander(f"📦 {sc.nodes[d_id].name} — {len(paths)} alternate route(s)"):
                        for i, p in enumerate(paths, 1):
                            st.write(f"**Route {i}** (cost: {p['cost']}):  `{' → '.join(p['path'])}`")
            else:
                st.error("❌ No alternate routes — this is a single point of failure!")

            if st.button("🔄 Reset disruption"):
                st.session_state.disruption_result = None
                st.session_state.disrupted_edge = None
                st.session_state.highlight_path = []
                st.rerun()

# ── Tab 3: Criticality Ranking ────────────────────────
with main_tab3:
    st.subheader("🏆 Critical Connection Ranking")
    st.caption("Stress-tests every connection — ranked by damage caused if removed")
    if not sc.edges:
        st.info("Add connections first")
    else:
        if st.button("🔍 Run Full Stress Test", type="primary"):
            with st.spinner(f"Testing all {len(sc.edges)} connections..."):
                ranking = sc.rank_critical_edges()
            st.session_state["ranking"] = ranking

        if "ranking" in st.session_state:
            ranking = st.session_state["ranking"]
            st.plotly_chart(draw_criticality_chart(ranking), use_container_width=True)

            st.subheader("Detailed breakdown")
            sev_icons = {"critical": "🔴 Critical", "high": "🟠 High", "medium": "🟡 Medium", "low": "🟢 Low"}
            rows = [{"Connection": r["label"],
                     "Avg Fulfillment Drop": f"{r['avg_fulfillment_drop']}%",
                     "Resilience Score": f"{r['resilience_score']}%",
                     "Severity": sev_icons.get(r["severity"], r["severity"])} for r in ranking]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("💡 Recommendations")
            critical = [r for r in ranking if r["severity"] == "critical"]
            high     = [r for r in ranking if r["severity"] == "high"]
            safe     = [r for r in ranking if r["severity"] == "low"]
            if critical:
                st.error("**🚨 Critical connections — add redundancy immediately:**\n\n" +
                         "\n".join(f"- {r['label']}" for r in critical))
            if high:
                st.warning("**⚠️ High-risk connections — plan backup routes:**\n\n" +
                           "\n".join(f"- {r['label']}" for r in high))
            if safe:
                st.success("**✅ Low-risk connections — safely redundant:**\n\n" +
                           "\n".join(f"- {r['label']}" for r in safe))
