"""
Supply Chain & Operations Helper v5.0
SR — Supply Chain Intelligence Platform
All improvements: Custom Logo, Transport Logic, Green-Red Heatmap,
Report Generation, Free AI (Groq), Enhanced UI
"""

# ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import json, math, io, re, requests
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils import get_column_letter
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# CUSTOM SVG LOGO (SR + Supply Chain Network)
# ═══════════════════════════════════════════════════════════════
LOGO_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120' width='60' height='60'>
  <defs>
    <linearGradient id='bg' x1='0%' y1='0%' x2='100%' y2='100%'>
      <stop offset='0%' style='stop-color:#1B4F72'/>
      <stop offset='100%' style='stop-color:#0F6E56'/>
    </linearGradient>
  </defs>
  <circle cx='60' cy='60' r='58' fill='url(#bg)' stroke='#FFFFFF' stroke-width='2.5'/>
  <circle cx='30' cy='38' r='8' fill='#F39C12' stroke='white' stroke-width='1.5'/>
  <circle cx='60' cy='22' r='8' fill='#27AE60' stroke='white' stroke-width='1.5'/>
  <circle cx='90' cy='38' r='8' fill='#E74C3C' stroke='white' stroke-width='1.5'/>
  <circle cx='38' cy='68' r='8' fill='#9B59B6' stroke='white' stroke-width='1.5'/>
  <circle cx='82' cy='68' r='8' fill='#2980B9' stroke='white' stroke-width='1.5'/>
  <circle cx='60' cy='88' r='8' fill='#F39C12' stroke='white' stroke-width='1.5'/>
  <line x1='30' y1='38' x2='60' y2='22' stroke='#F8C471' stroke-width='2.5'/>
  <line x1='60' y1='22' x2='90' y2='38' stroke='#7DCEA0' stroke-width='2.5'/>
  <line x1='30' y1='38' x2='38' y2='68' stroke='#F8C471' stroke-width='2.5'/>
  <line x1='90' y1='38' x2='82' y2='68' stroke='#7DCEA0' stroke-width='2.5'/>
  <line x1='38' y1='68' x2='60' y2='88' stroke='#AED6F1' stroke-width='2.5'/>
  <line x1='82' y1='68' x2='60' y2='88' stroke='#AED6F1' stroke-width='2.5'/>
  <line x1='38' y1='68' x2='82' y2='68' stroke='white' stroke-width='1.5' opacity='0.5' stroke-dasharray='3,2'/>
  <text x='60' y='110' text-anchor='middle' font-family='Arial,sans-serif' font-size='13' font-weight='900' fill='white' letter-spacing='3'>SR</text>
</svg>"""

LOGO_SIDEBAR = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120' width='42' height='42'>
  <defs><linearGradient id='bg2' x1='0%' y1='0%' x2='100%' y2='100%'><stop offset='0%' style='stop-color:#1B4F72'/><stop offset='100%' style='stop-color:#0F6E56'/></linearGradient></defs>
  <circle cx='60' cy='60' r='58' fill='url(#bg2)' stroke='#FFFFFF' stroke-width='2'/>
  <circle cx='30' cy='38' r='7' fill='#F39C12' stroke='white' stroke-width='1.5'/>
  <circle cx='60' cy='22' r='7' fill='#27AE60' stroke='white' stroke-width='1.5'/>
  <circle cx='90' cy='38' r='7' fill='#E74C3C' stroke='white' stroke-width='1.5'/>
  <circle cx='38' cy='68' r='7' fill='#9B59B6' stroke='white' stroke-width='1.5'/>
  <circle cx='82' cy='68' r='7' fill='#2980B9' stroke='white' stroke-width='1.5'/>
  <circle cx='60' cy='88' r='7' fill='#F39C12' stroke='white' stroke-width='1.5'/>
  <line x1='30' y1='38' x2='60' y2='22' stroke='#F8C471' stroke-width='2'/>
  <line x1='60' y1='22' x2='90' y2='38' stroke='#7DCEA0' stroke-width='2'/>
  <line x1='30' y1='38' x2='38' y2='68' stroke='#F8C471' stroke-width='2'/>
  <line x1='90' y1='38' x2='82' y2='68' stroke='#7DCEA0' stroke-width='2'/>
  <line x1='38' y1='68' x2='60' y2='88' stroke='#AED6F1' stroke-width='2'/>
  <line x1='82' y1='68' x2='60' y2='88' stroke='#AED6F1' stroke-width='2'/>
  <text x='60' y='110' text-anchor='middle' font-family='Arial,sans-serif' font-size='12' font-weight='900' fill='white' letter-spacing='2'>SR</text>
</svg>"""

# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════
@dataclass
class Node:
    id: str; name: str; node_type: str; capacity: float
    location: str = ""; x: float = 0.0; y: float = 0.0

@dataclass
class Edge:
    source: str; target: str; capacity: float
    cost: float = 1.0; active: bool = True

# ═══════════════════════════════════════════════════════════════
# TRANSPORT LOGIC
# ═══════════════════════════════════════════════════════════════
TRANSPORT_MODES = {
    "road":  {"speed_kmh": 60,  "cost_per_km": 2.5,  "label": "Road (Truck)",  "icon": "🚛"},
    "rail":  {"speed_kmh": 80,  "cost_per_km": 1.2,  "label": "Rail",          "icon": "🚂"},
    "air":   {"speed_kmh": 800, "cost_per_km": 12.0,  "label": "Air",           "icon": "✈️"},
    "sea":   {"speed_kmh": 35,  "cost_per_km": 0.8,  "label": "Sea/Inland",    "icon": "🚢"},
}

def haversine_km(lat1, lon1, lat2, lon2):
    """Distance between two lat/lon points in km"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def get_state(location_str):
    """Extract state from 'City, State' format"""
    parts = location_str.split(",")
    return parts[-1].strip().lower() if len(parts) > 1 else location_str.strip().lower()

def recommend_transport(src_node, tgt_node, load_units, urgent=False):
    """
    Smart transport mode recommendation based on:
    - Same city/state → road
    - Load size → truck / rail / air
    - Urgent → air
    - Distance → affects mode
    """
    src_loc = src_node.location; tgt_loc = tgt_node.location
    src_state = get_state(src_loc); tgt_state = get_state(tgt_loc)
    same_state = (src_state == tgt_state)

    # Compute distance if coordinates available
    dist_km = 0
    if src_node.x and src_node.y and tgt_node.x and tgt_node.y:
        dist_km = haversine_km(src_node.y, src_node.x, tgt_node.y, tgt_node.x)

    recommendations = []

    if urgent:
        mode = "air"
        reason = "Urgent delivery — air freight selected"
    elif same_state or dist_km < 150:
        mode = "road"
        reason = "Same region — road transport (cheapest)"
    elif load_units >= 500:
        mode = "rail"
        reason = f"High load ({load_units} units) — rail preferred"
    elif load_units >= 150:
        # Offer both
        mode = "rail"
        reason = f"Medium load ({load_units} units) — rail recommended"
    else:
        mode = "road"
        reason = f"Small load ({load_units} units) — road (truck)"

    m = TRANSPORT_MODES[mode]
    if dist_km > 0:
        cost = dist_km * m["cost_per_km"]
        hours = dist_km / m["speed_kmh"]
        days = hours / 24
    else:
        cost = None; hours = None; days = None

    return {
        "mode": mode, "label": m["label"], "icon": m["icon"],
        "reason": reason, "dist_km": round(dist_km, 1) if dist_km else None,
        "cost_estimate": round(cost, 0) if cost else None,
        "hours": round(hours, 1) if hours else None,
        "days": round(days, 2) if days else None,
        "same_state": same_state,
    }

# ═══════════════════════════════════════════════════════════════
# GRAPH ENGINE
# ═══════════════════════════════════════════════════════════════
class SupplyChainGraph:
    def __init__(self):
        self.nodes: dict = {}
        self.edges: list = []

    def add_node(self, node): self.nodes[node.id] = node

    def add_edge(self, edge):
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError(f"Node {edge.source} or {edge.target} not found")
        for e in self.edges:
            if e.source == edge.source and e.target == edge.target: return
        self.edges.append(edge)

    def remove_edge(self, src, tgt):
        self.edges = [e for e in self.edges if not (e.source==src and e.target==tgt)]

    def toggle_edge(self, src, tgt, active):
        for e in self.edges:
            if e.source==src and e.target==tgt: e.active = active

    def to_nx(self):
        G = nx.DiGraph()
        for nid, n in self.nodes.items(): G.add_node(nid, **vars(n))
        for e in self.edges:
            if e.active:
                G.add_edge(e.source, e.target, capacity=e.capacity, weight=e.cost)
        return G

    def geo_shortest_path(self, src, tgt):
        """Shortest path using real lat/lon distances as weights"""
        G = nx.DiGraph()
        for nid, n in self.nodes.items(): G.add_node(nid, **vars(n))
        for e in self.edges:
            if not e.active: continue
            sn = self.nodes[e.source]; tn = self.nodes[e.target]
            if sn.x and sn.y and tn.x and tn.y:
                dist = haversine_km(sn.y, sn.x, tn.y, tn.x)
                w = dist if dist > 0 else e.cost
            else:
                w = e.cost
            G.add_edge(e.source, e.target, capacity=e.capacity, weight=w, cost=e.cost)
        try:
            path = nx.dijkstra_path(G, src, tgt, weight="weight")
            total_dist = sum(
                haversine_km(self.nodes[path[i]].y, self.nodes[path[i]].x,
                             self.nodes[path[i+1]].y, self.nodes[path[i+1]].x)
                if (self.nodes[path[i]].x and self.nodes[path[i+1]].x) else 0
                for i in range(len(path)-1)
            )
            total_cost = sum(G[path[i]][path[i+1]].get("cost", 1) for i in range(len(path)-1))
            return {"found": True, "path": path, "dist_km": round(total_dist, 1), "cost": round(total_cost, 2)}
        except:
            return {"found": False, "path": [], "dist_km": None, "cost": None}

    def shortest_path(self, src, tgt):
        return self.geo_shortest_path(src, tgt)

    def all_shortest_paths(self, src, tgt, k=3):
        G = self.to_nx(); results = []
        try:
            for path in nx.shortest_simple_paths(G, src, tgt, weight="weight"):
                cost = sum(G[path[i]][path[i+1]]["weight"] for i in range(len(path)-1))
                results.append({"path": path, "cost": round(cost, 2)})
                if len(results) >= k: break
        except: pass
        return results

    def demand_fulfillment(self):
        G = self.to_nx()
        plants  = [n for n, d in self.nodes.items() if d.node_type=="plant"]
        demands = [n for n, d in self.nodes.items() if d.node_type=="demand"]
        results = {}
        for d_id in demands:
            req = self.nodes[d_id].capacity; total, reach = 0.0, []
            for p in plants:
                try:
                    fv, _ = nx.maximum_flow(G, p, d_id, capacity="capacity")
                    if fv > 0: total += fv; reach.append(p)
                except: pass
            ful = min(total, req)
            results[d_id] = {"required": req, "fulfilled": round(ful, 2),
                             "pct": round(ful/req*100 if req>0 else 100, 1),
                             "reachable_from": reach}
        return results

    def simulate_disruption(self, src, tgt):
        baseline = self.demand_fulfillment()
        self.toggle_edge(src, tgt, False)
        disrupted = self.demand_fulfillment()
        self.toggle_edge(src, tgt, True)
        impact = {}
        for d_id, base in baseline.items():
            dis = disrupted[d_id]; drop = base["pct"] - dis["pct"]
            impact[d_id] = {
                "demand_name": self.nodes[d_id].name,
                "before_pct": base["pct"], "after_pct": dis["pct"],
                "drop_pct": round(drop,1), "before_fulfilled": base["fulfilled"],
                "after_fulfilled": dis["fulfilled"],
                "lost_units": round(base["fulfilled"]-dis["fulfilled"],2),
                "severity": "critical" if drop>=50 else "high" if drop>=25 else "medium" if drop>0 else "none"
            }
        alt_paths = {}
        for d_id, imp in impact.items():
            if imp["drop_pct"] > 0:
                self.toggle_edge(src, tgt, False)
                paths = []
                for p in [n for n, nd in self.nodes.items() if nd.node_type=="plant"]:
                    r = self.shortest_path(p, d_id)
                    if r["found"]:
                        paths.append({"from_plant": self.nodes[p].name,
                                      "path": [self.nodes[n].name for n in r["path"]],
                                      "path_ids": r["path"], "cost": r["cost"]})
                paths.sort(key=lambda x: x["cost"])
                alt_paths[d_id] = paths[:3]
                self.toggle_edge(src, tgt, True)
        avg_drop = sum(v["drop_pct"] for v in impact.values())/len(impact) if impact else 0
        return {"removed_edge": f"{self.nodes[src].name} → {self.nodes[tgt].name}",
                "removed_src": src, "removed_tgt": tgt,
                "resilience_score": round(max(0, 100-avg_drop), 1),
                "impact": impact, "alt_paths": alt_paths}

    def rank_critical_edges(self):
        ranking = []
        for e in self.edges:
            if not e.active: continue
            r = self.simulate_disruption(e.source, e.target)
            avg = sum(v["drop_pct"] for v in r["impact"].values())/len(r["impact"]) if r["impact"] else 0
            ranking.append({"source":e.source,"target":e.target,"label":r["removed_edge"],
                "avg_fulfillment_drop":round(avg,1),"resilience_score":r["resilience_score"],
                "severity":"critical" if avg>=50 else "high" if avg>=25 else "medium" if avg>=5 else "low"})
        return sorted(ranking, key=lambda x: x["avg_fulfillment_drop"], reverse=True)

    def to_dict(self):
        return {"nodes":[vars(n) for n in self.nodes.values()],"edges":[vars(e) for e in self.edges]}


# ═══════════════════════════════════════════════════════════════
# INVENTORY MANAGER
# ═══════════════════════════════════════════════════════════════
class InventoryManager:
    def __init__(self):
        self.items = {}; self.stock = {}

    def add_item(self, iid, name, unit="units"):
        self.items[iid] = {"name": name, "unit": unit}

    def set_stock(self, node_id, iid, current, safety, reorder, daily_demand=1.0):
        if node_id not in self.stock: self.stock[node_id] = {}
        self.stock[node_id][iid] = {"current":float(current),"safety":float(safety),
                                     "reorder":float(reorder),"daily_demand":float(daily_demand)}

    def update_stock(self, node_id, iid, delta):
        if node_id in self.stock and iid in self.stock[node_id]:
            self.stock[node_id][iid]["current"] = max(0.0, self.stock[node_id][iid]["current"]+delta)
            return True
        return False

    def coverage_days(self, node_id, iid):
        if node_id in self.stock and iid in self.stock[node_id]:
            s = self.stock[node_id][iid]; dd = s.get("daily_demand",1)
            return round(s["current"]/dd,1) if dd>0 else 999
        return None

    def get_alerts(self, sc_nodes=None):
        alerts = []
        for node_id, items in self.stock.items():
            nn = sc_nodes[node_id].name if sc_nodes and node_id in sc_nodes else node_id
            for iid, s in items.items():
                iname = self.items.get(iid,{}).get("name",iid)
                if s["current"] <= s["reorder"]:
                    alerts.append({"node_id":node_id,"node_name":nn,"item_id":iid,"item_name":iname,
                        "level":"critical" if s["current"]<=s["safety"] else "warning",
                        "current":s["current"],"safety":s["safety"],"reorder":s["reorder"],
                        "coverage":self.coverage_days(node_id,iid)})
        return sorted(alerts, key=lambda x:(x["level"]!="critical", x["coverage"] or 999))

    def find_alternatives(self, demand_id, iid, required, sc, disrupted=None):
        alts = []
        for node_id, items in self.stock.items():
            if node_id==demand_id or iid not in items: continue
            s=items[iid]; avail=max(0.0, s["current"]-s["safety"])
            if avail<=0: continue
            if disrupted: sc.toggle_edge(disrupted[0], disrupted[1], False)
            r = sc.shortest_path(node_id, demand_id)
            if disrupted: sc.toggle_edge(disrupted[0], disrupted[1], True)
            if r["found"]:
                alts.append({"node_id":node_id,
                    "node_name":sc.nodes[node_id].name if node_id in sc.nodes else node_id,
                    "available":avail,"can_cover":avail>=required,
                    "coverage_pct":min(100, round(avail/max(required,1)*100,1)),
                    "path":[sc.nodes[n].name for n in r["path"] if n in sc.nodes],
                    "path_ids":r["path"],"route_cost":r["cost"],
                    "coverage_days":self.coverage_days(node_id,iid)})
        return sorted(alts, key=lambda x:(-x["coverage_pct"], x["route_cost"]))[:5]

    def to_df(self, sc_nodes=None):
        rows = []
        for node_id, items in self.stock.items():
            nn = sc_nodes[node_id].name if sc_nodes and node_id in sc_nodes else node_id
            nt = sc_nodes[node_id].node_type if sc_nodes and node_id in sc_nodes else ""
            for iid, s in items.items():
                iname=self.items.get(iid,{}).get("name",iid); unit=self.items.get(iid,{}).get("unit","units")
                dd=s.get("daily_demand",1); cov=round(s["current"]/dd,1) if dd>0 else 999
                status="Critical" if s["current"]<=s["safety"] else "Low" if s["current"]<=s["reorder"] else "Normal"
                rows.append({"Node":nn,"Type":nt.capitalize(),"Item":iname,"Unit":unit,
                    "Current Stock":s["current"],"Safety Stock":s["safety"],"Reorder Point":s["reorder"],
                    "Daily Demand":dd,"Coverage Days":cov,
                    "Available (above safety)":max(0,s["current"]-s["safety"]),"Status":status})
        return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════
# DEMAND FORECASTER
# ═══════════════════════════════════════════════════════════════
class DemandForecaster:
    def __init__(self):
        self.models={}; self.history={}; self.forecasts={}; self.metrics={}

    def generate_synthetic_history(self, node_id, node_name, base_demand, days=365, seed=None):
        if seed is None: seed=hash(node_id)%1000
        np.random.seed(seed); t=np.arange(days)
        demand=np.maximum(0, base_demand+0.05*t+base_demand*0.15*np.sin(2*np.pi*t/7)+
                          base_demand*0.20*np.sin(2*np.pi*t/365)+np.random.normal(0,base_demand*0.08,days))
        dates=[datetime.today()-timedelta(days=days-i) for i in range(days)]
        df=pd.DataFrame({"date":dates,"demand":demand,"node_id":node_id,"node_name":node_name})
        self.history[node_id]=df; return df

    def _make_features(self, y, lags=[1,7,14,30]):
        ml=max(lags); X,yo=[],[]
        for i in range(ml, len(y)):
            feats=[i,i%7,i%30,i//30]
            for lag in lags: feats.append(float(y[i-lag]))
            feats.append(float(np.mean(y[max(0,i-7):i]))); feats.append(float(np.mean(y[max(0,i-30):i])))
            X.append(feats); yo.append(float(y[i]))
        return np.array(X,dtype=float), np.array(yo,dtype=float)

    def train(self, node_id, horizon=30):
        if node_id not in self.history: return None
        df=self.history[node_id]; y=df["demand"].values
        X,yt=self._make_features(y); split=max(int(len(X)*0.80),1)
        rf=RandomForestRegressor(n_estimators=100,max_depth=6,random_state=42,n_jobs=-1)
        gbm=GradientBoostingRegressor(n_estimators=80,max_depth=4,learning_rate=0.1,random_state=42)
        rf.fit(X[:split],yt[:split]); gbm.fit(X[:split],yt[:split])
        if split<len(X):
            ep=0.5*rf.predict(X[split:])+0.5*gbm.predict(X[split:])
            yv=yt[split:]
            rmse=float(np.sqrt(mean_squared_error(yv,ep))); mae=float(mean_absolute_error(yv,ep))
            mape=float(np.mean(np.abs((yv-ep)/(yv+1e-6)))*100)
            r2=float(1-np.sum((yv-ep)**2)/np.sum((yv-np.mean(yv))**2))
        else:
            rmse=0;mae=0;mape=0;r2=1
        self.models[node_id]=(rf,gbm)
        self.metrics[node_id]={"rmse":round(rmse,2),"mae":round(mae,2),"mape":round(mape,2),"r2":round(r2,3)}
        hv=list(y); fp=[]
        for step in range(horizon):
            i=len(hv); lags=[1,7,14,30]
            feats=[i,i%7,i%30,i//30]
            for lag in lags: feats.append(float(hv[-lag]) if lag<=len(hv) else float(np.mean(hv[-min(lag,len(hv)):])))
            feats.append(float(np.mean(hv[-7:]))); feats.append(float(np.mean(hv[-30:])))
            arr=np.array(feats,dtype=float).reshape(1,-1)
            pred=max(0, 0.5*rf.predict(arr)[0]+0.5*gbm.predict(arr)[0])
            fp.append(pred); hv.append(pred)
        ld=df["date"].iloc[-1]; fd=[ld+timedelta(days=i+1) for i in range(horizon)]
        fdf=pd.DataFrame({"date":fd,"forecast":fp,"node_id":node_id,"node_name":df["node_name"].iloc[0]})
        fdf["upper"]=fdf["forecast"]+1.5*rmse; fdf["lower"]=np.maximum(0,fdf["forecast"]-1.5*rmse)
        self.forecasts[node_id]=fdf; return fdf

    def aggregate_to_warehouses(self, sc, horizon=30):
        wh_fc={}
        for wid, wh in sc.nodes.items():
            if wh.node_type!="warehouse": continue
            G=sc.to_nx(); served=[]
            for did, d in sc.nodes.items():
                if d.node_type=="demand":
                    try: nx.shortest_path(G,wid,did); served.append(did)
                    except: pass
            total=np.zeros(horizon)
            for did in served:
                if did in self.forecasts:
                    vals=self.forecasts[did]["forecast"].values[:horizon]; total[:len(vals)]+=vals
            wh_fc[wid]={"name":wh.name,"forecast":total.tolist(),"served_demands":served}
        return wh_fc

    def get_plant_requirements(self, sc, wh_fc, horizon=30):
        pr={}
        for pid, p in sc.nodes.items():
            if p.node_type!="plant": continue
            G=sc.to_nx(); served=[]
            for wid in wh_fc:
                try: nx.shortest_path(G,pid,wid); served.append(wid)
                except: pass
            total=np.zeros(horizon)
            for wid in served: total+=np.array(wh_fc[wid]["forecast"][:horizon])
            pr[pid]={"name":p.name,"required":total.tolist(),"capacity":p.capacity,"served_wh":served}
        return pr


# ═══════════════════════════════════════════════════════════════
# REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════
def generate_excel_report(sc, inv, forecaster, ranking, start_date, end_date):
    """Generate comprehensive Excel report with charts and color coding"""
    wb = openpyxl.Workbook()

    # ── Color fills ──────────────────────────────────────────────
    fill_green  = PatternFill("solid", fgColor="D5F5E3")
    fill_yellow = PatternFill("solid", fgColor="FEF9E7")
    fill_red    = PatternFill("solid", fgColor="FADBD8")
    fill_blue   = PatternFill("solid", fgColor="D6EAF8")
    fill_header = PatternFill("solid", fgColor="1B4F72")
    fill_sub    = PatternFill("solid", fgColor="EBF5FB")

    font_header = Font(bold=True, color="FFFFFF", size=11)
    font_title  = Font(bold=True, size=14, color="1B4F72")
    font_bold   = Font(bold=True, size=10)
    font_normal = Font(size=10)
    align_center= Alignment(horizontal="center", vertical="center")
    align_left  = Alignment(horizontal="left",   vertical="center")
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"),  bottom=Side(style="thin"))

    def style_header_row(ws, row, cols):
        for c in range(1, cols+1):
            cell=ws.cell(row=row, column=c)
            cell.fill=fill_header; cell.font=font_header; cell.alignment=align_center; cell.border=thin_border

    def style_row(ws, row, cols, fill=None):
        for c in range(1, cols+1):
            cell=ws.cell(row=row, column=c)
            if fill: cell.fill=fill
            cell.font=font_normal; cell.border=thin_border; cell.alignment=align_left

    # ════════════════════════════════════════════════
    # SHEET 1 — COVER / SUMMARY
    # ════════════════════════════════════════════════
    ws = wb.active; ws.title = "Report Summary"
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 40

    ws["A1"] = "SUPPLY CHAIN & OPERATIONS REPORT"
    ws["A1"].font = Font(bold=True, size=16, color="1B4F72")
    ws["A2"] = f"Period: {start_date} to {end_date}"
    ws["A2"].font = Font(size=11, color="5D6D7E")
    ws["A3"] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ws["A3"].font = Font(size=10, color="5D6D7E")
    ws["A4"] = "SR — Supply Chain & Operations Helper"
    ws["A4"].font = Font(bold=True, size=10, color="0F6E56")

    ws.append([]); ws.append(["NETWORK SUMMARY"])
    ws["A6"].font = font_title
    plants    = [n for n in sc.nodes.values() if n.node_type=="plant"]
    whs       = [n for n in sc.nodes.values() if n.node_type=="warehouse"]
    demands   = [n for n in sc.nodes.values() if n.node_type=="demand"]
    summary_rows = [
        ("Manufacturing Plants", len(plants)),
        ("Warehouses", len(whs)),
        ("Demand Points", len(demands)),
        ("Network Connections", len(sc.edges)),
        ("Total Plant Capacity", sum(n.capacity for n in plants)),
        ("Total Demand", sum(n.capacity for n in demands)),
        ("Supply Coverage %", round(sum(n.capacity for n in plants)/max(sum(n.capacity for n in demands),1)*100,1)),
    ]
    for r,(label,val) in enumerate(summary_rows, start=7):
        ws[f"A{r}"] = label; ws[f"A{r}"].font = font_bold
        ws[f"B{r}"] = val;   ws[f"B{r}"].font = font_normal
        ws[f"B{r}"].fill = fill_green if isinstance(val, (int,float)) and (label=="Supply Coverage %" and val>=100 or label!="Supply Coverage %") else fill_sub

    # ════════════════════════════════════════════════
    # SHEET 2 — DEMAND FULFILLMENT
    # ════════════════════════════════════════════════
    ws2 = wb.create_sheet("Demand Fulfillment")
    ws2.column_dimensions["A"].width = 22
    ws2.column_dimensions["B"].width = 14
    ws2.column_dimensions["C"].width = 14
    ws2.column_dimensions["D"].width = 14
    ws2.column_dimensions["E"].width = 18
    ws2.column_dimensions["F"].width = 18

    ws2["A1"] = "DEMAND FULFILLMENT ANALYSIS"; ws2["A1"].font = font_title
    ws2["A2"] = f"Period: {start_date} to {end_date}"; ws2["A2"].font = Font(size=10, color="5D6D7E")

    headers = ["Demand Point","Required","Fulfilled","Fulfillment %","Status","Supply Sources"]
    for c,h in enumerate(headers,1): ws2.cell(row=4,column=c,value=h)
    style_header_row(ws2, 4, len(headers))

    ff = sc.demand_fulfillment()
    for r,(did,info) in enumerate(ff.items(), start=5):
        pct=info["pct"]; status="OK" if pct>=90 else "Warning" if pct>=60 else "Shortage"
        fill = fill_green if pct>=90 else fill_yellow if pct>=60 else fill_red
        vals=[sc.nodes[did].name, info["required"], info["fulfilled"], f"{pct}%", status,
              ", ".join(sc.nodes[p].name for p in info["reachable_from"]) or "None"]
        for c,v in enumerate(vals,1):
            ws2.cell(row=r,column=c,value=v)
        style_row(ws2, r, len(headers), fill)

    # ════════════════════════════════════════════════
    # SHEET 3 — INVENTORY
    # ════════════════════════════════════════════════
    ws3 = wb.create_sheet("Inventory Status")
    for col,w in zip("ABCDEFGHIJK",[22,14,16,10,14,14,14,12,14,18,10]):
        ws3.column_dimensions[col].width=w

    ws3["A1"] = "INVENTORY STATUS REPORT"; ws3["A1"].font = font_title
    ws3["A2"] = f"As of: {datetime.now().strftime('%Y-%m-%d')}"; ws3["A2"].font = Font(size=10, color="5D6D7E")

    inv_headers = ["Node","Type","Item","Unit","Current Stock","Safety Stock",
                   "Reorder Point","Daily Demand","Coverage Days","Available","Status"]
    for c,h in enumerate(inv_headers,1): ws3.cell(row=4,column=c,value=h)
    style_header_row(ws3, 4, len(inv_headers))

    inv_df = inv.to_df(sc.nodes)
    for r,row in enumerate(inv_df.itertuples(), start=5):
        status=row.Status
        fill = fill_green if status=="Normal" else fill_blue if status=="Low" else fill_red
        vals=[row.Node,row.Type,row.Item,row.Unit,row._5,row._6,row._7,row._8,row._9,row._10,status]
        for c,v in enumerate(vals,1): ws3.cell(row=r,column=c,value=v)
        style_row(ws3, r, len(inv_headers), fill)

    # ════════════════════════════════════════════════
    # SHEET 4 — RISK ANALYSIS
    # ════════════════════════════════════════════════
    ws4 = wb.create_sheet("Risk Analysis")
    ws4.column_dimensions["A"].width=28; ws4.column_dimensions["B"].width=18
    ws4.column_dimensions["C"].width=16; ws4.column_dimensions["D"].width=14

    ws4["A1"]="RISK ANALYSIS — CRITICAL CONNECTIONS"; ws4["A1"].font=font_title
    ws4.append([]); ws4.append(["Connection","Avg Fulfillment Drop","Resilience Score","Severity"])
    style_header_row(ws4, 3, 4)

    if ranking:
        for r,rec in enumerate(ranking, start=4):
            sev=rec["severity"]
            fill=fill_red if sev=="critical" else fill_yellow if sev=="high" else fill_blue if sev=="medium" else fill_green
            vals=[rec["label"],f"{rec['avg_fulfillment_drop']}%",f"{rec['resilience_score']}%",sev.upper()]
            for c,v in enumerate(vals,1): ws4.cell(row=r,column=c,value=v)
            style_row(ws4, r, 4, fill)

    # Recommendations
    r_start=len(ranking)+6 if ranking else 6
    ws4.cell(row=r_start,column=1,value="RECOMMENDATIONS").font=font_title
    critical=[x for x in ranking if x["severity"]=="critical"] if ranking else []
    high=[x for x in ranking if x["severity"]=="high"] if ranking else []
    recs=[]
    if critical:
        recs.append(f"URGENT: {len(critical)} critical connection(s) are single points of failure. Add redundant paths immediately.")
        for cr in critical: recs.append(f"  → Reinforce: {cr['label']}")
    if high:
        recs.append(f"HIGH: {len(high)} high-risk connections require backup routes.")
    if not critical and not high:
        recs.append("Network shows good resilience. Continue monitoring.")
    for i,rec in enumerate(recs):
        ws4.cell(row=r_start+1+i,column=1,value=rec).font=Font(size=10)

    # ════════════════════════════════════════════════
    # SHEET 5 — FORECASTING
    # ════════════════════════════════════════════════
    ws5 = wb.create_sheet("Demand Forecast")
    ws5.column_dimensions["A"].width=20; ws5.column_dimensions["B"].width=14
    ws5.column_dimensions["C"].width=14; ws5.column_dimensions["D"].width=14
    ws5.column_dimensions["E"].width=14; ws5.column_dimensions["F"].width=14

    ws5["A1"]="DEMAND FORECASTING REPORT"; ws5["A1"].font=font_title

    row_idx=3
    for node_id, fdf in forecaster.forecasts.items():
        ws5.cell(row=row_idx,column=1,value=f"Node: {fdf['node_name'].iloc[0]}").font=font_bold
        row_idx+=1
        if node_id in forecaster.metrics:
            m=forecaster.metrics[node_id]
            ws5.cell(row=row_idx,column=1,value=f"RMSE: {m['rmse']}  MAE: {m['mae']}  R²: {m['r2']}").font=Font(size=9,color="5D6D7E")
            row_idx+=1
        headers5=["Date","Forecast","Lower CI","Upper CI"]
        for c,h in enumerate(headers5,1): ws5.cell(row=row_idx,column=c,value=h)
        style_header_row(ws5, row_idx, 4); row_idx+=1
        for _,frow in fdf.iterrows():
            vals=[str(frow["date"])[:10],round(frow["forecast"],1),round(frow["lower"],1),round(frow["upper"],1)]
            for c,v in enumerate(vals,1): ws5.cell(row=row_idx,column=c,value=v)
            style_row(ws5, row_idx, 4, fill_blue); row_idx+=1
        row_idx+=2

    # ════════════════════════════════════════════════
    # SHEET 6 — SUPPLIER SCORECARD
    # ════════════════════════════════════════════════
    ws6 = wb.create_sheet("Supplier Scorecard")
    ws6.column_dimensions["A"].width=22; ws6.column_dimensions["B"].width=14
    ws6.column_dimensions["C"].width=14; ws6.column_dimensions["D"].width=14
    ws6.column_dimensions["E"].width=16; ws6.column_dimensions["F"].width=12; ws6.column_dimensions["G"].width=10

    ws6["A1"]="SUPPLIER & NODE SCORECARD"; ws6["A1"].font=font_title
    sc_headers=["Node","Type","Reliability","Lead Time","Quality","Cost Efficiency","Grade"]
    for c,h in enumerate(sc_headers,1): ws6.cell(row=3,column=c,value=h)
    style_header_row(ws6, 3, 7)

    scores=st.session_state.get("scores",{})
    row6=4
    for nid, node in sc.nodes.items():
        if node.node_type not in ("plant","warehouse"): continue
        if nid in scores:
            s=scores[nid]
            ov=round((s["reliability"]+s["lead_time"]+s["quality"]+s["cost_efficiency"])/4,1)
            grade="A" if ov>=90 else "B" if ov>=75 else "C" if ov>=60 else "D"
            fill=fill_green if grade=="A" else fill_blue if grade=="B" else fill_yellow if grade=="C" else fill_red
            vals=[node.name,node.node_type.capitalize(),s["reliability"],s["lead_time"],s["quality"],s["cost_efficiency"],grade]
            for c,v in enumerate(vals,1): ws6.cell(row=row6,column=c,value=v)
            style_row(ws6, row6, 7, fill); row6+=1

    # Save
    buf=io.BytesIO(); wb.save(buf); buf.seek(0); return buf.getvalue()


# ═══════════════════════════════════════════════════════════════
# DEMO DATA
# ═══════════════════════════════════════════════════════════════
def load_demo_data():
    sc=SupplyChainGraph()
    sc.add_node(Node("P1","Plant Mumbai",  "plant",    500,"Mumbai, Maharashtra",  72.88,19.08))
    sc.add_node(Node("P2","Plant Chennai", "plant",    400,"Chennai, Tamil Nadu",  80.27,13.08))
    sc.add_node(Node("P3","Plant Pune",    "plant",    350,"Pune, Maharashtra",    73.86,18.52))
    sc.add_node(Node("W1","WH North",  "warehouse",400,"Delhi, Delhi",          77.21,28.61))
    sc.add_node(Node("W2","WH West",   "warehouse",350,"Ahmedabad, Gujarat",    72.57,23.02))
    sc.add_node(Node("W3","WH East",   "warehouse",300,"Kolkata, West Bengal",  88.36,22.57))
    sc.add_node(Node("W4","WH South",  "warehouse",280,"Bangalore, Karnataka",  77.59,12.97))
    sc.add_node(Node("D1","Delhi Market",    "demand",200,"Delhi, Delhi",          77.21,28.61))
    sc.add_node(Node("D2","Jaipur Market",   "demand",120,"Jaipur, Rajasthan",    75.79,26.91))
    sc.add_node(Node("D3","Surat Market",    "demand",180,"Surat, Gujarat",       72.83,21.17))
    sc.add_node(Node("D4","Bhubaneswar Mkt", "demand",100,"Bhubaneswar, Odisha", 85.82,20.30))
    sc.add_node(Node("D5","Hyderabad Market","demand",160,"Hyderabad, Telangana", 78.49,17.39))
    sc.add_node(Node("D6","Kochi Market",    "demand",140,"Kochi, Kerala",        76.27, 9.93))
    for src,tgt,cap,cost in [
        ("P1","W1",300,2.0),("P1","W2",250,1.5),("P2","W3",200,1.8),
        ("P2","W4",220,2.2),("P3","W2",180,1.2),("P3","W4",200,1.6),
        ("P1","W3",150,3.0),("P2","W1",100,3.5),("W1","D1",220,1.0),
        ("W1","D2",150,1.5),("W2","D2",130,1.2),("W2","D3",200,1.0),
        ("W3","D4",120,1.0),("W3","D5",130,1.8),("W4","D5",180,1.0),
        ("W4","D6",160,1.2),("W1","D4",80,2.5),("W2","D6",90,2.0)]:
        sc.add_edge(Edge(src,tgt,cap,cost))
    return sc

def load_demo_inventory():
    inv=InventoryManager()
    for iid,name,unit in [("SKU001","Rice","Tonnes"),("SKU002","Wheat","Tonnes"),
                           ("SKU003","Sugar","Tonnes"),("SKU004","Edible Oil","KL")]:
        inv.add_item(iid,name,unit)
    for nid,iid,cur,saf,reo,dd in [
        ("P1","SKU001",520,100,150,22),("P1","SKU002",410,80,120,16),
        ("P2","SKU002",360,70,110,14),("P2","SKU003",310,60,90,11),
        ("P3","SKU001",285,55,85,11),("P3","SKU004",205,40,65,9),
        ("W1","SKU001",185,50,75,9),("W1","SKU002",155,40,65,7),
        ("W2","SKU001",125,30,55,6),("W2","SKU003",42,25,45,5),
        ("W2","SKU004",82,20,35,4),("W3","SKU002",92,20,38,5),
        ("W3","SKU003",18,15,28,4),
        ("W4","SKU001",62,15,28,4),("W4","SKU004",52,12,22,3)]:
        inv.set_stock(nid,iid,cur,saf,reo,dd)
    return inv

def load_demo_scores():
    return {"P1":{"reliability":92,"lead_time":88,"quality":95,"cost_efficiency":78},
            "P2":{"reliability":85,"lead_time":91,"quality":89,"cost_efficiency":84},
            "P3":{"reliability":79,"lead_time":83,"quality":91,"cost_efficiency":90},
            "W1":{"reliability":94,"lead_time":90,"quality":87,"cost_efficiency":75},
            "W2":{"reliability":88,"lead_time":85,"quality":82,"cost_efficiency":88},
            "W3":{"reliability":76,"lead_time":79,"quality":84,"cost_efficiency":92},
            "W4":{"reliability":82,"lead_time":86,"quality":88,"cost_efficiency":85}}

def create_excel_template():
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as w:
        pd.DataFrame({"id":["P1","W1","D1"],"name":["Plant 1","Warehouse 1","Market 1"],
            "node_type":["plant","warehouse","demand"],"capacity":[500,400,200],
            "location":["Mumbai, Maharashtra","Delhi, Delhi","Jaipur, Rajasthan"],
            "x_longitude":[72.88,77.21,75.79],"y_latitude":[19.08,28.61,26.91]
        }).to_excel(w,"Nodes",index=False)
        pd.DataFrame({"source":["P1","W1"],"target":["W1","D1"],"capacity":[300,200],"cost":[2.0,1.0]
        }).to_excel(w,"Connections",index=False)
        pd.DataFrame({"node_id":["P1","W1"],"item_id":["SKU001","SKU001"],
            "item_name":["Rice","Rice"],"unit":["Tonnes","Tonnes"],
            "current_stock":[500,180],"safety_stock":[100,50],"reorder_point":[150,70],"daily_demand":[20,8]
        }).to_excel(w,"Inventory",index=False)
        pd.DataFrame({"date":["2024-01-01","2024-01-02"],"node_id":["D1","D1"],"demand":[198,205]
        }).to_excel(w,"Historical_Demand",index=False)
    buf.seek(0); return buf.getvalue()


# ═══════════════════════════════════════════════════════════════
# VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════
NC={"plant":"#0F6E56","warehouse":"#185FA5","demand":"#993C1D"}
NS={"plant":"square","warehouse":"diamond","demand":"circle"}
SEV={"critical":"#E74C3C","high":"#E67E22","medium":"#3498DB","low":"#27AE60","none":"#95A5A6"}

# Green → Yellow → Red heatmap (proper, visible)
HEATMAP_COLORSCALE=[
    [0.0,  "#27AE60"],   # bright green — safe
    [0.25, "#82E0AA"],   # light green
    [0.50, "#F9E79F"],   # yellow — moderate
    [0.65, "#F0B27A"],   # orange
    [0.80, "#E74C3C"],   # red — high risk
    [1.0,  "#922B21"],   # dark red — critical
]

def _auto_layout(sc):
    layers={"plant":[],"warehouse":[],"demand":[]}
    for nid,n in sc.nodes.items(): layers.get(n.node_type,layers["warehouse"]).append(nid)
    pos={}
    for lname,nids in layers.items():
        x={"plant":0.0,"warehouse":1.0,"demand":2.0}[lname]; n=len(nids)
        for i,nid in enumerate(nids): pos[nid]=(x,(i-(n-1)/2)*1.5)
    return pos

def draw_network(sc, highlight_path=None, disrupted_edge=None, show_cap=True, in_transit=None):
    pos=_auto_layout(sc); hp=highlight_path or []; it=in_transit or []
    hp_set=set(zip(hp,hp[1:])) if len(hp)>1 else set()
    it_edges={(d.get("from_id",""),d.get("to_id","")) for d in it if d.get("status")=="In Transit"}
    traces=[]
    for e in sc.edges:
        x0,y0=pos[e.source]; x1,y1=pos[e.target]
        is_dis=disrupted_edge and e.source==disrupted_edge[0] and e.target==disrupted_edge[1]
        is_hi=(e.source,e.target) in hp_set; is_it=(e.source,e.target) in it_edges
        col="#E74C3C" if is_dis else "#E67E22" if is_hi else "#2980B9" if is_it else "#BDC3C7"
        w=3 if is_hi else 2.5 if is_dis else 2.5 if is_it else 1.5
        dash="dot" if(not e.active or is_dis) else "solid"
        ht=f"<b>{sc.nodes[e.source].name} → {sc.nodes[e.target].name}</b><br>Capacity: {e.capacity} | Cost: {e.cost}"
        traces.append(go.Scatter(x=[x0,x1,None],y=[y0,y1,None],mode="lines",
            line=dict(color=col,width=w,dash=dash),hovertext=ht,hoverinfo="text",showlegend=False))
        if show_cap:
            mx,my=(x0+x1)/2,(y0+y1)/2
            traces.append(go.Scatter(x=[mx],y=[my],mode="text",text=[f"{int(e.capacity)}"],
                textfont=dict(size=9,color=col),showlegend=False,hoverinfo="skip"))
        dx,dy=x1-x0,y1-y0; L=math.hypot(dx,dy)
        if L>0:
            ux,uy=dx/L,dy/L
            traces.append(go.Scatter(x=[x1-ux*0.07],y=[y1-uy*0.07],mode="markers",
                marker=dict(symbol="arrow",size=10,color=col,angle=math.degrees(math.atan2(-dy,dx))+90),
                showlegend=False,hoverinfo="skip"))
    for ntype in ["plant","warehouse","demand"]:
        nids=[n for n,nd in sc.nodes.items() if nd.node_type==ntype]
        if not nids: continue
        in_p=[n in hp for n in nids]
        traces.append(go.Scatter(
            x=[pos[n][0] for n in nids],y=[pos[n][1] for n in nids],
            mode="markers+text",name=ntype.capitalize()+"s",
            text=[sc.nodes[n].name for n in nids],
            textposition="middle left" if ntype=="plant" else "top center" if ntype=="warehouse" else "middle right",
            textfont=dict(size=11,color="#2C3E50"),
            hovertext=[f"<b>{sc.nodes[n].name}</b><br>{ntype}<br>Cap:{sc.nodes[n].capacity}<br>{sc.nodes[n].location}" for n in nids],
            hoverinfo="text",
            marker=dict(symbol=NS[ntype],size=[22 if ip else 15 for ip in in_p],
                color=["#E67E22" if ip else NC[ntype] for ip in in_p],
                line=dict(width=2,color="white"))))
    fig=go.Figure(data=traces)
    fig.update_layout(paper_bgcolor="#FDFEFE",plot_bgcolor="#FDFEFE",
        margin=dict(l=10,r=10,t=10,b=10),height=460,hovermode="closest",
        xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
        yaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,
            font=dict(size=11,color="#2C3E50"),bgcolor="rgba(0,0,0,0)"))
    return fig

def draw_gauge_charts(ff, nodes):
    demands=list(ff.items()); cols=min(3,len(demands)); rows=math.ceil(len(demands)/cols)
    specs=[[{"type":"indicator"} for _ in range(cols)] for _ in range(rows)]
    fig=make_subplots(rows=rows,cols=cols,specs=specs)
    for i,(d_id,info) in enumerate(demands):
        c=(i%cols)+1; r=(i//cols)+1; pct=info["pct"]
        col="#E74C3C" if pct<50 else "#E67E22" if pct<80 else "#27AE60"
        fig.add_trace(go.Indicator(mode="gauge+number",value=pct,
            title={"text":nodes[d_id].name,"font":{"size":10,"color":"#2C3E50"}},
            number={"suffix":"%","font":{"size":16,"color":col}},
            gauge={"axis":{"range":[0,100],"tickwidth":1},
                   "bar":{"color":col},
                   "steps":[{"range":[0,50],"color":"#FADBD8"},{"range":[50,80],"color":"#FDEBD0"},{"range":[80,100],"color":"#D5F5E3"}]}),
            row=r,col=c)
    fig.update_layout(height=210*rows,paper_bgcolor="#FDFEFE",margin=dict(l=5,r=5,t=20,b=5))
    return fig

def draw_impact_chart(impact):
    names=[v["demand_name"] for v in impact.values()]
    before=[v["before_pct"] for v in impact.values()]; after=[v["after_pct"] for v in impact.values()]
    fig=go.Figure()
    fig.add_trace(go.Bar(name="Before",x=names,y=before,marker_color="#27AE60",
        text=[f"{v}%" for v in before],textposition="outside",textfont=dict(size=10,color="#2C3E50")))
    fig.add_trace(go.Bar(name="After",x=names,y=after,marker_color="#E74C3C",
        text=[f"{v}%" for v in after],textposition="outside",textfont=dict(size=10,color="#2C3E50")))
    fig.update_layout(barmode="group",yaxis=dict(title="Fulfillment (%)",range=[0,118],gridcolor="#ECF0F1"),
        xaxis=dict(tickfont=dict(color="#2C3E50")),paper_bgcolor="#FDFEFE",plot_bgcolor="#FDFEFE",height=300,
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1),margin=dict(l=10,r=10,t=10,b=10))
    fig.add_hline(y=100,line_dash="dot",line_color="#AAB7B8")
    return fig

def draw_heatmap(sc, ranking):
    """Green-Red heatmap — safe=green, danger=red"""
    if not ranking: return go.Figure()
    node_ids=list(sc.nodes.keys()); node_names=[sc.nodes[n].name for n in node_ids]
    z=[]
    for nid in node_ids:
        outs=[r for r in ranking if r["source"]==nid]; ins=[r for r in ranking if r["target"]==nid]
        max_out=max((r["avg_fulfillment_drop"] for r in outs),default=0)
        max_in =max((r["avg_fulfillment_drop"] for r in ins),default=0)
        nc_out=sum(1 for r in outs if r["severity"]=="critical")*25
        nc_in =sum(1 for r in ins if r["severity"]=="critical")*25
        z.append([max_out,max_in,nc_out,nc_in])
    fig=go.Figure(go.Heatmap(
        z=z, x=["Outbound Risk","Inbound Risk","Critical Out Links","Critical In Links"],
        y=node_names,
        colorscale=HEATMAP_COLORSCALE,
        text=[[f"<b>{v:.0f}</b>" for v in row] for row in z],
        texttemplate="%{text}",textfont={"size":12,"color":"#2C3E50"},
        hoverongaps=False,showscale=True,zmin=0,zmax=100,
        colorbar=dict(title=dict(text="Risk Level",font=dict(color="#2C3E50",size=11)),
                     tickfont=dict(color="#2C3E50"),
                     tickvals=[0,25,50,75,100],ticktext=["0 — Safe","25","50 — Med","75","100 — Critical"])))
    fig.update_layout(
        height=max(350,len(node_ids)*48),
        paper_bgcolor="#FDFEFE",plot_bgcolor="#FDFEFE",
        margin=dict(l=10,r=10,t=50,b=10),
        title=dict(text="<b>Node Risk Exposure Matrix</b>  (Green = Safe → Red = Critical)",
                   font=dict(color="#2C3E50",size=13),x=0.5),
        xaxis=dict(side="top",tickfont=dict(size=11,color="#2C3E50")),
        yaxis=dict(tickfont=dict(size=11,color="#2C3E50"),autorange="reversed"))
    return fig

def draw_criticality_chart(ranking):
    if not ranking: return go.Figure()
    labels=[r["label"] for r in ranking]; drops=[r["avg_fulfillment_drop"] for r in ranking]
    colors=[SEV[r["severity"]] for r in ranking]
    fig=go.Figure(go.Bar(x=drops,y=labels,orientation="h",marker_color=colors,
        text=[f"  {d}%" for d in drops],textposition="outside",textfont=dict(size=11,color="#2C3E50")))
    fig.update_layout(
        xaxis=dict(title="<b>Avg. Fulfillment Drop (%)</b>",range=[0,max(drops or [10])*1.35],gridcolor="#ECF0F1"),
        yaxis=dict(autorange="reversed",tickfont=dict(size=11,color="#2C3E50")),
        paper_bgcolor="#FDFEFE",plot_bgcolor="#FDFEFE",
        height=max(320,len(ranking)*44),margin=dict(l=10,r=80,t=10,b=10))
    return fig

def draw_resilience_gauge(score):
    col="#E74C3C" if score<40 else "#E67E22" if score<70 else "#27AE60"
    fig=go.Figure(go.Indicator(mode="gauge+number",value=score,
        number={"suffix":"%","font":{"size":36,"color":col}},
        gauge={"axis":{"range":[0,100]},"bar":{"color":col},
               "steps":[{"range":[0,40],"color":"#FADBD8"},{"range":[40,70],"color":"#FDEBD0"},{"range":[70,100],"color":"#D5F5E3"}],
               "threshold":{"line":{"color":col,"width":3},"thickness":0.75,"value":score}}))
    fig.update_layout(height=200,margin=dict(l=20,r=20,t=10,b=10),paper_bgcolor="#FDFEFE")
    return fig

def draw_forecast_chart(fc, node_id, sc_nodes):
    if node_id not in fc.history or node_id not in fc.forecasts: return go.Figure()
    hist=fc.history[node_id]; fore=fc.forecasts[node_id]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=hist["date"],y=hist["demand"],mode="lines",
        name="Historical",line=dict(color="#2980B9",width=1.5),opacity=0.8))
    fig.add_trace(go.Scatter(x=fore["date"],y=fore["forecast"],mode="lines",
        name="Forecast",line=dict(color="#E67E22",width=2.5,dash="dash")))
    fig.add_trace(go.Scatter(
        x=list(fore["date"])+list(fore["date"][::-1]),
        y=list(fore["upper"])+list(fore["lower"][::-1]),
        fill="toself",fillcolor="rgba(230,126,34,0.12)",
        line=dict(color="rgba(0,0,0,0)"),name="CI Band"))
    node_name=sc_nodes[node_id].name if node_id in sc_nodes else node_id
    fig.update_layout(
        title=dict(text=f"<b>Demand Forecast — {node_name}</b>",font=dict(color="#2C3E50",size=13),x=0.5),
        xaxis=dict(gridcolor="#ECF0F1"),yaxis=dict(title="Units",gridcolor="#ECF0F1"),
        paper_bgcolor="#FDFEFE",plot_bgcolor="#FDFEFE",height=360,
        legend=dict(font=dict(color="#2C3E50"),bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10,r=10,t=40,b=10))
    return fig

def draw_scorecard_radar(name, scores):
    cats=["Reliability","Lead Time","Quality","Cost Efficiency","Reliability"]
    vals=[scores["reliability"],scores["lead_time"],scores["quality"],scores["cost_efficiency"],scores["reliability"]]
    fig=go.Figure(go.Scatterpolar(r=vals,theta=cats,fill="toself",
        line=dict(color="#1B4F72",width=2),fillcolor="rgba(27,79,114,0.15)"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100],gridcolor="#E5E8E8")),
        showlegend=False,height=280,paper_bgcolor="#FDFEFE",
        margin=dict(l=30,r=30,t=30,b=10),
        title=dict(text=f"<b>{name}</b>",font=dict(size=12,color="#2C3E50"),x=0.5))
    return fig

def draw_geo_map(sc, scope="india"):
    fig=go.Figure()
    for e in sc.edges:
        s=sc.nodes[e.source]; t=sc.nodes[e.target]
        if s.x and s.y and t.x and t.y:
            fig.add_trace(go.Scattergeo(lon=[s.x,t.x,None],lat=[s.y,t.y,None],
                mode="lines",line=dict(width=1.5,color="#AAB7B8"),showlegend=False,hoverinfo="skip"))
    for ntype,nlist,col,sym,sz in [
        ("plant",[n for n in sc.nodes.values() if n.node_type=="plant"],"#0F6E56","square",14),
        ("warehouse",[n for n in sc.nodes.values() if n.node_type=="warehouse"],"#185FA5","diamond",12),
        ("demand",[n for n in sc.nodes.values() if n.node_type=="demand"],"#993C1D","circle",10)]:
        if nlist:
            fig.add_trace(go.Scattergeo(lon=[n.x for n in nlist],lat=[n.y for n in nlist],
                mode="markers+text",name=ntype.capitalize()+"s",
                text=[n.name for n in nlist],textposition="top center",textfont=dict(size=9,color="#2C3E50"),
                hovertext=[f"<b>{n.name}</b><br>{ntype}<br>{n.location}" for n in nlist],hoverinfo="text",
                marker=dict(size=sz,color=col,symbol=sym,line=dict(width=1.5,color="white"))))
    sc2="asia" if scope=="india" else "world"
    geo=dict(scope=sc2,showland=True,landcolor="#F2F3F4",showocean=True,oceancolor="#EBF5FB",
             showcountries=True,countrycolor="#BDC3C7",showcoastlines=True,coastlinecolor="#85929E",bgcolor="#FDFEFE")
    if scope=="india": geo.update(center=dict(lon=80,lat=22),projection_scale=4.5)
    fig.update_layout(geo=geo,height=500,paper_bgcolor="#FDFEFE",
        margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,font=dict(size=11,color="#2C3E50")))
    return fig


# ═══════════════════════════════════════════════════════════════
# FREE AI (Groq — free tier with llama3)
# ═══════════════════════════════════════════════════════════════
FREE_AI_MODELS = {
    "Groq — Llama 3.1 8B (Fast, Free)": {
        "provider":"groq","model":"llama-3.1-8b-instant","url":"https://api.groq.com/openai/v1/chat/completions"
    },
    "Groq — Llama 3.3 70B (Smart, Free)": {
        "provider":"groq","model":"llama-3.3-70b-versatile","url":"https://api.groq.com/openai/v1/chat/completions"
    },
    "Groq — Gemma 2 9B (Free)": {
        "provider":"groq","model":"gemma2-9b-it","url":"https://api.groq.com/openai/v1/chat/completions"
    },
}

GROQ_SIGNUP = "https://console.groq.com"  # Free signup, no credit card needed

SC_SYSTEM_PROMPT = """You are an expert AI assistant for SR's Supply Chain & Operations Helper platform.
You help with supply chain management, inventory optimization, demand forecasting, risk analysis, and logistics.

When users describe actions (e.g. "I added 100 units of Rice"), extract:
- Intent (update_stock, find_path, check_status, etc.)
- Entities (node name, item, quantity)
- Then include an action block if appropriate:

ACTION_JSON_START
{"action":"update_stock","node":"Plant Mumbai","item":"Rice","quantity":100,"operation":"add"}
ACTION_JSON_END

Available actions: update_stock, find_path, run_disruption, get_status, check_atp, run_forecast
Always ask for confirmation before modifying data. Be concise and professional."""

def call_free_ai(messages, api_key, model_config):
    if not api_key or not api_key.strip():
        return None, "no_key"
    try:
        r=requests.post(
            model_config["url"],
            headers={"Authorization":f"Bearer {api_key.strip()}","Content-Type":"application/json"},
            json={"model":model_config["model"],"messages":[{"role":"system","content":SC_SYSTEM_PROMPT}]+messages,"max_tokens":1200,"temperature":0.7},
            timeout=30)
        if r.status_code==200:
            data=r.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"], "ok"
            return None,"empty"
        elif r.status_code==401: return None,"invalid_key"
        elif r.status_code==429: return None,"rate_limit"
        else: return None,f"error_{r.status_code}"
    except requests.exceptions.Timeout: return None,"timeout"
    except Exception as ex: return None,f"exception_{str(ex)}"

def parse_action(text):
    match=re.search(r"ACTION_JSON_START\s*(.*?)\s*ACTION_JSON_END",text,re.DOTALL)
    if match:
        try: return json.loads(match.group(1).strip())
        except: return None
    return None

def clean_response(text):
    return re.sub(r"ACTION_JSON_START.*?ACTION_JSON_END","",text,flags=re.DOTALL).strip()

def execute_action(action, sc, inv):
    a=action.get("action","")
    try:
        if a=="update_stock":
            nn=action.get("node",""); iname=action.get("item","")
            qty=float(action.get("quantity",0)); op=action.get("operation","add")
            nid=next((n.id for n in sc.nodes.values() if n.name.lower()==nn.lower()),None)
            iid=next((id for id,iv in inv.items.items() if iv["name"].lower()==iname.lower()),None)
            if not nid: return False,f"Node '{nn}' not found"
            if not iid: return False,f"Item '{iname}' not found"
            delta=qty if op=="add" else -qty if op=="remove" else None
            if delta is not None:
                inv.update_stock(nid,iid,delta)
                return True,f"{'Added' if op=='add' else 'Removed'} {qty:.0f} units of {iname} {'to' if op=='add' else 'from'} {nn}"
        elif a=="find_path":
            frm=action.get("from",""); to=action.get("to","")
            fid=next((n.id for n in sc.nodes.values() if n.name.lower()==frm.lower()),None)
            tid=next((n.id for n in sc.nodes.values() if n.name.lower()==to.lower()),None)
            if not fid or not tid: return False,"One or both nodes not found"
            res=sc.all_shortest_paths(fid,tid,k=3)
            if res:
                st.session_state.highlight_path=res[0]["path"]
                pnames=" → ".join(sc.nodes[n].name for n in res[0]["path"])
                return True,f"Path highlighted: {pnames}"
            return False,"No path found"
        elif a=="get_status":
            plants=[n for n in sc.nodes.values() if n.node_type=="plant"]
            al=inv.get_alerts(sc.nodes)
            return True,(f"Network: {len(plants)} plants, {len(sc.edges)} connections. "
                        f"Alerts: {len([x for x in al if x['level']=='critical'])} critical.")
    except Exception as ex: return False,f"Action failed: {str(ex)}"
    return False,"Unknown action"


# ═══════════════════════════════════════════════════════════════
# CSS — Clean Light Professional Theme
# ═══════════════════════════════════════════════════════════════
APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}

.hdr{background:linear-gradient(135deg,#1B2631 0%,#1B4F72 100%);
  padding:16px 24px;border-radius:10px;display:flex;align-items:center;gap:16px;
  margin-bottom:20px;box-shadow:0 2px 12px rgba(0,0,0,0.12);}
.hdr h1{color:#fff;font-size:19px;font-weight:700;margin:0;}
.hdr p{color:#AEB6BF;font-size:11px;margin:2px 0 0;text-transform:uppercase;letter-spacing:0.8px;}
.hdr span{color:#F39C12;font-weight:600;font-size:12px;}

.kpi{background:#fff;border:1px solid #E5E8E8;border-radius:8px;padding:14px 18px;
  border-left:4px solid #1B4F72;transition:box-shadow 0.2s;}
.kpi:hover{box-shadow:0 2px 8px rgba(0,0,0,0.08);}
.kpi-lbl{font-size:10px;color:#7F8C8D;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;}
.kpi-val{font-size:24px;font-weight:700;color:#1B2631;line-height:1;}
.kpi-sub{font-size:10px;color:#5D6D7E;margin-top:3px;}

.sh{font-size:11px;font-weight:700;color:#2C3E50;text-transform:uppercase;
  letter-spacing:1.2px;border-bottom:2px solid #E5E8E8;padding-bottom:6px;margin-bottom:14px;}

.section-card{background:#FFFFFF;border:1px solid #E5E8E8;border-radius:10px;
  padding:16px 20px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,0.05);}

.al-r{background:#FDEDEC;border-left:4px solid #E74C3C;padding:10px 14px;border-radius:0 6px 6px 0;margin:6px 0;font-size:13px;color:#2C3E50;}
.al-a{background:#FEF9E7;border-left:4px solid #E67E22;padding:10px 14px;border-radius:0 6px 6px 0;margin:6px 0;font-size:13px;color:#2C3E50;}
.al-g{background:#EAFAF1;border-left:4px solid #27AE60;padding:10px 14px;border-radius:0 6px 6px 0;margin:6px 0;font-size:13px;color:#2C3E50;}
.al-b{background:#EBF5FB;border-left:4px solid #2980B9;padding:10px 14px;border-radius:0 6px 6px 0;margin:6px 0;font-size:13px;color:#2C3E50;}

.transport-card{background:#F8F9FA;border:1px solid #E5E8E8;border-radius:8px;padding:14px 18px;margin:8px 0;}
.transport-mode{font-size:18px;font-weight:700;color:#1B4F72;}
.transport-detail{font-size:12px;color:#5D6D7E;margin-top:4px;}

.card{background:#F8F9FA;border:1px solid #E5E8E8;border-radius:6px;padding:12px 16px;margin:5px 0;font-size:13px;color:#2C3E50;}

.b-r{background:#FADBD8;color:#C0392B;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.b-a{background:#FDEBD0;color:#E67E22;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.b-g{background:#D5F5E3;color:#1A8A4A;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.b-b{background:#D6EAF8;color:#1B4F72;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}

.stButton>button{background:#1B4F72!important;color:#fff!important;border:none!important;
  border-radius:6px!important;font-weight:600!important;font-size:13px!important;}
.stButton>button:hover{background:#154360!important;}

div[data-testid="stExpander"]{border:1px solid #E5E8E8!important;border-radius:8px!important;}

.stTabs [data-baseweb="tab"]{font-size:13px;font-weight:500;color:#5D6D7E;}
.stTabs [aria-selected="true"]{color:#1B4F72!important;font-weight:700!important;}

.user-bubble{background:#1B4F72;color:#fff;padding:10px 14px;border-radius:14px 14px 2px 14px;
  max-width:75%;font-size:13px;line-height:1.5;margin:6px 0;}
.ai-bubble{background:#F8F9FA;border:1px solid #E5E8E8;color:#2C3E50;padding:10px 14px;
  border-radius:14px 14px 14px 2px;max-width:80%;font-size:13px;line-height:1.6;margin:6px 0;}
.chat-wrap{display:flex;margin:6px 0;}
.chat-right{justify-content:flex-end;}.chat-left{justify-content:flex-start;}

.sb-sec{font-size:10px;font-weight:700;color:#7F8C8D;text-transform:uppercase;letter-spacing:1px;margin:12px 0 6px;}
b,.bold-label{font-weight:700!important;}
</style>
"""

# ═══════════════════════════════════════════════════════════════
# VOICE COMPONENT
# ═══════════════════════════════════════════════════════════════
def voice_component():
    html="""
    <div style="background:#F8F9FA;border:1px solid #E5E8E8;border-radius:10px;padding:16px;font-family:Inter,sans-serif">
      <div style="display:flex;gap:10px;align-items:center;margin-bottom:10px">
        <button id="mic-btn" onclick="toggleMic()" style="background:#1B4F72;color:#fff;border:none;border-radius:6px;padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer">🎤 Start Listening</button>
        <button id="tts-btn" onclick="toggleTTS()" style="background:#0F6E56;color:#fff;border:none;border-radius:6px;padding:8px 14px;font-size:13px;font-weight:600;cursor:pointer">🔊 Voice On</button>
        <span id="status" style="font-size:11px;color:#5D6D7E;margin-left:8px"></span>
      </div>
      <div id="transcript" style="min-height:44px;background:#fff;border:1px solid #D5D8DC;border-radius:6px;padding:10px;font-size:13px;color:#2C3E50;margin-bottom:10px">Your speech will appear here...</div>
      <div style="display:flex;gap:8px">
        <button id="copy-btn" onclick="copyText()" style="display:none;background:#1B4F72;color:#fff;border:none;border-radius:6px;padding:6px 14px;font-size:12px;font-weight:600;cursor:pointer">📋 Copy to Chat</button>
        <button id="clear-btn" onclick="clearText()" style="display:none;background:#E74C3C;color:#fff;border:none;border-radius:6px;padding:6px 14px;font-size:12px;font-weight:600;cursor:pointer">Clear</button>
      </div>
      <div style="margin-top:10px;font-size:11px;color:#7F8C8D">💡 Click <b>Start Listening</b> → speak → <b>Copy to Chat</b> → paste below</div>
    </div>
    <script>
    let isListening=false,ttsEnabled=true,recognition=null,finalText='';
    if('SpeechRecognition' in window||'webkitSpeechRecognition' in window){
      recognition=new(window.SpeechRecognition||window.webkitSpeechRecognition)();
      recognition.continuous=true;recognition.interimResults=true;recognition.lang='en-US';
      recognition.onresult=function(e){let int='';finalText='';
        for(let i=0;i<e.results.length;i++){if(e.results[i].isFinal)finalText+=e.results[i][0].transcript;else int+=e.results[i][0].transcript;}
        document.getElementById('transcript').textContent=finalText+(int?' ['+int+']':'');
        if(finalText){document.getElementById('copy-btn').style.display='inline-block';document.getElementById('clear-btn').style.display='inline-block';}};
      recognition.onerror=function(e){document.getElementById('status').textContent='Error: '+e.error;isListening=false;document.getElementById('mic-btn').textContent='🎤 Start Listening';document.getElementById('mic-btn').style.background='#1B4F72';};
      recognition.onend=function(){if(isListening)recognition.start();};
    }else{document.getElementById('mic-btn').disabled=true;document.getElementById('mic-btn').textContent='🎤 Not Supported';}
    function toggleMic(){if(!recognition)return;if(isListening){recognition.stop();isListening=false;document.getElementById('mic-btn').textContent='🎤 Start Listening';document.getElementById('mic-btn').style.background='#1B4F72';document.getElementById('status').textContent='Stopped';}else{finalText='';document.getElementById('transcript').textContent='Listening...';recognition.start();isListening=true;document.getElementById('mic-btn').textContent='⏹ Stop';document.getElementById('mic-btn').style.background='#E74C3C';document.getElementById('status').textContent='● Recording';}}
    function toggleTTS(){ttsEnabled=!ttsEnabled;document.getElementById('tts-btn').textContent=ttsEnabled?'🔊 Voice On':'🔇 Voice Off';document.getElementById('tts-btn').style.background=ttsEnabled?'#0F6E56':'#95A5A6';}
    function copyText(){if(!finalText)return;navigator.clipboard.writeText(finalText).then(()=>{document.getElementById('status').textContent='✓ Copied!';setTimeout(()=>document.getElementById('status').textContent='',3000);});}
    function clearText(){finalText='';document.getElementById('transcript').textContent='Your speech will appear here...';document.getElementById('copy-btn').style.display='none';document.getElementById('clear-btn').style.display='none';}
    window.speakText=function(text){if(!ttsEnabled||!('speechSynthesis' in window))return;speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text.replace(/<[^>]*>/g,'').substring(0,400));u.rate=1.0;speechSynthesis.speak(u);};
    </script>"""
    components.html(html, height=210)


# ═══════════════════════════════════════════════════════════════
# STREAMLIT APP
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="SR — Supply Chain & Operations Helper",
    page_icon="⬡", layout="wide", initial_sidebar_state="expanded")
st.markdown(APP_CSS, unsafe_allow_html=True)

# Session state
for k,v in [("sc",None),("inv",None),("scores",None),("dispatch_log",[]),
            ("disruption_result",None),("highlight_path",[]),("disrupted_edge",None),
            ("ranking",None),("forecaster",None),("forecast_trained",set()),
            ("chat_history",[]),("ai_key",""),("ai_model",list(FREE_AI_MODELS.keys())[0]),
            ("last_ai_text",""),("wh_forecasts",None),("plant_req",None)]:
    if k not in st.session_state: st.session_state[k]=v

if st.session_state.sc is None:     st.session_state.sc=load_demo_data()
if st.session_state.inv is None:    st.session_state.inv=load_demo_inventory()
if st.session_state.scores is None: st.session_state.scores=load_demo_scores()
if st.session_state.forecaster is None: st.session_state.forecaster=DemandForecaster()

sc=st.session_state.sc; inv=st.session_state.inv

# ── HEADER ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="hdr">
  {LOGO_SVG}
  <div>
    <h1>Supply Chain &amp; Operations Helper</h1>
    <p>SR Platform &nbsp;·&nbsp; Network Intelligence &nbsp;·&nbsp; v5.0 &nbsp;&nbsp;
    <span>Supply Chain &amp; Operations Helper</span></p>
  </div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 0 14px;border-bottom:1px solid #E5E8E8">
      {LOGO_SIDEBAR}
      <div>
        <div style="font-size:13px;font-weight:700;color:#1B2631">SR Network Builder</div>
        <div style="font-size:10px;color:#7F8C8D">Supply Chain & Operations</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st_a,st_b,st_c=st.tabs(["Nodes","Connect","Data"])

    with st_a:
        st.markdown('<div class="sb-sec">Add New Node</div>', unsafe_allow_html=True)
        nn=st.text_input("**Node Name**",placeholder="e.g. Plant Delhi",key="nn",label_visibility="collapsed")
        c1,c2=st.columns(2)
        nt=c1.selectbox("**Type**",["plant","warehouse","demand"],key="nt")
        nc=c2.number_input("**Capacity**",min_value=1,value=200,key="nc")
        nl=st.text_input("**Location**",placeholder="City, State",key="nl",label_visibility="collapsed")
        if st.button("➕ Add Node",use_container_width=True):
            if nn.strip():
                nid=nt[0].upper()+str(len([n for n in sc.nodes.values() if n.node_type==nt])+1)
                sc.add_node(Node(nid,nn.strip(),nt,nc,nl)); st.success(f"✓ Added: {nn}"); st.rerun()
            else: st.error("Enter a name")
        st.markdown('<div class="sb-sec">Current Nodes</div>', unsafe_allow_html=True)
        for ntype,label in [("plant","🏭 Plants"),("warehouse","🏢 Warehouses"),("demand","📦 Demand Points")]:
            nlist=[n for n in sc.nodes.values() if n.node_type==ntype]
            if nlist:
                with st.expander(f"**{label}** ({len(nlist)})"):
                    for n in nlist:
                        c1,c2=st.columns([4,1])
                        c1.markdown(f"**{n.name}** <span style='color:#7F8C8D;font-size:11px'>{int(n.capacity)}</span>",unsafe_allow_html=True)
                        if c2.button("✕",key=f"dn_{n.id}"):
                            del sc.nodes[n.id]; sc.edges=[e for e in sc.edges if e.source!=n.id and e.target!=n.id]; st.rerun()

    with st_b:
        st.markdown('<div class="sb-sec">Add Connection</div>', unsafe_allow_html=True)
        no={n.name:n.id for n in sc.nodes.values()}
        if len(sc.nodes)>=2:
            sl=st.selectbox("**From Node**",list(no.keys()),key="es")
            tl=st.selectbox("**To Node**",  list(no.keys()),key="et")
            c1,c2=st.columns(2)
            ecap=c1.number_input("**Capacity**",min_value=1,value=100,key="ec")
            ecos=c2.number_input("**Cost**",min_value=0.1,value=1.0,step=0.1,key="ecs")
            if st.button("🔗 Add Connection",use_container_width=True):
                s,t=no[sl],no[tl]
                if s==t: st.error("Source and target must differ")
                else:
                    try: sc.add_edge(Edge(s,t,ecap,ecos)); st.success("✓ Connected"); st.rerun()
                    except ValueError as ex: st.error(str(ex))
        else: st.info("Add at least 2 nodes first")
        if sc.edges:
            st.markdown('<div class="sb-sec">Connections</div>', unsafe_allow_html=True)
            for e in sc.edges:
                c1,c2=st.columns([5,1])
                c1.markdown(f"<span style='font-size:11px'><b>{sc.nodes[e.source].name}</b>→{sc.nodes[e.target].name} <span style='color:#7F8C8D'>({int(e.capacity)})</span></span>",unsafe_allow_html=True)
                if c2.button("✕",key=f"de_{e.source}_{e.target}"): sc.remove_edge(e.source,e.target); st.rerun()

    with st_c:
        st.markdown('<div class="sb-sec">Quick Start</div>', unsafe_allow_html=True)
        if st.button("🔄 Load Demo Supply Chain",use_container_width=True):
            for k in ["sc","inv","scores","disruption_result","highlight_path","disrupted_edge","ranking","forecaster","forecast_trained","dispatch_log","wh_forecasts","plant_req"]:
                st.session_state[k]=(load_demo_data() if k=="sc" else load_demo_inventory() if k=="inv" else load_demo_scores() if k=="scores" else DemandForecaster() if k=="forecaster" else set() if k=="forecast_trained" else [] if k=="dispatch_log" else None)
            st.rerun()

        st.markdown('<div class="sb-sec">Download Templates</div>', unsafe_allow_html=True)
        try:
            eb=create_excel_template()
            st.download_button("📥 Excel Template",eb,"sc_template.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        except: pass

        st.markdown('<div class="sb-sec">Import Data</div>', unsafe_allow_html=True)
        uf=st.file_uploader("Upload Excel or CSV",type=["xlsx","csv","xls"],key="uf")
        if uf:
            fn=uf.name.lower()
            try:
                if fn.endswith((".xlsx",".xls")):
                    xls=pd.ExcelFile(uf); nsc=SupplyChainGraph()
                    if "Nodes" in xls.sheet_names:
                        for _,r in pd.read_excel(xls,"Nodes").iterrows():
                            nsc.add_node(Node(str(r["id"]),str(r["name"]),str(r["node_type"]),float(r["capacity"]),
                                str(r.get("location","")),float(r.get("x_longitude",0)),float(r.get("y_latitude",0))))
                    if "Connections" in xls.sheet_names:
                        for _,r in pd.read_excel(xls,"Connections").iterrows():
                            nsc.add_edge(Edge(str(r["source"]),str(r["target"]),float(r["capacity"]),float(r.get("cost",1.0))))
                    ni=InventoryManager()
                    if "Inventory" in xls.sheet_names:
                        for _,r in pd.read_excel(xls,"Inventory").iterrows():
                            iid=str(r["item_id"])
                            if iid not in ni.items: ni.add_item(iid,str(r.get("item_name",iid)),str(r.get("unit","units")))
                            ni.set_stock(str(r["node_id"]),iid,float(r["current_stock"]),float(r["safety_stock"]),float(r["reorder_point"]),float(r.get("daily_demand",1)))
                    fc=DemandForecaster()
                    if "Historical_Demand" in xls.sheet_names:
                        hdf=pd.read_excel(xls,"Historical_Demand"); hdf["date"]=pd.to_datetime(hdf["date"])
                        for nid in hdf["node_id"].unique():
                            sub=hdf[hdf["node_id"]==nid].sort_values("date").reset_index(drop=True)
                            nn2=nsc.nodes[nid].name if nid in nsc.nodes else nid
                            sub["node_name"]=nn2; fc.history[nid]=sub
                    st.session_state.sc=nsc; st.session_state.inv=ni; st.session_state.forecaster=fc
                    st.success("✓ Imported!"); st.rerun()
                else:
                    df=pd.read_csv(uf)
                    if "node_type" in df.columns:
                        nsc=SupplyChainGraph()
                        for _,r in df.iterrows():
                            nsc.add_node(Node(str(r["id"]),str(r["name"]),str(r["node_type"]),float(r["capacity"]),str(r.get("location",""))))
                        st.session_state.sc=nsc; st.success("✓ Nodes imported"); st.rerun()
                    elif "source" in df.columns:
                        for _,r in df.iterrows(): sc.add_edge(Edge(str(r["source"]),str(r["target"]),float(r["capacity"]),float(r.get("cost",1.0))))
                        st.success("✓ Edges imported"); st.rerun()
            except Exception as ex: st.error(f"Import failed: {ex}")

        st.markdown('<div class="sb-sec">Export</div>', unsafe_allow_html=True)
        ndf=pd.DataFrame([vars(n) for n in sc.nodes.values()]); edf=pd.DataFrame([vars(e) for e in sc.edges])
        c1,c2=st.columns(2)
        if not ndf.empty: c1.download_button("Nodes",ndf.to_csv(index=False),"nodes.csv",use_container_width=True)
        if not edf.empty: c2.download_button("Edges",edf.to_csv(index=False),"edges.csv",use_container_width=True)

        st.markdown('<div class="sb-sec">🤖 AI Assistant Setup (Free)</div>', unsafe_allow_html=True)
        sel_model=st.selectbox("**Select Free AI Model**",list(FREE_AI_MODELS.keys()),key="model_sel")
        st.session_state.ai_model=sel_model
        st.caption(f"**Free signup:** [console.groq.com]({GROQ_SIGNUP}) — No credit card needed!")
        key_in=st.text_input("**Groq API Key**",value=st.session_state.ai_key,type="password",placeholder="gsk_...",key="key_in")
        if key_in!=st.session_state.ai_key: st.session_state.ai_key=key_in
        if st.session_state.ai_key: st.success("✓ API key set")
        else: st.info("Get free key at console.groq.com")


# ═══════════════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════════════
T=st.tabs(["🗺 Network Map","📦 Inventory","⚡ Disruption","🔥 Risk Heatmap",
           "📈 Demand Forecast","🚚 Dispatch Log","⭐ ATP & Scorecard",
           "🌍 Geographic View","📊 Reports","🤖 AI Assistant"])
t1,t2,t3,t4,t5,t6,t7,t8,t9,t10=T

# ─────────────────────────────────────────────────────────────
# TAB 1 — NETWORK MAP
# ─────────────────────────────────────────────────────────────
with t1:
    if not sc.nodes:
        st.info("Add nodes in the sidebar or load the demo supply chain.")
    else:
        plants=[n for n in sc.nodes.values() if n.node_type=="plant"]
        whs   =[n for n in sc.nodes.values() if n.node_type=="warehouse"]
        dems  =[n for n in sc.nodes.values() if n.node_type=="demand"]
        active_dis=[d for d in st.session_state.dispatch_log if d.get("status")=="In Transit"]

        c1,c2,c3,c4,c5=st.columns(5)
        def kpi(col,label,val,sub,color="#1B4F72"):
            col.markdown(f'<div class="kpi" style="border-left-color:{color}"><div class="kpi-lbl">{label}</div><div class="kpi-val">{val}</div><div class="kpi-sub">{sub}</div></div>',unsafe_allow_html=True)
        kpi(c1,"🏭 Plants",len(plants),f"Cap: {sum(n.capacity for n in plants):,.0f}")
        kpi(c2,"🏢 Warehouses",len(whs),f"Cap: {sum(n.capacity for n in whs):,.0f}","#185FA5")
        kpi(c3,"📦 Demand Pts",len(dems),f"Demand: {sum(n.capacity for n in dems):,.0f}","#993C1D")
        kpi(c4,"🔗 Connections",len(sc.edges),f"Active dispatches: {len(active_dis)}","#1A5276")
        cov=round(sum(n.capacity for n in plants)/max(sum(n.capacity for n in dems),1)*100,1)
        cc="#27AE60" if cov>=100 else "#E67E22" if cov>=70 else "#E74C3C"
        kpi(c5,"📊 Coverage",f"{min(cov,999):.0f}%","vs total demand",cc)

        al=inv.get_alerts(sc.nodes); ca=[a for a in al if a["level"]=="critical"]
        if ca:
            items=" | ".join(f"<b>{a['node_name']}/{a['item_name']}</b>" for a in ca[:3])
            st.markdown(f'<div class="al-r" style="margin-top:12px">⚠ Critical stock: {items}</div>',unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        _,co=st.columns([5,1]); show_cap=co.checkbox("**Edge labels**",value=True,key="ec_cb")
        fig=draw_network(sc,st.session_state.highlight_path,st.session_state.disrupted_edge,show_cap,active_dis)
        st.plotly_chart(fig,use_container_width=True)
        st.markdown('<div style="display:flex;gap:20px;font-size:11px;color:#5D6D7E">'+
            '<span>■ <b>Plant</b></span><span>◆ <b>Warehouse</b></span><span>● <b>Demand</b></span>'+
            '<span style="color:#E67E22">■ Highlighted path</span>'+
            '<span style="color:#2980B9">■ In Transit</span>'+
            '<span style="color:#E74C3C">■ Disrupted</span></div>',unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="sh">🔍 Shortest Path Finder with Transport Mode</div>',unsafe_allow_html=True)
        nlab={n.name:n.id for n in sc.nodes.values()}
        c1,c2,c3,c4=st.columns([2,2,1,1])
        sp1=c1.selectbox("**From**",list(nlab.keys()),key="sp1")
        sp2=c2.selectbox("**To**",list(nlab.keys()),key="sp2",index=min(2,len(nlab)-1))
        load_units=c3.number_input("**Load (units)**",min_value=1,value=100,key="load_u")
        urgent=c4.checkbox("**Urgent?**",key="urgent_cb")

        if st.button("🔍 Find Path & Transport Mode",use_container_width=False,key="find_path_btn"):
            fid=nlab[sp1]; tid=nlab[sp2]
            # Check connection exists
            edge_exists=any((e.source==fid and e.target==tid) or
                            nx.has_path(sc.to_nx(),fid,tid) for e in sc.edges
                            if sc.to_nx().number_of_nodes()>0)
            res=sc.all_shortest_paths(fid,tid,k=3)
            if res:
                st.session_state.highlight_path=res[0]["path"]
                # Get transport recommendation for each hop
                path_ids=res[0]["path"]
                transport_recs=[]
                total_dist=0; total_cost_est=0
                for i in range(len(path_ids)-1):
                    sn=sc.nodes[path_ids[i]]; tn=sc.nodes[path_ids[i+1]]
                    tr=recommend_transport(sn,tn,load_units,urgent)
                    transport_recs.append(tr)
                    if tr["dist_km"]: total_dist+=tr["dist_km"]
                    if tr["cost_estimate"]: total_cost_est+=tr["cost_estimate"]

                st.session_state["last_path_result"]=(res,transport_recs,total_dist,total_cost_est)
                st.rerun()
            else:
                st.error("⚠ **No path found** between these nodes. Check that connections exist.")
                st.session_state.highlight_path=[]

        if "last_path_result" in st.session_state and st.session_state.highlight_path:
            res,transport_recs,total_dist,total_cost_est=st.session_state["last_path_result"]
            path=st.session_state.highlight_path
            pnames=[sc.nodes[n].name for n in path]
            st.markdown(f'<div class="al-g">✓ **Path:** {" → ".join(pnames)}</div>',unsafe_allow_html=True)

            st.markdown('<div class="sh" style="margin-top:12px">Transport Recommendations</div>',unsafe_allow_html=True)
            if transport_recs:
                for i,tr in enumerate(transport_recs):
                    src_name=sc.nodes[path[i]].name; tgt_name=sc.nodes[path[i+1]].name
                    dist_str=f"**{tr['dist_km']} km**" if tr['dist_km'] else "distance N/A"
                    cost_str=f"₹{tr['cost_estimate']:,.0f}" if tr['cost_estimate'] else "N/A"
                    time_str=f"{tr['hours']:.1f} hrs ({tr['days']:.1f} days)" if tr['hours'] else "N/A"
                    st.markdown(f"""
                    <div class="transport-card">
                      <div style="display:flex;justify-content:space-between;align-items:center">
                        <div><b>{src_name} → {tgt_name}</b></div>
                        <div class="transport-mode">{tr['icon']} {tr['label']}</div>
                      </div>
                      <div class="transport-detail">
                        📏 Distance: {dist_str} &nbsp;|&nbsp;
                        💰 Est. Cost: <b>{cost_str}</b> &nbsp;|&nbsp;
                        ⏱ Est. Time: <b>{time_str}</b>
                      </div>
                      <div style="font-size:11px;color:#5D6D7E;margin-top:4px">💡 {tr['reason']}</div>
                    </div>""",unsafe_allow_html=True)
                if total_dist>0 or total_cost_est>0:
                    st.markdown(f'<div class="al-b">📊 <b>Total Route:</b> {total_dist:.0f} km total distance | Est. Cost: ₹{total_cost_est:,.0f}</div>',unsafe_allow_html=True)

            if st.button("Clear path",key="clear_path"): st.session_state.highlight_path=[]; del st.session_state["last_path_result"]; st.rerun()

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="sh">📊 Current Demand Fulfillment</div>',unsafe_allow_html=True)
        if sc.edges:
            with st.spinner("Computing fulfillment..."): ff=sc.demand_fulfillment()
            st.plotly_chart(draw_gauge_charts(ff,sc.nodes),use_container_width=True)
            with st.expander("📋 **View Detailed Table**"):
                rows=[{"Demand Point":sc.nodes[d].name,"Required":info["required"],"Fulfilled":info["fulfilled"],
                       "Fulfillment %":info["pct"],"Sources":", ".join(sc.nodes[p].name for p in info["reachable_from"]) or "None"}
                      for d,info in ff.items()]
                df_ff=pd.DataFrame(rows)
                def cpct(v): return "background-color:#D5F5E3" if v>=90 else "background-color:#FDEBD0" if v>=50 else "background-color:#FADBD8"
                st.dataframe(df_ff.style.map(cpct,subset=["Fulfillment %"]),use_container_width=True,hide_index=True)
        else: st.info("Add connections to compute demand fulfillment.")


# ─────────────────────────────────────────────────────────────
# TAB 2 — INVENTORY
# ─────────────────────────────────────────────────────────────
with t2:
    st.markdown('<div class="sh">📦 Inventory Overview</div>',unsafe_allow_html=True)
    al=inv.get_alerts(sc.nodes)
    if al:
        for a in [x for x in al if x["level"]=="critical"]:
            st.markdown(f'<div class="al-r"><span class="b-r">CRITICAL</span> <b>{a["node_name"]}</b> — {a["item_name"]}: {a["current"]:.0f} / Safety: {a["safety"]:.0f} · <b>{a["coverage"]} days</b> left</div>',unsafe_allow_html=True)
        for a in [x for x in al if x["level"]=="warning"]:
            st.markdown(f'<div class="al-a"><span class="b-a">LOW</span> <b>{a["node_name"]}</b> — {a["item_name"]}: {a["current"]:.0f} · <b>{a["coverage"]} days</b></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="al-g">✓ All stock levels within normal range.</div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sh">📋 Stock Levels by Node</div>',unsafe_allow_html=True)
    inv_df=inv.to_df(sc.nodes)
    if not inv_df.empty:
        STC={"Normal":"#27AE60","Low":"#E67E22","Critical":"#E74C3C"}
        def cs(v): return f"color:{STC.get(v,'#2C3E50')};font-weight:700"
        def cc2(v): return "background-color:#FADBD8" if v<=3 else "background-color:#FDEBD0" if v<=7 else "background-color:#D5F5E3"
        st.dataframe(inv_df.style.map(cs,subset=["Status"]).map(cc2,subset=["Coverage Days"]),use_container_width=True,hide_index=True)

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sh">📈 Stock Chart</div>',unsafe_allow_html=True)
    nws=[nid for nid in sc.nodes if nid in inv.stock and inv.stock[nid]]
    if nws:
        sel_n=st.selectbox("**Select Node**",[sc.nodes[n].name for n in nws],key="inv_ns")
        sel_id=[n for n in nws if sc.nodes[n].name==sel_n]
        if sel_id:
            nid=sel_id[0]; items_data=inv.stock[nid]
            inames=[inv.items.get(iid,{}).get("name",iid) for iid in items_data]
            curs=[s["current"] for s in items_data.values()]
            safs=[s["safety"] for s in items_data.values()]
            reos=[s["reorder"] for s in items_data.values()]
            cbars=["#E74C3C" if c<=s else "#E67E22" if c<=r else "#27AE60" for c,s,r in zip(curs,safs,reos)]
            fig_bar=go.Figure()
            fig_bar.add_trace(go.Bar(x=inames,y=curs,marker_color=cbars,name="Current",text=[f"{c:.0f}" for c in curs],textposition="outside"))
            fig_bar.add_trace(go.Scatter(x=inames,y=safs,mode="markers+lines",marker=dict(symbol="line-ew",size=18,color="#E74C3C",line=dict(width=2,color="#E74C3C")),line=dict(dash="dot",color="#E74C3C"),name="Safety Stock"))
            fig_bar.add_trace(go.Scatter(x=inames,y=reos,mode="markers+lines",marker=dict(symbol="line-ew",size=18,color="#E67E22",line=dict(width=2,color="#E67E22")),line=dict(dash="dash",color="#E67E22"),name="Reorder Point"))
            fig_bar.update_layout(height=280,paper_bgcolor="#FDFEFE",plot_bgcolor="#FDFEFE",
                legend=dict(font=dict(color="#2C3E50")),margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_bar,use_container_width=True)

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sh">⚡ Live Stock Update</div>',unsafe_allow_html=True)
    with st.form("stock_upd"):
        c1,c2,c3,c4=st.columns([2,2,1,2])
        un=[sc.nodes[n].name for n in sc.nodes if n in inv.stock]
        upd_n=c1.selectbox("**Node**",un,key="upd_n") if un else c1.text_input("Node")
        uid=[n for n in sc.nodes if sc.nodes[n].name==upd_n and n in inv.stock]
        iopts={inv.items.get(iid,{}).get("name",iid):iid for iid in (inv.stock.get(uid[0],{}) if uid else {})}
        upd_i=c2.selectbox("**Item**",list(iopts.keys()),key="upd_i") if iopts else c2.text_input("Item ID")
        upd_q=c3.number_input("**Qty (±)**",value=0.0,step=1.0,key="upd_q")
        upd_nt=c4.text_input("**Note**",placeholder="Optional",key="upd_nt")
        if st.form_submit_button("✅ Update Stock",use_container_width=True) and uid:
            iid=iopts.get(upd_i,upd_i)
            if inv.update_stock(uid[0],iid,upd_q):
                st.session_state.dispatch_log.append({"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "from_node":upd_n,"to_node":"Manual Update","from_id":uid[0],"to_id":"",
                    "item":inv.items.get(iid,{}).get("name",iid),"item_id":iid,
                    "quantity":upd_q,"status":"Delivered","notes":upd_nt})
                st.success(f"✓ Updated: {upd_q:+.0f} units"); st.rerun()
            else: st.error("Node/item not found")


# ─────────────────────────────────────────────────────────────
# TAB 3 — DISRUPTION SIMULATOR
# ─────────────────────────────────────────────────────────────
with t3:
    st.markdown('<div class="sh">⚡ Disruption Scenario Analysis</div>',unsafe_allow_html=True)
    st.caption("Simulate a connection failure — see **resilience score**, **alternate routes**, and **safety stock** coverage.")
    if not sc.edges: st.info("Add connections to run disruption analysis.")
    else:
        eopts={f"{sc.nodes[e.source].name} → {sc.nodes[e.target].name} (cap:{int(e.capacity)})":(e.source,e.target) for e in sc.edges}
        c1,c2=st.columns([4,1])
        chosen=c1.selectbox("**Connection to disrupt**",list(eopts.keys()),label_visibility="collapsed",key="dis_sel")
        c2.markdown("<br>",unsafe_allow_html=True)
        if c2.button("⚡ Analyse",use_container_width=True,type="primary",key="dis_btn"):
            src,tgt=eopts[chosen]
            with st.spinner("Running disruption analysis..."): result=sc.simulate_disruption(src,tgt)
            st.session_state.disruption_result=result; st.session_state.disrupted_edge=(src,tgt); st.rerun()

        if st.session_state.disruption_result:
            result=st.session_state.disruption_result; st.markdown("<br>",unsafe_allow_html=True)
            cg,cs2=st.columns([1,2])
            with cg:
                st.markdown('<div class="sh">Resilience Score</div>',unsafe_allow_html=True)
                st.plotly_chart(draw_resilience_gauge(result["resilience_score"]),use_container_width=True)
            with cs2:
                st.markdown(f'<div class="sh">Impact — {result["removed_edge"]}</div>',unsafe_allow_html=True)
                sv=result["resilience_score"]
                cls="al-g" if sv>=70 else "al-a" if sv>=40 else "al-r"
                txt="**Low Risk** — Chain retains continuity." if sv>=70 else "**Moderate Risk** — Partial disruption." if sv>=40 else "**Critical Risk** — Major disruption!"
                st.markdown(f'<div class="{cls}"><b>{sv}%</b> — {txt}</div>',unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                for d_id,imp in result["impact"].items():
                    if imp["drop_pct"]>0:
                        sv2=SEV[imp["severity"]]
                        st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                          padding:7px 12px;background:#F8F9FA;border-radius:5px;margin:3px 0;border-left:3px solid {sv2}">
                          <b style="font-size:13px">{imp['demand_name']}</b>
                          <span style="font-size:12px;color:#5D6D7E">{imp['before_pct']}%→{imp['after_pct']}% | <b>−{imp['drop_pct']}%</b> | −{imp['lost_units']} units</span>
                          <span style="color:{sv2};font-size:11px;font-weight:700">{imp['severity'].upper()}</span></div>""",unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">📊 Fulfillment Before vs After</div>',unsafe_allow_html=True)
            st.plotly_chart(draw_impact_chart(result["impact"]),use_container_width=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">🔄 Alternate Network Routes</div>',unsafe_allow_html=True)
            if result["alt_paths"]:
                for d_id,paths in result["alt_paths"].items():
                    if paths:
                        st.markdown(f"**{sc.nodes[d_id].name}** — {len(paths)} alternate route(s):")
                        for i,p in enumerate(paths,1):
                            st.markdown(f'<div class="card"><b>Route {i}</b> | Cost: {p["cost"]} | {" → ".join(p["path"])}</div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="al-r"><b>No alternate routes found</b> — This is a single point of failure!</div>',unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">🏭 Safety Stock Alternatives</div>',unsafe_allow_html=True)
            de=st.session_state.disrupted_edge
            for d_id,imp in result["impact"].items():
                if imp["drop_pct"]<=0: continue
                sf=imp["lost_units"]
                st.markdown(f"**{imp['demand_name']}** — shortfall: **{sf:.0f} units**")
                rows_s=[]
                for iid in list(inv.items.keys()):
                    alts=inv.find_alternatives(d_id,iid,sf,sc,de)
                    for alt in alts:
                        rows_s.append({"Source":alt["node_name"],"Item":inv.items[iid]["name"],
                            "Available":f"{alt['available']:.0f}","Covers":("✓ Yes" if alt["can_cover"] else f"Partial {alt['coverage_pct']}%"),
                            "Route":" → ".join(alt["path"]),"Cost":alt["route_cost"],"Coverage Days":alt.get("coverage_days","—")})
                if rows_s:
                    df_s=pd.DataFrame(rows_s)
                    def cov_s(v): return "background-color:#D5F5E3;font-weight:700" if "Yes" in str(v) else "background-color:#FDEBD0"
                    st.dataframe(df_s.style.map(cov_s,subset=["Covers"]),use_container_width=True,hide_index=True)
                else:
                    st.markdown('<div class="al-a">No above-safety stock available.</div>',unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">🗺 Network View — Disruption Highlighted</div>',unsafe_allow_html=True)
            alt_hi=[]
            if result["alt_paths"]:
                first=[v for v in result["alt_paths"].values() if v]
                if first and first[0]: alt_hi=first[0][0].get("path_ids",[])
            st.plotly_chart(draw_network(sc,alt_hi,st.session_state.disrupted_edge,True,
                [d for d in st.session_state.dispatch_log if d.get("status")=="In Transit"]),use_container_width=True)
            if st.button("🔄 Reset Simulation",key="res_dis"):
                st.session_state.disruption_result=None; st.session_state.disrupted_edge=None
                st.session_state.highlight_path=[]; st.rerun()


# ─────────────────────────────────────────────────────────────
# TAB 4 — RISK HEATMAP (Green → Red, proper colors)
# ─────────────────────────────────────────────────────────────
with t4:
    st.markdown('<div class="sh">🔥 Network Risk Heatmap</div>',unsafe_allow_html=True)
    st.caption("**Green = Safe | Yellow = Moderate | Red = High Risk | Dark Red = Critical**")
    if not sc.edges: st.info("Add connections first.")
    else:
        c1,c2=st.columns([3,1])
        if c2.button("▶ Run Stress Test",use_container_width=True,key="hm_btn"):
            with st.spinner("Testing all connections..."): st.session_state.ranking=sc.rank_critical_edges(); st.rerun()
        if st.session_state.ranking is None:
            st.info("Click **Run Stress Test** to populate the risk heatmap.")
        if st.session_state.ranking:
            ranking=st.session_state.ranking
            st.plotly_chart(draw_heatmap(sc,ranking),use_container_width=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">📋 Node Risk Summary</div>',unsafe_allow_html=True)
            rows=[]
            for nid,node in sc.nodes.items():
                outs=[r for r in ranking if r["source"]==nid]; ins=[r for r in ranking if r["target"]==nid]
                md=max((r["avg_fulfillment_drop"] for r in outs+ins),default=0)
                nc=sum(1 for r in outs+ins if r["severity"]=="critical")
                rl="Critical" if md>=50 else "High" if md>=25 else "Medium" if md>=5 else "Low"
                rows.append({"Node":node.name,"Type":node.node_type.capitalize(),
                             "Max Drop If Link Fails":f"**{md:.0f}%**","Critical Links":nc,"Risk Level":rl})
            df_r=pd.DataFrame(rows).sort_values("Max Drop If Link Fails",ascending=False)
            def rl_col(v):
                c={"Critical":"#FADBD8","High":"#FDEBD0","Medium":"#D6EAF8","Low":"#D5F5E3"}
                return f"background-color:{c.get(v,'#FFFFFF')}"
            st.dataframe(df_r.style.map(rl_col,subset=["Risk Level"]),use_container_width=True,hide_index=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">📊 Criticality Ranking</div>',unsafe_allow_html=True)
            st.plotly_chart(draw_criticality_chart(ranking),use_container_width=True)

            st.markdown('<div class="sh">💡 Risk Mitigation Recommendations</div>',unsafe_allow_html=True)
            for sev,cls,label in [("critical","al-r","🚨 Immediate Action"),("high","al-a","⚠ High Priority"),("low","al-g","✓ Well Redundant")]:
                items=[r for r in ranking if r["severity"]==sev]
                if items:
                    links="".join(f"<li><b>{r['label']}</b></li>" for r in items)
                    st.markdown(f'<div class="{cls}"><b>{label} ({len(items)} links):</b><ul style="margin:4px 0 0 16px">{links}</ul></div>',unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 5 — DEMAND FORECAST
# ─────────────────────────────────────────────────────────────
with t5:
    st.markdown('<div class="sh">📈 AI-Powered Demand Forecasting</div>',unsafe_allow_html=True)
    st.caption("**RandomForest + GradientBoosting ensemble** · Forecast → Warehouse → Plant propagation")
    fc=st.session_state.forecaster
    demand_nodes=[n for n in sc.nodes.values() if n.node_type=="demand"]
    if not demand_nodes: st.info("Add demand nodes to enable forecasting.")
    else:
        c1,c2,c3=st.columns([2,1,1])
        sel_dem=c1.selectbox("**Demand node**",[n.name for n in demand_nodes],key="fc_node")
        horizon=c2.selectbox("**Horizon (days)**",[14,30,60,90],index=1,key="fc_h")
        use_syn=c3.checkbox("**Use generated history**",value=True,key="fc_syn")

        sel_node=next(n for n in demand_nodes if n.name==sel_dem)
        if not use_syn:
            st.caption("Upload CSV with columns: **date** (YYYY-MM-DD), **demand** (number)")
            hf=st.file_uploader("Upload historical CSV",type=["csv"],key="fc_up")
            if hf:
                try:
                    hdf=pd.read_csv(hf); hdf["date"]=pd.to_datetime(hdf["date"])
                    hdf["node_id"]=sel_node.id; hdf["node_name"]=sel_node.name
                    fc.history[sel_node.id]=hdf.sort_values("date").reset_index(drop=True)
                    st.success(f"✓ Loaded {len(hdf)} days of data")
                except Exception as ex: st.error(f"Upload failed: {ex}")

        if st.button("▶ Train Model & Forecast",use_container_width=True,key="train_btn"):
            nid=sel_node.id
            if nid not in fc.history or use_syn: fc.generate_synthetic_history(nid,sel_node.name,sel_node.capacity)
            with st.spinner("Training RF + GBM ensemble..."):
                fdf=fc.train(nid,horizon=int(horizon))
            if fdf is not None:
                st.session_state.forecast_trained.add(nid)
                m=fc.metrics[nid]
                st.success(f"✓ Model trained! **RMSE:{m['rmse']:.1f}** | **MAE:{m['mae']:.1f}** | **MAPE:{m['mape']:.1f}%** | **R²:{m['r2']:.3f}**")
            st.rerun()

        nid=sel_node.id
        if nid in st.session_state.forecast_trained and nid in fc.forecasts:
            m=fc.metrics.get(nid,{})
            mc1,mc2,mc3,mc4=st.columns(4)
            mc1.metric("**RMSE**",f"{m.get('rmse','—')}")
            mc2.metric("**MAE**",f"{m.get('mae','—')}")
            mc3.metric("**MAPE**",f"{m.get('mape','—')}%")
            mc4.metric("**R²**",f"{m.get('r2','—')}")
            st.plotly_chart(draw_forecast_chart(fc,nid,sc.nodes),use_container_width=True)
            with st.expander("📋 **Forecast Values Table**"):
                fdf=fc.forecasts[nid]
                df_show=fdf[["date","forecast","lower","upper"]].copy()
                df_show.columns=["Date","Forecast","Lower CI","Upper CI"]
                df_show["Date"]=df_show["Date"].dt.strftime("%Y-%m-%d")
                for col in ["Forecast","Lower CI","Upper CI"]: df_show[col]=df_show[col].round(1)
                st.dataframe(df_show,use_container_width=True,hide_index=True)

        st.markdown("<br>",unsafe_allow_html=True)
        if st.session_state.forecast_trained:
            if st.button("▶ Aggregate to Warehouses & Plants",use_container_width=True,key="agg_btn"):
                with st.spinner("Aggregating forecasts..."):
                    for dn in demand_nodes:
                        if dn.id not in fc.history: fc.generate_synthetic_history(dn.id,dn.name,dn.capacity)
                        if dn.id not in fc.forecasts: fc.train(dn.id,horizon=int(horizon)); st.session_state.forecast_trained.add(dn.id)
                    wh_fc=fc.aggregate_to_warehouses(sc,int(horizon))
                    pr=fc.get_plant_requirements(sc,wh_fc,int(horizon))
                    st.session_state.wh_forecasts=wh_fc; st.session_state.plant_req=pr
                st.rerun()

            if st.session_state.wh_forecasts:
                st.markdown('<div class="sh">🏢 Warehouse Aggregated Demand</div>',unsafe_allow_html=True)
                wh_fc=st.session_state.wh_forecasts
                fig_wh=go.Figure()
                for i,(wid,wi) in enumerate(wh_fc.items()):
                    fig_wh.add_trace(go.Scatter(x=list(range(1,len(wi["forecast"])+1)),y=wi["forecast"],
                        mode="lines",name=wi["name"],line=dict(width=2)))
                fig_wh.update_layout(title=dict(text="<b>Aggregated Warehouse Demand Forecast</b>",font=dict(size=13,color="#2C3E50"),x=0.5),
                    xaxis=dict(title="Days",gridcolor="#ECF0F1"),yaxis=dict(title="Units",gridcolor="#ECF0F1"),
                    paper_bgcolor="#FDFEFE",plot_bgcolor="#FDFEFE",height=320,margin=dict(l=10,r=10,t=40,b=10))
                st.plotly_chart(fig_wh,use_container_width=True)

            if st.session_state.plant_req:
                st.markdown('<div class="sh">🏭 Plant Manufacturing Requirements vs Capacity</div>',unsafe_allow_html=True)
                pr=st.session_state.plant_req
                fig_pr=go.Figure()
                for i,(pid,pi) in enumerate(pr.items()):
                    x=list(range(1,len(pi["required"])+1))
                    fig_pr.add_trace(go.Scatter(x=x,y=pi["required"],mode="lines",name=pi["name"],line=dict(width=2)))
                    fig_pr.add_trace(go.Scatter(x=x,y=[pi["capacity"]]*len(x),mode="lines",name=f"{pi['name']} Capacity",line=dict(dash="dot",width=1.5),showlegend=False))
                fig_pr.update_layout(title=dict(text="<b>Plant Requirements vs Capacity</b>",font=dict(size=13,color="#2C3E50"),x=0.5),
                    xaxis=dict(title="Days",gridcolor="#ECF0F1"),yaxis=dict(title="Units",gridcolor="#ECF0F1"),
                    paper_bgcolor="#FDFEFE",plot_bgcolor="#FDFEFE",height=320,margin=dict(l=10,r=10,t=40,b=10))
                st.plotly_chart(fig_pr,use_container_width=True)

        if st.button("🔁 Train All Demand Nodes",use_container_width=True,key="train_all"):
            prog=st.progress(0)
            for i,dn in enumerate(demand_nodes):
                if dn.id not in fc.history: fc.generate_synthetic_history(dn.id,dn.name,dn.capacity)
                fc.train(dn.id,horizon=int(horizon)); st.session_state.forecast_trained.add(dn.id)
                prog.progress((i+1)/len(demand_nodes))
            st.success(f"✓ Trained {len(demand_nodes)} demand nodes"); st.rerun()


# ─────────────────────────────────────────────────────────────
# TAB 6 — DISPATCH LOG
# ─────────────────────────────────────────────────────────────
with t6:
    st.markdown('<div class="sh">🚚 Dispatch Log — Live Goods Movement</div>',unsafe_allow_html=True)
    with st.form("dis_form"):
        st.markdown("**Log New Dispatch**")
        c1,c2,c3=st.columns(3)
        all_names=[n.name for n in sc.nodes.values()]
        df_from=c1.selectbox("**From Node**",all_names,key="df"); df_to=c2.selectbox("**To Node**",all_names,key="dt",index=min(1,len(all_names)-1))
        ai2={inv.items[iid]["name"]:iid for iid in inv.items} if inv.items else {}
        df_item=c3.selectbox("**Item**",list(ai2.keys()) or ["—"],key="di")
        c1b,c2b,c3b=st.columns(3)
        df_qty=c1b.number_input("**Quantity**",min_value=0.1,value=50.0,key="dq")
        df_st=c2b.selectbox("**Status**",["In Transit","Delivered","Delayed"],key="ds")
        df_no=c3b.text_input("**Notes**",placeholder="Optional",key="dno")
        if st.form_submit_button("✅ Log Dispatch",use_container_width=True):
            fid=[n.id for n in sc.nodes.values() if n.name==df_from]
            tid=[n.id for n in sc.nodes.values() if n.name==df_to]
            iid=ai2.get(df_item,"")
            if fid and tid:
                if df_st in ("In Transit","Delivered") and iid: inv.update_stock(fid[0],iid,-df_qty)
                if df_st=="Delivered" and iid: inv.update_stock(tid[0],iid,df_qty)
                st.session_state.dispatch_log.append({"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "from_node":df_from,"to_node":df_to,"from_id":fid[0],"to_id":tid[0],
                    "item":df_item,"item_id":iid,"quantity":df_qty,"status":df_st,"notes":df_no})
                st.success(f"✓ Logged: **{df_qty:.0f} units** of **{df_item}**"); st.rerun()

    if st.session_state.dispatch_log:
        st.markdown("<br>",unsafe_allow_html=True)
        ldf=pd.DataFrame(st.session_state.dispatch_log[::-1])
        cs=[c for c in ["timestamp","from_node","to_node","item","quantity","status","notes"] if c in ldf.columns]
        ldf_s=ldf[cs].copy(); ldf_s.columns=["Time","From","To","Item","Qty","Status","Notes"][:len(cs)]
        def ss(v):
            c={"In Transit":"#D6EAF8","Delivered":"#D5F5E3","Delayed":"#FADBD8"}
            return f"background-color:{c.get(v,'#fff')};font-weight:600"
        st.dataframe(ldf_s.style.map(ss,subset=["Status"]),use_container_width=True,hide_index=True)
        it=len([d for d in st.session_state.dispatch_log if d["status"]=="In Transit"])
        dv=len([d for d in st.session_state.dispatch_log if d["status"]=="Delivered"])
        dl=len([d for d in st.session_state.dispatch_log if d["status"]=="Delayed"])
        c1,c2,c3=st.columns(3)
        c1.markdown(f'<div class="kpi" style="border-left-color:#2980B9"><div class="kpi-lbl">In Transit</div><div class="kpi-val">{it}</div></div>',unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi" style="border-left-color:#27AE60"><div class="kpi-lbl">Delivered</div><div class="kpi-val">{dv}</div></div>',unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi" style="border-left-color:#E74C3C"><div class="kpi-lbl">Delayed</div><div class="kpi-val">{dl}</div></div>',unsafe_allow_html=True)
        if st.button("🗑 Clear Log",key="cl_log"): st.session_state.dispatch_log=[]; st.rerun()


# ─────────────────────────────────────────────────────────────
# TAB 7 — ATP & SCORECARD
# ─────────────────────────────────────────────────────────────
with t7:
    atp_tab,sc_tab=st.tabs(["✅ Available-to-Promise","⭐ Supplier Scorecard"])
    with atp_tab:
        st.markdown('<div class="sh">✅ Available-to-Promise Analysis</div>',unsafe_allow_html=True)
        ai3={inv.items[iid]["name"]:iid for iid in inv.items} if inv.items else {}
        c1,c2,c3=st.columns([2,1,1])
        atp_i=c1.selectbox("**Item**",list(ai3.keys()) or ["No items"],key="atp_i")
        atp_q=c2.number_input("**Required Qty**",min_value=1.0,value=100.0,key="atp_q")
        atp_d=c3.selectbox("**Destination**",[n.name for n in sc.nodes.values() if n.node_type=="demand"],key="atp_d")
        if st.button("🔍 Check Availability",use_container_width=True,key="atp_chk"):
            iid=ai3.get(atp_i,""); did=[n.id for n in sc.nodes.values() if n.name==atp_d]
            if iid and did:
                alts=inv.find_alternatives(did[0],iid,atp_q,sc)
                if alts:
                    for i,a in enumerate(alts,1):
                        cls="al-g" if a["can_cover"] else "al-a"; bdg="b-g" if a["can_cover"] else "b-a"
                        can_txt = "Can Fulfill" if a["can_cover"] else f"Partial {a['coverage_pct']}%"
                        route_txt = " → ".join(a["path"])
                        st.markdown(f'<div class="{cls}"><b>Option {i}: {a["node_name"]}</b> <span class="{bdg}">{can_txt}</span><br>Available: <b>{a["available"]:.0f}</b> | Coverage: {a["coverage_days"]} days | Route: {route_txt} | Cost: {a["route_cost"]}</div>',unsafe_allow_html=True)
                else:
                    st.markdown('<div class="al-r"><b>No nodes can fulfill this request</b> with current stock levels.</div>',unsafe_allow_html=True)

    with sc_tab:
        st.markdown('<div class="sh">⭐ Supplier & Node Scorecard</div>',unsafe_allow_html=True)
        scores=st.session_state.scores
        node_opts=[n for n in sc.nodes.values() if n.node_type in ("plant","warehouse")]
        if node_opts:
            snm=st.selectbox("**Select Node**",[n.name for n in node_opts],key="sc_sel")
            snid=[n.id for n in node_opts if n.name==snm]
            if snid:
                nid=snid[0]
                if nid not in scores: scores[nid]={"reliability":80,"lead_time":80,"quality":80,"cost_efficiency":80}
                s=scores[nid]
                c1,c2=st.columns([1,1])
                with c1:
                    st.markdown("**Edit Performance Scores (0–100)**")
                    s["reliability"]    =st.slider("**Reliability**",   0,100,int(s["reliability"]),   key=f"sr_{nid}")
                    s["lead_time"]      =st.slider("**Lead Time**",     0,100,int(s["lead_time"]),     key=f"sl_{nid}")
                    s["quality"]        =st.slider("**Quality**",       0,100,int(s["quality"]),       key=f"sq_{nid}")
                    s["cost_efficiency"]=st.slider("**Cost Efficiency**",0,100,int(s["cost_efficiency"]),key=f"sc_{nid}")
                    ov=round((s["reliability"]+s["lead_time"]+s["quality"]+s["cost_efficiency"])/4,1)
                    grade="A" if ov>=90 else "B" if ov>=75 else "C" if ov>=60 else "D"
                    gc_="b-g" if grade=="A" else "b-b" if grade=="B" else "b-a" if grade=="C" else "b-r"
                    st.markdown(f"<br><b>Overall: {ov}</b> <span class='{gc_}'>Grade {grade}</span>",unsafe_allow_html=True)
                with c2: st.plotly_chart(draw_scorecard_radar(snm,s),use_container_width=True)

            rows_sc=[]
            for n in node_opts:
                if n.id in scores:
                    s=scores[n.id]; ov=round((s["reliability"]+s["lead_time"]+s["quality"]+s["cost_efficiency"])/4,1)
                    g="A" if ov>=90 else "B" if ov>=75 else "C" if ov>=60 else "D"
                    rows_sc.append({"Node":n.name,"Type":n.node_type.capitalize(),"Reliability":s["reliability"],
                        "Lead Time":s["lead_time"],"Quality":s["quality"],"Cost Eff":s["cost_efficiency"],"Overall":ov,"Grade":g})
            if rows_sc:
                df_sc=pd.DataFrame(rows_sc).sort_values("Overall",ascending=False)
                def gc2(v):
                    c={"A":"#D5F5E3","B":"#D6EAF8","C":"#FDEBD0","D":"#FADBD8"}
                    return f"background-color:{c.get(v,'#fff')};font-weight:700"
                st.dataframe(df_sc.style.map(gc2,subset=["Grade"]),use_container_width=True,hide_index=True)


# ─────────────────────────────────────────────────────────────
# TAB 8 — GEOGRAPHIC VIEW
# ─────────────────────────────────────────────────────────────
with t8:
    st.markdown('<div class="sh">🌍 Geographic Network View</div>',unsafe_allow_html=True)
    _,cr=st.columns([3,1]); mscope=cr.radio("**Scope**",["India","World"],key="geo_s")
    has_c=[n for n in sc.nodes.values() if n.x!=0 or n.y!=0]
    if not has_c: st.info("No coordinates found. Load the demo supply chain to see the India map.")
    else:
        st.plotly_chart(draw_geo_map(sc,mscope.lower()),use_container_width=True)
        with st.expander("📋 **Node Coordinates**"):
            st.dataframe(pd.DataFrame([{"Node":n.name,"Type":n.node_type,"Lat":n.y,"Lon":n.x,"Location":n.location} for n in sc.nodes.values()]),use_container_width=True,hide_index=True)


# ─────────────────────────────────────────────────────────────
# TAB 9 — REPORTS
# ─────────────────────────────────────────────────────────────
with t9:
    st.markdown('<div class="sh">📊 Supply Chain Report Generator</div>',unsafe_allow_html=True)
    st.caption("Generate a **comprehensive Excel report** with charts, data, color coding, and recommendations.")

    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**📅 Report Period**")
        c1,c2=st.columns(2)
        start_dt=c1.date_input("**From Date**",value=date.today()-timedelta(days=30),key="rpt_start")
        end_dt  =c2.date_input("**To Date**",  value=date.today(),                   key="rpt_end")

        st.markdown("**📋 Report Sections**")
        c1,c2,c3=st.columns(3)
        inc_network =c1.checkbox("**Network Summary**",value=True,key="r1")
        inc_demand  =c1.checkbox("**Demand Fulfillment**",value=True,key="r2")
        inc_inv     =c2.checkbox("**Inventory Status**",value=True,key="r3")
        inc_risk    =c2.checkbox("**Risk Analysis**",value=True,key="r4")
        inc_forecast=c3.checkbox("**Demand Forecast**",value=True,key="r5")
        inc_score   =c3.checkbox("**Supplier Scorecard**",value=True,key="r6")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("📥 Generate & Download Excel Report",use_container_width=True,type="primary",key="gen_report"):
        with st.spinner("Generating comprehensive report..."):
            try:
                ranking_for_report=st.session_state.ranking or []
                report_bytes=generate_excel_report(sc,inv,st.session_state.forecaster,
                                                   ranking_for_report,start_dt,end_dt)
                fname=f"SC_Report_{start_dt}_{end_dt}.xlsx"
                st.download_button(
                    label=f"⬇ Download: {fname}",
                    data=report_bytes,file_name=fname,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
                st.success(f"✓ Report generated! Click above to download.")
            except Exception as ex:
                st.error(f"Report generation failed: {ex}")

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sh">📋 Report Preview</div>',unsafe_allow_html=True)
    with st.expander("**Network Summary Preview**"):
        plants=[n for n in sc.nodes.values() if n.node_type=="plant"]
        whs_=[n for n in sc.nodes.values() if n.node_type=="warehouse"]
        dems_=[n for n in sc.nodes.values() if n.node_type=="demand"]
        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | **Manufacturing Plants** | {len(plants)} |
        | **Warehouses** | {len(whs_)} |
        | **Demand Points** | {len(dems_)} |
        | **Network Connections** | {len(sc.edges)} |
        | **Total Plant Capacity** | {sum(n.capacity for n in plants):,.0f} |
        | **Total Demand** | {sum(n.capacity for n in dems_):,.0f} |
        | **Supply Coverage** | {round(sum(n.capacity for n in plants)/max(sum(n.capacity for n in dems_),1)*100,1)}% |
        """)
    with st.expander("**Inventory Status Preview**"):
        inv_df=inv.to_df(sc.nodes)
        if not inv_df.empty:
            def cs3(v): return f"color:{'#E74C3C' if v=='Critical' else '#E67E22' if v=='Low' else '#27AE60'};font-weight:700"
            st.dataframe(inv_df[["Node","Item","Current Stock","Safety Stock","Coverage Days","Status"]].style.map(cs3,subset=["Status"]),use_container_width=True,hide_index=True)
    with st.expander("**Risk Analysis Preview**"):
        if st.session_state.ranking:
            for r in st.session_state.ranking[:5]:
                badge={"critical":"b-r","high":"b-a","medium":"b-b","low":"b-g"}[r["severity"]]
                st.markdown(f'<span class="{badge}">{r["severity"].upper()}</span> **{r["label"]}** — Drop: **{r["avg_fulfillment_drop"]}%** | Resilience: **{r["resilience_score"]}%**',unsafe_allow_html=True)
        else:
            st.info("Run **Stress Test** in Risk Heatmap tab first.")


# ─────────────────────────────────────────────────────────────
# TAB 10 — AI ASSISTANT (Free via Groq)
# ─────────────────────────────────────────────────────────────
with t10:
    st.markdown('<div class="sh">🤖 AI Supply Chain Assistant</div>',unsafe_allow_html=True)

    if not st.session_state.ai_key:
        st.markdown(f"""
        <div class="al-a">
        <b>🔑 Free AI Setup Required</b><br><br>
        This assistant uses <b>Groq</b> — completely free, no credit card needed!<br><br>
        <b>Steps:</b><br>
        1. Go to <a href="{GROQ_SIGNUP}" target="_blank"><b>console.groq.com</b></a><br>
        2. Sign up free → API Keys → Create Key<br>
        3. Copy key (starts with <code>gsk_</code>)<br>
        4. Paste in sidebar → <b>AI Assistant Setup</b><br><br>
        <i>Models available: Llama 3.1 8B (fast) · Llama 3.3 70B (smart) · Gemma 2 9B</i>
        </div>""", unsafe_allow_html=True)

    # Voice
    st.markdown('<div class="sh">🎤 Voice Interface</div>', unsafe_allow_html=True)
    voice_component()
    st.markdown("<br>",unsafe_allow_html=True)

    # Quick actions
    st.markdown('<div class="sh">⚡ Quick Actions</div>', unsafe_allow_html=True)
    qa_cols=st.columns(4)
    for i,(label,query) in enumerate([
        ("Platform Tour","Give me a complete tour of this supply chain platform."),
        ("Network Status","What is my current supply chain network status?"),
        ("Stock Alerts","Check my inventory and tell me what needs urgent attention."),
        ("Best Practices","What supply chain resilience best practices should I implement?"),
    ]):
        if qa_cols[i].button(label,use_container_width=True,key=f"qa_{i}"):
            st.session_state.chat_history.append({"role":"user","content":query}); st.rerun()

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sh">💬 Conversation</div>', unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown("""
        <div style="background:#F8F9FA;border:1px solid #E5E8E8;border-radius:12px;padding:28px;
          text-align:center;color:#5D6D7E;margin:10px 0">
          <div style="font-size:32px;margin-bottom:8px">⬡</div>
          <div style="font-size:15px;font-weight:700;color:#2C3E50;margin-bottom:6px">SR AI Assistant</div>
          <div style="font-size:13px">Ask anything, execute actions, or use quick buttons above.</div>
        </div>""", unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            role=msg["role"]; content=msg.get("display",msg["content"])
            if role=="user":
                st.markdown(f'<div class="chat-wrap chat-right"><div class="user-bubble">{content}</div></div>',unsafe_allow_html=True)
            else:
                ar=msg.get("action_result","")
                ar_html=f'<div class="al-g" style="margin-top:6px;font-size:12px">{ar}</div>' if ar else ""
                st.markdown(f'<div class="chat-wrap chat-left"><div class="ai-bubble">{content}{ar_html}</div></div>',unsafe_allow_html=True)

    # Auto-respond
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"]=="user":
        if not st.session_state.ai_key:
            um=st.session_state.chat_history[-1]["content"].lower()
            if any(w in um for w in ["status","network","supply"]):
                plants=[n for n in sc.nodes.values() if n.node_type=="plant"]
                al=inv.get_alerts(sc.nodes)
                reply=f"Network: **{len(plants)} plants**, **{len(sc.edges)} connections**. Stock alerts: **{len([a for a in al if a['level']=='critical'])} critical**. Add your free Groq API key in the sidebar for full AI responses!"
            else:
                reply="Add your **free Groq API key** in the sidebar (AI Assistant Setup) to enable full AI responses. Get it free at [console.groq.com](https://console.groq.com)!"
            disp=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',reply)
            st.session_state.chat_history.append({"role":"assistant","content":reply,"display":disp}); st.rerun()
        else:
            mc=FREE_AI_MODELS[st.session_state.ai_model]
            # Build context
            plants=[n for n in sc.nodes.values() if n.node_type=="plant"]
            al=inv.get_alerts(sc.nodes)
            ctx=(f"[NETWORK: {len(plants)} plants, {len(sc.nodes)-len(plants)} other nodes, "
                 f"{len(sc.edges)} connections, "
                 f"{len([a for a in al if a['level']=='critical'])} critical stock alerts]\n")
            messages=[]
            for m in st.session_state.chat_history:
                content=m["content"]
                if m["role"]=="user" and len(messages)==0: content=ctx+"User: "+content
                messages.append({"role":m["role"],"content":content})
            with st.spinner("Thinking..."):
                reply_text,status=call_free_ai(messages,st.session_state.ai_key,mc)
            if status=="ok" and reply_text:
                action=parse_action(reply_text); display=clean_response(reply_text)
                dhtml=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',display).replace('\n','<br>')
                ar=""
                if action:
                    modifying=action.get("action") in ("update_stock",)
                    if modifying:
                        st.session_state["pending_action"]=action
                        dhtml+="<br><br><i>⚡ I can execute this. Type <b>confirm</b> to proceed or <b>cancel</b> to abort.</i>"
                    else:
                        ok,msg=execute_action(action,sc,inv)
                        ar=("✓ "+msg) if ok else ("✗ "+msg)
                st.session_state.chat_history.append({"role":"assistant","content":reply_text,"display":dhtml,"action_result":ar})
                st.session_state.last_ai_text=display; st.rerun()
            elif status=="rate_limit":
                st.session_state.chat_history.append({"role":"assistant","content":"Rate limit reached. Please wait a moment and try again.","display":"Rate limit reached. Please wait a moment and try again."}); st.rerun()
            elif status=="invalid_key":
                st.session_state.chat_history.append({"role":"assistant","content":"Invalid API key. Check your Groq key in the sidebar.","display":"Invalid API key. Check your Groq key in the sidebar."}); st.rerun()
            elif status=="timeout":
                st.session_state.chat_history.append({"role":"assistant","content":"Request timed out. Please try again.","display":"Request timed out. Please try again."}); st.rerun()
            else:
                st.session_state.chat_history.append({"role":"assistant","content":f"Error: {status}","display":f"Error: {status}"}); st.rerun()

    # Pending action confirmation
    if "pending_action" in st.session_state and st.session_state.chat_history and st.session_state.chat_history[-1]["role"]=="user":
        ut=st.session_state.chat_history[-1]["content"].strip().lower()
        if ut in ("confirm","yes","proceed","ok"):
            ok,msg=execute_action(st.session_state["pending_action"],sc,inv)
            st.session_state.chat_history.append({"role":"assistant","content":f"✓ {msg}","display":f"✓ {msg}","action_result":("✓" if ok else "✗")+" "+msg})
            del st.session_state["pending_action"]; st.rerun()
        elif ut in ("cancel","no","abort"):
            st.session_state.chat_history.append({"role":"assistant","content":"Action cancelled.","display":"Action cancelled."})
            del st.session_state["pending_action"]; st.rerun()

    st.markdown("<br>",unsafe_allow_html=True)
    with st.form("chat_form",clear_on_submit=True):
        c1,c2=st.columns([5,1])
        ui=c1.text_input("**Message...**",placeholder="Ask anything or paste voice text...",label_visibility="collapsed",key="chat_in")
        send=c2.form_submit_button("Send",use_container_width=True)
        if send and ui.strip():
            st.session_state.chat_history.append({"role":"user","content":ui.strip()}); st.rerun()

    if st.session_state.last_ai_text:
        st.markdown(f"""<script>setTimeout(function(){{if(window.speakText)window.speakText({json.dumps(st.session_state.last_ai_text[:400])});}},800);</script>""",unsafe_allow_html=True)

    col_clr,_=st.columns([1,4])
    if col_clr.button("🗑 Clear Chat",key="clr_chat"):
        st.session_state.chat_history=[]; st.session_state.last_ai_text=""; st.rerun()
