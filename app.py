"""
Supply Chain Resilience Platform
Birla Institute of Technology, Mesra
Professional Enterprise Dashboard
"""

# ═══════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════

import networkx as nx
from dataclasses import dataclass
import json, math, io, base64
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ═══════════════════════════════════════════════════════
# BIT MESRA LOGO (embedded base64)
# ═══════════════════════════════════════════════════════

LOGO_B64 = "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"

# ═══════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════
# GRAPH ENGINE
# ═══════════════════════════════════════════════════════

class SupplyChainGraph:
    def __init__(self):
        self.nodes: dict = {}
        self.edges: list = []

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_edge(self, edge):
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError(f"Node {edge.source} or {edge.target} not found")
        for e in self.edges:
            if e.source == edge.source and e.target == edge.target:
                return
        self.edges.append(edge)

    def remove_edge(self, source, target):
        self.edges = [e for e in self.edges if not (e.source == source and e.target == target)]

    def toggle_edge(self, source, target, active):
        for e in self.edges:
            if e.source == source and e.target == target:
                e.active = active

    def to_nx(self, include_inactive=False):
        G = nx.DiGraph()
        for nid, n in self.nodes.items():
            G.add_node(nid, **vars(n))
        for e in self.edges:
            if include_inactive or e.active:
                G.add_edge(e.source, e.target, capacity=e.capacity, weight=e.cost)
        return G

    def shortest_path(self, source, target):
        G = self.to_nx()
        try:
            path = nx.dijkstra_path(G, source, target, weight="weight")
            length = nx.dijkstra_path_length(G, source, target, weight="weight")
            return {"found": True, "path": path, "cost": round(length, 2)}
        except:
            return {"found": False, "path": [], "cost": None}

    def all_shortest_paths(self, source, target, k=3):
        G = self.to_nx()
        results = []
        try:
            for path in nx.shortest_simple_paths(G, source, target, weight="weight"):
                cost = sum(G[path[i]][path[i+1]]["weight"] for i in range(len(path)-1))
                results.append({"path": path, "cost": round(cost, 2)})
                if len(results) >= k:
                    break
        except:
            pass
        return results

    def demand_fulfillment(self):
        G = self.to_nx()
        plants  = [n for n, d in self.nodes.items() if d.node_type == "plant"]
        demands = [n for n, d in self.nodes.items() if d.node_type == "demand"]
        results = {}
        for d_id in demands:
            required = self.nodes[d_id].capacity
            total_flow, reachable = 0.0, []
            for p_id in plants:
                try:
                    fv, _ = nx.maximum_flow(G, p_id, d_id, capacity="capacity")
                    if fv > 0:
                        total_flow += fv
                        reachable.append(p_id)
                except:
                    pass
            fulfilled = min(total_flow, required)
            pct = (fulfilled / required * 100) if required > 0 else 100.0
            results[d_id] = {"required": required, "fulfilled": round(fulfilled, 2),
                             "pct": round(pct, 1), "reachable_from": reachable}
        return results

    def simulate_disruption(self, remove_source, remove_target):
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
                "before_pct": base["pct"], "after_pct": dis["pct"],
                "drop_pct": round(drop, 1),
                "before_fulfilled": base["fulfilled"], "after_fulfilled": dis["fulfilled"],
                "lost_units": round(base["fulfilled"] - dis["fulfilled"], 2),
                "severity": ("critical" if drop >= 50 else "high" if drop >= 25 else "medium" if drop > 0 else "none"),
            }
        alt_paths = {}
        for d_id, imp in impact.items():
            if imp["drop_pct"] > 0:
                self.toggle_edge(remove_source, remove_target, active=False)
                paths = []
                for p_id in [n for n, nd in self.nodes.items() if nd.node_type == "plant"]:
                    r = self.shortest_path(p_id, d_id)
                    if r["found"]:
                        paths.append({"from_plant": self.nodes[p_id].name,
                                      "path": [self.nodes[n].name for n in r["path"]],
                                      "path_ids": r["path"], "cost": r["cost"]})
                paths.sort(key=lambda x: x["cost"])
                alt_paths[d_id] = paths[:3]
                self.toggle_edge(remove_source, remove_target, active=True)
        avg_drop = sum(v["drop_pct"] for v in impact.values()) / len(impact) if impact else 0
        return {
            "removed_edge": f"{self.nodes[remove_source].name} → {self.nodes[remove_target].name}",
            "removed_src": remove_source, "removed_tgt": remove_target,
            "resilience_score": round(max(0, 100 - avg_drop), 1),
            "impact": impact, "alt_paths": alt_paths,
        }

    def rank_critical_edges(self):
        ranking = []
        for edge in self.edges:
            if not edge.active:
                continue
            result = self.simulate_disruption(edge.source, edge.target)
            avg_drop = sum(v["drop_pct"] for v in result["impact"].values()) / len(result["impact"]) if result["impact"] else 0
            ranking.append({
                "source": edge.source, "target": edge.target,
                "label": result["removed_edge"],
                "avg_fulfillment_drop": round(avg_drop, 1),
                "resilience_score": result["resilience_score"],
                "severity": ("critical" if avg_drop >= 50 else "high" if avg_drop >= 25 else "medium" if avg_drop >= 5 else "low"),
            })
        ranking.sort(key=lambda x: x["avg_fulfillment_drop"], reverse=True)
        return ranking

    def to_dict(self):
        return {"nodes": [vars(n) for n in self.nodes.values()],
                "edges": [vars(e) for e in self.edges]}


# ═══════════════════════════════════════════════════════
# DEMO DATA
# ═══════════════════════════════════════════════════════

def load_demo_data():
    sc = SupplyChainGraph()
    sc.add_node(Node("P1", "Plant Mumbai",   "plant",     500, "Mumbai, India",    72.8777, 19.0760))
    sc.add_node(Node("P2", "Plant Chennai",  "plant",     400, "Chennai, India",   80.2707, 13.0827))
    sc.add_node(Node("P3", "Plant Pune",     "plant",     350, "Pune, India",      73.8567, 18.5204))
    sc.add_node(Node("W1", "WH North",       "warehouse", 400, "Delhi, India",     77.2090, 28.6139))
    sc.add_node(Node("W2", "WH West",        "warehouse", 350, "Ahmedabad, India", 72.5714, 23.0225))
    sc.add_node(Node("W3", "WH East",        "warehouse", 300, "Kolkata, India",   88.3639, 22.5726))
    sc.add_node(Node("W4", "WH South",       "warehouse", 280, "Bangalore, India", 77.5946, 12.9716))
    sc.add_node(Node("D1", "Delhi Market",     "demand",  200, "Delhi, India",     77.2090, 28.6139))
    sc.add_node(Node("D2", "Jaipur Market",    "demand",  120, "Jaipur, India",    75.7873, 26.9124))
    sc.add_node(Node("D3", "Surat Market",     "demand",  180, "Surat, India",     72.8311, 21.1702))
    sc.add_node(Node("D4", "Bhubaneswar Mkt",  "demand",  100, "Bhubaneswar, India", 85.8245, 20.2961))
    sc.add_node(Node("D5", "Hyderabad Market", "demand",  160, "Hyderabad, India", 78.4867, 17.3850))
    sc.add_node(Node("D6", "Kochi Market",     "demand",  140, "Kochi, India",     76.2673, 9.9312))
    sc.add_edge(Edge("P1","W1",300,2.0)); sc.add_edge(Edge("P1","W2",250,1.5))
    sc.add_edge(Edge("P2","W3",200,1.8)); sc.add_edge(Edge("P2","W4",220,2.2))
    sc.add_edge(Edge("P3","W2",180,1.2)); sc.add_edge(Edge("P3","W4",200,1.6))
    sc.add_edge(Edge("P1","W3",150,3.0)); sc.add_edge(Edge("P2","W1",100,3.5))
    sc.add_edge(Edge("W1","D1",220,1.0)); sc.add_edge(Edge("W1","D2",150,1.5))
    sc.add_edge(Edge("W2","D2",130,1.2)); sc.add_edge(Edge("W2","D3",200,1.0))
    sc.add_edge(Edge("W3","D4",120,1.0)); sc.add_edge(Edge("W3","D5",130,1.8))
    sc.add_edge(Edge("W4","D5",180,1.0)); sc.add_edge(Edge("W4","D6",160,1.2))
    sc.add_edge(Edge("W1","D4",80,2.5));  sc.add_edge(Edge("W2","D6",90,2.0))
    return sc


# ═══════════════════════════════════════════════════════
# VISUALIZATIONS
# ═══════════════════════════════════════════════════════

NODE_COLORS  = {"plant": "#1B4F72", "warehouse": "#154360", "demand": "#7B241C"}
NODE_SYMBOLS = {"plant": "square",  "warehouse": "diamond", "demand": "circle"}
SEVERITY_COLORS = {"critical":"#C0392B","high":"#E67E22","medium":"#2980B9","low":"#1A8A4A","none":"#7F8C8D"}

def _auto_layout(sc):
    layers = {"plant": [], "warehouse": [], "demand": []}
    for nid, node in sc.nodes.items():
        layers.get(node.node_type, layers["warehouse"]).append(nid)
    pos = {}
    x_map = {"plant": 0.0, "warehouse": 1.0, "demand": 2.0}
    for lname, nids in layers.items():
        x = x_map[lname]
        n = len(nids)
        for i, nid in enumerate(nids):
            pos[nid] = (x, (i - (n-1)/2) * 1.5)
    return pos

def draw_supply_chain(sc, highlight_path=None, disrupted_edge=None, show_capacity=True):
    pos = _auto_layout(sc)
    highlight_path = highlight_path or []
    highlight_set = set(zip(highlight_path, highlight_path[1:])) if len(highlight_path) > 1 else set()
    traces = []
    for edge in sc.edges:
        x0,y0 = pos[edge.source]; x1,y1 = pos[edge.target]
        is_dis = disrupted_edge and edge.source==disrupted_edge[0] and edge.target==disrupted_edge[1]
        is_hi  = (edge.source, edge.target) in highlight_set
        color  = "#C0392B" if is_dis else "#D4AC0D" if is_hi else "#AAB7B8" if not edge.active else "#566573"
        width  = 3 if is_hi else 2.5 if is_dis else 1.5
        dash   = "dot" if (not edge.active or is_dis) else "solid"
        cap_lbl= f"  {int(edge.capacity)}" if show_capacity else ""
        traces.append(go.Scatter(x=[x0,x1,None],y=[y0,y1,None],mode="lines+text",
            line=dict(color=color,width=width,dash=dash),
            text=["",cap_lbl,""],textposition="middle center",textfont=dict(size=9,color=color),
            hoverinfo="skip",showlegend=False))
        dx,dy=x1-x0,y1-y0; l=math.hypot(dx,dy)
        if l>0:
            ux,uy=dx/l,dy/l
            traces.append(go.Scatter(x=[x1-ux*0.07],y=[y1-uy*0.07],mode="markers",
                marker=dict(symbol="arrow",size=10,color=color,angle=math.degrees(math.atan2(-dy,dx))+90),
                showlegend=False,hoverinfo="skip"))
    for ntype in ["plant","warehouse","demand"]:
        nids=[n for n,nd in sc.nodes.items() if nd.node_type==ntype]
        if not nids: continue
        in_path=[n in highlight_path for n in nids]
        traces.append(go.Scatter(
            x=[pos[n][0] for n in nids], y=[pos[n][1] for n in nids],
            mode="markers+text", name=ntype.capitalize()+"s",
            text=[sc.nodes[n].name for n in nids],
            textposition="middle left" if ntype=="plant" else "top center" if ntype=="warehouse" else "middle right",
            textfont=dict(size=11,color="#2C3E50"),
            hovertext=[f"<b>{sc.nodes[n].name}</b><br>Type: {ntype}<br>Capacity: {sc.nodes[n].capacity}<br>Location: {sc.nodes[n].location}" for n in nids],
            hoverinfo="text",
            marker=dict(symbol=NODE_SYMBOLS[ntype],size=[20 if ip else 14 for ip in in_path],
                       color=["#D4AC0D" if ip else NODE_COLORS[ntype] for ip in in_path],
                       line=dict(width=2,color="white"))))
    fig = go.Figure(data=traces)
    fig.update_layout(plot_bgcolor="#FDFEFE",paper_bgcolor="#FDFEFE",
        margin=dict(l=10,r=10,t=10,b=10),height=460,hovermode="closest",
        xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
        yaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,
                   font=dict(size=11,color="#2C3E50"),bgcolor="rgba(0,0,0,0)"))
    return fig

def draw_gauge_charts(fulfillment, nodes):
    demands = {k:v for k,v in fulfillment.items()}
    cols = min(3, len(demands))
    rows = math.ceil(len(demands)/cols)
    fig = go.Figure()
    positions = []
    col_step = 1.0/cols
    row_step = 1.0/rows
    for i,(d_id,info) in enumerate(demands.items()):
        col = i % cols
        row = i // cols
        cx = col_step*(col+0.5)
        cy = 1 - row_step*(row+0.5)
        positions.append((d_id,info,cx,cy))
    specs = [[{"type":"indicator"} for _ in range(cols)] for _ in range(rows)]
    fig = go.Figure()
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=rows, cols=cols, specs=specs)
    for i,(d_id,info) in enumerate(demands.items()):
        col = (i % cols) + 1
        row = (i // cols) + 1
        pct = info["pct"]
        color = "#C0392B" if pct < 50 else "#E67E22" if pct < 80 else "#1A8A4A"
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=pct,
            title={"text": nodes[d_id].name, "font": {"size": 11, "color": "#2C3E50"}},
            number={"suffix":"%","font":{"size":18,"color":color}},
            gauge={"axis":{"range":[0,100],"tickwidth":1,"tickcolor":"#BDC3C7"},
                   "bar":{"color":color},
                   "steps":[{"range":[0,50],"color":"#FADBD8"},{"range":[50,80],"color":"#FDEBD0"},{"range":[80,100],"color":"#D5F5E3"}],
                   "threshold":{"line":{"color":color,"width":2},"thickness":0.75,"value":pct}}),
            row=row, col=col)
    fig.update_layout(height=220*rows, plot_bgcolor="#FDFEFE", paper_bgcolor="#FDFEFE",
                     margin=dict(l=10,r=10,t=20,b=10))
    return fig

def draw_impact_chart(impact):
    names  = [v["demand_name"] for v in impact.values()]
    before = [v["before_pct"]  for v in impact.values()]
    after  = [v["after_pct"]   for v in impact.values()]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Before",x=names,y=before,marker_color="#1A8A4A",opacity=0.85,
                        text=[f"{v}%" for v in before],textposition="outside",textfont=dict(size=10)))
    fig.add_trace(go.Bar(name="After", x=names,y=after, marker_color="#C0392B",opacity=0.85,
                        text=[f"{v}%" for v in after],textposition="outside",textfont=dict(size=10)))
    fig.update_layout(barmode="group",yaxis=dict(title="Fulfillment (%)",range=[0,115]),
        plot_bgcolor="#FDFEFE",paper_bgcolor="#FDFEFE",height=300,
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1),
        margin=dict(l=10,r=10,t=10,b=10))
    fig.add_hline(y=100,line_dash="dot",line_color="#7F8C8D")
    return fig

def draw_criticality_chart(ranking):
    labels = [r["label"] for r in ranking]
    drops  = [r["avg_fulfillment_drop"] for r in ranking]
    colors = [SEVERITY_COLORS[r["severity"]] for r in ranking]
    fig = go.Figure(go.Bar(x=drops,y=labels,orientation="h",marker_color=colors,
        text=[f"  {d}%" for d in drops],textposition="outside",
        textfont=dict(size=11,color="#2C3E50")))
    fig.update_layout(
        xaxis=dict(title="Avg. Demand Fulfillment Drop (%)",range=[0,max(drops or [10])*1.35],
                  gridcolor="#ECF0F1"),
        yaxis=dict(autorange="reversed",tickfont=dict(size=11,color="#2C3E50")),
        plot_bgcolor="#FDFEFE",paper_bgcolor="#FDFEFE",
        height=max(320, len(ranking)*44),
        margin=dict(l=10,r=80,t=10,b=10))
    return fig

def draw_resilience_gauge(score):
    color = "#C0392B" if score < 40 else "#E67E22" if score < 70 else "#1A8A4A"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",value=score,
        number={"suffix":"%","font":{"size":36,"color":color}},
        gauge={"axis":{"range":[0,100],"tickwidth":1},
               "bar":{"color":color},
               "steps":[{"range":[0,40],"color":"#FADBD8"},{"range":[40,70],"color":"#FDEBD0"},{"range":[70,100],"color":"#D5F5E3"}],
               "threshold":{"line":{"color":color,"width":3},"thickness":0.75,"value":score}}))
    fig.update_layout(height=200,margin=dict(l=20,r=20,t=10,b=10),paper_bgcolor="#FDFEFE")
    return fig

def draw_geo_map(sc, map_scope="india"):
    plants     = [n for n in sc.nodes.values() if n.node_type=="plant"]
    warehouses = [n for n in sc.nodes.values() if n.node_type=="warehouse"]
    demands    = [n for n in sc.nodes.values() if n.node_type=="demand"]
    fig = go.Figure()
    # edges first
    for edge in sc.edges:
        s = sc.nodes[edge.source]; t = sc.nodes[edge.target]
        if s.x and s.y and t.x and t.y:
            fig.add_trace(go.Scattergeo(
                lon=[s.x,t.x,None],lat=[s.y,t.y,None],
                mode="lines",line=dict(width=1.5,color="#AAB7B8"),showlegend=False,hoverinfo="skip"))
    # nodes
    for ntype, nodes_list, color, symbol, size in [
        ("plant",     plants,     "#1B4F72", "square",  14),
        ("warehouse", warehouses, "#154360", "diamond", 12),
        ("demand",    demands,    "#7B241C", "circle",  10),
    ]:
        if nodes_list:
            fig.add_trace(go.Scattergeo(
                lon=[n.x for n in nodes_list], lat=[n.y for n in nodes_list],
                mode="markers+text", name=ntype.capitalize()+"s",
                text=[n.name for n in nodes_list], textposition="top center",
                textfont=dict(size=9,color="#2C3E50"),
                hovertext=[f"<b>{n.name}</b><br>{n.node_type}<br>Capacity: {n.capacity}<br>{n.location}" for n in nodes_list],
                hoverinfo="text",
                marker=dict(size=size,color=color,symbol=symbol,line=dict(width=1.5,color="white"))))
    scope = "asia" if map_scope == "india" else "world"
    geo_cfg = dict(scope=scope,showland=True,landcolor="#F2F3F4",
                  showocean=True,oceancolor="#EBF5FB",
                  showlakes=True,lakecolor="#EBF5FB",
                  showrivers=True,rivercolor="#AED6F1",
                  showcountries=True,countrycolor="#BDC3C7",
                  showcoastlines=True,coastlinecolor="#85929E",
                  bgcolor="#FDFEFE")
    if map_scope == "india":
        geo_cfg.update(center=dict(lon=80, lat=22), projection_scale=4.5)
    fig.update_layout(geo=geo_cfg, height=500, paper_bgcolor="#FDFEFE",
        margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,
                   font=dict(size=11)))
    return fig

# ═══════════════════════════════════════════════════════
# SAMPLE CSV TEMPLATES
# ═══════════════════════════════════════════════════════

SAMPLE_NODES_CSV = """id,name,node_type,capacity,location
P1,Plant Name 1,plant,500,City1 India
P2,Plant Name 2,plant,400,City2 India
W1,Warehouse North,warehouse,400,City3 India
W2,Warehouse South,warehouse,350,City4 India
D1,Demand Point 1,demand,200,City5 India
D2,Demand Point 2,demand,150,City6 India
"""

SAMPLE_EDGES_CSV = """source,target,capacity,cost
P1,W1,300,2.0
P1,W2,250,1.5
P2,W1,200,1.8
P2,W2,220,2.2
W1,D1,220,1.0
W1,D2,150,1.5
W2,D1,130,1.2
W2,D2,200,1.0
"""

# ═══════════════════════════════════════════════════════
# STREAMLIT APP
# ═══════════════════════════════════════════════════════

st.set_page_config(
    page_title="Supply Chain Resilience Platform | BIT Mesra",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Professional CSS ──────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #1B2631 0%, #2E4057 100%);
        padding: 18px 28px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: 600;
        margin: 0;
        letter-spacing: 0.3px;
    }
    .main-header p {
        color: #AEB6BF;
        font-size: 12px;
        margin: 2px 0 0 0;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E8E8;
        border-radius: 8px;
        padding: 16px 20px;
        border-left: 4px solid #1B4F72;
    }
    .kpi-label {
        font-size: 11px;
        color: #7F8C8D;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1B2631;
        line-height: 1;
    }
    .kpi-sub {
        font-size: 11px;
        color: #5D6D7E;
        margin-top: 4px;
    }
    .section-header {
        font-size: 13px;
        font-weight: 600;
        color: #2C3E50;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid #E5E8E8;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
    .severity-critical { color: #C0392B; font-weight: 600; font-size: 13px; }
    .severity-high     { color: #E67E22; font-weight: 600; font-size: 13px; }
    .severity-medium   { color: #2980B9; font-weight: 600; font-size: 13px; }
    .severity-none     { color: #1A8A4A; font-weight: 600; font-size: 13px; }
    .alert-critical {
        background: #FDEDEC; border-left: 4px solid #C0392B;
        padding: 12px 16px; border-radius: 0 6px 6px 0; margin: 8px 0;
        font-size: 13px; color: #2C3E50;
    }
    .alert-warning {
        background: #FEF9E7; border-left: 4px solid #E67E22;
        padding: 12px 16px; border-radius: 0 6px 6px 0; margin: 8px 0;
        font-size: 13px; color: #2C3E50;
    }
    .alert-success {
        background: #EAFAF1; border-left: 4px solid #1A8A4A;
        padding: 12px 16px; border-radius: 0 6px 6px 0; margin: 8px 0;
        font-size: 13px; color: #2C3E50;
    }
    .path-card {
        background: #F8F9FA; border: 1px solid #E5E8E8;
        border-radius: 6px; padding: 12px 16px; margin: 6px 0;
        font-size: 13px; color: #2C3E50;
    }
    .stButton > button {
        background: #1B4F72; color: white; border: none;
        border-radius: 6px; font-weight: 500; font-size: 13px;
        padding: 8px 18px; transition: all 0.2s;
    }
    .stButton > button:hover { background: #154360; }
    div[data-testid="stExpander"] {
        border: 1px solid #E5E8E8; border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 13px; font-weight: 500; color: #5D6D7E;
    }
    .stTabs [aria-selected="true"] { color: #1B4F72; }
    .sidebar-section {
        font-size: 11px; font-weight: 600; color: #7F8C8D;
        text-transform: uppercase; letter-spacing: 1px;
        margin: 16px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────
if "sc" not in st.session_state:
    st.session_state.sc = load_demo_data()
if "disruption_result" not in st.session_state:
    st.session_state.disruption_result = None
if "highlight_path" not in st.session_state:
    st.session_state.highlight_path = []
if "disrupted_edge" not in st.session_state:
    st.session_state.disrupted_edge = None
if "ranking" not in st.session_state:
    st.session_state.ranking = None

sc = st.session_state.sc

# ── Header ────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <img src="data:image/png;base64,{LOGO_B64}" width="56" height="56" style="border-radius:50%;border:2px solid rgba(255,255,255,0.2);">
    <div>
        <h1>Supply Chain Resilience Platform</h1>
        <p>Birla Institute of Technology, Mesra &nbsp;·&nbsp; Operations & Supply Chain Analytics</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:12px 0 16px 0;border-bottom:1px solid #E5E8E8">
        <img src="data:image/png;base64,{LOGO_B64}" width="38" height="38" style="border-radius:50%;">
        <div>
            <div style="font-size:13px;font-weight:600;color:#1B2631">Network Builder</div>
            <div style="font-size:11px;color:#7F8C8D">Configure supply chain</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Nodes", "Connect", "Data"])

    with tab1:
        st.markdown('<div class="sidebar-section">Add Node</div>', unsafe_allow_html=True)
        node_name = st.text_input("Name", placeholder="e.g. Plant Delhi", label_visibility="collapsed")
        col_a, col_b = st.columns(2)
        with col_a:
            node_type = st.selectbox("Type", ["plant","warehouse","demand"])
        with col_b:
            node_cap = st.number_input("Capacity", min_value=1, value=200)
        node_loc = st.text_input("Location", placeholder="City, Country")
        if st.button("Add Node", use_container_width=True):
            if node_name.strip():
                nid = node_type[0].upper() + str(len([n for n in sc.nodes.values() if n.node_type==node_type])+1)
                sc.add_node(Node(nid, node_name.strip(), node_type, node_cap, node_loc))
                st.success(f"Node added: {node_name}")
                st.rerun()
            else:
                st.error("Enter a node name")

        st.markdown('<div class="sidebar-section">Current Nodes</div>', unsafe_allow_html=True)
        for ntype, label in [("plant","Manufacturing Plants"),("warehouse","Warehouses"),("demand","Demand Points")]:
            nlist = [n for n in sc.nodes.values() if n.node_type==ntype]
            if nlist:
                with st.expander(f"{label} ({len(nlist)})"):
                    for n in nlist:
                        c1,c2 = st.columns([4,1])
                        c1.markdown(f"<span style='font-size:12px;color:#2C3E50'><b>{n.name}</b><br><span style='color:#7F8C8D'>{n.capacity} units</span></span>", unsafe_allow_html=True)
                        if c2.button("✕", key=f"del_{n.id}", help="Remove"):
                            del sc.nodes[n.id]
                            sc.edges = [e for e in sc.edges if e.source!=n.id and e.target!=n.id]
                            st.rerun()

    with tab2:
        st.markdown('<div class="sidebar-section">Add Connection</div>', unsafe_allow_html=True)
        node_opts = {f"{n.name}": n.id for n in sc.nodes.values()}
        if len(sc.nodes) >= 2:
            src_lbl = st.selectbox("From", list(node_opts.keys()), key="edge_src")
            tgt_lbl = st.selectbox("To",   list(node_opts.keys()), key="edge_tgt")
            c1,c2 = st.columns(2)
            edge_cap  = c1.number_input("Capacity", min_value=1, value=100)
            edge_cost = c2.number_input("Cost", min_value=0.1, value=1.0, step=0.1)
            if st.button("Add Connection", use_container_width=True):
                s,t = node_opts[src_lbl], node_opts[tgt_lbl]
                if s==t:
                    st.error("Source and target must differ")
                else:
                    try:
                        sc.add_edge(Edge(s,t,edge_cap,edge_cost))
                        st.success("Connection added")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
        else:
            st.info("Add at least 2 nodes first")
        st.markdown('<div class="sidebar-section">Connections</div>', unsafe_allow_html=True)
        if sc.edges:
            for e in sc.edges:
                c1,c2 = st.columns([5,1])
                c1.markdown(f"<span style='font-size:11px;color:#2C3E50'>{sc.nodes[e.source].name} → {sc.nodes[e.target].name} <span style='color:#7F8C8D'>({int(e.capacity)})</span></span>", unsafe_allow_html=True)
                if c2.button("✕", key=f"del_e_{e.source}_{e.target}"):
                    sc.remove_edge(e.source, e.target)
                    st.rerun()

    with tab3:
        st.markdown('<div class="sidebar-section">Quick Start</div>', unsafe_allow_html=True)
        if st.button("Load Demo Supply Chain", use_container_width=True):
            st.session_state.sc = load_demo_data()
            st.session_state.disruption_result = None
            st.session_state.highlight_path = []
            st.session_state.disrupted_edge = None
            st.session_state.ranking = None
            st.rerun()

        st.markdown('<div class="sidebar-section">Download Templates</div>', unsafe_allow_html=True)
        st.caption("Fill these templates with your data and upload below")
        c1,c2 = st.columns(2)
        c1.download_button("Nodes CSV", SAMPLE_NODES_CSV, "template_nodes.csv", "text/csv", use_container_width=True)
        c2.download_button("Edges CSV", SAMPLE_EDGES_CSV, "template_edges.csv", "text/csv", use_container_width=True)

        st.markdown('<div class="sidebar-section">Import Data</div>', unsafe_allow_html=True)
        nf = st.file_uploader("Nodes CSV", type="csv", key="ncsv")
        ef = st.file_uploader("Edges CSV", type="csv", key="ecsv")
        if nf and ef:
            if st.button("Import", use_container_width=True):
                try:
                    nd = pd.read_csv(nf); ed = pd.read_csv(ef)
                    new_sc = SupplyChainGraph()
                    for _,r in nd.iterrows():
                        new_sc.add_node(Node(str(r["id"]),str(r["name"]),str(r["node_type"]),float(r["capacity"]),str(r.get("location",""))))
                    for _,r in ed.iterrows():
                        new_sc.add_edge(Edge(str(r["source"]),str(r["target"]),float(r["capacity"]),float(r.get("cost",1.0))))
                    st.session_state.sc = new_sc
                    st.success("Import successful")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Import failed: {ex}")

        st.markdown('<div class="sidebar-section">Export</div>', unsafe_allow_html=True)
        ndf = pd.DataFrame([vars(n) for n in sc.nodes.values()])
        edf = pd.DataFrame([vars(e) for e in sc.edges])
        c1,c2 = st.columns(2)
        if not ndf.empty:
            c1.download_button("Nodes", ndf.to_csv(index=False), "nodes.csv", use_container_width=True)
        if not edf.empty:
            c2.download_button("Edges", edf.to_csv(index=False), "edges.csv", use_container_width=True)


# ═══════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════

tab_map, tab_sim, tab_rank, tab_geo = st.tabs([
    "Network Map",
    "Disruption Simulator",
    "Criticality Analysis",
    "Geographic View",
])

# ══════════════════════════════════════════════
# TAB 1 — NETWORK MAP
# ══════════════════════════════════════════════
with tab_map:
    if not sc.nodes:
        st.info("Add nodes in the sidebar or load the demo supply chain to begin.")
    else:
        plants     = [n for n in sc.nodes.values() if n.node_type=="plant"]
        warehouses = [n for n in sc.nodes.values() if n.node_type=="warehouse"]
        demands    = [n for n in sc.nodes.values() if n.node_type=="demand"]

        # KPI row
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Manufacturing Plants</div><div class="kpi-value">{len(plants)}</div><div class="kpi-sub">Total capacity: {sum(n.capacity for n in plants):,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card" style="border-left-color:#154360"><div class="kpi-label">Warehouses</div><div class="kpi-value">{len(warehouses)}</div><div class="kpi-sub">Total capacity: {sum(n.capacity for n in warehouses):,.0f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-card" style="border-left-color:#7B241C"><div class="kpi-label">Demand Points</div><div class="kpi-value">{len(demands)}</div><div class="kpi-sub">Total demand: {sum(n.capacity for n in demands):,.0f}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="kpi-card" style="border-left-color:#1A5276"><div class="kpi-label">Connections</div><div class="kpi-value">{len(sc.edges)}</div><div class="kpi-sub">Active links</div></div>', unsafe_allow_html=True)
        with c5:
            coverage = round(sum(n.capacity for n in plants) / max(sum(n.capacity for n in demands),1) * 100, 1)
            c_color = "#1A8A4A" if coverage >= 100 else "#E67E22" if coverage >= 70 else "#C0392B"
            st.markdown(f'<div class="kpi-card" style="border-left-color:{c_color}"><div class="kpi-label">Supply Coverage</div><div class="kpi-value" style="color:{c_color}">{min(coverage,999):.0f}%</div><div class="kpi-sub">vs total demand</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Map + options
        col_show, col_opt = st.columns([5,1])
        with col_opt:
            show_cap = st.checkbox("Edge labels", value=True)

        fig = draw_supply_chain(sc, st.session_state.highlight_path, st.session_state.disrupted_edge, show_cap)
        st.plotly_chart(fig, use_container_width=True)

        # Legend
        st.markdown("""
        <div style="display:flex;gap:24px;font-size:11px;color:#5D6D7E;margin-top:-8px">
            <span><span style="display:inline-block;width:10px;height:10px;background:#1B4F72;margin-right:4px;border-radius:1px"></span>Manufacturing Plant</span>
            <span><span style="display:inline-block;width:10px;height:10px;background:#154360;margin-right:4px;transform:rotate(45deg)"></span>Warehouse</span>
            <span><span style="display:inline-block;width:10px;height:10px;background:#7B241C;border-radius:50%;margin-right:4px"></span>Demand Point</span>
            <span><span style="display:inline-block;width:10px;height:2px;background:#D4AC0D;margin-right:4px;vertical-align:middle"></span>Highlighted Path</span>
            <span><span style="display:inline-block;width:10px;height:2px;background:#C0392B;margin-right:4px;vertical-align:middle;border-top:2px dotted #C0392B"></span>Disrupted Link</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Shortest path
        st.markdown('<div class="section-header">Shortest Path Analysis</div>', unsafe_allow_html=True)
        node_labels = {n.name: n.id for n in sc.nodes.values()}
        c1,c2,c3 = st.columns([2,2,1])
        sp_src = c1.selectbox("Origin Node", list(node_labels.keys()), key="sp_src")
        sp_tgt = c2.selectbox("Destination Node", list(node_labels.keys()), key="sp_tgt", index=min(2,len(node_labels)-1))
        c3.markdown("<br>", unsafe_allow_html=True)
        if c3.button("Compute", use_container_width=True):
            results = sc.all_shortest_paths(node_labels[sp_src], node_labels[sp_tgt], k=3)
            if results:
                st.session_state.highlight_path = results[0]["path"]
                st.rerun()
            else:
                st.warning("No viable path found between selected nodes.")
                st.session_state.highlight_path = []

        if st.session_state.highlight_path:
            path = st.session_state.highlight_path
            names = [sc.nodes[n].name for n in path]
            st.markdown(f'<div class="alert-success">Shortest path identified: <b>{" → ".join(names)}</b></div>', unsafe_allow_html=True)
            if st.button("Clear Path"):
                st.session_state.highlight_path = []
                st.rerun()

        # Demand fulfillment
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Demand Fulfillment Analysis</div>', unsafe_allow_html=True)
        if sc.edges:
            with st.spinner("Computing fulfillment metrics..."):
                fulfillment = sc.demand_fulfillment()

            st.plotly_chart(draw_gauge_charts(fulfillment, sc.nodes), use_container_width=True)

            with st.expander("View Detailed Fulfillment Table"):
                rows = []
                for d_id,info in fulfillment.items():
                    rows.append({
                        "Demand Point": sc.nodes[d_id].name,
                        "Required Units": f"{info['required']:,.0f}",
                        "Fulfilled Units": f"{info['fulfilled']:,.0f}",
                        "Fulfillment %": info["pct"],
                        "Supply Sources": ", ".join(sc.nodes[p].name for p in info["reachable_from"]) or "No source found",
                    })
                df = pd.DataFrame(rows)
                def color_pct(val):
                    if val >= 90: return "background-color:#D5F5E3"
                    if val >= 50: return "background-color:#FDEBD0"
                    return "background-color:#FADBD8"
                st.dataframe(df.style.applymap(color_pct, subset=["Fulfillment %"]),
                            use_container_width=True, hide_index=True)
        else:
            st.info("Add connections to compute demand fulfillment.")


# ══════════════════════════════════════════════
# TAB 2 — DISRUPTION SIMULATOR
# ══════════════════════════════════════════════
with tab_sim:
    st.markdown('<div class="section-header">Disruption Scenario Analysis</div>', unsafe_allow_html=True)
    st.caption("Select a supply chain link to simulate its failure and analyze the downstream impact.")

    if not sc.edges:
        st.info("Add connections to run disruption analysis.")
    else:
        edge_opts = {
            f"{sc.nodes[e.source].name}  →  {sc.nodes[e.target].name}  (capacity: {int(e.capacity)})": (e.source,e.target)
            for e in sc.edges
        }
        c1,c2 = st.columns([4,1])
        chosen = c1.selectbox("Select connection to disrupt", list(edge_opts.keys()), label_visibility="collapsed")
        c2.markdown("<br>", unsafe_allow_html=True)
        run_sim = c2.button("Run Analysis", use_container_width=True)

        if run_sim:
            src,tgt = edge_opts[chosen]
            with st.spinner("Running disruption analysis..."):
                result = sc.simulate_disruption(src,tgt)
            st.session_state.disruption_result = result
            st.session_state.disrupted_edge = (src,tgt)
            st.rerun()

        if st.session_state.disruption_result:
            result = st.session_state.disruption_result
            st.markdown("<br>", unsafe_allow_html=True)

            # Score + summary
            c_gauge, c_summary = st.columns([1,2])
            with c_gauge:
                st.markdown('<div class="section-header">Resilience Score</div>', unsafe_allow_html=True)
                st.plotly_chart(draw_resilience_gauge(result["resilience_score"]), use_container_width=True)

            with c_summary:
                st.markdown(f'<div class="section-header">Impact Summary — {result["removed_edge"]}</div>', unsafe_allow_html=True)
                score = result["resilience_score"]
                if score >= 70:
                    st.markdown(f'<div class="alert-success"><b>Low Risk</b> — Supply chain retains operational continuity. Resilience score: {score}%</div>', unsafe_allow_html=True)
                elif score >= 40:
                    st.markdown(f'<div class="alert-warning"><b>Moderate Risk</b> — Partial disruption to demand fulfillment. Resilience score: {score}%</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-critical"><b>Critical Risk</b> — Severe supply chain disruption detected. Resilience score: {score}%</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                for d_id,imp in result["impact"].items():
                    if imp["drop_pct"] > 0:
                        sev_class = f"severity-{imp['severity']}"
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:8px 12px;background:#F8F9FA;border-radius:6px;margin:4px 0;
                            border-left:3px solid {SEVERITY_COLORS[imp['severity']]}">
                            <span style="font-size:13px;font-weight:500;color:#2C3E50">{imp['demand_name']}</span>
                            <span style="font-size:12px;color:#5D6D7E">{imp['before_pct']}% → {imp['after_pct']}%
                            &nbsp;|&nbsp; <b>−{imp['drop_pct']}%</b> &nbsp;|&nbsp; −{imp['lost_units']} units</span>
                            <span class="{sev_class}">{imp['severity'].upper()}</span>
                        </div>""", unsafe_allow_html=True)

            # Impact chart
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">Before vs After Fulfillment</div>', unsafe_allow_html=True)
            st.plotly_chart(draw_impact_chart(result["impact"]), use_container_width=True)

            # Alternate paths + network visualization
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">Alternate Supply Routes</div>', unsafe_allow_html=True)
            if result["alt_paths"]:
                for d_id,paths in result["alt_paths"].items():
                    if paths:
                        st.markdown(f"**{sc.nodes[d_id].name}** — {len(paths)} alternate route(s) available")
                        for i,p in enumerate(paths,1):
                            route_str = " → ".join(p["path"])
                            st.markdown(f'<div class="path-card"><b>Route {i}</b> &nbsp;|&nbsp; Cost: {p["cost"]} &nbsp;|&nbsp; {route_str}</div>', unsafe_allow_html=True)
                        st.markdown("")
            else:
                st.markdown('<div class="alert-critical"><b>No alternate routes found</b> — This connection is a single point of failure in your supply chain.</div>', unsafe_allow_html=True)

            # Network map below alternate paths
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">Network View — Disruption Highlighted</div>', unsafe_allow_html=True)
            st.caption("Red dashed line indicates the disrupted connection. Gold nodes/links show the best alternate route.")

            # highlight best alt path if available
            alt_highlight = []
            if result["alt_paths"]:
                first_affected = next(iter(result["alt_paths"]))
                paths_for_first = result["alt_paths"][first_affected]
                if paths_for_first:
                    alt_highlight = paths_for_first[0].get("path_ids", [])

            fig_dis = draw_supply_chain(
                sc,
                highlight_path=alt_highlight,
                disrupted_edge=st.session_state.disrupted_edge,
                show_capacity=True
            )
            st.plotly_chart(fig_dis, use_container_width=True)

            if st.button("Reset Simulation"):
                st.session_state.disruption_result = None
                st.session_state.disrupted_edge = None
                st.session_state.highlight_path = []
                st.rerun()


# ══════════════════════════════════════════════
# TAB 3 — CRITICALITY ANALYSIS
# ══════════════════════════════════════════════
with tab_rank:
    st.markdown('<div class="section-header">Connection Criticality Ranking</div>', unsafe_allow_html=True)
    st.caption("Stress-tests every connection in the network to identify which links pose the highest risk if disrupted.")

    if not sc.edges:
        st.info("Add connections to run criticality analysis.")
    else:
        if st.button("Run Full Stress Test", use_container_width=False):
            with st.spinner(f"Analysing all {len(sc.edges)} connections..."):
                st.session_state.ranking = sc.rank_critical_edges()

        if st.session_state.ranking:
            ranking = st.session_state.ranking

            # Chart with visible labels
            fig_rank = draw_criticality_chart(ranking)
            st.plotly_chart(fig_rank, use_container_width=True)

            # Detailed table
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">Detailed Breakdown</div>', unsafe_allow_html=True)

            rows = []
            sev_map = {"critical":"Critical","high":"High","medium":"Medium","low":"Low"}
            for r in ranking:
                rows.append({
                    "Connection": r["label"],
                    "Avg. Fulfillment Drop": f"{r['avg_fulfillment_drop']}%",
                    "Resilience Score": f"{r['resilience_score']}%",
                    "Risk Level": sev_map.get(r["severity"],r["severity"]),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Recommendations
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">Risk Mitigation Recommendations</div>', unsafe_allow_html=True)
            critical = [r for r in ranking if r["severity"]=="critical"]
            high     = [r for r in ranking if r["severity"]=="high"]
            low      = [r for r in ranking if r["severity"]=="low"]
            if critical:
                links = "".join(f"<li>{r['label']}</li>" for r in critical)
                st.markdown(f'<div class="alert-critical"><b>Immediate Action Required</b> — {len(critical)} critical connection(s) identified. These are single points of failure that require immediate redundancy planning.<ul style="margin:6px 0 0 16px">{links}</ul></div>', unsafe_allow_html=True)
            if high:
                links = "".join(f"<li>{r['label']}</li>" for r in high)
                st.markdown(f'<div class="alert-warning"><b>High Priority</b> — {len(high)} high-risk connection(s) require backup routing plans.<ul style="margin:6px 0 0 16px">{links}</ul></div>', unsafe_allow_html=True)
            if low:
                links = "".join(f"<li>{r['label']}</li>" for r in low)
                st.markdown(f'<div class="alert-success"><b>Well-Redundant</b> — {len(low)} low-risk connection(s) with adequate redundancy.<ul style="margin:6px 0 0 16px">{links}</ul></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 4 — GEOGRAPHIC VIEW
# ══════════════════════════════════════════════
with tab_geo:
    st.markdown('<div class="section-header">Geographic Network View</div>', unsafe_allow_html=True)
    st.caption("Nodes with valid coordinates (lon/lat stored in x/y fields) are plotted on the map.")

    c1,c2 = st.columns([3,1])
    map_scope = c2.radio("Map scope", ["India", "World"], horizontal=False)

    nodes_with_coords = [n for n in sc.nodes.values() if n.x != 0.0 and n.y != 0.0]
    if not nodes_with_coords:
        st.info("No geographic coordinates found. Load the demo supply chain to see the India map view.")
    else:
        fig_geo = draw_geo_map(sc, map_scope.lower())
        st.plotly_chart(fig_geo, use_container_width=True)

        st.markdown('<div class="section-header">Node Coordinates</div>', unsafe_allow_html=True)
        with st.expander("View / edit node coordinates"):
            st.caption("To add coordinates to your own nodes, set the x field to longitude and y field to latitude when adding nodes. Or re-import your nodes CSV with x and y columns.")
            coord_rows = [{"Node": n.name, "Type": n.node_type,
                           "Latitude (y)": n.y, "Longitude (x)": n.x,
                           "Location": n.location}
                          for n in sc.nodes.values()]
            st.dataframe(pd.DataFrame(coord_rows), use_container_width=True, hide_index=True)
