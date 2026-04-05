"""
Supply Chain Resilience Platform v4.0 — Enterprise Edition
Birla Institute of Technology, Mesra
All features: AI Assistant (fixed), Dark Heatmap, Demand Forecasting,
AI-Driven Automation, Voice Assistant, Premium UI
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
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import json, math, io, re, requests
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# LOGO (BIT Mesra)
# ═══════════════════════════════════════════════════════════════
LOGO_B64 = "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"

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
# SUPPLY CHAIN ENGINE
# ═══════════════════════════════════════════════════════════════
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

    def remove_edge(self, src, tgt):
        self.edges = [e for e in self.edges if not (e.source == src and e.target == tgt)]

    def toggle_edge(self, src, tgt, active):
        for e in self.edges:
            if e.source == src and e.target == tgt:
                e.active = active

    def to_nx(self):
        G = nx.DiGraph()
        for nid, n in self.nodes.items():
            G.add_node(nid, **vars(n))
        for e in self.edges:
            if e.active:
                G.add_edge(e.source, e.target, capacity=e.capacity, weight=e.cost)
        return G

    def shortest_path(self, src, tgt):
        G = self.to_nx()
        try:
            path = nx.dijkstra_path(G, src, tgt, weight="weight")
            cost = nx.dijkstra_path_length(G, src, tgt, weight="weight")
            return {"found": True, "path": path, "cost": round(cost, 2)}
        except:
            return {"found": False, "path": [], "cost": None}

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
        plants  = [n for n, d in self.nodes.items() if d.node_type == "plant"]
        demands = [n for n, d in self.nodes.items() if d.node_type == "demand"]
        results = {}
        for d_id in demands:
            req = self.nodes[d_id].capacity
            total, reach = 0.0, []
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
                "resilience_score": round(max(0,100-avg_drop),1),
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
        self.items = {}
        self.stock = {}

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
            node_name = sc_nodes[node_id].name if sc_nodes and node_id in sc_nodes else node_id
            for iid, s in items.items():
                iname = self.items.get(iid,{}).get("name",iid)
                if s["current"] <= s["reorder"]:
                    alerts.append({"node_id":node_id,"node_name":node_name,"item_id":iid,
                        "item_name":iname,"level":"critical" if s["current"]<=s["safety"] else "warning",
                        "current":s["current"],"safety":s["safety"],"reorder":s["reorder"],
                        "coverage":self.coverage_days(node_id,iid)})
        return sorted(alerts, key=lambda x:(x["level"]!="critical",x["coverage"] or 999))

    def find_alternatives(self, demand_id, iid, required, sc, disrupted=None):
        alts = []
        for node_id, items in self.stock.items():
            if node_id == demand_id or iid not in items: continue
            s = items[iid]; avail = max(0.0, s["current"]-s["safety"])
            if avail <= 0: continue
            if disrupted: sc.toggle_edge(disrupted[0], disrupted[1], False)
            r = sc.shortest_path(node_id, demand_id)
            if disrupted: sc.toggle_edge(disrupted[0], disrupted[1], True)
            if r["found"]:
                alts.append({"node_id":node_id,
                    "node_name":sc.nodes[node_id].name if node_id in sc.nodes else node_id,
                    "available":avail,"can_cover":avail>=required,
                    "coverage_pct":min(100,round(avail/max(required,1)*100,1)),
                    "path":[sc.nodes[n].name for n in r["path"] if n in sc.nodes],
                    "path_ids":r["path"],"route_cost":r["cost"],
                    "coverage_days":self.coverage_days(node_id,iid)})
        return sorted(alts, key=lambda x:(-x["coverage_pct"],x["route_cost"]))[:5]

    def to_df(self, sc_nodes=None):
        rows = []
        for node_id, items in self.stock.items():
            nn = sc_nodes[node_id].name if sc_nodes and node_id in sc_nodes else node_id
            nt = sc_nodes[node_id].node_type if sc_nodes and node_id in sc_nodes else ""
            for iid, s in items.items():
                iname = self.items.get(iid,{}).get("name",iid)
                unit = self.items.get(iid,{}).get("unit","units")
                dd = s.get("daily_demand",1)
                cov = round(s["current"]/dd,1) if dd>0 else 999
                avail = max(0,s["current"]-s["safety"])
                status = "Critical" if s["current"]<=s["safety"] else "Low" if s["current"]<=s["reorder"] else "Normal"
                rows.append({"Node":nn,"Type":nt.capitalize(),"Item":iname,"Unit":unit,
                    "Current Stock":s["current"],"Safety Stock":s["safety"],
                    "Reorder Point":s["reorder"],"Daily Demand":dd,
                    "Coverage Days":cov,"Available (above safety)":avail,"Status":status})
        return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════
# DEMAND FORECASTING ENGINE
# ═══════════════════════════════════════════════════════════════
class DemandForecaster:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.history = {}
        self.forecasts = {}
        self.metrics = {}

    def generate_synthetic_history(self, node_id, node_name, base_demand, days=365, seed=None):
        if seed is None: seed = hash(node_id) % 1000
        np.random.seed(seed); t = np.arange(days)
        # Trend + weekly + annual seasonality + noise
        trend = base_demand + 0.05*t
        weekly = base_demand*0.15*np.sin(2*np.pi*t/7 + np.random.uniform(0,np.pi))
        annual = base_demand*0.20*np.sin(2*np.pi*t/365)
        noise  = np.random.normal(0, base_demand*0.08, days)
        demand = np.maximum(0, trend + weekly + annual + noise)
        dates = [datetime.today() - timedelta(days=days-i) for i in range(days)]
        df = pd.DataFrame({"date":dates,"demand":demand,"node_id":node_id,"node_name":node_name})
        self.history[node_id] = df
        return df

    def _make_features(self, y, lags=[1,7,14,30]):
        max_lag = max(lags); X, y_out = [], []
        for i in range(max_lag, len(y)):
            feats = [i, i%7, i%30, i//30, i//90]
            for lag in lags: feats.append(float(y[i-lag]))
            feats.append(float(np.mean(y[max(0,i-7):i])))
            feats.append(float(np.mean(y[max(0,i-30):i])))
            feats.append(float(np.std(y[max(0,i-14):i]) if i>=14+max_lag else 1.0))
            X.append(feats); y_out.append(float(y[i]))
        return np.array(X, dtype=float), np.array(y_out, dtype=float)

    def train(self, node_id, horizon=30):
        if node_id not in self.history: return None
        df = self.history[node_id]; y = df["demand"].values
        X, y_trim = self._make_features(y)
        split = int(len(X)*0.80)
        if split < 30: split = len(X)-15

        # Ensemble: RF + GBM
        rf  = RandomForestRegressor(n_estimators=120, max_depth=8, random_state=42, n_jobs=-1)
        gbm = GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
        rf.fit(X[:split], y_trim[:split])
        gbm.fit(X[:split], y_trim[:split])

        # Validation metrics
        rf_pred  = rf.predict(X[split:])
        gbm_pred = gbm.predict(X[split:])
        ens_pred = 0.5*rf_pred + 0.5*gbm_pred
        y_val    = y_trim[split:]

        rmse = float(np.sqrt(mean_squared_error(y_val, ens_pred)))
        mae  = float(mean_absolute_error(y_val, ens_pred))
        mape = float(np.mean(np.abs((y_val - ens_pred)/(y_val+1e-6)))*100)
        r2   = float(1 - np.sum((y_val-ens_pred)**2)/np.sum((y_val-np.mean(y_val))**2))

        self.models[node_id] = (rf, gbm)
        self.metrics[node_id] = {"rmse":round(rmse,2),"mae":round(mae,2),
                                  "mape":round(mape,2),"r2":round(r2,3)}

        # Future forecast — iterative
        history_vals = list(y)
        future_preds = []
        for step in range(horizon):
            i = len(history_vals)
            lags = [1,7,14,30]
            feats = [i, i%7, i%30, i//30, i//90]
            for lag in lags:
                feats.append(float(history_vals[-lag]) if lag<=len(history_vals) else float(np.mean(history_vals[-min(lag,len(history_vals)):])))
            feats.append(float(np.mean(history_vals[-7:])))
            feats.append(float(np.mean(history_vals[-30:])))
            feats.append(float(np.std(history_vals[-14:])) if len(history_vals)>=14 else 1.0)
            arr = np.array(feats, dtype=float).reshape(1,-1)
            pred = 0.5*rf.predict(arr)[0] + 0.5*gbm.predict(arr)[0]
            pred = max(0, pred); future_preds.append(pred); history_vals.append(pred)

        last_date = df["date"].iloc[-1]
        future_dates = [last_date + timedelta(days=i+1) for i in range(horizon)]
        fdf = pd.DataFrame({"date":future_dates,"forecast":future_preds,"node_id":node_id,"node_name":df["node_name"].iloc[0]})
        # Confidence interval ±1.5*RMSE
        fdf["upper"] = fdf["forecast"] + 1.5*rmse
        fdf["lower"] = np.maximum(0, fdf["forecast"] - 1.5*rmse)
        self.forecasts[node_id] = fdf
        return fdf

    def aggregate_to_warehouses(self, sc, horizon=30):
        """Sum demand node forecasts to serving warehouses"""
        wh_forecasts = {}
        for wh_id, wh in sc.nodes.items():
            if wh.node_type != "warehouse": continue
            G = sc.to_nx()
            served_demands = []
            for d_id, d in sc.nodes.items():
                if d.node_type == "demand":
                    try:
                        nx.shortest_path(G, wh_id, d_id)
                        served_demands.append(d_id)
                    except: pass
            if not served_demands: continue
            total = np.zeros(horizon)
            for d_id in served_demands:
                if d_id in self.forecasts:
                    vals = self.forecasts[d_id]["forecast"].values[:horizon]
                    total[:len(vals)] += vals
            wh_forecasts[wh_id] = {"name":wh.name,"forecast":total.tolist(),"served_demands":served_demands}
        return wh_forecasts

    def get_plant_requirements(self, sc, wh_forecasts, horizon=30):
        """Aggregate warehouse requirements to plants"""
        plant_req = {}
        for p_id, p in sc.nodes.items():
            if p.node_type != "plant": continue
            G = sc.to_nx()
            served_wh = []
            for wh_id in wh_forecasts:
                try:
                    nx.shortest_path(G, p_id, wh_id)
                    served_wh.append(wh_id)
                except: pass
            total = np.zeros(horizon)
            for wh_id in served_wh:
                total += np.array(wh_forecasts[wh_id]["forecast"][:horizon])
            plant_req[p_id] = {"name":p.name,"required":total.tolist(),
                               "capacity":p.capacity,"served_wh":served_wh}
        return plant_req


# ═══════════════════════════════════════════════════════════════
# AI ASSISTANT ENGINE
# ═══════════════════════════════════════════════════════════════

AI_SYSTEM_PROMPT = """You are an expert AI assistant embedded inside the Supply Chain Resilience Platform — Birla Institute of Technology, Mesra.

You can BOTH answer questions AND execute actions in the system. When you need to perform an action, include an action block EXACTLY like this in your response:

ACTION_JSON_START
{"action":"update_stock","node":"Plant Mumbai","item":"Rice","quantity":100,"operation":"add"}
ACTION_JSON_END

Available actions and their JSON formats:
1. Update stock: {"action":"update_stock","node":"<node name>","item":"<item name>","quantity":<number>,"operation":"add|remove|set"}
2. Find path: {"action":"find_path","from":"<node name>","to":"<node name>"}
3. Run disruption: {"action":"run_disruption","connection":"<source name> → <target name>"}
4. Check ATP: {"action":"check_atp","item":"<item name>","quantity":<number>,"destination":"<node name>"}
5. Get status: {"action":"get_status"}
6. Run forecast: {"action":"run_forecast","node":"<demand node name>","horizon":<days>}

IMPORTANT RULES:
- ALWAYS ask for confirmation before executing any action that modifies data (stock update, etc.)
- If information is missing, ask for it specifically (e.g., which node, which item, how many units)
- Be concise, professional, and helpful
- For complex queries, break down your response into clear steps
- When you detect an action intent, extract all entities before suggesting the action

PLATFORM GUIDE:
Tab 1 - Network Map: Interactive supply chain visualization. Nodes (Plants=squares, Warehouses=diamonds, Demand=circles). Shortest path finder, demand fulfillment gauges.
Tab 2 - Inventory & Stock: SKU-level stock tracking, alerts, live updates, coverage days analysis.
Tab 3 - Disruption Simulator: Simulate connection failures, see resilience score, alternate routes, safety stock alternatives.
Tab 4 - Risk Heatmap: Dark color matrix showing node risk exposure. Run stress test to rank critical connections.
Tab 5 - Demand Forecasting: AI-powered demand prediction using RandomForest+GBM ensemble. Upload historical data or use generated data.
Tab 6 - Dispatch Log: Record goods movement, live blue markers on map.
Tab 7 - ATP & Scorecard: Available-to-Promise check, supplier performance radar charts.
Tab 8 - Geographic View: India/World map with node locations.
Tab 9 - AI Assistant: You! With voice input/output, action execution, and full platform integration.

Common errors:
- "No path found": Nodes not connected by active edges
- "Node not found": Check node ID exists before adding connections
- Stock not updating: Verify node ID and item ID match exactly
"""

def call_ai(messages, api_key):
    """Call Anthropic API and return response text"""
    if not api_key or not api_key.strip():
        return None, "no_key"
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type":"application/json",
                     "x-api-key":api_key.strip(),
                     "anthropic-version":"2023-06-01"},
            json={"model":"claude-opus-4-5",
                  "max_tokens":1500,
                  "system":AI_SYSTEM_PROMPT,
                  "messages":messages},
            timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "content" in data and data["content"]:
                return data["content"][0]["text"], "ok"
            return None, "empty"
        elif r.status_code == 401:
            return None, "invalid_key"
        else:
            return None, f"error_{r.status_code}"
    except requests.exceptions.Timeout:
        return None, "timeout"
    except Exception as e:
        return None, f"exception_{str(e)}"

def parse_action(text):
    """Extract action JSON from AI response"""
    pattern = r"ACTION_JSON_START\s*(.*?)\s*ACTION_JSON_END"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except:
            return None
    return None

def clean_response(text):
    """Remove action blocks from display text"""
    return re.sub(r"ACTION_JSON_START.*?ACTION_JSON_END", "", text, flags=re.DOTALL).strip()

def execute_action(action, sc, inv):
    """Execute a parsed action and return result message"""
    a = action.get("action","")
    try:
        if a == "update_stock":
            node_name = action.get("node",""); item_name = action.get("item","")
            qty = float(action.get("quantity",0)); op = action.get("operation","add")
            # Find node id by name
            node_id = next((n.id for n in sc.nodes.values() if n.name.lower()==node_name.lower()), None)
            item_id = next((iid for iid,iv in inv.items.items() if iv["name"].lower()==item_name.lower()), None)
            if not node_id: return False, f"Node '{node_name}' not found"
            if not item_id: return False, f"Item '{item_name}' not found in inventory"
            if op == "add":
                inv.update_stock(node_id, item_id, qty)
                return True, f"Added {qty:.0f} units of {item_name} to {node_name}"
            elif op == "remove":
                inv.update_stock(node_id, item_id, -qty)
                return True, f"Removed {qty:.0f} units of {item_name} from {node_name}"
            elif op == "set":
                if node_id in inv.stock and item_id in inv.stock[node_id]:
                    inv.stock[node_id][item_id]["current"] = qty
                    return True, f"Set {item_name} at {node_name} to {qty:.0f} units"
            return False, "Unknown operation"

        elif a == "find_path":
            frm = action.get("from",""); to = action.get("to","")
            from_id = next((n.id for n in sc.nodes.values() if n.name.lower()==frm.lower()), None)
            to_id   = next((n.id for n in sc.nodes.values() if n.name.lower()==to.lower()), None)
            if not from_id or not to_id: return False, "One or both nodes not found"
            result = sc.all_shortest_paths(from_id, to_id, k=3)
            if result:
                st.session_state.highlight_path = result[0]["path"]
                paths_text = " → ".join(sc.nodes[n].name for n in result[0]["path"])
                return True, f"Path found and highlighted on map: {paths_text} (cost: {result[0]['cost']})"
            return False, "No path found between these nodes"

        elif a == "run_disruption":
            conn = action.get("connection","")
            parts = conn.split("→")
            if len(parts) != 2: return False, "Invalid connection format. Use 'Source → Target'"
            src_name = parts[0].strip(); tgt_name = parts[1].strip()
            src_id = next((n.id for n in sc.nodes.values() if n.name.lower()==src_name.lower()), None)
            tgt_id = next((n.id for n in sc.nodes.values() if n.name.lower()==tgt_name.lower()), None)
            if not src_id or not tgt_id: return False, "One or both nodes not found"
            result = sc.simulate_disruption(src_id, tgt_id)
            st.session_state.disruption_result = result
            st.session_state.disrupted_edge = (src_id, tgt_id)
            return True, f"Disruption simulated for {conn}. Resilience score: {result['resilience_score']}%. Check Disruption Simulator tab."

        elif a == "get_status":
            plants = [n for n in sc.nodes.values() if n.node_type=="plant"]
            wh     = [n for n in sc.nodes.values() if n.node_type=="warehouse"]
            dem    = [n for n in sc.nodes.values() if n.node_type=="demand"]
            alerts = inv.get_alerts(sc.nodes)
            return True, (f"Network: {len(plants)} plants, {len(wh)} warehouses, {len(dem)} demand points, "
                         f"{len(sc.edges)} connections. "
                         f"Stock alerts: {len([a for a in alerts if a['level']=='critical'])} critical, "
                         f"{len([a for a in alerts if a['level']=='warning'])} warnings.")

        elif a == "run_forecast":
            node_name = action.get("node",""); horizon = int(action.get("horizon",30))
            node_id = next((n.id for n in sc.nodes.values() if n.name.lower()==node_name.lower()), None)
            if not node_id: return False, f"Node '{node_name}' not found"
            node = sc.nodes[node_id]
            fc = st.session_state.forecaster
            if node_id not in fc.history:
                fc.generate_synthetic_history(node_id, node.name, node.capacity, days=365)
            fdf = fc.train(node_id, horizon=horizon)
            if fdf is not None:
                m = fc.metrics[node_id]
                st.session_state.forecast_trained.add(node_id)
                return True, (f"Forecast completed for {node_name} ({horizon} days). "
                             f"Model accuracy — RMSE: {m['rmse']:.1f}, MAE: {m['mae']:.1f}, R²: {m['r2']:.3f}. "
                             f"Check Demand Forecasting tab for charts.")
            return False, "Forecast training failed"

    except Exception as ex:
        return False, f"Action failed: {str(ex)}"
    return False, "Unknown action"


# ═══════════════════════════════════════════════════════════════
# DEMO DATA
# ═══════════════════════════════════════════════════════════════
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
    sc.add_node(Node("D4","Bhubaneswar Mkt", "demand",100,"Bhubaneswar",    85.82,20.30))
    sc.add_node(Node("D5","Hyderabad Market","demand",160,"Hyderabad, India",78.49,17.39))
    sc.add_node(Node("D6","Kochi Market",    "demand",140,"Kochi, India",   76.27, 9.93))
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
    inv = InventoryManager()
    for iid,name,unit in [("SKU001","Rice","Tonnes"),("SKU002","Wheat","Tonnes"),
                           ("SKU003","Sugar","Tonnes"),("SKU004","Edible Oil","KL")]:
        inv.add_item(iid,name,unit)
    for node_id,iid,cur,saf,reo,dd in [
        ("P1","SKU001",520,100,150,22),("P1","SKU002",410,80,120,16),
        ("P2","SKU002",360,70,110,14),("P2","SKU003",310,60,90,11),
        ("P3","SKU001",285,55,85,11),("P3","SKU004",205,40,65,9),
        ("W1","SKU001",185,50,75,9),("W1","SKU002",155,40,65,7),
        ("W2","SKU001",125,30,55,6),("W2","SKU003",42,25,45,5),  # low!
        ("W2","SKU004",82,20,35,4),("W3","SKU002",92,20,38,5),
        ("W3","SKU003",18,15,28,4),  # critical!
        ("W4","SKU001",62,15,28,4),("W4","SKU004",52,12,22,3)]:
        inv.set_stock(node_id,iid,cur,saf,reo,dd)
    return inv

def load_demo_scores():
    return {"P1":{"reliability":92,"lead_time":88,"quality":95,"cost_efficiency":78},
            "P2":{"reliability":85,"lead_time":91,"quality":89,"cost_efficiency":84},
            "P3":{"reliability":79,"lead_time":83,"quality":91,"cost_efficiency":90},
            "W1":{"reliability":94,"lead_time":90,"quality":87,"cost_efficiency":75},
            "W2":{"reliability":88,"lead_time":85,"quality":82,"cost_efficiency":88},
            "W3":{"reliability":76,"lead_time":79,"quality":84,"cost_efficiency":92},
            "W4":{"reliability":82,"lead_time":86,"quality":88,"cost_efficiency":85}}


# ═══════════════════════════════════════════════════════════════
# EXCEL TEMPLATE
# ═══════════════════════════════════════════════════════════════
def create_excel_template():
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        pd.DataFrame({"id":["P1","W1","D1"],"name":["Plant 1","Warehouse North","Demand Point 1"],
            "node_type":["plant","warehouse","demand"],"capacity":[500,400,200],
            "location":["City1","City2","City3"],"x_longitude":[0,0,0],"y_latitude":[0,0,0]
        }).to_excel(w,"Nodes",index=False)
        pd.DataFrame({"source":["P1","W1"],"target":["W1","D1"],"capacity":[300,200],"cost":[2.0,1.0]
        }).to_excel(w,"Connections",index=False)
        pd.DataFrame({"node_id":["P1","W1"],"item_id":["SKU001","SKU001"],
            "item_name":["Rice","Rice"],"unit":["Tonnes","Tonnes"],
            "current_stock":[500,180],"safety_stock":[100,50],"reorder_point":[150,70],"daily_demand":[20,8]
        }).to_excel(w,"Inventory",index=False)
        pd.DataFrame({"date":["2024-01-01","2024-01-02","2024-01-03"],
            "node_id":["D1","D1","D1"],"demand":[198,205,192]
        }).to_excel(w,"Historical_Demand",index=False)
    buf.seek(0); return buf.getvalue()


# ═══════════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════════
NC  = {"plant":"#1A6B4A","warehouse":"#1A3F6B","demand":"#6B1A1A"}  # Node colors
NS  = {"plant":"square","warehouse":"diamond","demand":"circle"}     # Node symbols
SC  = {"critical":"#C0392B","high":"#E67E22","medium":"#2980B9","low":"#1A8A4A","none":"#7F8C8D"}
STC = {"Normal":"#1A8A4A","Low":"#E67E22","Critical":"#C0392B"}

DARK_HEATMAP = [[0.0,"#0A1628"],[0.15,"#0D2B4F"],[0.3,"#1B4F8A"],
                [0.5,"#E87722"],[0.7,"#C0392B"],[0.85,"#8B0000"],[1.0,"#4A0000"]]


# ═══════════════════════════════════════════════════════════════
# VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════
def _auto_layout(sc):
    layers = {"plant":[],"warehouse":[],"demand":[]}
    for nid,n in sc.nodes.items(): layers.get(n.node_type,layers["warehouse"]).append(nid)
    pos = {}
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
        is_hi=(e.source,e.target) in hp_set
        is_it=(e.source,e.target) in it_edges
        col="#C0392B" if is_dis else "#F39C12" if is_hi else "#2E86C1" if is_it else "#5D6D7E"
        w=3 if is_hi else 2.5 if is_dis else 2.5 if is_it else 1.5
        dash="dot" if(not e.active or is_dis) else "solid"
        traces.append(go.Scatter(x=[x0,x1,None],y=[y0,y1,None],mode="lines",
            line=dict(color=col,width=w,dash=dash),
            hovertext=f"{sc.nodes[e.source].name}→{sc.nodes[e.target].name} cap:{e.capacity}",
            hoverinfo="text",showlegend=False))
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
            textfont=dict(size=11,color="#ECF0F1"),
            hovertext=[f"<b>{sc.nodes[n].name}</b><br>{ntype}<br>Cap:{sc.nodes[n].capacity}" for n in nids],
            hoverinfo="text",
            marker=dict(symbol=NS[ntype],size=[22 if ip else 15 for ip in in_p],
                color=["#F39C12" if ip else NC[ntype] for ip in in_p],
                line=dict(width=2,color="#ECF0F1"))))
    fig=go.Figure(data=traces)
    fig.update_layout(paper_bgcolor="#1A1A2E",plot_bgcolor="#16213E",
        margin=dict(l=10,r=10,t=10,b=10),height=460,hovermode="closest",
        xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
        yaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,
            font=dict(size=11,color="#ECF0F1"),bgcolor="rgba(0,0,0,0)"))
    return fig

def draw_gauge_charts(ff, nodes):
    demands=list(ff.items()); cols=min(3,len(demands)); rows=math.ceil(len(demands)/cols)
    specs=[[{"type":"indicator"} for _ in range(cols)] for _ in range(rows)]
    fig=make_subplots(rows=rows,cols=cols,specs=specs)
    for i,(d_id,info) in enumerate(demands):
        c=(i%cols)+1; r=(i//cols)+1; pct=info["pct"]
        col="#C0392B" if pct<50 else "#E67E22" if pct<80 else "#1A8A4A"
        fig.add_trace(go.Indicator(mode="gauge+number",value=pct,
            title={"text":nodes[d_id].name,"font":{"size":10,"color":"#BDC3C7"}},
            number={"suffix":"%","font":{"size":16,"color":col}},
            gauge={"axis":{"range":[0,100],"tickwidth":1,"tickcolor":"#5D6D7E"},
                   "bar":{"color":col},
                   "steps":[{"range":[0,50],"color":"#2C1B1B"},{"range":[50,80],"color":"#2C2A1B"},{"range":[80,100],"color":"#1B2C1B"}],
                   "bgcolor":"#1A1A2E"}),row=r,col=c)
    fig.update_layout(height=210*rows,paper_bgcolor="#1A1A2E",margin=dict(l=5,r=5,t=20,b=5))
    return fig

def draw_impact_chart(impact):
    names=[v["demand_name"] for v in impact.values()]
    before=[v["before_pct"] for v in impact.values()]
    after=[v["after_pct"] for v in impact.values()]
    fig=go.Figure()
    fig.add_trace(go.Bar(name="Before",x=names,y=before,marker_color="#1A8A4A",
        text=[f"{v}%" for v in before],textposition="outside",textfont=dict(size=10,color="#ECF0F1")))
    fig.add_trace(go.Bar(name="After",x=names,y=after,marker_color="#C0392B",
        text=[f"{v}%" for v in after],textposition="outside",textfont=dict(size=10,color="#ECF0F1")))
    fig.update_layout(barmode="group",yaxis=dict(title="Fulfillment (%)",range=[0,118],
        gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
        xaxis=dict(tickfont=dict(color="#BDC3C7")),
        paper_bgcolor="#1A1A2E",plot_bgcolor="#16213E",height=300,
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,font=dict(color="#BDC3C7")),
        margin=dict(l=10,r=10,t=10,b=10))
    fig.add_hline(y=100,line_dash="dot",line_color="#5D6D7E")
    return fig

def draw_dark_heatmap(sc, ranking):
    if not ranking: return go.Figure()
    node_ids=list(sc.nodes.keys()); node_names=[sc.nodes[n].name for n in node_ids]
    z=[]
    for nid in node_ids:
        outs=[r for r in ranking if r["source"]==nid]
        ins =[r for r in ranking if r["target"]==nid]
        max_out=max((r["avg_fulfillment_drop"] for r in outs),default=0)
        max_in =max((r["avg_fulfillment_drop"] for r in ins),default=0)
        nc_out=sum(1 for r in outs if r["severity"]=="critical")
        nc_in =sum(1 for r in ins if r["severity"]=="critical")
        z.append([max_out,max_in,nc_out*25,nc_in*25])
    fig=go.Figure(go.Heatmap(
        z=z,x=["Outbound<br>Max Drop","Inbound<br>Max Drop","Critical<br>Out Links","Critical<br>In Links"],
        y=node_names,colorscale=DARK_HEATMAP,
        text=[[f"<b>{v:.0f}</b>" for v in row] for row in z],
        texttemplate="%{text}",textfont={"size":12,"color":"#FFFFFF"},
        hoverongaps=False,showscale=True,zmin=0,zmax=100,
        colorbar=dict(title=dict(text="Risk",font=dict(color="#ECF0F1")),
                     tickfont=dict(color="#ECF0F1"),bgcolor="#1A1A2E",
                     outlinecolor="#2C3E50")))
    fig.update_layout(height=max(350,len(node_ids)*45),
        paper_bgcolor="#1A1A2E",plot_bgcolor="#1A1A2E",
        margin=dict(l=10,r=10,t=40,b=10),
        title=dict(text="Node Risk Exposure Matrix",font=dict(color="#ECF0F1",size=14),x=0.5),
        xaxis=dict(side="top",tickfont=dict(size=11,color="#BDC3C7")),
        yaxis=dict(tickfont=dict(size=11,color="#BDC3C7"),autorange="reversed"))
    return fig

def draw_criticality_chart(ranking):
    labels=[r["label"] for r in ranking]
    drops=[r["avg_fulfillment_drop"] for r in ranking]
    colors=[SC[r["severity"]] for r in ranking]
    fig=go.Figure(go.Bar(x=drops,y=labels,orientation="h",marker_color=colors,
        text=[f"  {d}%" for d in drops],textposition="outside",
        textfont=dict(size=11,color="#ECF0F1")))
    fig.update_layout(
        xaxis=dict(title="Avg. Fulfillment Drop (%)",range=[0,max(drops or [10])*1.35],
            gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
        yaxis=dict(autorange="reversed",tickfont=dict(size=11,color="#BDC3C7")),
        paper_bgcolor="#1A1A2E",plot_bgcolor="#16213E",
        height=max(320,len(ranking)*44),margin=dict(l=10,r=80,t=10,b=10))
    return fig

def draw_resilience_gauge(score):
    col="#C0392B" if score<40 else "#E67E22" if score<70 else "#1A8A4A"
    fig=go.Figure(go.Indicator(mode="gauge+number",value=score,
        number={"suffix":"%","font":{"size":36,"color":col}},
        gauge={"axis":{"range":[0,100],"tickwidth":1,"tickcolor":"#5D6D7E"},
               "bar":{"color":col},
               "steps":[{"range":[0,40],"color":"#2C1B1B"},{"range":[40,70],"color":"#2C2A1B"},{"range":[70,100],"color":"#1B2C1B"}],
               "bgcolor":"#1A1A2E",
               "threshold":{"line":{"color":col,"width":3},"thickness":0.75,"value":score}}))
    fig.update_layout(height=200,margin=dict(l=20,r=20,t=10,b=10),paper_bgcolor="#1A1A2E")
    return fig

def draw_forecast_chart(fc, node_id, sc_nodes):
    if node_id not in fc.history or node_id not in fc.forecasts: return go.Figure()
    hist=fc.history[node_id]; fore=fc.forecasts[node_id]
    fig=go.Figure()
    # Historical
    fig.add_trace(go.Scatter(x=hist["date"],y=hist["demand"],mode="lines",
        name="Historical",line=dict(color="#2E86C1",width=1.5),opacity=0.8))
    # Forecast
    fig.add_trace(go.Scatter(x=fore["date"],y=fore["forecast"],mode="lines",
        name="Forecast",line=dict(color="#F39C12",width=2.5,dash="dash")))
    # CI
    fig.add_trace(go.Scatter(
        x=list(fore["date"])+list(fore["date"][::-1]),
        y=list(fore["upper"])+list(fore["lower"][::-1]),
        fill="toself",fillcolor="rgba(243,156,18,0.15)",
        line=dict(color="rgba(0,0,0,0)"),name="95% CI",showlegend=True))
    node_name=sc_nodes[node_id].name if node_id in sc_nodes else node_id
    fig.update_layout(
        title=dict(text=f"Demand Forecast — {node_name}",font=dict(color="#ECF0F1",size=13),x=0.5),
        xaxis=dict(gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
        yaxis=dict(title="Units",gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
        paper_bgcolor="#1A1A2E",plot_bgcolor="#16213E",height=360,
        legend=dict(font=dict(color="#BDC3C7"),bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10,r=10,t=40,b=10))
    return fig

def draw_plant_requirements_chart(plant_req, horizon=30):
    fig=go.Figure()
    colors=["#2E86C1","#1A8A4A","#C0392B","#E67E22","#8E44AD"]
    for i,(pid,info) in enumerate(plant_req.items()):
        vals=info["required"][:horizon]
        cap_line=[info["capacity"]]*len(vals)
        x=list(range(1,len(vals)+1))
        fig.add_trace(go.Scatter(x=x,y=vals,mode="lines",
            name=info["name"],line=dict(color=colors[i%len(colors)],width=2)))
        fig.add_trace(go.Scatter(x=x,y=cap_line,mode="lines",
            name=f"{info['name']} Capacity",line=dict(color=colors[i%len(colors)],width=1,dash="dot"),
            showlegend=False))
    fig.update_layout(
        title=dict(text="Plant Manufacturing Requirements vs Capacity",font=dict(color="#ECF0F1",size=13),x=0.5),
        xaxis=dict(title="Days",gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
        yaxis=dict(title="Units Required",gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
        paper_bgcolor="#1A1A2E",plot_bgcolor="#16213E",height=340,
        legend=dict(font=dict(color="#BDC3C7"),bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10,r=10,t=40,b=10))
    return fig

def draw_scorecard_radar(name, scores):
    cats=["Reliability","Lead Time","Quality","Cost Efficiency","Reliability"]
    vals=[scores["reliability"],scores["lead_time"],scores["quality"],scores["cost_efficiency"],scores["reliability"]]
    fig=go.Figure(go.Scatterpolar(r=vals,theta=cats,fill="toself",
        line=dict(color="#2E86C1",width=2),fillcolor="rgba(46,134,193,0.2)"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100],gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
        angularaxis=dict(tickfont=dict(color="#BDC3C7")),bgcolor="#1A1A2E"),
        showlegend=False,height=280,paper_bgcolor="#1A1A2E",
        margin=dict(l=30,r=30,t=30,b=10),
        title=dict(text=name,font=dict(size=12,color="#ECF0F1"),x=0.5))
    return fig

def draw_geo_map(sc, scope="india"):
    fig=go.Figure()
    for e in sc.edges:
        s=sc.nodes[e.source]; t=sc.nodes[e.target]
        if s.x and s.y and t.x and t.y:
            fig.add_trace(go.Scattergeo(lon=[s.x,t.x,None],lat=[s.y,t.y,None],
                mode="lines",line=dict(width=1.5,color="#5D6D7E"),showlegend=False,hoverinfo="skip"))
    for ntype,nlist,col,sym,sz in [
        ("plant",[n for n in sc.nodes.values() if n.node_type=="plant"],"#1A6B4A","square",14),
        ("warehouse",[n for n in sc.nodes.values() if n.node_type=="warehouse"],"#1A3F6B","diamond",12),
        ("demand",[n for n in sc.nodes.values() if n.node_type=="demand"],"#6B1A1A","circle",10)]:
        if nlist:
            fig.add_trace(go.Scattergeo(lon=[n.x for n in nlist],lat=[n.y for n in nlist],
                mode="markers+text",name=ntype.capitalize()+"s",
                text=[n.name for n in nlist],textposition="top center",textfont=dict(size=9,color="#ECF0F1"),
                hovertext=[f"<b>{n.name}</b><br>{ntype}<br>Cap:{n.capacity}" for n in nlist],hoverinfo="text",
                marker=dict(size=sz,color=col,symbol=sym,line=dict(width=1.5,color="white"))))
    sc2="asia" if scope=="india" else "world"
    geo=dict(scope=sc2,showland=True,landcolor="#1A2744",showocean=True,oceancolor="#0D1B2A",
             showcountries=True,countrycolor="#2C3E50",showcoastlines=True,coastlinecolor="#34495E",
             bgcolor="#0D1B2A")
    if scope=="india": geo.update(center=dict(lon=80,lat=22),projection_scale=4.5)
    fig.update_layout(geo=geo,height=500,paper_bgcolor="#0D1B2A",
        margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,
            font=dict(size=11,color="#ECF0F1"),bgcolor="rgba(0,0,0,0)"))
    return fig


# ═══════════════════════════════════════════════════════════════
# VOICE COMPONENT (Web Speech API via HTML)
# ═══════════════════════════════════════════════════════════════
def voice_component():
    html = """
    <div id="vc" style="background:#16213E;border:1px solid #2C3E50;border-radius:10px;padding:16px;font-family:Inter,sans-serif">
      <div style="display:flex;gap:10px;align-items:center;margin-bottom:10px">
        <button id="mic-btn" onclick="toggleMic()" style="background:#1A3F6B;color:#ECF0F1;border:none;
          border-radius:6px;padding:8px 16px;font-size:13px;cursor:pointer;transition:all 0.2s">
          🎤 Start Listening
        </button>
        <button id="tts-btn" onclick="toggleTTS()" style="background:#1A6B4A;color:#ECF0F1;border:none;
          border-radius:6px;padding:8px 14px;font-size:13px;cursor:pointer">
          🔊 Voice On
        </button>
        <span id="status" style="font-size:11px;color:#7F8C8D;margin-left:8px"></span>
      </div>
      <div id="transcript" style="min-height:44px;background:#0D1B2A;border:1px solid #2C3E50;
        border-radius:6px;padding:10px;font-size:13px;color:#BDC3C7;margin-bottom:10px">
        Your speech will appear here...
      </div>
      <div style="display:flex;gap:8px">
        <button id="copy-btn" onclick="copyText()" style="display:none;background:#2C3E50;color:#ECF0F1;
          border:none;border-radius:6px;padding:6px 14px;font-size:12px;cursor:pointer">
          📋 Copy to Chat
        </button>
        <button id="clear-btn" onclick="clearText()" style="display:none;background:#4A1515;color:#ECF0F1;
          border:none;border-radius:6px;padding:6px 14px;font-size:12px;cursor:pointer">
          Clear
        </button>
      </div>
      <div style="margin-top:10px;font-size:11px;color:#5D6D7E">
        ℹ️ Click "Start Listening", speak your query, then "Copy to Chat" and paste it in the chat input below.
        Voice output reads AI responses aloud when enabled.
      </div>
    </div>

    <script>
    let isListening = false;
    let ttsEnabled = true;
    let recognition = null;
    let finalText = '';

    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = function(e) {
        let interim = '';
        finalText = '';
        for (let i = 0; i < e.results.length; i++) {
          if (e.results[i].isFinal) finalText += e.results[i][0].transcript;
          else interim += e.results[i][0].transcript;
        }
        document.getElementById('transcript').style.color = '#ECF0F1';
        document.getElementById('transcript').textContent = finalText + (interim ? ' [' + interim + ']' : '');
        if (finalText) {
          document.getElementById('copy-btn').style.display = 'inline-block';
          document.getElementById('clear-btn').style.display = 'inline-block';
        }
      };

      recognition.onerror = function(e) {
        document.getElementById('status').textContent = 'Error: ' + e.error;
        document.getElementById('status').style.color = '#C0392B';
        isListening = false;
        document.getElementById('mic-btn').textContent = '🎤 Start Listening';
        document.getElementById('mic-btn').style.background = '#1A3F6B';
      };

      recognition.onend = function() {
        if (isListening) recognition.start();
      };
    } else {
      document.getElementById('mic-btn').disabled = true;
      document.getElementById('mic-btn').textContent = '🎤 Not Supported';
      document.getElementById('status').textContent = 'Browser does not support speech recognition';
    }

    function toggleMic() {
      if (!recognition) return;
      if (isListening) {
        recognition.stop(); isListening = false;
        document.getElementById('mic-btn').textContent = '🎤 Start Listening';
        document.getElementById('mic-btn').style.background = '#1A3F6B';
        document.getElementById('status').textContent = 'Stopped';
      } else {
        finalText = '';
        document.getElementById('transcript').textContent = 'Listening...';
        document.getElementById('transcript').style.color = '#F39C12';
        recognition.start(); isListening = true;
        document.getElementById('mic-btn').textContent = '⏹ Stop';
        document.getElementById('mic-btn').style.background = '#6B1A1A';
        document.getElementById('status').textContent = '● Recording';
        document.getElementById('status').style.color = '#C0392B';
      }
    }

    function toggleTTS() {
      ttsEnabled = !ttsEnabled;
      document.getElementById('tts-btn').textContent = ttsEnabled ? '🔊 Voice On' : '🔇 Voice Off';
      document.getElementById('tts-btn').style.background = ttsEnabled ? '#1A6B4A' : '#4A4A4A';
    }

    function copyText() {
      if (!finalText) return;
      navigator.clipboard.writeText(finalText).then(() => {
        document.getElementById('status').textContent = '✓ Copied! Paste in chat below.';
        document.getElementById('status').style.color = '#1A8A4A';
        setTimeout(() => { document.getElementById('status').textContent = ''; }, 3000);
      });
    }

    function clearText() {
      finalText = '';
      document.getElementById('transcript').textContent = 'Your speech will appear here...';
      document.getElementById('transcript').style.color = '#BDC3C7';
      document.getElementById('copy-btn').style.display = 'none';
      document.getElementById('clear-btn').style.display = 'none';
    }

    window.speakText = function(text) {
      if (!ttsEnabled || !('speechSynthesis' in window)) return;
      speechSynthesis.cancel();
      const clean = text.replace(/<[^>]*>/g, '').replace(/\n/g, ' ').substring(0, 500);
      const u = new SpeechSynthesisUtterance(clean);
      u.rate = 1.0; u.pitch = 1.0; u.lang = 'en-US';
      const voices = speechSynthesis.getVoices();
      const en = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google'));
      if (en) u.voice = en;
      speechSynthesis.speak(u);
    };
    </script>
    """
    components.html(html, height=230)


# ═══════════════════════════════════════════════════════════════
# PREMIUM CSS
# ═══════════════════════════════════════════════════════════════
PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html,body,[class*="css"]{font-family:'Inter',sans-serif;}

/* Dark theme override */
.main .block-container{background:#0D1B2A;color:#ECF0F1;padding-top:1rem;}
section[data-testid="stSidebar"]{background:#111827 !important;}
section[data-testid="stSidebar"] *{color:#ECF0F1;}

/* Header */
.hdr{background:linear-gradient(135deg,#0D1B2A 0%,#1A2744 60%,#1A3F6B 100%);
  padding:18px 24px;border-radius:12px;display:flex;align-items:center;gap:18px;
  margin-bottom:20px;border:1px solid #1E3A5F;
  box-shadow:0 4px 24px rgba(0,0,0,0.4);}
.hdr h1{color:#ECF0F1;font-size:20px;font-weight:600;margin:0;letter-spacing:0.3px;}
.hdr p{color:#7F8C8D;font-size:11px;margin:2px 0 0;text-transform:uppercase;letter-spacing:0.8px;}

/* KPI Cards */
.kpi{background:#16213E;border:1px solid #1E3A5F;border-radius:10px;
  padding:14px 18px;border-left:4px solid #2E86C1;transition:all 0.2s;}
.kpi:hover{border-left-color:#F39C12;transform:translateY(-1px);}
.kpi-lbl{font-size:10px;color:#7F8C8D;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px;}
.kpi-val{font-size:26px;font-weight:700;color:#ECF0F1;line-height:1;}
.kpi-sub{font-size:10px;color:#5D6D7E;margin-top:3px;}

/* Section headers */
.sh{font-size:11px;font-weight:600;color:#7F8C8D;text-transform:uppercase;
  letter-spacing:1.2px;border-bottom:1px solid #1E3A5F;padding-bottom:7px;margin-bottom:14px;}

/* Alerts */
.al-r{background:#1C0A0A;border-left:4px solid #C0392B;padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0;font-size:13px;color:#ECF0F1;}
.al-a{background:#1C1200;border-left:4px solid #E67E22;padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0;font-size:13px;color:#ECF0F1;}
.al-g{background:#0A1C0A;border-left:4px solid #1A8A4A;padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0;font-size:13px;color:#ECF0F1;}
.al-b{background:#0A0F1C;border-left:4px solid #2E86C1;padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0;font-size:13px;color:#ECF0F1;}

/* Cards */
.card{background:#16213E;border:1px solid #1E3A5F;border-radius:8px;padding:12px 16px;margin:5px 0;font-size:13px;color:#ECF0F1;}

/* Badges */
.b-r{background:#4A0A0A;color:#E74C3C;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.b-a{background:#4A2A00;color:#F39C12;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.b-g{background:#0A2A0A;color:#2ECC71;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}
.b-b{background:#0A1A4A;color:#3498DB;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;}

/* Buttons */
.stButton>button{background:#1A3F6B!important;color:#ECF0F1!important;border:1px solid #2E86C1!important;
  border-radius:6px!important;font-weight:500!important;font-size:13px!important;
  transition:all 0.2s!important;}
.stButton>button:hover{background:#2E86C1!important;border-color:#3498DB!important;}

/* Inputs */
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stTextArea>div>textarea{
  background:#16213E!important;color:#ECF0F1!important;border:1px solid #1E3A5F!important;border-radius:6px!important;}
.stSelectbox>div>div{background:#16213E!important;color:#ECF0F1!important;border:1px solid #1E3A5F!important;border-radius:6px!important;}

/* Tabs */
.stTabs [data-baseweb="tab"]{font-size:13px;font-weight:500;color:#7F8C8D;}
.stTabs [aria-selected="true"]{color:#3498DB!important;}
.stTabs [data-baseweb="tab-list"]{background:#111827;border-bottom:1px solid #1E3A5F;}

/* Expander */
div[data-testid="stExpander"]{background:#16213E;border:1px solid #1E3A5F;border-radius:8px;}

/* Dataframe */
.dataframe{background:#16213E!important;}

/* Metrics */
[data-testid="metric-container"]{background:#16213E;border:1px solid #1E3A5F;border-radius:8px;padding:12px;}
[data-testid="metric-container"] label,[data-testid="metric-container"] div{color:#ECF0F1!important;}

/* Chat bubbles */
.user-bubble{background:#1A3F6B;color:#ECF0F1;padding:10px 14px;border-radius:14px 14px 2px 14px;
  max-width:75%;font-size:13px;line-height:1.5;margin:6px 0;}
.ai-bubble{background:#16213E;border:1px solid #1E3A5F;color:#ECF0F1;padding:10px 14px;
  border-radius:14px 14px 14px 2px;max-width:80%;font-size:13px;line-height:1.6;margin:6px 0;}
.chat-wrap{display:flex;margin:6px 0;}
.chat-right{justify-content:flex-end;}
.chat-left{justify-content:flex-start;}

/* Scrollbar */
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:#0D1B2A;}
::-webkit-scrollbar-thumb{background:#2C3E50;border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:#34495E;}

/* Sidebar */
.sb-sec{font-size:10px;font-weight:600;color:#5D6D7E;text-transform:uppercase;letter-spacing:1px;margin:12px 0 6px;}
.stSlider [data-baseweb="slider"] div{background:#2E86C1!important;}
</style>
"""


# ═══════════════════════════════════════════════════════════════
# STREAMLIT APP
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="SC Platform | BIT Mesra",page_icon="⬡",
    layout="wide",initial_sidebar_state="expanded")
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────
for k,v in [("sc",None),("inv",None),("scores",None),("dispatch_log",[]),
            ("disruption_result",None),("highlight_path",[]),("disrupted_edge",None),
            ("ranking",None),("forecaster",None),("forecast_trained",set()),
            ("chat_history",[]),("api_key",""),("last_ai_text","")]:
    if k not in st.session_state:
        st.session_state[k] = v

# Load defaults if needed
if st.session_state.sc is None: st.session_state.sc = load_demo_data()
if st.session_state.inv is None: st.session_state.inv = load_demo_inventory()
if st.session_state.scores is None: st.session_state.scores = load_demo_scores()
if st.session_state.forecaster is None: st.session_state.forecaster = DemandForecaster()

sc  = st.session_state.sc
inv = st.session_state.inv

# ── Header ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="hdr">
  <img src="data:image/png;base64,{LOGO_B64}" width="54" height="54"
    style="border-radius:50%;border:2px solid rgba(46,134,193,0.4)">
  <div>
    <h1>Supply Chain Resilience Platform</h1>
    <p>Birla Institute of Technology, Mesra &nbsp;·&nbsp; Operations &amp; Supply Chain Analytics &nbsp;·&nbsp; v4.0</p>
  </div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 0 14px;border-bottom:1px solid #1E3A5F">
      <img src="data:image/png;base64,{LOGO_B64}" width="36" height="36" style="border-radius:50%">
      <div><div style="font-size:13px;font-weight:600">Network Builder</div>
        <div style="font-size:10px;color:#7F8C8D">Configure supply chain</div></div>
    </div>""", unsafe_allow_html=True)

    st_tab_a, st_tab_b, st_tab_c = st.tabs(["Nodes","Connect","Data"])

    with st_tab_a:
        st.markdown('<div class="sb-sec">Add Node</div>', unsafe_allow_html=True)
        nn=st.text_input("Name",placeholder="e.g. Plant Delhi",key="nn",label_visibility="collapsed")
        c1,c2=st.columns(2)
        nt=c1.selectbox("Type",["plant","warehouse","demand"],key="nt")
        nc=c2.number_input("Capacity",min_value=1,value=200,key="nc")
        nl=st.text_input("Location",placeholder="City, Country",key="nl",label_visibility="collapsed")
        if st.button("Add Node",use_container_width=True,key="add_node_btn"):
            if nn.strip():
                nid=nt[0].upper()+str(len([n for n in sc.nodes.values() if n.node_type==nt])+1)
                sc.add_node(Node(nid,nn.strip(),nt,nc,nl)); st.success(f"Added: {nn}"); st.rerun()
            else: st.error("Enter a name")
        st.markdown('<div class="sb-sec">Nodes</div>', unsafe_allow_html=True)
        for ntype,label in [("plant","Plants"),("warehouse","Warehouses"),("demand","Demand")]:
            nlist=[n for n in sc.nodes.values() if n.node_type==ntype]
            if nlist:
                with st.expander(f"{label} ({len(nlist)})"):
                    for n in nlist:
                        c1,c2=st.columns([4,1])
                        c1.markdown(f"<span style='font-size:12px'><b>{n.name}</b> <span style='color:#7F8C8D'>{int(n.capacity)}</span></span>",unsafe_allow_html=True)
                        if c2.button("✕",key=f"dn_{n.id}"):
                            del sc.nodes[n.id]; sc.edges=[e for e in sc.edges if e.source!=n.id and e.target!=n.id]; st.rerun()

    with st_tab_b:
        st.markdown('<div class="sb-sec">Add Connection</div>', unsafe_allow_html=True)
        no={n.name:n.id for n in sc.nodes.values()}
        if len(sc.nodes)>=2:
            sl=st.selectbox("From",list(no.keys()),key="es")
            tl=st.selectbox("To",  list(no.keys()),key="et")
            c1,c2=st.columns(2)
            ecap=c1.number_input("Capacity",min_value=1,value=100,key="ec")
            ecos=c2.number_input("Cost",min_value=0.1,value=1.0,step=0.1,key="ecs")
            if st.button("Add Connection",use_container_width=True,key="add_edge_btn"):
                s,t=no[sl],no[tl]
                if s==t: st.error("Source and target must differ")
                else:
                    try: sc.add_edge(Edge(s,t,ecap,ecos)); st.success("Added"); st.rerun()
                    except ValueError as ex: st.error(str(ex))
        else: st.info("Add 2+ nodes first")
        if sc.edges:
            st.markdown('<div class="sb-sec">Connections</div>', unsafe_allow_html=True)
            for e in sc.edges:
                c1,c2=st.columns([5,1])
                c1.markdown(f"<span style='font-size:11px;color:#BDC3C7'>{sc.nodes[e.source].name}→{sc.nodes[e.target].name} <span style='color:#5D6D7E'>({int(e.capacity)})</span></span>",unsafe_allow_html=True)
                if c2.button("✕",key=f"de_{e.source}_{e.target}"): sc.remove_edge(e.source,e.target); st.rerun()

    with st_tab_c:
        st.markdown('<div class="sb-sec">Quick Start</div>', unsafe_allow_html=True)
        if st.button("Load Demo Supply Chain",use_container_width=True):
            for k in ["sc","inv","scores","disruption_result","highlight_path","disrupted_edge","ranking","forecaster","forecast_trained","dispatch_log"]:
                st.session_state[k]= (load_demo_data() if k=="sc" else load_demo_inventory() if k=="inv" else
                    load_demo_scores() if k=="scores" else DemandForecaster() if k=="forecaster" else set() if k=="forecast_trained" else [] if k=="dispatch_log" else None)
            st.rerun()

        st.markdown('<div class="sb-sec">Download Templates</div>', unsafe_allow_html=True)
        try:
            eb=create_excel_template()
            st.download_button("Excel Template",eb,"sc_template.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        except: pass
        c1,c2=st.columns(2)
        c1.download_button("Nodes CSV","id,name,node_type,capacity,location\nP1,Plant 1,plant,500,City\n","nodes.csv","text/csv",use_container_width=True)
        c2.download_button("Edges CSV","source,target,capacity,cost\nP1,W1,300,2.0\n","edges.csv","text/csv",use_container_width=True)

        st.markdown('<div class="sb-sec">Import</div>', unsafe_allow_html=True)
        uf=st.file_uploader("Upload Excel or CSV",type=["xlsx","csv","xls"],key="uf")
        if uf:
            fn=uf.name.lower()
            try:
                if fn.endswith(".xlsx") or fn.endswith(".xls"):
                    xls=pd.ExcelFile(uf); nsc=SupplyChainGraph()
                    if "Nodes" in xls.sheet_names:
                        for _,r in pd.read_excel(xls,"Nodes").iterrows():
                            nsc.add_node(Node(str(r["id"]),str(r["name"]),str(r["node_type"]),float(r["capacity"]),str(r.get("location","")),float(r.get("x_longitude",0)),float(r.get("y_latitude",0))))
                    if "Connections" in xls.sheet_names:
                        for _,r in pd.read_excel(xls,"Connections").iterrows():
                            nsc.add_edge(Edge(str(r["source"]),str(r["target"]),float(r["capacity"]),float(r.get("cost",1.0))))
                    ni=InventoryManager()
                    if "Inventory" in xls.sheet_names:
                        for _,r in pd.read_excel(xls,"Inventory").iterrows():
                            iid=str(r["item_id"])
                            if iid not in ni.items: ni.add_item(iid,str(r.get("item_name",iid)),str(r.get("unit","units")))
                            ni.set_stock(str(r["node_id"]),iid,float(r["current_stock"]),float(r["safety_stock"]),float(r["reorder_point"]),float(r.get("daily_demand",1)))
                    # Historical demand
                    fc=DemandForecaster()
                    if "Historical_Demand" in xls.sheet_names:
                        hdf=pd.read_excel(xls,"Historical_Demand"); hdf["date"]=pd.to_datetime(hdf["date"])
                        for nid in hdf["node_id"].unique():
                            sub=hdf[hdf["node_id"]==nid].sort_values("date").reset_index(drop=True)
                            nn_name=nsc.nodes[nid].name if nid in nsc.nodes else nid
                            sub["node_name"]=nn_name; fc.history[nid]=sub
                    st.session_state.sc=nsc; st.session_state.inv=ni; st.session_state.forecaster=fc
                    st.success("Imported!"); st.rerun()
                else:
                    df=pd.read_csv(uf)
                    if "node_type" in df.columns:
                        nsc=SupplyChainGraph()
                        for _,r in df.iterrows(): nsc.add_node(Node(str(r["id"]),str(r["name"]),str(r["node_type"]),float(r["capacity"]),str(r.get("location",""))))
                        st.session_state.sc=nsc; st.success("Nodes imported"); st.rerun()
                    elif "source" in df.columns:
                        for _,r in df.iterrows(): sc.add_edge(Edge(str(r["source"]),str(r["target"]),float(r["capacity"]),float(r.get("cost",1.0))))
                        st.success("Edges imported"); st.rerun()
            except Exception as ex: st.error(f"Import failed: {ex}")

        st.markdown('<div class="sb-sec">Export</div>', unsafe_allow_html=True)
        ndf=pd.DataFrame([vars(n) for n in sc.nodes.values()])
        edf=pd.DataFrame([vars(e) for e in sc.edges])
        c1,c2=st.columns(2)
        if not ndf.empty: c1.download_button("Nodes",ndf.to_csv(index=False),"nodes.csv",use_container_width=True)
        if not edf.empty: c2.download_button("Edges",edf.to_csv(index=False),"edges.csv",use_container_width=True)

        # AI API Key
        st.markdown('<div class="sb-sec">AI Assistant Setup</div>', unsafe_allow_html=True)
        key_input = st.text_input("Anthropic API Key",value=st.session_state.api_key,
            type="password",placeholder="sk-ant-...",key="api_key_input",
            help="Get your key at console.anthropic.com")
        if key_input != st.session_state.api_key:
            st.session_state.api_key = key_input
        if st.session_state.api_key:
            st.success("API key configured")
        else:
            st.info("Add API key to enable AI Assistant")


# ═══════════════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════════════
T = st.tabs(["Network Map","Inventory","Disruption Sim","Risk Heatmap",
             "Demand Forecast","Dispatch Log","ATP & Scorecard","Geographic View","AI Assistant"])
t1,t2,t3,t4,t5,t6,t7,t8,t9 = T

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

        # KPI row
        cols=st.columns(5)
        kpi_data=[(len(plants),f"Cap:{sum(n.capacity for n in plants):,.0f}","#1A6B4A","Plants"),
                  (len(whs),  f"Cap:{sum(n.capacity for n in whs):,.0f}","#1A3F6B","Warehouses"),
                  (len(dems), f"Dem:{sum(n.capacity for n in dems):,.0f}","#6B1A1A","Demand Pts"),
                  (len(sc.edges),f"Dispatches:{len(active_dis)}","#1A4A6B","Connections")]
        cov=round(sum(n.capacity for n in plants)/max(sum(n.capacity for n in dems),1)*100,1)
        cc="#1A8A4A" if cov>=100 else "#E67E22" if cov>=70 else "#C0392B"
        kpi_data.append((f"{min(cov,999):.0f}%","vs total demand",cc,"Supply Cover"))
        for i,(val,sub,col,lbl) in enumerate(kpi_data):
            with cols[i]:
                st.markdown(f'<div class="kpi" style="border-left-color:{col}"><div class="kpi-lbl">{lbl}</div><div class="kpi-val">{val}</div><div class="kpi-sub">{sub}</div></div>',unsafe_allow_html=True)

        # Stock alerts
        alerts=inv.get_alerts(sc.nodes)
        crit_alerts=[a for a in alerts if a["level"]=="critical"]
        if crit_alerts:
            items=" | ".join(f"{a['node_name']}/{a['item_name']}" for a in crit_alerts[:3])
            st.markdown(f'<div class="al-r" style="margin-top:12px">⚠ Critical stock: {items}</div>',unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        _,co=st.columns([5,1]); show_cap=co.checkbox("Edge labels",value=True,key="ec_cb")
        fig=draw_network(sc,st.session_state.highlight_path,st.session_state.disrupted_edge,show_cap,active_dis)
        st.plotly_chart(fig,use_container_width=True)
        st.markdown('<div style="display:flex;gap:20px;font-size:11px;color:#5D6D7E">'+
            '<span>■ Plant</span><span>◆ Warehouse</span><span>● Demand</span>'+
            '<span style="color:#F39C12">■ Highlighted</span><span style="color:#2E86C1">■ In Transit</span>'+
            '<span style="color:#C0392B">■ Disrupted</span></div>',unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="sh">Shortest Path Finder</div>',unsafe_allow_html=True)
        nlab={n.name:n.id for n in sc.nodes.values()}
        c1,c2,c3=st.columns([2,2,1])
        sp1=c1.selectbox("From",list(nlab.keys()),key="sp1")
        sp2=c2.selectbox("To",list(nlab.keys()),key="sp2",index=min(2,len(nlab)-1))
        c3.markdown("<br>",unsafe_allow_html=True)
        if c3.button("Find",use_container_width=True,key="find_path_btn"):
            res=sc.all_shortest_paths(nlab[sp1],nlab[sp2],k=3)
            if res: st.session_state.highlight_path=res[0]["path"]; st.rerun()
            else: st.warning("No path found."); st.session_state.highlight_path=[]
        if st.session_state.highlight_path:
            pnames=[sc.nodes[n].name for n in st.session_state.highlight_path]
            st.markdown(f'<div class="al-g">Path: <b>{" → ".join(pnames)}</b></div>',unsafe_allow_html=True)
            if st.button("Clear",key="clear_path"): st.session_state.highlight_path=[]; st.rerun()

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="sh">Demand Fulfillment</div>',unsafe_allow_html=True)
        if sc.edges:
            with st.spinner("Computing..."): ff=sc.demand_fulfillment()
            st.plotly_chart(draw_gauge_charts(ff,sc.nodes),use_container_width=True)
            with st.expander("Detailed Fulfillment Table"):
                rows=[{"Demand Point":sc.nodes[d].name,"Required":info["required"],"Fulfilled":info["fulfilled"],
                       "Fulfillment %":info["pct"],"Sources":", ".join(sc.nodes[p].name for p in info["reachable_from"]) or "None"}
                      for d,info in ff.items()]
                df_ff=pd.DataFrame(rows)
                def cpct(v):
                    return "background-color:#0A2A0A" if v>=90 else "background-color:#2A1A00" if v>=50 else "background-color:#2A0A0A"
                st.dataframe(df_ff.style.map(cpct,subset=["Fulfillment %"]),use_container_width=True,hide_index=True)


# ─────────────────────────────────────────────────────────────
# TAB 2 — INVENTORY
# ─────────────────────────────────────────────────────────────
with t2:
    st.markdown('<div class="sh">Inventory Overview</div>',unsafe_allow_html=True)
    alerts=inv.get_alerts(sc.nodes)
    if alerts:
        for a in [x for x in alerts if x["level"]=="critical"]:
            st.markdown(f'<div class="al-r"><span class="b-r">CRITICAL</span> <b>{a["node_name"]}</b> — {a["item_name"]}: {a["current"]:.0f} / Safety: {a["safety"]:.0f} · {a["coverage"]} days left</div>',unsafe_allow_html=True)
        for a in [x for x in alerts if x["level"]=="warning"]:
            st.markdown(f'<div class="al-a"><span class="b-a">LOW</span> <b>{a["node_name"]}</b> — {a["item_name"]}: {a["current"]:.0f} · {a["coverage"]} days</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="al-g">All stock levels within normal range.</div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sh">Stock Levels</div>',unsafe_allow_html=True)
    inv_df=inv.to_df(sc.nodes)
    if not inv_df.empty:
        def cs(v): return f"color:{STC.get(v,'#ECF0F1')};font-weight:600"
        def cc2(v): return "background-color:#0A2A0A" if v<=3 else "background-color:#2A1A00" if v<=7 else "background-color:#0A1A0A"
        # Use applymap replacement (map)
        st.dataframe(inv_df.style.map(cs,subset=["Status"]).map(cc2,subset=["Coverage Days"]),use_container_width=True,hide_index=True)

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sh">Stock Chart</div>',unsafe_allow_html=True)
    nws=[nid for nid in sc.nodes if nid in inv.stock and inv.stock[nid]]
    if nws:
        sel_n=st.selectbox("Node",[sc.nodes[n].name for n in nws],key="inv_ns")
        sel_id=[n for n in nws if sc.nodes[n].name==sel_n]
        if sel_id:
            nid=sel_id[0]; items_data=inv.stock[nid]
            inames=[inv.items.get(iid,{}).get("name",iid) for iid in items_data]
            curs=[s["current"] for s in items_data.values()]
            safs=[s["safety"] for s in items_data.values()]
            reos=[s["reorder"] for s in items_data.values()]
            cols_bar=["#C0392B" if c<=s else "#E67E22" if c<=r else "#1A8A4A" for c,s,r in zip(curs,safs,reos)]
            fig_bar=go.Figure()
            fig_bar.add_trace(go.Bar(x=inames,y=curs,marker_color=cols_bar,name="Current",text=[f"{c:.0f}" for c in curs],textposition="outside",textfont=dict(color="#ECF0F1")))
            fig_bar.add_trace(go.Scatter(x=inames,y=safs,mode="markers+lines",marker=dict(symbol="line-ew",size=18,color="#C0392B",line=dict(width=2,color="#C0392B")),line=dict(dash="dot",color="#C0392B"),name="Safety"))
            fig_bar.add_trace(go.Scatter(x=inames,y=reos,mode="markers+lines",marker=dict(symbol="line-ew",size=18,color="#E67E22",line=dict(width=2,color="#E67E22")),line=dict(dash="dash",color="#E67E22"),name="Reorder"))
            fig_bar.update_layout(height=280,paper_bgcolor="#1A1A2E",plot_bgcolor="#16213E",
                yaxis=dict(gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
                xaxis=dict(tickfont=dict(color="#BDC3C7")),
                legend=dict(font=dict(color="#BDC3C7"),bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_bar,use_container_width=True)

    # Live update form
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sh">Live Stock Update</div>',unsafe_allow_html=True)
    with st.form("stock_upd"):
        c1,c2,c3,c4=st.columns([2,2,1,2])
        un=[sc.nodes[n].name for n in sc.nodes if n in inv.stock]
        upd_n=c1.selectbox("Node",un,key="upd_n") if un else c1.text_input("Node")
        uid=[n for n in sc.nodes if sc.nodes[n].name==upd_n and n in inv.stock]
        iopts={inv.items.get(iid,{}).get("name",iid):iid for iid in (inv.stock.get(uid[0],{}) if uid else {})}
        upd_i=c2.selectbox("Item",list(iopts.keys()),key="upd_i") if iopts else c2.text_input("Item ID")
        upd_q=c3.number_input("Qty(±)",value=0.0,step=1.0,key="upd_q")
        upd_note=c4.text_input("Note",placeholder="Optional",key="upd_nt")
        if st.form_submit_button("Update Stock",use_container_width=True) and uid:
            iid=iopts.get(upd_i,upd_i)
            if inv.update_stock(uid[0],iid,upd_q):
                st.session_state.dispatch_log.append({"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "from_node":upd_n,"to_node":"Manual","from_id":uid[0],"to_id":"",
                    "item":inv.items.get(iid,{}).get("name",iid),"item_id":iid,
                    "quantity":upd_q,"status":"Delivered","notes":upd_note})
                st.success(f"Updated: {upd_q:+.0f} units"); st.rerun()
            else: st.error("Node/item not found")

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sh">Add Item to Node</div>',unsafe_allow_html=True)
    with st.form("add_stock"):
        c1,c2,c3=st.columns(3)
        new_node=c1.selectbox("Node",[n.name for n in sc.nodes.values()],key="ns_n")
        new_iid =c2.text_input("Item ID",placeholder="SKU005",key="ns_iid")
        new_inm =c3.text_input("Item Name",placeholder="Salt",key="ns_inm")
        c1b,c2b,c3b,c4b,c5b=st.columns(5)
        ns_unit=c1b.text_input("Unit",value="Tonnes",key="ns_u")
        ns_cur =c2b.number_input("Current",min_value=0.0,value=100.0,key="ns_c")
        ns_saf =c3b.number_input("Safety",min_value=0.0,value=20.0,key="ns_s")
        ns_reo =c4b.number_input("Reorder",min_value=0.0,value=40.0,key="ns_r")
        ns_dd  =c5b.number_input("Daily Demand",min_value=0.1,value=5.0,key="ns_d")
        if st.form_submit_button("Add to Inventory",use_container_width=True):
            if new_iid.strip() and new_inm.strip():
                nid=[n.id for n in sc.nodes.values() if n.name==new_node]
                if nid:
                    inv.add_item(new_iid.strip(),new_inm.strip(),ns_unit)
                    inv.set_stock(nid[0],new_iid.strip(),ns_cur,ns_saf,ns_reo,ns_dd)
                    st.success(f"Added {new_inm} to {new_node}"); st.rerun()
            else: st.error("Enter item ID and name")


# ─────────────────────────────────────────────────────────────
# TAB 3 — DISRUPTION SIMULATOR
# ─────────────────────────────────────────────────────────────
with t3:
    st.markdown('<div class="sh">Disruption Scenario Analysis</div>',unsafe_allow_html=True)
    st.caption("Simulate a connection failure — see resilience score, alternate routes, and safety stock options.")
    if not sc.edges:
        st.info("Add connections to run disruption analysis.")
    else:
        eopts={f"{sc.nodes[e.source].name} → {sc.nodes[e.target].name} (cap:{int(e.capacity)})":(e.source,e.target) for e in sc.edges}
        c1,c2=st.columns([4,1])
        chosen=c1.selectbox("Connection to disrupt",list(eopts.keys()),label_visibility="collapsed",key="dis_sel")
        c2.markdown("<br>",unsafe_allow_html=True)
        if c2.button("Analyse",use_container_width=True,type="primary",key="dis_btn"):
            src,tgt=eopts[chosen]
            with st.spinner("Analysing..."): result=sc.simulate_disruption(src,tgt)
            st.session_state.disruption_result=result; st.session_state.disrupted_edge=(src,tgt); st.rerun()

        if st.session_state.disruption_result:
            result=st.session_state.disruption_result; st.markdown("<br>",unsafe_allow_html=True)
            cg,cs2=st.columns([1,2])
            with cg:
                st.markdown('<div class="sh">Resilience Score</div>',unsafe_allow_html=True)
                st.plotly_chart(draw_resilience_gauge(result["resilience_score"]),use_container_width=True)
            with cs2:
                st.markdown(f'<div class="sh">Impact — {result["removed_edge"]}</div>',unsafe_allow_html=True)
                sc2_val=result["resilience_score"]
                msg_cls="al-g" if sc2_val>=70 else "al-a" if sc2_val>=40 else "al-r"
                msg_txt="Low Risk — Chain retains continuity." if sc2_val>=70 else "Moderate Risk — Partial disruption." if sc2_val>=40 else "Critical Risk — Major disruption!"
                st.markdown(f'<div class="{msg_cls}"><b>{sc2_val}%</b> — {msg_txt}</div>',unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                for d_id,imp in result["impact"].items():
                    if imp["drop_pct"]>0:
                        sv=SC[imp["severity"]]
                        st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:7px 12px;
                          background:#16213E;border-radius:5px;margin:3px 0;border-left:3px solid {sv}">
                          <b style="font-size:13px;color:#ECF0F1">{imp['demand_name']}</b>
                          <span style="font-size:12px;color:#BDC3C7">{imp['before_pct']}%→{imp['after_pct']}% | <b>−{imp['drop_pct']}%</b> | −{imp['lost_units']} units</span>
                          <span style="color:{sv};font-size:11px;font-weight:600">{imp['severity'].upper()}</span></div>""",unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">Fulfillment Before vs After</div>',unsafe_allow_html=True)
            st.plotly_chart(draw_impact_chart(result["impact"]),use_container_width=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">Network Alternate Routes</div>',unsafe_allow_html=True)
            if result["alt_paths"]:
                for d_id,paths in result["alt_paths"].items():
                    if paths:
                        st.markdown(f"**{sc.nodes[d_id].name}** — {len(paths)} route(s) available")
                        for i,p in enumerate(paths,1):
                            st.markdown(f'<div class="card">Route {i} | Cost: {p["cost"]} | {" → ".join(p["path"])}</div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="al-r">No alternate routes — single point of failure!</div>',unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">Safety Stock Alternatives</div>',unsafe_allow_html=True)
            de=st.session_state.disrupted_edge
            for d_id,imp in result["impact"].items():
                if imp["drop_pct"]<=0: continue
                shortfall=imp["lost_units"]
                st.markdown(f"**{imp['demand_name']}** — shortfall: {shortfall:.0f} units")
                rows_s=[]
                for iid in list(inv.items.keys()):
                    alts=inv.find_alternatives(d_id,iid,shortfall,sc,de)
                    for alt in alts:
                        rows_s.append({"Source":alt["node_name"],"Item":inv.items[iid]["name"],
                            "Available":f"{alt['available']:.0f}","Covers":("Yes" if alt["can_cover"] else f"{alt['coverage_pct']}%"),
                            "Route":" → ".join(alt["path"]),"Cost":alt["route_cost"],"Days":alt.get("coverage_days","—")})
                if rows_s:
                    df_s=pd.DataFrame(rows_s)
                    def cov_style(v): return "background-color:#0A2A0A;font-weight:600" if v=="Yes" else "background-color:#2A1A00"
                    st.dataframe(df_s.style.map(cov_style,subset=["Covers"]),use_container_width=True,hide_index=True)
                else:
                    st.markdown('<div class="al-a">No above-safety stock available for any item.</div>',unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">Network View — Disruption Highlighted</div>',unsafe_allow_html=True)
            alt_hi=[]
            if result["alt_paths"]:
                first=[v for v in result["alt_paths"].values() if v]
                if first and first[0]: alt_hi=first[0][0].get("path_ids",[])
            st.plotly_chart(draw_network(sc,alt_hi,st.session_state.disrupted_edge,True,
                [d for d in st.session_state.dispatch_log if d.get("status")=="In Transit"]),use_container_width=True)
            if st.button("Reset",key="res_dis"):
                st.session_state.disruption_result=None; st.session_state.disrupted_edge=None
                st.session_state.highlight_path=[]; st.rerun()


# ─────────────────────────────────────────────────────────────
# TAB 4 — RISK HEATMAP (DARK)
# ─────────────────────────────────────────────────────────────
with t4:
    st.markdown('<div class="sh">Network Risk Heatmap</div>',unsafe_allow_html=True)
    st.caption("Dark color = high risk. Stress-test all connections to populate the matrix.")
    if not sc.edges: st.info("Add connections first.")
    else:
        if st.session_state.ranking is None:
            st.info("Click the button below to run the full stress test and populate the heatmap.")
        c1,c2=st.columns([3,1])
        if c2.button("Run Stress Test",use_container_width=True,key="hm_btn"):
            with st.spinner("Analysing all connections..."): st.session_state.ranking=sc.rank_critical_edges(); st.rerun()
        if st.session_state.ranking:
            ranking=st.session_state.ranking
            st.plotly_chart(draw_dark_heatmap(sc,ranking),use_container_width=True)
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">Node Risk Summary</div>',unsafe_allow_html=True)
            rows=[]
            for nid,node in sc.nodes.items():
                outs=[r for r in ranking if r["source"]==nid]; ins=[r for r in ranking if r["target"]==nid]
                md=max((r["avg_fulfillment_drop"] for r in outs+ins),default=0)
                nc=sum(1 for r in outs+ins if r["severity"]=="critical")
                rl="Critical" if md>=50 else "High" if md>=25 else "Medium" if md>=5 else "Low"
                rows.append({"Node":node.name,"Type":node.node_type.capitalize(),"Max Drop":f"{md:.0f}%","Critical Links":nc,"Risk":rl})
            df_r=pd.DataFrame(rows).sort_values("Max Drop",ascending=False)
            def rl_col(v):
                c={"Critical":"#2A0A0A","High":"#2A1A00","Medium":"#0A1A2A","Low":"#0A2A0A"}
                return f"background-color:{c.get(v,'#16213E')}"
            st.dataframe(df_r.style.map(rl_col,subset=["Risk"]),use_container_width=True,hide_index=True)
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="sh">Criticality Ranking</div>',unsafe_allow_html=True)
            st.plotly_chart(draw_criticality_chart(ranking),use_container_width=True)
            st.markdown('<div class="sh">Recommendations</div>',unsafe_allow_html=True)
            for sev,cls,label in [("critical","al-r","Immediate Action"),("high","al-a","High Priority"),("low","al-g","Well Redundant")]:
                items=[r for r in ranking if r["severity"]==sev]
                if items:
                    links="".join(f"<li>{r['label']}</li>" for r in items)
                    st.markdown(f'<div class="{cls}"><b>{label} ({len(items)}):</b><ul style="margin:4px 0 0 16px">{links}</ul></div>',unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 5 — DEMAND FORECASTING
# ─────────────────────────────────────────────────────────────
with t5:
    st.markdown('<div class="sh">AI-Powered Demand Forecasting</div>',unsafe_allow_html=True)
    st.caption("Random Forest + Gradient Boosting ensemble. Predicts future demand and propagates to warehouses and plants.")

    fc = st.session_state.forecaster
    demand_nodes=[n for n in sc.nodes.values() if n.node_type=="demand"]

    if not demand_nodes:
        st.info("Add demand nodes to enable forecasting.")
    else:
        # Controls
        c1,c2,c3=st.columns([2,1,1])
        sel_dem=c1.selectbox("Demand node to forecast",[n.name for n in demand_nodes],key="fc_node")
        horizon=c2.selectbox("Forecast horizon (days)",[14,30,60,90],index=1,key="fc_horizon")
        use_synthetic=c3.checkbox("Use generated history",value=True,key="fc_syn")

        sel_dem_node=next(n for n in demand_nodes if n.name==sel_dem)

        # Upload historical data
        if not use_synthetic:
            st.markdown('<div class="sh">Upload Historical Data</div>',unsafe_allow_html=True)
            st.caption("CSV with columns: date (YYYY-MM-DD), demand (numeric). One row per day.")
            hist_file=st.file_uploader("Upload CSV",type=["csv"],key="fc_upload")
            if hist_file:
                try:
                    hdf=pd.read_csv(hist_file)
                    hdf["date"]=pd.to_datetime(hdf["date"])
                    hdf["node_id"]=sel_dem_node.id; hdf["node_name"]=sel_dem_node.name
                    hdf=hdf.sort_values("date").reset_index(drop=True)
                    fc.history[sel_dem_node.id]=hdf
                    st.success(f"Loaded {len(hdf)} days of historical data")
                except Exception as ex: st.error(f"Upload failed: {ex}")

        # Train & forecast
        if st.button("Train Model & Forecast",use_container_width=True,key="train_btn"):
            nid=sel_dem_node.id
            if nid not in fc.history or use_synthetic:
                fc.generate_synthetic_history(nid,sel_dem_node.name,sel_dem_node.capacity)
            with st.spinner("Training RF + GBM ensemble..."):
                fdf=fc.train(nid,horizon=int(horizon))
            if fdf is not None:
                st.session_state.forecast_trained.add(nid)
                m=fc.metrics[nid]
                st.success(f"Model trained! RMSE:{m['rmse']:.1f} | MAE:{m['mae']:.1f} | MAPE:{m['mape']:.1f}% | R²:{m['r2']:.3f}")
            st.rerun()

        # Show forecast if trained
        nid=sel_dem_node.id
        if nid in st.session_state.forecast_trained and nid in fc.forecasts:
            m=fc.metrics.get(nid,{})
            mc1,mc2,mc3,mc4=st.columns(4)
            mc1.metric("RMSE",f"{m.get('rmse','—')}")
            mc2.metric("MAE", f"{m.get('mae','—')}")
            mc3.metric("MAPE",f"{m.get('mape','—')}%")
            mc4.metric("R²",  f"{m.get('r2','—')}")
            st.plotly_chart(draw_forecast_chart(fc,nid,sc.nodes),use_container_width=True)

            # Forecast table
            with st.expander("Forecast Values"):
                fdf=fc.forecasts[nid]
                df_show=fdf[["date","forecast","lower","upper"]].copy()
                df_show.columns=["Date","Forecast","Lower CI","Upper CI"]
                df_show["Date"]=df_show["Date"].dt.strftime("%Y-%m-%d")
                for col in ["Forecast","Lower CI","Upper CI"]: df_show[col]=df_show[col].round(1)
                st.dataframe(df_show,use_container_width=True,hide_index=True)

        # Aggregate to warehouses
        st.markdown("<br>",unsafe_allow_html=True)
        if st.session_state.forecast_trained:
            if st.button("Aggregate to Warehouses & Plants",use_container_width=True,key="agg_btn"):
                with st.spinner("Aggregating..."):
                    # Train all demand nodes first
                    for dn in demand_nodes:
                        if dn.id not in fc.history:
                            fc.generate_synthetic_history(dn.id,dn.name,dn.capacity)
                        if dn.id not in fc.forecasts:
                            fc.train(dn.id,horizon=int(horizon))
                            st.session_state.forecast_trained.add(dn.id)
                    wh_fc=fc.aggregate_to_warehouses(sc,horizon=int(horizon))
                    plant_req=fc.get_plant_requirements(sc,wh_fc,horizon=int(horizon))
                    st.session_state["wh_forecasts"]=wh_fc
                    st.session_state["plant_req"]=plant_req
                st.rerun()

            if "wh_forecasts" in st.session_state and st.session_state["wh_forecasts"]:
                st.markdown('<div class="sh">Warehouse Forecast Aggregation</div>',unsafe_allow_html=True)
                wh_fc=st.session_state["wh_forecasts"]
                fig_wh=go.Figure()
                colors=["#2E86C1","#1A8A4A","#C0392B","#E67E22"]
                for i,(wid,winfo) in enumerate(wh_fc.items()):
                    x=list(range(1,len(winfo["forecast"])+1))
                    fig_wh.add_trace(go.Scatter(x=x,y=winfo["forecast"],mode="lines",
                        name=winfo["name"],line=dict(color=colors[i%len(colors)],width=2)))
                fig_wh.update_layout(title=dict(text="Aggregated Warehouse Demand Forecast",font=dict(color="#ECF0F1",size=13),x=0.5),
                    xaxis=dict(title="Days",gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
                    yaxis=dict(title="Units",gridcolor="#2C3E50",tickfont=dict(color="#BDC3C7")),
                    paper_bgcolor="#1A1A2E",plot_bgcolor="#16213E",height=320,
                    legend=dict(font=dict(color="#BDC3C7"),bgcolor="rgba(0,0,0,0)"),
                    margin=dict(l=10,r=10,t=40,b=10))
                st.plotly_chart(fig_wh,use_container_width=True)

                # Plant requirements
                if "plant_req" in st.session_state and st.session_state["plant_req"]:
                    st.markdown('<div class="sh">Plant Manufacturing Requirements</div>',unsafe_allow_html=True)
                    st.plotly_chart(draw_plant_requirements_chart(st.session_state["plant_req"],horizon=int(horizon)),use_container_width=True)

                    # Requirements table
                    st.markdown('<div class="sh">Daily Requirements vs Capacity</div>',unsafe_allow_html=True)
                    pr=st.session_state["plant_req"]
                    rows_pr=[]
                    for pid,pinfo in pr.items():
                        avg_req=np.mean(pinfo["required"])
                        max_req=np.max(pinfo["required"])
                        util=round(avg_req/pinfo["capacity"]*100,1)
                        over="YES" if max_req>pinfo["capacity"] else "No"
                        rows_pr.append({"Plant":pinfo["name"],"Avg Daily Required":f"{avg_req:.0f}",
                            "Peak Required":f"{max_req:.0f}","Capacity":pinfo["capacity"],
                            "Avg Utilization":f"{util}%","Capacity Breach":over})
                    df_pr=pd.DataFrame(rows_pr)
                    def breach_col(v):
                        return "background-color:#2A0A0A;color:#E74C3C;font-weight:600" if v=="YES" else "background-color:#0A2A0A;color:#2ECC71"
                    st.dataframe(df_pr.style.map(breach_col,subset=["Capacity Breach"]),use_container_width=True,hide_index=True)

        # Bulk forecast all
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("Train All Demand Nodes",use_container_width=True,key="train_all_btn"):
            progress=st.progress(0)
            for i,dn in enumerate(demand_nodes):
                if dn.id not in fc.history:
                    fc.generate_synthetic_history(dn.id,dn.name,dn.capacity)
                fc.train(dn.id,horizon=int(horizon))
                st.session_state.forecast_trained.add(dn.id)
                progress.progress((i+1)/len(demand_nodes))
            st.success(f"Trained models for all {len(demand_nodes)} demand nodes."); st.rerun()


# ─────────────────────────────────────────────────────────────
# TAB 6 — DISPATCH LOG
# ─────────────────────────────────────────────────────────────
with t6:
    st.markdown('<div class="sh">Dispatch Log — Live Goods Movement</div>',unsafe_allow_html=True)
    with st.form("dis_form"):
        st.markdown("**Log New Dispatch**")
        c1,c2,c3=st.columns(3)
        all_names=[n.name for n in sc.nodes.values()]
        df_from=c1.selectbox("From",all_names,key="df"); df_to=c2.selectbox("To",all_names,key="dt",index=min(1,len(all_names)-1))
        all_items2={inv.items[iid]["name"]:iid for iid in inv.items} if inv.items else {}
        df_item=c3.selectbox("Item",list(all_items2.keys()) or ["—"],key="di")
        c1b,c2b,c3b=st.columns(3)
        df_qty=c1b.number_input("Quantity",min_value=0.1,value=50.0,key="dq")
        df_status=c2b.selectbox("Status",["In Transit","Delivered","Delayed"],key="ds")
        df_note=c3b.text_input("Notes",placeholder="Optional",key="dno")
        if st.form_submit_button("Log Dispatch",use_container_width=True):
            fid=[n.id for n in sc.nodes.values() if n.name==df_from]
            tid=[n.id for n in sc.nodes.values() if n.name==df_to]
            iid=all_items2.get(df_item,"")
            if fid and tid:
                if df_status in ("In Transit","Delivered") and iid: inv.update_stock(fid[0],iid,-df_qty)
                if df_status=="Delivered" and iid: inv.update_stock(tid[0],iid,df_qty)
                st.session_state.dispatch_log.append({"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "from_node":df_from,"to_node":df_to,"from_id":fid[0],"to_id":tid[0],
                    "item":df_item,"item_id":iid,"quantity":df_qty,"status":df_status,"notes":df_note})
                st.success(f"Logged: {df_qty:.0f} units of {df_item}"); st.rerun()

    if st.session_state.dispatch_log:
        st.markdown("<br>",unsafe_allow_html=True); st.markdown('<div class="sh">All Dispatches</div>',unsafe_allow_html=True)
        ldf=pd.DataFrame(st.session_state.dispatch_log[::-1])
        cs_show=[c for c in ["timestamp","from_node","to_node","item","quantity","status","notes"] if c in ldf.columns]
        ldf_show=ldf[cs_show].copy(); ldf_show.columns=["Time","From","To","Item","Qty","Status","Notes"][:len(cs_show)]
        def ss(v):
            c={"In Transit":"#0A1A2A","Delivered":"#0A2A0A","Delayed":"#2A0A0A"}; return f"background-color:{c.get(v,'#16213E')};font-weight:600"
        st.dataframe(ldf_show.style.map(ss,subset=["Status"]),use_container_width=True,hide_index=True)
        in_t=len([d for d in st.session_state.dispatch_log if d["status"]=="In Transit"])
        delv=len([d for d in st.session_state.dispatch_log if d["status"]=="Delivered"])
        deld=len([d for d in st.session_state.dispatch_log if d["status"]=="Delayed"])
        c1,c2,c3=st.columns(3)
        c1.markdown(f'<div class="kpi" style="border-left-color:#2E86C1"><div class="kpi-lbl">In Transit</div><div class="kpi-val">{in_t}</div></div>',unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi" style="border-left-color:#1A8A4A"><div class="kpi-lbl">Delivered</div><div class="kpi-val">{delv}</div></div>',unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi" style="border-left-color:#C0392B"><div class="kpi-lbl">Delayed</div><div class="kpi-val">{deld}</div></div>',unsafe_allow_html=True)
        if st.button("Clear Log",key="cl_log"): st.session_state.dispatch_log=[]; st.rerun()


# ─────────────────────────────────────────────────────────────
# TAB 7 — ATP & SCORECARD
# ─────────────────────────────────────────────────────────────
with t7:
    atp_tab, sc_tab = st.tabs(["Available-to-Promise","Supplier Scorecard"])
    with atp_tab:
        st.markdown('<div class="sh">Available-to-Promise</div>',unsafe_allow_html=True)
        atp_items2={inv.items[iid]["name"]:iid for iid in inv.items} if inv.items else {}
        c1,c2,c3=st.columns([2,1,1])
        atp_item2=c1.selectbox("Item",list(atp_items2.keys()) or ["No items"],key="atp_i")
        atp_qty2=c2.number_input("Qty needed",min_value=1.0,value=100.0,key="atp_q")
        atp_dest2=c3.selectbox("Destination",[n.name for n in sc.nodes.values() if n.node_type=="demand"],key="atp_d")
        if st.button("Check Availability",use_container_width=True,key="atp_chk"):
            iid=atp_items2.get(atp_item2,""); did=[n.id for n in sc.nodes.values() if n.name==atp_dest2]
            if iid and did:
                alts=inv.find_alternatives(did[0],iid,atp_qty2,sc)
                if alts:
                    for i,a in enumerate(alts,1):
                        cls="al-g" if a["can_cover"] else "al-a"; bdg="b-g" if a["can_cover"] else "b-a"
                        stxt="Can Fulfill" if a["can_cover"] else f"Partial {a['coverage_pct']}%"
                        st.markdown(f'<div class="{cls}"><b>Option {i}: {a["node_name"]}</b> <span class="{bdg}">{stxt}</span><br>Available: <b>{a["available"]:.0f}</b> | Days: {a["coverage_days"]} | Route: {" → ".join(a["path"])} | Cost: {a["route_cost"]}</div>',unsafe_allow_html=True)
                else:
                    st.markdown('<div class="al-r">No nodes can fulfil this request.</div>',unsafe_allow_html=True)

    with sc_tab:
        st.markdown('<div class="sh">Supplier & Node Scorecard</div>',unsafe_allow_html=True)
        scores=st.session_state.scores
        node_opts=[n for n in sc.nodes.values() if n.node_type in ("plant","warehouse")]
        if node_opts:
            snm=st.selectbox("Node",[n.name for n in node_opts],key="sc_sel")
            snid=[n.id for n in node_opts if n.name==snm]
            if snid:
                nid=snid[0]
                if nid not in scores: scores[nid]={"reliability":80,"lead_time":80,"quality":80,"cost_efficiency":80}
                s=scores[nid]
                c1,c2=st.columns([1,1])
                with c1:
                    st.markdown("**Edit Scores (0–100)**")
                    s["reliability"]    =st.slider("Reliability",   0,100,int(s["reliability"]),   key=f"sr_{nid}")
                    s["lead_time"]      =st.slider("Lead Time",     0,100,int(s["lead_time"]),     key=f"sl_{nid}")
                    s["quality"]        =st.slider("Quality",       0,100,int(s["quality"]),       key=f"sq_{nid}")
                    s["cost_efficiency"]=st.slider("Cost Efficiency",0,100,int(s["cost_efficiency"]),key=f"sc_{nid}")
                    ov=round((s["reliability"]+s["lead_time"]+s["quality"]+s["cost_efficiency"])/4,1)
                    grade="A" if ov>=90 else "B" if ov>=75 else "C" if ov>=60 else "D"
                    gbc="b-g" if grade=="A" else "b-b" if grade=="B" else "b-a" if grade=="C" else "b-r"
                    st.markdown(f"<br><b style='color:#ECF0F1'>Overall: {ov}</b> <span class='{gbc}'>Grade {grade}</span>",unsafe_allow_html=True)
                with c2: st.plotly_chart(draw_scorecard_radar(snm,s),use_container_width=True)

            st.markdown("<br>",unsafe_allow_html=True); st.markdown('<div class="sh">All Nodes Ranking</div>',unsafe_allow_html=True)
            rows_sc=[]
            for n in node_opts:
                if n.id in scores:
                    s=scores[n.id]; ov=round((s["reliability"]+s["lead_time"]+s["quality"]+s["cost_efficiency"])/4,1)
                    g="A" if ov>=90 else "B" if ov>=75 else "C" if ov>=60 else "D"
                    rows_sc.append({"Node":n.name,"Type":n.node_type.capitalize(),"Reliability":s["reliability"],
                        "Lead Time":s["lead_time"],"Quality":s["quality"],"Cost Eff":s["cost_efficiency"],"Overall":ov,"Grade":g})
            if rows_sc:
                df_sc=pd.DataFrame(rows_sc).sort_values("Overall",ascending=False)
                def gc(v):
                    c={"A":"#0A2A0A","B":"#0A1A2A","C":"#2A1A00","D":"#2A0A0A"}; return f"background-color:{c.get(v,'#16213E')};font-weight:600"
                st.dataframe(df_sc.style.map(gc,subset=["Grade"]),use_container_width=True,hide_index=True)


# ─────────────────────────────────────────────────────────────
# TAB 8 — GEOGRAPHIC VIEW
# ─────────────────────────────────────────────────────────────
with t8:
    st.markdown('<div class="sh">Geographic Network View</div>',unsafe_allow_html=True)
    _,cr=st.columns([3,1]); mscope=cr.radio("Scope",["India","World"],key="geo_s")
    has_coords=[n for n in sc.nodes.values() if n.x!=0 or n.y!=0]
    if not has_coords: st.info("No coordinates found. Load the demo supply chain to see the India map.")
    else:
        st.plotly_chart(draw_geo_map(sc,mscope.lower()),use_container_width=True)
        with st.expander("Node Coordinates"):
            st.dataframe(pd.DataFrame([{"Node":n.name,"Type":n.node_type,"Lat":n.y,"Lon":n.x,"Location":n.location} for n in sc.nodes.values()]),use_container_width=True,hide_index=True)


# ─────────────────────────────────────────────────────────────
# TAB 9 — AI ASSISTANT (FIXED + ACTIONS + VOICE)
# ─────────────────────────────────────────────────────────────
with t9:
    st.markdown('<div class="sh">AI Supply Chain Assistant</div>',unsafe_allow_html=True)

    # API Key check
    if not st.session_state.api_key:
        st.markdown('<div class="al-a">⚙ Add your Anthropic API key in the sidebar (Data tab → AI Assistant Setup) to enable the AI assistant.</div>',unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
        <b>How to get an API key:</b><br>
        1. Go to <a href="https://console.anthropic.com" target="_blank" style="color:#2E86C1">console.anthropic.com</a><br>
        2. Sign up / log in → API Keys → Create Key<br>
        3. Copy the key (starts with sk-ant-...)<br>
        4. Paste it in the sidebar under <b>AI Assistant Setup</b>
        </div>""", unsafe_allow_html=True)

    # Voice component
    st.markdown('<div class="sh">Voice Interface</div>', unsafe_allow_html=True)
    voice_component()
    st.markdown("<br>",unsafe_allow_html=True)

    # Quick actions
    st.markdown('<div class="sh">Quick Actions</div>', unsafe_allow_html=True)
    qa_cols=st.columns(4)
    quick_actions=[
        ("Platform Tour","Give me a complete tour of the Supply Chain Resilience Platform."),
        ("Network Status","What is the current status of my supply chain network?"),
        ("Stock Alerts","Check inventory and tell me which items need urgent attention."),
        ("Best Practices","What supply chain resilience best practices should I implement?"),
    ]
    for i,(label,query) in enumerate(quick_actions):
        if qa_cols[i].button(label,use_container_width=True,key=f"qa_{i}"):
            st.session_state.chat_history.append({"role":"user","content":query})
            st.rerun()

    st.markdown("<br>",unsafe_allow_html=True)

    # Chat display
    st.markdown('<div class="sh">Conversation</div>', unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="background:#16213E;border:1px solid #1E3A5F;border-radius:12px;padding:28px;
          text-align:center;color:#5D6D7E;margin:10px 0">
          <div style="font-size:32px;margin-bottom:10px">⬡</div>
          <div style="font-size:15px;font-weight:600;color:#BDC3C7;margin-bottom:6px">
            Supply Chain AI Assistant</div>
          <div style="font-size:13px">Ask anything, execute actions, or use the quick buttons above.<br>
            Speak using the voice widget, or type below.</div>
        </div>""", unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            role=msg["role"]; content=msg.get("display",msg["content"])
            if role=="user":
                st.markdown(f'<div class="chat-wrap chat-right"><div class="user-bubble">{content}</div></div>',unsafe_allow_html=True)
            else:
                # Check for action result
                ar=msg.get("action_result","")
                ar_html=f'<div class="al-g" style="margin-top:6px;font-size:12px">{ar}</div>' if ar else ""
                st.markdown(f'<div class="chat-wrap chat-left"><div class="ai-bubble">{content}{ar_html}</div></div>',unsafe_allow_html=True)

    # Auto-respond if last message is from user
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"]=="user":
        if not st.session_state.api_key:
            # Rule-based fallback
            user_msg=st.session_state.chat_history[-1]["content"].lower()
            if "status" in user_msg or "network" in user_msg:
                plants=[n for n in sc.nodes.values() if n.node_type=="plant"]
                whs_=[n for n in sc.nodes.values() if n.node_type=="warehouse"]
                dems_=[n for n in sc.nodes.values() if n.node_type=="demand"]
                alerts_=inv.get_alerts(sc.nodes)
                reply=f"Network has {len(plants)} plants, {len(whs_)} warehouses, {len(dems_)} demand points, {len(sc.edges)} connections. Stock alerts: {len([a for a in alerts_ if a['level']=='critical'])} critical, {len([a for a in alerts_ if a['level']=='warning'])} warnings. Add your API key in the sidebar to get full AI responses!"
            else:
                reply="Please add your Anthropic API key in the sidebar (Data tab → AI Assistant Setup) to enable full AI responses. I can still show you basic network status without a key!"
            st.session_state.chat_history.append({"role":"assistant","content":reply,"display":reply})
            st.rerun()
        else:
            # Build context about current state
            plants=[n for n in sc.nodes.values() if n.node_type=="plant"]
            dems_=[n for n in sc.nodes.values() if n.node_type=="demand"]
            alerts_=inv.get_alerts(sc.nodes)
            ctx_msg=f"""[CURRENT NETWORK STATE]
Nodes: {len(sc.nodes)} total ({len(plants)} plants, {len([n for n in sc.nodes.values() if n.node_type=='warehouse'])} warehouses, {len(dems_)} demand points)
Connections: {len(sc.edges)}
Stock alerts: {len([a for a in alerts_ if a['level']=='critical'])} critical, {len([a for a in alerts_ if a['level']=='warning'])} warnings
Node names: {', '.join(n.name for n in list(sc.nodes.values())[:10])}
Items tracked: {', '.join(iv['name'] for iv in list(inv.items.values())[:5])}
[END STATE]"""

            messages=[]
            for m in st.session_state.chat_history:
                if m["role"]=="user":
                    content=m["content"]
                    if len(messages)==0: content=ctx_msg+"\n\nUser: "+content
                    messages.append({"role":"user","content":content})
                elif m["role"]=="assistant":
                    messages.append({"role":"assistant","content":m["content"]})

            with st.spinner("Thinking..."):
                reply_text, status = call_ai(messages, st.session_state.api_key)

            if status=="ok" and reply_text:
                # Parse action
                action=parse_action(reply_text)
                display_text=clean_response(reply_text)
                # Format display
                display_html=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',display_text)
                display_html=display_html.replace('\n','<br>')
                action_result=""
                if action:
                    # Ask for confirmation for modifying actions
                    modifying=action.get("action") in ("update_stock","add_node")
                    if modifying:
                        st.session_state["pending_action"]=action
                        display_html+="<br><br><i>⚡ I can execute this action. Type <b>'confirm'</b> to proceed or <b>'cancel'</b> to abort.</i>"
                    else:
                        ok,msg=execute_action(action,sc,inv)
                        action_result=("✓ "+msg) if ok else ("✗ "+msg)
                st.session_state.chat_history.append({"role":"assistant","content":reply_text,
                    "display":display_html,"action_result":action_result})
                st.session_state.last_ai_text=display_text
                st.rerun()
            elif status=="invalid_key":
                st.session_state.chat_history.append({"role":"assistant",
                    "content":"Invalid API key. Please check your key in the sidebar.",
                    "display":"Invalid API key. Please check your key in the sidebar."})
                st.rerun()
            elif status=="timeout":
                st.session_state.chat_history.append({"role":"assistant",
                    "content":"Request timed out. Please try again.",
                    "display":"Request timed out. Please try again."})
                st.rerun()
            else:
                err_msg=f"Connection error ({status}). Check your internet connection and API key."
                st.session_state.chat_history.append({"role":"assistant","content":err_msg,"display":err_msg})
                st.rerun()

    # Handle pending action confirmation
    if "pending_action" in st.session_state and st.session_state.chat_history:
        last=st.session_state.chat_history[-1]
        if last["role"]=="user":
            user_text=last["content"].strip().lower()
            if user_text in ("confirm","yes","proceed","ok"):
                ok,msg=execute_action(st.session_state["pending_action"],sc,inv)
                st.session_state.chat_history.append({"role":"assistant",
                    "content":"Action executed: "+msg,"display":"Action executed: "+msg,
                    "action_result":("✓" if ok else "✗")+" "+msg})
                del st.session_state["pending_action"]; st.rerun()
            elif user_text in ("cancel","no","abort"):
                st.session_state.chat_history.append({"role":"assistant",
                    "content":"Action cancelled.","display":"Action cancelled."})
                del st.session_state["pending_action"]; st.rerun()

    # Chat input with TTS
    st.markdown("<br>",unsafe_allow_html=True)
    with st.form("chat_form",clear_on_submit=True):
        c1,c2=st.columns([5,1])
        user_in=c1.text_input("Message...",placeholder="Type or paste voice text here...",
            label_visibility="collapsed",key="chat_in")
        send=c2.form_submit_button("Send",use_container_width=True)
        if send and user_in.strip():
            st.session_state.chat_history.append({"role":"user","content":user_in.strip()})
            st.rerun()

    # TTS for last AI message
    if st.session_state.last_ai_text:
        tts_js=f"""
        <script>
        setTimeout(function(){{
          if(window.speakText) {{
            window.speakText({json.dumps(st.session_state.last_ai_text[:400])});
          }}
        }}, 800);
        </script>"""
        st.markdown(tts_js, unsafe_allow_html=True)

    # Clear conversation
    col_clr,_=st.columns([1,4])
    if col_clr.button("Clear Chat",key="clr_chat"):
        st.session_state.chat_history=[]; st.session_state.last_ai_text=""; st.rerun()
