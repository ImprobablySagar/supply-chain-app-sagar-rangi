# Supply Chain Resilience Dashboard

A Python-based interactive dashboard to build, visualize, and stress-test your
supply chain network. Built with **Streamlit** + **NetworkX** + **Plotly**.

---

## Features

| Feature | Description |
|---|---|
| 🗺️ Supply Chain Map | Interactive graph of plants → warehouses → demand points |
| ➕ Node & Connection Builder | Add/remove nodes and connections from the sidebar |
| 🔍 Shortest Path Finder | Find cheapest route between any two nodes |
| 📊 Demand Fulfillment | See what % of each demand point is currently being met |
| ⚡ Disruption Simulator | Remove any connection — instantly see impact scores & alternate routes |
| 🏆 Criticality Ranking | Stress-test ALL connections, ranked by damage they cause if removed |
| 💾 Import / Export | Upload your own CSV data, export to JSON |

---

## Setup (5 minutes)

### 1. Install Python 3.10+
Download from https://python.org if not installed.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```
The app opens automatically at **http://localhost:8501**

---

## Project Structure

```
supply_chain_app/
│
├── app.py                    ← Main Streamlit dashboard
│
├── core/
│   ├── graph_engine.py       ← All graph logic & algorithms
│   └── visualizer.py         ← Plotly figure generators
│
├── data/
│   ├── sample_data.py        ← Built-in demo supply chain
│   ├── sample_nodes.csv      ← Template for your own nodes
│   └── sample_edges.csv      ← Template for your own connections
│
└── requirements.txt
```

---

## How to use your own data

### Option 1 — Upload CSV files in the app
In the sidebar → **Save/Load** tab → upload your nodes and edges CSV files.

**nodes.csv format:**
| Column | Description |
|---|---|
| id | Unique ID (e.g. P1, W2, D3) |
| name | Human-readable name |
| node_type | `plant`, `warehouse`, or `demand` |
| capacity | Units produced / stored / demanded |
| location | Optional — city, country |

**edges.csv format:**
| Column | Description |
|---|---|
| source | Source node id |
| target | Target node id |
| capacity | Max units this link can carry |
| cost | Transport cost per unit (used for shortest path) |

### Option 2 — Edit sample_data.py directly
Open `data/sample_data.py` and add your real plants, warehouses, and demand points.

---

## Understanding the algorithms

### Shortest Path
Uses **Dijkstra's algorithm** on transport cost as the edge weight.
Finds the cheapest route from any plant to any demand point.

### Demand Fulfillment
Uses **Max-Flow** (Edmonds-Karp algorithm) from each plant to each demand point.
Answers: "Given all capacity constraints, how much of this demand can actually be met?"

### Disruption Simulation
1. Remove selected edge from graph
2. Re-run demand fulfillment on reduced graph
3. Compare before vs after — compute impact per demand node
4. Find alternate shortest paths for affected nodes
5. Compute overall resilience score = `100 - avg_fulfillment_drop`

### Criticality Ranking
Runs disruption simulation on every edge one at a time.
Ranks edges by `avg_fulfillment_drop` across all demand nodes.
Use this to know which connections to make redundant first.

---

## Resilience Score Guide

| Score | Status | Action |
|---|---|---|
| 70 – 100 | 🟢 Resilient | Monitor, low priority |
| 40 – 69 | 🟡 Moderate risk | Plan backup routes |
| 0 – 39 | 🔴 Critical | Add redundancy urgently |

---

## Next steps / extensions

- **Multi-node disruption**: test what happens if 2 connections fail simultaneously
- **Cost optimization**: use min-cost max-flow to find the cheapest way to meet all demand
- **Time dimension**: add lead times to edges for delivery timeline analysis  
- **Geospatial map**: swap Plotly scatter for a map background using `plotly.express.scatter_mapbox`
- **Export reports**: generate PDF resilience reports for management
