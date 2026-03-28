"""
Supply Chain Resilience Platform v3.0
Birla Institute of Technology, Mesra
Enterprise SCM Dashboard
"""

# ═══════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════
import networkx as nx
from dataclasses import dataclass
import json, math, io
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ═══════════════════════════════════════════════════════
# BIT MESRA LOGO
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

    def to_nx(self):
        G = nx.DiGraph()
        for nid, n in self.nodes.items():
            G.add_node(nid, **vars(n))
        for e in self.edges:
            if e.active:
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
# INVENTORY MANAGER
# ═══════════════════════════════════════════════════════

class InventoryManager:
    def __init__(self):
        self.items = {}   # item_id -> {name, unit}
        self.stock = {}   # node_id -> item_id -> {current, safety, reorder, daily_demand}

    def add_item(self, item_id, name, unit="units"):
        self.items[item_id] = {"name": name, "unit": unit}

    def set_stock(self, node_id, item_id, current, safety, reorder, daily_demand=1.0):
        if node_id not in self.stock:
            self.stock[node_id] = {}
        self.stock[node_id][item_id] = {
            "current": float(current), "safety": float(safety),
            "reorder": float(reorder), "daily_demand": float(daily_demand),
        }

    def update_stock(self, node_id, item_id, delta):
        if node_id in self.stock and item_id in self.stock[node_id]:
            self.stock[node_id][item_id]["current"] = max(0.0,
                self.stock[node_id][item_id]["current"] + delta)
            return True
        return False

    def coverage_days(self, node_id, item_id):
        if node_id in self.stock and item_id in self.stock[node_id]:
            s = self.stock[node_id][item_id]
            dd = s.get("daily_demand", 1)
            return round(s["current"] / dd, 1) if dd > 0 else 999
        return None

    def get_alerts(self, sc_nodes=None):
        alerts = []
        for node_id, items in self.stock.items():
            node_name = sc_nodes[node_id].name if sc_nodes and node_id in sc_nodes else node_id
            for item_id, s in items.items():
                item_name = self.items.get(item_id, {}).get("name", item_id)
                if s["current"] <= s["reorder"]:
                    level = "critical" if s["current"] <= s["safety"] else "warning"
                    alerts.append({
                        "node_id": node_id, "node_name": node_name,
                        "item_id": item_id, "item_name": item_name,
                        "level": level,
                        "current": s["current"], "safety": s["safety"],
                        "reorder": s["reorder"],
                        "coverage": self.coverage_days(node_id, item_id),
                    })
        return sorted(alerts, key=lambda x: (x["level"] != "critical", x["coverage"] or 999))

    def find_stock_alternatives(self, demand_node_id, item_id, required_qty, sc, disrupted_edge=None):
        alternatives = []
        for node_id, items in self.stock.items():
            if node_id == demand_node_id:
                continue
            if item_id not in items:
                continue
            s = items[item_id]
            available = max(0.0, s["current"] - s["safety"])
            if available <= 0:
                continue
            if disrupted_edge:
                sc.toggle_edge(disrupted_edge[0], disrupted_edge[1], active=False)
            path_result = sc.shortest_path(node_id, demand_node_id)
            if disrupted_edge:
                sc.toggle_edge(disrupted_edge[0], disrupted_edge[1], active=True)
            if path_result["found"]:
                alternatives.append({
                    "node_id": node_id,
                    "node_name": sc.nodes[node_id].name if node_id in sc.nodes else node_id,
                    "available": available,
                    "can_cover": available >= required_qty,
                    "coverage_pct": min(100, round(available / max(required_qty, 1) * 100, 1)),
                    "path": [sc.nodes[n].name for n in path_result["path"] if n in sc.nodes],
                    "path_ids": path_result["path"],
                    "route_cost": path_result["cost"],
                    "coverage_days": self.coverage_days(node_id, item_id),
                })
        alternatives.sort(key=lambda x: (-x["coverage_pct"], x["route_cost"]))
        return alternatives[:5]

    def to_dataframe(self, sc_nodes=None):
        rows = []
        for node_id, items in self.stock.items():
            node_name = sc_nodes[node_id].name if sc_nodes and node_id in sc_nodes else node_id
            node_type = sc_nodes[node_id].node_type if sc_nodes and node_id in sc_nodes else ""
            for item_id, s in items.items():
                item_name = self.items.get(item_id, {}).get("name", item_id)
                unit = self.items.get(item_id, {}).get("unit", "units")
                dd = s.get("daily_demand", 1)
                coverage = round(s["current"] / dd, 1) if dd > 0 else 999
                avail_above_safety = max(0, s["current"] - s["safety"])
                status = "Critical" if s["current"] <= s["safety"] else \
                         "Low" if s["current"] <= s["reorder"] else "Normal"
                rows.append({
                    "Node": node_name, "Type": node_type.capitalize(),
                    "Item": item_name, "Unit": unit,
                    "Current Stock": s["current"],
                    "Safety Stock": s["safety"],
                    "Reorder Point": s["reorder"],
                    "Daily Demand": dd,
                    "Coverage Days": coverage,
                    "Available (above safety)": avail_above_safety,
                    "Status": status,
                })
        return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════
# DEMO DATA
# ═══════════════════════════════════════════════════════

def load_demo_data():
    sc = SupplyChainGraph()
    sc.add_node(Node("P1","Plant Mumbai",  "plant",    500,"Mumbai, India",  72.88,19.08))
    sc.add_node(Node("P2","Plant Chennai", "plant",    400,"Chennai, India", 80.27,13.08))
    sc.add_node(Node("P3","Plant Pune",    "plant",    350,"Pune, India",    73.86,18.52))
    sc.add_node(Node("W1","WH North",  "warehouse",400,"Delhi, India",    77.21,28.61))
    sc.add_node(Node("W2","WH West",   "warehouse",350,"Ahmedabad, India",72.57,23.02))
    sc.add_node(Node("W3","WH East",   "warehouse",300,"Kolkata, India",  88.36,22.57))
    sc.add_node(Node("W4","WH South",  "warehouse",280,"Bangalore, India",77.59,12.97))
    sc.add_node(Node("D1","Delhi Market",    "demand",200,"Delhi, India",    77.21,28.61))
    sc.add_node(Node("D2","Jaipur Market",   "demand",120,"Jaipur, India",   75.79,26.91))
    sc.add_node(Node("D3","Surat Market",    "demand",180,"Surat, India",    72.83,21.17))
    sc.add_node(Node("D4","Bhubaneswar Mkt", "demand",100,"Bhubaneswar, India",85.82,20.30))
    sc.add_node(Node("D5","Hyderabad Market","demand",160,"Hyderabad, India", 78.49,17.39))
    sc.add_node(Node("D6","Kochi Market",    "demand",140,"Kochi, India",    76.27,9.93))
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

def load_demo_inventory():
    inv = InventoryManager()
    inv.add_item("SKU001","Rice","Tonnes")
    inv.add_item("SKU002","Wheat","Tonnes")
    inv.add_item("SKU003","Sugar","Tonnes")
    inv.add_item("SKU004","Edible Oil","KL")
    data = [
        ("P1","SKU001",520,100,150,22), ("P1","SKU002",410,80,120,16),
        ("P2","SKU002",360,70,110,14), ("P2","SKU003",310,60,90,11),
        ("P3","SKU001",285,55,85,11), ("P3","SKU004",205,40,65,9),
        ("W1","SKU001",185,50,75,9), ("W1","SKU002",155,40,65,7),
        ("W2","SKU001",125,30,55,6), ("W2","SKU003",105,25,45,5),
        ("W2","SKU004",82,20,35,4), ("W3","SKU002",92,20,38,5),
        ("W3","SKU003",72,15,28,4), ("W4","SKU001",62,15,28,4),
        ("W4","SKU004",52,12,22,3),
    ]
    for node_id,item_id,cur,safety,reorder,dd in data:
        inv.set_stock(node_id,item_id,cur,safety,reorder,dd)
    return inv

def load_demo_scores():
    return {
        "P1":{"reliability":92,"lead_time":88,"quality":95,"cost_efficiency":78},
        "P2":{"reliability":85,"lead_time":91,"quality":89,"cost_efficiency":84},
        "P3":{"reliability":79,"lead_time":83,"quality":91,"cost_efficiency":90},
        "W1":{"reliability":94,"lead_time":90,"quality":87,"cost_efficiency":75},
        "W2":{"reliability":88,"lead_time":85,"quality":82,"cost_efficiency":88},
        "W3":{"reliability":76,"lead_time":79,"quality":84,"cost_efficiency":92},
        "W4":{"reliability":82,"lead_time":86,"quality":88,"cost_efficiency":85},
    }


# ═══════════════════════════════════════════════════════
# EXCEL TEMPLATE GENERATOR
# ═══════════════════════════════════════════════════════

def create_excel_template():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame({
            "id":["P1","P2","W1","W2","D1","D2"],
            "name":["Plant 1","Plant 2","Warehouse North","Warehouse South","Demand Point 1","Demand Point 2"],
            "node_type":["plant","plant","warehouse","warehouse","demand","demand"],
            "capacity":[500,400,350,300,200,150],
            "location":["City1","City2","City3","City4","City5","City6"],
            "x_longitude":[0,0,0,0,0,0], "y_latitude":[0,0,0,0,0,0],
        }).to_excel(writer, sheet_name="Nodes", index=False)
        pd.DataFrame({
            "source":["P1","P1","P2","W1","W2"],
            "target":["W1","W2","W1","D1","D2"],
            "capacity":[300,250,200,220,180],
            "cost":[2.0,1.5,1.8,1.0,1.2],
        }).to_excel(writer, sheet_name="Connections", index=False)
        pd.DataFrame({
            "node_id":["P1","P1","W1","W2"],
            "item_id":["SKU001","SKU002","SKU001","SKU001"],
            "item_name":["Rice","Wheat","Rice","Rice"],
            "unit":["Tonnes","Tonnes","Tonnes","Tonnes"],
            "current_stock":[500,400,180,120],
            "safety_stock":[100,80,50,30],
            "reorder_point":[150,120,70,50],
            "daily_demand":[20,15,8,5],
        }).to_excel(writer, sheet_name="Inventory", index=False)
    output.seek(0)
    return output.getvalue()


# ═══════════════════════════════════════════════════════
# COLORS & CONSTANTS
# ═══════════════════════════════════════════════════════

NODE_COLORS  = {"plant":"#1B4F72","warehouse":"#154360","demand":"#7B241C"}
NODE_SYMBOLS = {"plant":"square","warehouse":"diamond","demand":"circle"}
SEV_COLORS   = {"critical":"#C0392B","high":"#E67E22","medium":"#2980B9","low":"#1A8A4A","none":"#7F8C8D"}
STATUS_COLORS = {"Normal":"#1A8A4A","Low":"#E67E22","Critical":"#C0392B"}


# ═══════════════════════════════════════════════════════
# VISUALIZATIONS
# ═══════════════════════════════════════════════════════

def _auto_layout(sc):
    layers = {"plant":[],"warehouse":[],"demand":[]}
    for nid,node in sc.nodes.items():
        layers.get(node.node_type,layers["warehouse"]).append(nid)
    pos = {}
    for lname,nids in layers.items():
        x = {"plant":0.0,"warehouse":1.0,"demand":2.0}[lname]
        n = len(nids)
        for i,nid in enumerate(nids):
            pos[nid] = (x,(i-(n-1)/2)*1.5)
    return pos

def draw_supply_chain(sc, highlight_path=None, disrupted_edge=None,
                      show_capacity=True, active_dispatches=None):
    pos = _auto_layout(sc)
    highlight_path = highlight_path or []
    active_dispatches = active_dispatches or []
    highlight_set = set(zip(highlight_path,highlight_path[1:])) if len(highlight_path)>1 else set()
    # edges with active dispatches
    dispatch_edges = set()
    for d in active_dispatches:
        if d.get("status") == "In Transit":
            dispatch_edges.add((d.get("from_id",""),d.get("to_id","")))
    traces = []
    for edge in sc.edges:
        x0,y0=pos[edge.source]; x1,y1=pos[edge.target]
        is_dis = disrupted_edge and edge.source==disrupted_edge[0] and edge.target==disrupted_edge[1]
        is_hi  = (edge.source,edge.target) in highlight_set
        is_dispatch = (edge.source,edge.target) in dispatch_edges
        color = "#C0392B" if is_dis else "#D4AC0D" if is_hi else "#2980B9" if is_dispatch else "#AAB7B8"
        width = 3 if is_hi else 2.5 if is_dis else 2.5 if is_dispatch else 1.5
        dash  = "dot" if (not edge.active or is_dis) else "solid"
        cap_lbl = f"  {int(edge.capacity)}" if show_capacity else ""
        hover_txt = f"{sc.nodes[edge.source].name} → {sc.nodes[edge.target].name}<br>Capacity: {edge.capacity} | Cost: {edge.cost}"
        if is_dispatch:
            d_items = [d["item"] for d in active_dispatches if d.get("from_id")==edge.source and d.get("to_id")==edge.target and d.get("status")=="In Transit"]
            hover_txt += f"<br>In Transit: {', '.join(d_items)}"
        traces.append(go.Scatter(x=[x0,x1,None],y=[y0,y1,None],mode="lines",
            line=dict(color=color,width=width,dash=dash),
            hovertext=hover_txt,hoverinfo="text",showlegend=False))
        if show_capacity and cap_lbl:
            mx,my=(x0+x1)/2,(y0+y1)/2
            traces.append(go.Scatter(x=[mx],y=[my],mode="text",
                text=[cap_lbl],textfont=dict(size=9,color=color),
                showlegend=False,hoverinfo="skip"))
        dx,dy=x1-x0,y1-y0; l=math.hypot(dx,dy)
        if l>0:
            ux,uy=dx/l,dy/l
            traces.append(go.Scatter(x=[x1-ux*0.07],y=[y1-uy*0.07],mode="markers",
                marker=dict(symbol="arrow",size=10,color=color,angle=math.degrees(math.atan2(-dy,dx))+90),
                showlegend=False,hoverinfo="skip"))
        # dispatch pulse marker
        if is_dispatch:
            mx2,my2=(x0*0.35+x1*0.65),(y0*0.35+y1*0.65)
            traces.append(go.Scatter(x=[mx2],y=[my2],mode="markers",
                marker=dict(size=12,color="#2980B9",symbol="circle",
                           line=dict(width=2,color="white")),
                hovertext="In Transit",hoverinfo="text",showlegend=False))
    for ntype in ["plant","warehouse","demand"]:
        nids=[n for n,nd in sc.nodes.items() if nd.node_type==ntype]
        if not nids: continue
        in_path=[n in highlight_path for n in nids]
        traces.append(go.Scatter(
            x=[pos[n][0] for n in nids],y=[pos[n][1] for n in nids],
            mode="markers+text",name=ntype.capitalize()+"s",
            text=[sc.nodes[n].name for n in nids],
            textposition="middle left" if ntype=="plant" else "top center" if ntype=="warehouse" else "middle right",
            textfont=dict(size=11,color="#2C3E50"),
            hovertext=[f"<b>{sc.nodes[n].name}</b><br>{ntype}<br>Capacity: {sc.nodes[n].capacity}" for n in nids],
            hoverinfo="text",
            marker=dict(symbol=NODE_SYMBOLS[ntype],
                       size=[20 if ip else 14 for ip in in_path],
                       color=["#D4AC0D" if ip else NODE_COLORS[ntype] for ip in in_path],
                       line=dict(width=2,color="white"))))
    fig = go.Figure(data=traces)
    fig.update_layout(plot_bgcolor="#FDFEFE",paper_bgcolor="#FDFEFE",
        margin=dict(l=10,r=10,t=10,b=10),height=460,hovermode="closest",
        xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
        yaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,
                   font=dict(size=11),bgcolor="rgba(0,0,0,0)"))
    return fig

def draw_gauge_charts(fulfillment, nodes):
    demands = list(fulfillment.items())
    cols = min(3,len(demands)); rows = math.ceil(len(demands)/cols)
    specs = [[{"type":"indicator"} for _ in range(cols)] for _ in range(rows)]
    fig = make_subplots(rows=rows,cols=cols,specs=specs)
    for i,(d_id,info) in enumerate(demands):
        c=(i%cols)+1; r=(i//cols)+1
        pct=info["pct"]
        color="#C0392B" if pct<50 else "#E67E22" if pct<80 else "#1A8A4A"
        fig.add_trace(go.Indicator(
            mode="gauge+number",value=pct,
            title={"text":nodes[d_id].name,"font":{"size":11,"color":"#2C3E50"}},
            number={"suffix":"%","font":{"size":18,"color":color}},
            gauge={"axis":{"range":[0,100],"tickwidth":1},
                   "bar":{"color":color},
                   "steps":[{"range":[0,50],"color":"#FADBD8"},{"range":[50,80],"color":"#FDEBD0"},{"range":[80,100],"color":"#D5F5E3"}]}),
            row=r,col=c)
    fig.update_layout(height=220*rows,plot_bgcolor="#FDFEFE",paper_bgcolor="#FDFEFE",
                     margin=dict(l=10,r=10,t=20,b=10))
    return fig

def draw_impact_chart(impact):
    names=[v["demand_name"] for v in impact.values()]
    before=[v["before_pct"] for v in impact.values()]
    after=[v["after_pct"] for v in impact.values()]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Before",x=names,y=before,marker_color="#1A8A4A",
        text=[f"{v}%" for v in before],textposition="outside",textfont=dict(size=10)))
    fig.add_trace(go.Bar(name="After",x=names,y=after,marker_color="#C0392B",
        text=[f"{v}%" for v in after],textposition="outside",textfont=dict(size=10)))
    fig.update_layout(barmode="group",yaxis=dict(title="Fulfillment (%)",range=[0,115]),
        plot_bgcolor="#FDFEFE",paper_bgcolor="#FDFEFE",height=300,
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1),
        margin=dict(l=10,r=10,t=10,b=10))
    fig.add_hline(y=100,line_dash="dot",line_color="#7F8C8D")
    return fig

def draw_criticality_chart(ranking):
    labels=[r["label"] for r in ranking]
    drops=[r["avg_fulfillment_drop"] for r in ranking]
    colors=[SEV_COLORS[r["severity"]] for r in ranking]
    fig = go.Figure(go.Bar(x=drops,y=labels,orientation="h",marker_color=colors,
        text=[f"  {d}%" for d in drops],textposition="outside",
        textfont=dict(size=11,color="#2C3E50")))
    fig.update_layout(
        xaxis=dict(title="Avg. Fulfillment Drop (%)",range=[0,max(drops or [10])*1.35],gridcolor="#ECF0F1"),
        yaxis=dict(autorange="reversed",tickfont=dict(size=11,color="#2C3E50")),
        plot_bgcolor="#FDFEFE",paper_bgcolor="#FDFEFE",
        height=max(320,len(ranking)*44),margin=dict(l=10,r=80,t=10,b=10))
    return fig

def draw_resilience_gauge(score):
    color="#C0392B" if score<40 else "#E67E22" if score<70 else "#1A8A4A"
    fig = go.Figure(go.Indicator(mode="gauge+number",value=score,
        number={"suffix":"%","font":{"size":36,"color":color}},
        gauge={"axis":{"range":[0,100]},
               "bar":{"color":color},
               "steps":[{"range":[0,40],"color":"#FADBD8"},{"range":[40,70],"color":"#FDEBD0"},{"range":[70,100],"color":"#D5F5E3"}],
               "threshold":{"line":{"color":color,"width":3},"thickness":0.75,"value":score}}))
    fig.update_layout(height=200,margin=dict(l=20,r=20,t=10,b=10),paper_bgcolor="#FDFEFE")
    return fig

def draw_risk_heatmap(sc, ranking):
    if not ranking:
        return go.Figure()
    node_ids = list(sc.nodes.keys())
    node_names = [sc.nodes[n].name for n in node_ids]
    # Build risk matrix: rows = nodes, cols = risk factors
    risk_data = []
    for nid in node_ids:
        out_edges = [r for r in ranking if r["source"]==nid]
        in_edges  = [r for r in ranking if r["target"]==nid]
        max_out = max((r["avg_fulfillment_drop"] for r in out_edges),default=0)
        max_in  = max((r["avg_fulfillment_drop"] for r in in_edges),default=0)
        n_critical_out = sum(1 for r in out_edges if r["severity"]=="critical")
        n_critical_in  = sum(1 for r in in_edges  if r["severity"]=="critical")
        risk_data.append([max_out, max_in, n_critical_out*25, n_critical_in*25])
    z = risk_data
    fig = go.Figure(go.Heatmap(
        z=z, x=["Outbound<br>Max Drop","Inbound<br>Max Drop","Critical<br>Out Links","Critical<br>In Links"],
        y=node_names, colorscale=[[0,"#D5F5E3"],[0.4,"#FDEBD0"],[0.7,"#FAD7A0"],[1.0,"#FADBD8"]],
        text=[[f"{v:.0f}" for v in row] for row in z],
        texttemplate="%{text}", textfont={"size":11},
        hoverongaps=False, showscale=True,
        colorbar=dict(title="Risk Level",tickfont=dict(size=10))))
    fig.update_layout(height=max(300,len(node_ids)*40),
        plot_bgcolor="#FDFEFE",paper_bgcolor="#FDFEFE",
        margin=dict(l=10,r=10,t=30,b=10),
        xaxis=dict(side="top",tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11),autorange="reversed"))
    return fig

def draw_scorecard_radar(node_name, scores):
    cats = ["Reliability","Lead Time","Quality","Cost Efficiency","Reliability"]
    vals = [scores["reliability"],scores["lead_time"],scores["quality"],scores["cost_efficiency"],scores["reliability"]]
    fig = go.Figure(go.Scatterpolar(r=vals,theta=cats,fill="toself",
        line=dict(color="#1B4F72",width=2),fillcolor="rgba(27,79,114,0.15)"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),
        showlegend=False,height=280,paper_bgcolor="#FDFEFE",
        margin=dict(l=30,r=30,t=30,b=10),
        title=dict(text=node_name,font=dict(size=13,color="#2C3E50"),x=0.5))
    return fig

def draw_stock_bar(inv, node_id, sc_nodes=None):
    if node_id not in inv.stock:
        return go.Figure()
    items_data = inv.stock[node_id]
    item_names=[inv.items.get(iid,{}).get("name",iid) for iid in items_data]
    currents=[s["current"] for s in items_data.values()]
    safeties=[s["safety"] for s in items_data.values()]
    reorders=[s["reorder"] for s in items_data.values()]
    colors=["#C0392B" if c<=s else "#E67E22" if c<=r else "#1A8A4A"
            for c,s,r in zip(currents,safeties,reorders)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=item_names,y=currents,marker_color=colors,name="Current Stock",
        text=[f"{c:.0f}" for c in currents],textposition="outside",textfont=dict(size=10)))
    fig.add_trace(go.Scatter(x=item_names,y=safeties,mode="markers+lines",
        marker=dict(symbol="line-ew",size=16,color="#C0392B",line=dict(width=2,color="#C0392B")),
        line=dict(dash="dot",color="#C0392B"),name="Safety Stock"))
    fig.add_trace(go.Scatter(x=item_names,y=reorders,mode="markers+lines",
        marker=dict(symbol="line-ew",size=16,color="#E67E22",line=dict(width=2,color="#E67E22")),
        line=dict(dash="dash",color="#E67E22"),name="Reorder Point"))
    node_name = sc_nodes[node_id].name if sc_nodes and node_id in sc_nodes else node_id
    fig.update_layout(height=280,plot_bgcolor="#FDFEFE",paper_bgcolor="#FDFEFE",
        margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1))
    return fig

def draw_geo_map(sc, map_scope="india"):
    fig = go.Figure()
    for edge in sc.edges:
        s=sc.nodes[edge.source]; t=sc.nodes[edge.target]
        if s.x and s.y and t.x and t.y:
            fig.add_trace(go.Scattergeo(lon=[s.x,t.x,None],lat=[s.y,t.y,None],
                mode="lines",line=dict(width=1.5,color="#AAB7B8"),showlegend=False,hoverinfo="skip"))
    for ntype,nlist,color,symbol,size in [
        ("plant",[n for n in sc.nodes.values() if n.node_type=="plant"],"#1B4F72","square",14),
        ("warehouse",[n for n in sc.nodes.values() if n.node_type=="warehouse"],"#154360","diamond",12),
        ("demand",[n for n in sc.nodes.values() if n.node_type=="demand"],"#7B241C","circle",10),
    ]:
        if nlist:
            fig.add_trace(go.Scattergeo(
                lon=[n.x for n in nlist],lat=[n.y for n in nlist],
                mode="markers+text",name=ntype.capitalize()+"s",
                text=[n.name for n in nlist],textposition="top center",
                textfont=dict(size=9,color="#2C3E50"),
                hovertext=[f"<b>{n.name}</b><br>{ntype}<br>Cap: {n.capacity}<br>{n.location}" for n in nlist],
                hoverinfo="text",
                marker=dict(size=size,color=color,symbol=symbol,line=dict(width=1.5,color="white"))))
    scope = "asia" if map_scope=="india" else "world"
    geo = dict(scope=scope,showland=True,landcolor="#F2F3F4",showocean=True,oceancolor="#EBF5FB",
               showcountries=True,countrycolor="#BDC3C7",showcoastlines=True,
               coastlinecolor="#85929E",bgcolor="#FDFEFE")
    if map_scope=="india":
        geo.update(center=dict(lon=80,lat=22),projection_scale=4.5)
    fig.update_layout(geo=geo,height=500,paper_bgcolor="#FDFEFE",
        margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,font=dict(size=11)))
    return fig


# ═══════════════════════════════════════════════════════
# STREAMLIT APP
# ═══════════════════════════════════════════════════════

st.set_page_config(
    page_title="Supply Chain Platform | BIT Mesra",
    page_icon="⬡",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main-header{background:linear-gradient(135deg,#1B2631 0%,#2E4057 100%);padding:16px 24px;
  border-radius:10px;display:flex;align-items:center;gap:16px;margin-bottom:20px;
  box-shadow:0 2px 12px rgba(0,0,0,0.15);}
.main-header h1{color:#fff;font-size:20px;font-weight:600;margin:0;letter-spacing:0.3px;}
.main-header p{color:#AEB6BF;font-size:11px;margin:2px 0 0;text-transform:uppercase;letter-spacing:0.5px;}
.kpi-card{background:#fff;border:1px solid #E5E8E8;border-radius:8px;padding:14px 18px;border-left:4px solid #1B4F72;}
.kpi-label{font-size:10px;color:#7F8C8D;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;}
.kpi-value{font-size:26px;font-weight:700;color:#1B2631;line-height:1;}
.kpi-sub{font-size:10px;color:#5D6D7E;margin-top:3px;}
.sec-hdr{font-size:12px;font-weight:600;color:#2C3E50;text-transform:uppercase;letter-spacing:1px;
  border-bottom:2px solid #E5E8E8;padding-bottom:7px;margin-bottom:14px;}
.alert-r{background:#FDEDEC;border-left:4px solid #C0392B;padding:10px 14px;border-radius:0 6px 6px 0;margin:6px 0;font-size:13px;}
.alert-a{background:#FEF9E7;border-left:4px solid #E67E22;padding:10px 14px;border-radius:0 6px 6px 0;margin:6px 0;font-size:13px;}
.alert-g{background:#EAFAF1;border-left:4px solid #1A8A4A;padding:10px 14px;border-radius:0 6px 6px 0;margin:6px 0;font-size:13px;}
.card{background:#F8F9FA;border:1px solid #E5E8E8;border-radius:6px;padding:12px 16px;margin:5px 0;font-size:13px;}
.badge-r{background:#FADBD8;color:#C0392B;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.badge-a{background:#FDEBD0;color:#E67E22;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.badge-g{background:#D5F5E3;color:#1A8A4A;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.badge-b{background:#D6EAF8;color:#1B4F72;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.stButton>button{background:#1B4F72;color:white;border:none;border-radius:6px;
  font-weight:500;font-size:13px;padding:7px 16px;transition:all 0.2s;}
.stButton>button:hover{background:#154360;}
div[data-testid="stExpander"]{border:1px solid #E5E8E8;border-radius:8px;}
.sb-sec{font-size:10px;font-weight:600;color:#7F8C8D;text-transform:uppercase;
  letter-spacing:1px;margin:14px 0 6px;}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────
if "sc"     not in st.session_state: st.session_state.sc     = load_demo_data()
if "inv"    not in st.session_state: st.session_state.inv    = load_demo_inventory()
if "scores" not in st.session_state: st.session_state.scores = load_demo_scores()
if "dispatch_log" not in st.session_state: st.session_state.dispatch_log = []
if "disruption_result" not in st.session_state: st.session_state.disruption_result = None
if "highlight_path"    not in st.session_state: st.session_state.highlight_path = []
if "disrupted_edge"    not in st.session_state: st.session_state.disrupted_edge = None
if "ranking"           not in st.session_state: st.session_state.ranking = None

sc  = st.session_state.sc
inv = st.session_state.inv

# ── Header ────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
  <img src="data:image/png;base64,{LOGO_B64}" width="52" height="52" style="border-radius:50%;border:2px solid rgba(255,255,255,0.2)">
  <div>
    <h1>Supply Chain Resilience Platform</h1>
    <p>Birla Institute of Technology, Mesra &nbsp;·&nbsp; Operations &amp; Supply Chain Analytics</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 0 14px;border-bottom:1px solid #E5E8E8">
      <img src="data:image/png;base64,{LOGO_B64}" width="36" height="36" style="border-radius:50%">
      <div>
        <div style="font-size:13px;font-weight:600;color:#1B2631">Network Builder</div>
        <div style="font-size:10px;color:#7F8C8D">Configure your supply chain</div>
      </div>
    </div>""", unsafe_allow_html=True)

    tab_a, tab_b, tab_c = st.tabs(["Nodes", "Connect", "Data"])

    # ── Nodes Tab ──────────────────────────────────────
    with tab_a:
        st.markdown('<div class="sb-sec">Add Node</div>', unsafe_allow_html=True)
        n_name = st.text_input("Name", placeholder="e.g. Plant Delhi", key="nn")
        c1,c2 = st.columns(2)
        n_type = c1.selectbox("Type",["plant","warehouse","demand"],key="nt")
        n_cap  = c2.number_input("Capacity",min_value=1,value=200,key="nc")
        n_loc  = st.text_input("Location",placeholder="City, Country",key="nl")
        if st.button("Add Node",use_container_width=True):
            if n_name.strip():
                nid=n_type[0].upper()+str(len([n for n in sc.nodes.values() if n.node_type==n_type])+1)
                sc.add_node(Node(nid,n_name.strip(),n_type,n_cap,n_loc))
                st.success(f"Added: {n_name}"); st.rerun()
            else: st.error("Enter a name")

        st.markdown('<div class="sb-sec">Current Nodes</div>', unsafe_allow_html=True)
        for ntype,label in [("plant","Plants"),("warehouse","Warehouses"),("demand","Demand")]:
            nlist=[n for n in sc.nodes.values() if n.node_type==ntype]
            if nlist:
                with st.expander(f"{label} ({len(nlist)})"):
                    for n in nlist:
                        c1,c2=st.columns([4,1])
                        c1.markdown(f"<span style='font-size:12px'><b>{n.name}</b><br><span style='color:#7F8C8D'>{int(n.capacity)} units</span></span>",unsafe_allow_html=True)
                        if c2.button("✕",key=f"dn_{n.id}"):
                            del sc.nodes[n.id]
                            sc.edges=[e for e in sc.edges if e.source!=n.id and e.target!=n.id]
                            st.rerun()

    # ── Connect Tab ────────────────────────────────────
    with tab_b:
        st.markdown('<div class="sb-sec">Add Connection</div>', unsafe_allow_html=True)
        node_opts={n.name:n.id for n in sc.nodes.values()}
        if len(sc.nodes)>=2:
            src_l=st.selectbox("From",list(node_opts.keys()),key="es")
            tgt_l=st.selectbox("To",  list(node_opts.keys()),key="et")
            c1,c2=st.columns(2)
            ecap=c1.number_input("Capacity",min_value=1,value=100,key="ec")
            ecost=c2.number_input("Cost",min_value=0.1,value=1.0,step=0.1,key="ecs")
            if st.button("Add Connection",use_container_width=True):
                s,t=node_opts[src_l],node_opts[tgt_l]
                if s==t: st.error("Source and target must differ")
                else:
                    try: sc.add_edge(Edge(s,t,ecap,ecost)); st.success("Added"); st.rerun()
                    except ValueError as e: st.error(str(e))
        else: st.info("Add at least 2 nodes first")
        if sc.edges:
            st.markdown('<div class="sb-sec">Connections</div>', unsafe_allow_html=True)
            for e in sc.edges:
                c1,c2=st.columns([5,1])
                c1.markdown(f"<span style='font-size:11px'>{sc.nodes[e.source].name} → {sc.nodes[e.target].name} <span style='color:#7F8C8D'>({int(e.capacity)})</span></span>",unsafe_allow_html=True)
                if c2.button("✕",key=f"de_{e.source}_{e.target}"):
                    sc.remove_edge(e.source,e.target); st.rerun()

    # ── Data Tab ───────────────────────────────────────
    with tab_c:
        st.markdown('<div class="sb-sec">Quick Start</div>', unsafe_allow_html=True)
        if st.button("Load Demo Supply Chain",use_container_width=True):
            st.session_state.sc=load_demo_data()
            st.session_state.inv=load_demo_inventory()
            st.session_state.scores=load_demo_scores()
            st.session_state.dispatch_log=[]
            st.session_state.disruption_result=None
            st.session_state.highlight_path=[]
            st.session_state.disrupted_edge=None
            st.session_state.ranking=None
            st.rerun()

        st.markdown('<div class="sb-sec">Download Templates</div>', unsafe_allow_html=True)
        st.caption("Fill and re-upload with your real data")
        try:
            excel_bytes = create_excel_template()
            st.download_button("Excel Template (.xlsx)",excel_bytes,
                "supply_chain_template.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        except: pass
        c1,c2=st.columns(2)
        c1.download_button("Nodes CSV","id,name,node_type,capacity,location\nP1,Plant 1,plant,500,City\n",
            "template_nodes.csv","text/csv",use_container_width=True)
        c2.download_button("Edges CSV","source,target,capacity,cost\nP1,W1,300,2.0\n",
            "template_edges.csv","text/csv",use_container_width=True)

        st.markdown('<div class="sb-sec">Import Data</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload Excel or CSV",type=["xlsx","csv","xls"],key="upload_main")
        if uploaded:
            fname = uploaded.name.lower()
            if fname.endswith(".xlsx") or fname.endswith(".xls"):
                try:
                    xls = pd.ExcelFile(uploaded)
                    new_sc = SupplyChainGraph()
                    if "Nodes" in xls.sheet_names:
                        nd=pd.read_excel(xls,"Nodes")
                        for _,r in nd.iterrows():
                            new_sc.add_node(Node(str(r["id"]),str(r["name"]),
                                str(r["node_type"]),float(r["capacity"]),
                                str(r.get("location","")),
                                float(r.get("x_longitude",0)),float(r.get("y_latitude",0))))
                    if "Connections" in xls.sheet_names:
                        ed=pd.read_excel(xls,"Connections")
                        for _,r in ed.iterrows():
                            new_sc.add_edge(Edge(str(r["source"]),str(r["target"]),
                                float(r["capacity"]),float(r.get("cost",1.0))))
                    new_inv=InventoryManager()
                    if "Inventory" in xls.sheet_names:
                        id_=pd.read_excel(xls,"Inventory")
                        for _,r in id_.iterrows():
                            iid=str(r["item_id"])
                            if iid not in new_inv.items:
                                new_inv.add_item(iid,str(r.get("item_name",iid)),str(r.get("unit","units")))
                            new_inv.set_stock(str(r["node_id"]),iid,
                                float(r["current_stock"]),float(r["safety_stock"]),
                                float(r["reorder_point"]),float(r.get("daily_demand",1)))
                    st.session_state.sc=new_sc
                    st.session_state.inv=new_inv
                    st.success("Excel imported successfully!"); st.rerun()
                except Exception as ex: st.error(f"Import failed: {ex}")
            else:
                try:
                    df=pd.read_csv(uploaded)
                    if "node_type" in df.columns:
                        new_sc=SupplyChainGraph()
                        for _,r in df.iterrows():
                            new_sc.add_node(Node(str(r["id"]),str(r["name"]),
                                str(r["node_type"]),float(r["capacity"]),str(r.get("location",""))))
                        st.session_state.sc=new_sc; st.success("Nodes imported"); st.rerun()
                    elif "source" in df.columns:
                        for _,r in df.iterrows():
                            sc.add_edge(Edge(str(r["source"]),str(r["target"]),
                                float(r["capacity"]),float(r.get("cost",1.0))))
                        st.success("Edges imported"); st.rerun()
                except Exception as ex: st.error(f"Import failed: {ex}")

        st.markdown('<div class="sb-sec">Export</div>', unsafe_allow_html=True)
        ndf=pd.DataFrame([vars(n) for n in sc.nodes.values()])
        edf=pd.DataFrame([vars(e) for e in sc.edges])
        c1,c2=st.columns(2)
        if not ndf.empty: c1.download_button("Nodes",ndf.to_csv(index=False),"nodes.csv",use_container_width=True)
        if not edf.empty: c2.download_button("Edges",edf.to_csv(index=False),"edges.csv",use_container_width=True)


# ═══════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════
t1,t2,t3,t4,t5,t6,t7 = st.tabs([
    "Network Map","Inventory & Stock",
    "Disruption Simulator","Risk Heatmap",
    "Dispatch Log","ATP & Scorecard","Geographic View"
])

# ══════════ TAB 1 — NETWORK MAP ══════════════════════
with t1:
    if not sc.nodes:
        st.info("Add nodes in the sidebar or load the demo supply chain.")
    else:
        plants=[n for n in sc.nodes.values() if n.node_type=="plant"]
        warehouses=[n for n in sc.nodes.values() if n.node_type=="warehouse"]
        demands=[n for n in sc.nodes.values() if n.node_type=="demand"]
        active_dis=[d for d in st.session_state.dispatch_log if d.get("status")=="In Transit"]

        c1,c2,c3,c4,c5=st.columns(5)
        def kpi(col,label,value,sub,color="#1B4F72"):
            col.markdown(f'<div class="kpi-card" style="border-left-color:{color}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>',unsafe_allow_html=True)
        kpi(c1,"Plants",len(plants),f"Cap: {sum(n.capacity for n in plants):,.0f}")
        kpi(c2,"Warehouses",len(warehouses),f"Cap: {sum(n.capacity for n in warehouses):,.0f}","#154360")
        kpi(c3,"Demand Points",len(demands),f"Demand: {sum(n.capacity for n in demands):,.0f}","#7B241C")
        kpi(c4,"Connections",len(sc.edges),f"Active dispatches: {len(active_dis)}","#1A5276")
        cov=round(sum(n.capacity for n in plants)/max(sum(n.capacity for n in demands),1)*100,1)
        cov_c="#1A8A4A" if cov>=100 else "#E67E22" if cov>=70 else "#C0392B"
        kpi(c5,"Supply Coverage",f"{min(cov,999):.0f}%","vs total demand",cov_c)

        # stock alerts banner
        alerts=inv.get_alerts(sc.nodes)
        if alerts:
            critical_alerts=[a for a in alerts if a["level"]=="critical"]
            if critical_alerts:
                items_str=", ".join(f"{a['node_name']} / {a['item_name']}" for a in critical_alerts[:3])
                st.markdown(f'<div class="alert-r"><b>Stock Alert:</b> Critical stock levels at {items_str} — go to Inventory tab</div>',unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        _,col_opt=st.columns([5,1])
        show_cap=col_opt.checkbox("Edge labels",value=True)
        fig=draw_supply_chain(sc,st.session_state.highlight_path,
            st.session_state.disrupted_edge,show_cap,active_dis)
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("""<div style="display:flex;gap:20px;font-size:11px;color:#5D6D7E;margin-top:-6px">
            <span>&#9632; Plant</span><span>&#9670; Warehouse</span><span>&#9679; Demand</span>
            <span style="color:#D4AC0D">&#9632; Highlighted path</span>
            <span style="color:#2980B9">&#9632; In transit</span>
            <span style="color:#C0392B">&#9632; Disrupted</span></div>""",unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">Shortest Path Finder</div>',unsafe_allow_html=True)
        node_labels={n.name:n.id for n in sc.nodes.values()}
        c1,c2,c3=st.columns([2,2,1])
        sp_src=c1.selectbox("From",list(node_labels.keys()),key="sp1")
        sp_tgt=c2.selectbox("To",list(node_labels.keys()),key="sp2",index=min(2,len(node_labels)-1))
        c3.markdown("<br>",unsafe_allow_html=True)
        if c3.button("Find",use_container_width=True):
            results=sc.all_shortest_paths(node_labels[sp_src],node_labels[sp_tgt],k=3)
            if results:
                st.session_state.highlight_path=results[0]["path"]; st.rerun()
            else:
                st.warning("No path found."); st.session_state.highlight_path=[]
        if st.session_state.highlight_path:
            names=[sc.nodes[n].name for n in st.session_state.highlight_path]
            st.markdown(f'<div class="alert-g">Shortest path: <b>{" → ".join(names)}</b></div>',unsafe_allow_html=True)
            if st.button("Clear"): st.session_state.highlight_path=[]; st.rerun()

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">Demand Fulfillment</div>',unsafe_allow_html=True)
        if sc.edges:
            with st.spinner("Computing..."):
                ff=sc.demand_fulfillment()
            st.plotly_chart(draw_gauge_charts(ff,sc.nodes),use_container_width=True)
            with st.expander("Detailed Fulfillment Table"):
                rows=[{"Demand Point":sc.nodes[d].name,"Required":info["required"],
                       "Fulfilled":info["fulfilled"],"Fulfillment %":info["pct"],
                       "Sources":", ".join(sc.nodes[p].name for p in info["reachable_from"]) or "None"}
                      for d,info in ff.items()]
                df=pd.DataFrame(rows)
                def cpct(v):
                    if v>=90: return "background-color:#D5F5E3"
                    if v>=50: return "background-color:#FDEBD0"
                    return "background-color:#FADBD8"
                st.dataframe(df.style.applymap(cpct,subset=["Fulfillment %"]),use_container_width=True,hide_index=True)


# ══════════ TAB 2 — INVENTORY & STOCK ════════════════
with t2:
    st.markdown('<div class="sec-hdr">Inventory Overview</div>',unsafe_allow_html=True)

    # Alerts
    alerts=inv.get_alerts(sc.nodes)
    if alerts:
        c_alerts=[a for a in alerts if a["level"]=="critical"]
        w_alerts=[a for a in alerts if a["level"]=="warning"]
        if c_alerts:
            for a in c_alerts:
                st.markdown(f'<div class="alert-r"><span class="badge-r">CRITICAL</span> <b>{a["node_name"]}</b> — {a["item_name"]}: {a["current"]:.0f} (Safety: {a["safety"]:.0f}) · Coverage: {a["coverage"]} days</div>',unsafe_allow_html=True)
        if w_alerts:
            for a in w_alerts:
                st.markdown(f'<div class="alert-a"><span class="badge-a">LOW</span> <b>{a["node_name"]}</b> — {a["item_name"]}: {a["current"]:.0f} · Coverage: {a["coverage"]} days</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-g">All stock levels are within normal range.</div>',unsafe_allow_html=True)

    # Full inventory table
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">Stock Levels by Node</div>',unsafe_allow_html=True)
    inv_df=inv.to_dataframe(sc.nodes)
    if not inv_df.empty:
        def color_status(val):
            return f"color:{STATUS_COLORS.get(val,'#2C3E50')};font-weight:600"
        def color_cov(val):
            if val<=3: return "background-color:#FADBD8"
            if val<=7: return "background-color:#FDEBD0"
            return "background-color:#D5F5E3"
        styled=inv_df.style.applymap(color_status,subset=["Status"]).applymap(color_cov,subset=["Coverage Days"])
        st.dataframe(styled,use_container_width=True,hide_index=True)

    # Per-node stock chart
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">Stock Chart by Node</div>',unsafe_allow_html=True)
    nodes_with_stock=[nid for nid in sc.nodes if nid in inv.stock and inv.stock[nid]]
    if nodes_with_stock:
        sel_node=st.selectbox("Select node",
            [sc.nodes[n].name for n in nodes_with_stock],key="inv_node_sel")
        sel_id=[n for n in nodes_with_stock if sc.nodes[n].name==sel_node]
        if sel_id:
            st.plotly_chart(draw_stock_bar(inv,sel_id[0],sc.nodes),use_container_width=True)

    # Update stock
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">Live Stock Update</div>',unsafe_allow_html=True)
    st.caption("Manually log a stock dispatch (negative) or receipt (positive) to update live stock levels.")
    with st.form("stock_update_form"):
        c1,c2,c3,c4=st.columns([2,2,1,1])
        upd_node=c1.selectbox("Node",[sc.nodes[n].name for n in sc.nodes if n in inv.stock],key="upd_n")
        upd_node_id=[n for n in sc.nodes if sc.nodes[n].name==upd_node and n in inv.stock]
        if upd_node_id and inv.stock.get(upd_node_id[0]):
            item_opts={inv.items.get(iid,{}).get("name",iid):iid for iid in inv.stock[upd_node_id[0]]}
            upd_item=c2.selectbox("Item",list(item_opts.keys()),key="upd_i")
        else:
            upd_item=c2.text_input("Item ID",key="upd_i2"); item_opts={}
        upd_qty=c3.number_input("Qty (±)",value=0.0,step=1.0,key="upd_q")
        upd_note=c4.text_input("Note",placeholder="e.g. dispatch to W1",key="upd_note")
        submitted=st.form_submit_button("Update Stock",use_container_width=True)
        if submitted and upd_node_id:
            iid=item_opts.get(upd_item,upd_item)
            if inv.update_stock(upd_node_id[0],iid,upd_qty):
                ts=datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.dispatch_log.append({
                    "timestamp":ts,"from_node":upd_node,"to_node":"Manual Update",
                    "from_id":upd_node_id[0],"to_id":"",
                    "item":inv.items.get(iid,{}).get("name",iid),
                    "item_id":iid,"quantity":upd_qty,"status":"Delivered","notes":upd_note})
                st.success(f"Stock updated: {upd_qty:+.0f} units"); st.rerun()
            else: st.error("Node/item not found in inventory")

    # Add new item / node stock
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">Add New Item to Node</div>',unsafe_allow_html=True)
    with st.form("add_stock_form"):
        c1,c2,c3=st.columns(3)
        new_node=c1.selectbox("Node",[n.name for n in sc.nodes.values()],key="ns_node")
        new_item_id=c2.text_input("Item ID",placeholder="e.g. SKU005",key="ns_iid")
        new_item_name=c3.text_input("Item Name",placeholder="e.g. Salt",key="ns_iname")
        c1b,c2b,c3b,c4b,c5b=st.columns(5)
        ns_unit=c1b.text_input("Unit",value="Tonnes",key="ns_unit")
        ns_cur=c2b.number_input("Current",min_value=0.0,value=100.0,key="ns_cur")
        ns_saf=c3b.number_input("Safety",min_value=0.0,value=20.0,key="ns_saf")
        ns_reo=c4b.number_input("Reorder",min_value=0.0,value=40.0,key="ns_reo")
        ns_dd=c5b.number_input("Daily Demand",min_value=0.1,value=5.0,key="ns_dd")
        if st.form_submit_button("Add to Inventory",use_container_width=True):
            if new_item_id.strip() and new_item_name.strip():
                nid=[n.id for n in sc.nodes.values() if n.name==new_node]
                if nid:
                    inv.add_item(new_item_id.strip(),new_item_name.strip(),ns_unit)
                    inv.set_stock(nid[0],new_item_id.strip(),ns_cur,ns_saf,ns_reo,ns_dd)
                    st.success(f"Added {new_item_name} to {new_node}"); st.rerun()
            else: st.error("Enter item ID and name")


# ══════════ TAB 3 — DISRUPTION SIMULATOR ═════════════
with t3:
    st.markdown('<div class="sec-hdr">Disruption Scenario Analysis</div>',unsafe_allow_html=True)
    st.caption("Simulate a connection failure — see flow-based alternate paths AND safety stock alternatives per item.")
    if not sc.edges:
        st.info("Add connections to run disruption analysis.")
    else:
        edge_opts={f"{sc.nodes[e.source].name}  →  {sc.nodes[e.target].name}  (cap: {int(e.capacity)})":(e.source,e.target) for e in sc.edges}
        c1,c2=st.columns([4,1])
        chosen=c1.selectbox("Connection to disrupt",list(edge_opts.keys()),label_visibility="collapsed",key="dis_sel")
        c2.markdown("<br>",unsafe_allow_html=True)
        if c2.button("Analyse",use_container_width=True,type="primary"):
            src,tgt=edge_opts[chosen]
            with st.spinner("Running disruption analysis..."):
                result=sc.simulate_disruption(src,tgt)
            st.session_state.disruption_result=result
            st.session_state.disrupted_edge=(src,tgt)
            st.rerun()

        if st.session_state.disruption_result:
            result=st.session_state.disruption_result
            st.markdown("<br>",unsafe_allow_html=True)
            cg,cs=st.columns([1,2])
            with cg:
                st.markdown('<div class="sec-hdr">Resilience Score</div>',unsafe_allow_html=True)
                st.plotly_chart(draw_resilience_gauge(result["resilience_score"]),use_container_width=True)
            with cs:
                st.markdown(f'<div class="sec-hdr">Impact — {result["removed_edge"]}</div>',unsafe_allow_html=True)
                sc2=result["resilience_score"]
                msg=("Low Risk — Supply chain retains continuity." if sc2>=70 else
                     "Moderate Risk — Partial fulfillment disruption." if sc2>=40 else
                     "Critical Risk — Major supply chain disruption detected.")
                cls="alert-g" if sc2>=70 else "alert-a" if sc2>=40 else "alert-r"
                st.markdown(f'<div class="{cls}"><b>Score: {sc2}%</b> — {msg}</div>',unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                for d_id,imp in result["impact"].items():
                    if imp["drop_pct"]>0:
                        sev_color=SEV_COLORS[imp["severity"]]
                        st.markdown(f"""<div style="display:flex;justify-content:space-between;
                            padding:7px 12px;background:#F8F9FA;border-radius:5px;margin:3px 0;
                            border-left:3px solid {sev_color}">
                            <b style="font-size:13px">{imp['demand_name']}</b>
                            <span style="font-size:12px;color:#5D6D7E">{imp['before_pct']}% → {imp['after_pct']}%
                            | <b>−{imp['drop_pct']}%</b> | −{imp['lost_units']} units</span>
                            <span style="color:{sev_color};font-size:11px;font-weight:600">{imp['severity'].upper()}</span>
                        </div>""",unsafe_allow_html=True)

            # Impact chart
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">Fulfillment Before vs After</div>',unsafe_allow_html=True)
            st.plotly_chart(draw_impact_chart(result["impact"]),use_container_width=True)

            # Alternate paths (graph-based)
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">Alternate Supply Routes (Network Paths)</div>',unsafe_allow_html=True)
            if result["alt_paths"]:
                for d_id,paths in result["alt_paths"].items():
                    if paths:
                        st.markdown(f"**{sc.nodes[d_id].name}** — {len(paths)} alternate route(s)")
                        for i,p in enumerate(paths,1):
                            st.markdown(f'<div class="card"><b>Route {i}</b> | Cost: {p["cost"]} | {" → ".join(p["path"])}</div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-r">No network-based alternate routes found.</div>',unsafe_allow_html=True)

            # Safety stock alternatives
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">Safety Stock Alternatives</div>',unsafe_allow_html=True)
            st.caption("Which nodes have sufficient safety stock to cover the shortfall — and can reach the affected demand points?")
            dis_edge=st.session_state.disrupted_edge
            found_any=False
            for d_id,imp in result["impact"].items():
                if imp["drop_pct"]<=0: continue
                shortfall=imp["lost_units"]
                st.markdown(f"**{imp['demand_name']}** — shortfall: {shortfall:.0f} units")
                rows_stock=[]
                for iid in list(inv.items.keys()):
                    alts=inv.find_stock_alternatives(d_id,iid,shortfall,sc,dis_edge)
                    for alt in alts:
                        found_any=True
                        rows_stock.append({
                            "Source Node":alt["node_name"],
                            "Item":inv.items[iid]["name"],
                            "Available Stock":f"{alt['available']:.0f}",
                            "Covers Shortfall":"Yes" if alt["can_cover"] else f"Partial ({alt['coverage_pct']}%)",
                            "Route":" → ".join(alt["path"]),
                            "Route Cost":alt["route_cost"],
                            "Coverage Days":alt.get("coverage_days","—"),
                        })
                if rows_stock:
                    df_stock=pd.DataFrame(rows_stock)
                    def cov_color(val):
                        return "background-color:#D5F5E3;font-weight:600" if val=="Yes" else "background-color:#FDEBD0"
                    st.dataframe(df_stock.style.applymap(cov_color,subset=["Covers Shortfall"]),
                        use_container_width=True,hide_index=True)
                else:
                    st.markdown('<div class="alert-a">No nodes have above-safety-stock available for any item.</div>',unsafe_allow_html=True)
                st.markdown("")

            # Network map
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">Network View — Disruption Highlighted</div>',unsafe_allow_html=True)
            alt_hi=[]
            if result["alt_paths"]:
                first=[v for v in result["alt_paths"].values() if v]
                if first and first[0]: alt_hi=first[0][0].get("path_ids",[])
            st.plotly_chart(draw_supply_chain(sc,alt_hi,st.session_state.disrupted_edge,True,
                [d for d in st.session_state.dispatch_log if d.get("status")=="In Transit"]),
                use_container_width=True)
            if st.button("Reset Simulation"):
                st.session_state.disruption_result=None
                st.session_state.disrupted_edge=None
                st.session_state.highlight_path=[]; st.rerun()


# ══════════ TAB 4 — RISK HEATMAP ═════════════════════
with t4:
    st.markdown('<div class="sec-hdr">Network Risk Heatmap</div>',unsafe_allow_html=True)
    st.caption("Visual risk matrix showing which nodes carry the highest exposure based on connection criticality.")
    if not sc.edges:
        st.info("Add connections to view the risk heatmap.")
    else:
        if st.session_state.ranking is None:
            st.info("Run the Stress Test first (from Criticality tab) to populate the heatmap, or click below.")
            if st.button("Run Stress Test & Generate Heatmap"):
                with st.spinner("Analysing all connections..."):
                    st.session_state.ranking=sc.rank_critical_edges(); st.rerun()
        if st.session_state.ranking:
            ranking=st.session_state.ranking
            st.plotly_chart(draw_risk_heatmap(sc,ranking),use_container_width=True)

            # Risk summary per node
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">Node Risk Summary</div>',unsafe_allow_html=True)
            rows=[]
            for nid,node in sc.nodes.items():
                out=[r for r in ranking if r["source"]==nid]
                inn=[r for r in ranking if r["target"]==nid]
                max_drop=max([r["avg_fulfillment_drop"] for r in out+inn],default=0)
                n_crit=sum(1 for r in out+inn if r["severity"]=="critical")
                risk_lvl="Critical" if max_drop>=50 else "High" if max_drop>=25 else "Medium" if max_drop>=5 else "Low"
                rows.append({"Node":node.name,"Type":node.node_type.capitalize(),
                             "Max Drop If Link Fails":f"{max_drop:.0f}%",
                             "Critical Links":n_crit,"Risk Level":risk_lvl})
            df=pd.DataFrame(rows).sort_values("Max Drop If Link Fails",ascending=False)
            def rl_color(v):
                c={"Critical":"#FADBD8","High":"#FDEBD0","Medium":"#D6EAF8","Low":"#D5F5E3"}
                return f"background-color:{c.get(v,'white')}"
            st.dataframe(df.style.applymap(rl_color,subset=["Risk Level"]),
                use_container_width=True,hide_index=True)

            # Criticality bar chart
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">Connection Criticality Ranking</div>',unsafe_allow_html=True)
            st.plotly_chart(draw_criticality_chart(ranking),use_container_width=True)
            st.markdown('<div class="sec-hdr">Recommendations</div>',unsafe_allow_html=True)
            for sev,cls,label in [("critical","alert-r","Immediate Action"),("high","alert-a","High Priority"),("low","alert-g","Well Redundant")]:
                items=[r for r in ranking if r["severity"]==sev]
                if items:
                    links="".join(f"<li>{r['label']}</li>" for r in items)
                    st.markdown(f'<div class="{cls}"><b>{label} ({len(items)} links):</b><ul style="margin:5px 0 0 16px">{links}</ul></div>',unsafe_allow_html=True)


# ══════════ TAB 5 — DISPATCH LOG ═════════════════════
with t5:
    st.markdown('<div class="sec-hdr">Dispatch Log — Live Goods Movement</div>',unsafe_allow_html=True)
    st.caption("Record goods dispatches between nodes. In-Transit dispatches are highlighted on the network map.")

    # Log new dispatch
    with st.form("dispatch_form"):
        st.markdown("**Log New Dispatch**")
        c1,c2,c3=st.columns(3)
        node_names_all=[n.name for n in sc.nodes.values()]
        d_from=c1.selectbox("From Node",node_names_all,key="df")
        d_to  =c2.selectbox("To Node",  node_names_all,key="dt",index=min(1,len(node_names_all)-1))
        all_items={inv.items[iid]["name"]:iid for iid in inv.items} if inv.items else {"No items":""}
        d_item=c3.selectbox("Item",list(all_items.keys()),key="di")
        c1b,c2b,c3b=st.columns(3)
        d_qty =c1b.number_input("Quantity",min_value=0.1,value=50.0,key="dq")
        d_status=c2b.selectbox("Status",["In Transit","Delivered","Delayed"],key="ds")
        d_note=c3b.text_input("Notes",placeholder="Optional notes",key="dn")
        if st.form_submit_button("Log Dispatch",use_container_width=True):
            from_id=[n.id for n in sc.nodes.values() if n.name==d_from]
            to_id  =[n.id for n in sc.nodes.values() if n.name==d_to]
            iid=all_items.get(d_item,"")
            if from_id and to_id:
                # update stock
                if d_status in ("In Transit","Delivered") and iid:
                    inv.update_stock(from_id[0],iid,-d_qty)
                if d_status=="Delivered" and iid:
                    inv.update_stock(to_id[0],iid,d_qty)
                st.session_state.dispatch_log.append({
                    "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "from_node":d_from,"to_node":d_to,
                    "from_id":from_id[0],"to_id":to_id[0],
                    "item":d_item,"item_id":iid,
                    "quantity":d_qty,"status":d_status,"notes":d_note})
                st.success(f"Dispatch logged: {d_qty:.0f} units of {d_item}"); st.rerun()

    # Show log
    if st.session_state.dispatch_log:
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">All Dispatches</div>',unsafe_allow_html=True)
        log_df=pd.DataFrame(st.session_state.dispatch_log[::-1])
        cols_show=["timestamp","from_node","to_node","item","quantity","status","notes"]
        log_df=log_df[[c for c in cols_show if c in log_df.columns]]
        log_df.columns=["Time","From","To","Item","Qty","Status","Notes"][:len(log_df.columns)]
        def status_style(v):
            c={"In Transit":"#D6EAF8","Delivered":"#D5F5E3","Delayed":"#FADBD8"}
            return f"background-color:{c.get(v,'white')};font-weight:600"
        st.dataframe(log_df.style.applymap(status_style,subset=["Status"]),
            use_container_width=True,hide_index=True)

        # Summary
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        in_transit=[d for d in st.session_state.dispatch_log if d["status"]=="In Transit"]
        delivered=[d for d in st.session_state.dispatch_log if d["status"]=="Delivered"]
        delayed=[d for d in st.session_state.dispatch_log if d["status"]=="Delayed"]
        c1.markdown(f'<div class="kpi-card" style="border-left-color:#2980B9"><div class="kpi-label">In Transit</div><div class="kpi-value">{len(in_transit)}</div></div>',unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card" style="border-left-color:#1A8A4A"><div class="kpi-label">Delivered</div><div class="kpi-value">{len(delivered)}</div></div>',unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-card" style="border-left-color:#C0392B"><div class="kpi-label">Delayed</div><div class="kpi-value">{len(delayed)}</div></div>',unsafe_allow_html=True)

        if st.button("Clear Dispatch Log"):
            st.session_state.dispatch_log=[]; st.rerun()
    else:
        st.markdown('<div class="card" style="text-align:center;color:#7F8C8D">No dispatches logged yet. Use the form above to record goods movement.</div>',unsafe_allow_html=True)


# ══════════ TAB 6 — ATP & SCORECARD ══════════════════
with t6:
    sub1,sub2=st.tabs(["Available-to-Promise (ATP)","Supplier Scorecard"])

    with sub1:
        st.markdown('<div class="sec-hdr">Available-to-Promise Analysis</div>',unsafe_allow_html=True)
        st.caption("Enter an item and required quantity to find which nodes can promise fulfillment.")
        c1,c2,c3=st.columns([2,1,1])
        atp_items={inv.items[iid]["name"]:iid for iid in inv.items} if inv.items else {}
        atp_item=c1.selectbox("Item",list(atp_items.keys()) or ["No items"],key="atp_item")
        atp_qty=c2.number_input("Required Quantity",min_value=1.0,value=100.0,key="atp_qty")
        atp_dest=c3.selectbox("For demand point",
            [n.name for n in sc.nodes.values() if n.node_type=="demand"],key="atp_dest")
        if st.button("Check Availability",use_container_width=True):
            iid=atp_items.get(atp_item,"")
            d_id=[n.id for n in sc.nodes.values() if n.name==atp_dest]
            if iid and d_id:
                alts=inv.find_stock_alternatives(d_id[0],iid,atp_qty,sc)
                if alts:
                    st.markdown(f"<br>**ATP results for {atp_item} — {atp_qty:.0f} units to {atp_dest}:**",unsafe_allow_html=True)
                    for i,a in enumerate(alts,1):
                        status_cls="alert-g" if a["can_cover"] else "alert-a"
                        badge_cls="badge-g" if a["can_cover"] else "badge-a"
                        status_txt="Can Fulfill" if a["can_cover"] else f"Partial — {a['coverage_pct']}%"
                        st.markdown(f"""<div class="{status_cls}">
                            <b>Option {i}: {a['node_name']}</b> &nbsp;
                            <span class="{badge_cls}">{status_txt}</span><br>
                            Available: <b>{a['available']:.0f}</b> units above safety stock &nbsp;|&nbsp;
                            Coverage Days: {a['coverage_days']} &nbsp;|&nbsp;
                            Route: {" → ".join(a['path'])} &nbsp;|&nbsp; Cost: {a['route_cost']}
                        </div>""",unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alert-r">No nodes can fulfil this request with available stock.</div>',unsafe_allow_html=True)

    with sub2:
        st.markdown('<div class="sec-hdr">Supplier & Node Performance Scorecard</div>',unsafe_allow_html=True)
        st.caption("Rate each plant and warehouse on key performance indicators. Scores are stored per session.")
        scores=st.session_state.scores
        node_options=[n for n in sc.nodes.values() if n.node_type in ("plant","warehouse")]
        if node_options:
            sel_node_name=st.selectbox("Select node to view / edit",
                [n.name for n in node_options],key="sc_sel")
            sel_nid=[n.id for n in node_options if n.name==sel_node_name]
            if sel_nid:
                nid=sel_nid[0]
                if nid not in scores:
                    scores[nid]={"reliability":80,"lead_time":80,"quality":80,"cost_efficiency":80}
                s=scores[nid]
                c1,c2=st.columns([1,1])
                with c1:
                    st.markdown("**Edit Scores (0–100)**")
                    s["reliability"]    =st.slider("Reliability",0,100,int(s["reliability"]),key=f"sr_{nid}")
                    s["lead_time"]      =st.slider("Lead Time Performance",0,100,int(s["lead_time"]),key=f"sl_{nid}")
                    s["quality"]        =st.slider("Quality",0,100,int(s["quality"]),key=f"sq_{nid}")
                    s["cost_efficiency"]=st.slider("Cost Efficiency",0,100,int(s["cost_efficiency"]),key=f"sc_{nid}")
                    overall=round((s["reliability"]+s["lead_time"]+s["quality"]+s["cost_efficiency"])/4,1)
                    grade="A" if overall>=90 else "B" if overall>=75 else "C" if overall>=60 else "D"
                    badge_c="badge-g" if grade=="A" else "badge-b" if grade=="B" else "badge-a" if grade=="C" else "badge-r"
                    st.markdown(f"<br><b>Overall Score: {overall}</b> &nbsp; <span class='{badge_c}'>Grade {grade}</span>",unsafe_allow_html=True)
                with c2:
                    st.plotly_chart(draw_scorecard_radar(sel_node_name,s),use_container_width=True)

            # Overall ranking table
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">All Nodes Ranking</div>',unsafe_allow_html=True)
            sc_rows=[]
            for node in node_options:
                if node.id in scores:
                    s=scores[node.id]
                    ov=round((s["reliability"]+s["lead_time"]+s["quality"]+s["cost_efficiency"])/4,1)
                    grade="A" if ov>=90 else "B" if ov>=75 else "C" if ov>=60 else "D"
                    sc_rows.append({"Node":node.name,"Type":node.node_type.capitalize(),
                        "Reliability":s["reliability"],"Lead Time":s["lead_time"],
                        "Quality":s["quality"],"Cost Efficiency":s["cost_efficiency"],
                        "Overall":ov,"Grade":grade})
            if sc_rows:
                sc_df=pd.DataFrame(sc_rows).sort_values("Overall",ascending=False)
                def grade_color(v):
                    c={"A":"#D5F5E3","B":"#D6EAF8","C":"#FDEBD0","D":"#FADBD8"}
                    return f"background-color:{c.get(v,'white')};font-weight:600"
                st.dataframe(sc_df.style.applymap(grade_color,subset=["Grade"]),
                    use_container_width=True,hide_index=True)


# ══════════ TAB 7 — GEOGRAPHIC VIEW ══════════════════
with t7:
    st.markdown('<div class="sec-hdr">Geographic Network View</div>',unsafe_allow_html=True)
    c1,_=st.columns([3,1])
    map_scope=_.radio("Scope",["India","World"],key="geo_scope")
    nodes_with_coords=[n for n in sc.nodes.values() if n.x!=0 or n.y!=0]
    if not nodes_with_coords:
        st.info("No coordinates found. Load the demo supply chain to see the India map.")
    else:
        st.plotly_chart(draw_geo_map(sc,map_scope.lower()),use_container_width=True)
        with st.expander("Node Coordinates Reference"):
            st.dataframe(pd.DataFrame([{"Node":n.name,"Type":n.node_type,"Lat":n.y,"Lon":n.x,"Location":n.location}
                for n in sc.nodes.values()]),use_container_width=True,hide_index=True)
