"""
Supply Chain Resilience Dashboard
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
import io
from core.graph_engine import SupplyChainGraph, Node, Edge
from core.visualizer import (
    draw_supply_chain, draw_impact_chart,
    draw_criticality_chart, draw_resilience_gauge
)
from data.sample_data import load_demo_data

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Supply Chain Resilience",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #185FA5;
        margin-bottom: 8px;
    }
    .severity-critical { color: #E24B4A; font-weight: 600; }
    .severity-high     { color: #EF9F27; font-weight: 600; }
    .severity-medium   { color: #378ADD; font-weight: 600; }
    .severity-none     { color: #1D9E75; font-weight: 600; }
    div[data-testid="stExpander"] { border: 1px solid #e0e0e0; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────

if "sc" not in st.session_state:
    st.session_state.sc = load_demo_data()
if "disruption_result" not in st.session_state:
    st.session_state.disruption_result = None
if "highlight_path" not in st.session_state:
    st.session_state.highlight_path = []
if "disrupted_edge" not in st.session_state:
    st.session_state.disrupted_edge = None

sc: SupplyChainGraph = st.session_state.sc


# ─────────────────────────────────────────────
# Sidebar — Build your supply chain
# ─────────────────────────────────────────────

with st.sidebar:
    st.title("🔗 Supply Chain Builder")
    st.caption("Build, connect, and test your supply chain resilience")

    tab1, tab2, tab3 = st.tabs(["➕ Add Nodes", "🔗 Connections", "💾 Save/Load"])

    # ── Tab 1: Add Nodes ──────────────────────
    with tab1:
        st.subheader("Add a new node")
        col_a, col_b = st.columns(2)
        with col_a:
            node_name = st.text_input("Name", placeholder="e.g. Plant Delhi")
            node_type = st.selectbox("Type", ["plant", "warehouse", "demand"])
        with col_b:
            node_cap  = st.number_input("Capacity / Demand", min_value=1, value=200)
            node_loc  = st.text_input("Location", placeholder="City, Country")

        if st.button("Add Node", use_container_width=True, type="primary"):
            if node_name.strip():
                nid = node_type[0].upper() + str(len([
                    n for n in sc.nodes.values() if n.node_type == node_type
                ]) + 1)
                sc.add_node(Node(nid, node_name.strip(), node_type, node_cap, node_loc))
                st.success(f"✅ Added {node_name}")
                st.rerun()
            else:
                st.error("Please enter a node name")

        # Display existing nodes
        st.divider()
        st.subheader("Current nodes")
        for ntype, emoji in [("plant", "🏭"), ("warehouse", "🏢"), ("demand", "📦")]:
            nodes_of_type = [n for n in sc.nodes.values() if n.node_type == ntype]
            if nodes_of_type:
                with st.expander(f"{emoji} {ntype.capitalize()}s ({len(nodes_of_type)})"):
                    for n in nodes_of_type:
                        col1, col2 = st.columns([3, 1])
                        col1.write(f"**{n.name}** — cap: {n.capacity}")
                        if col2.button("🗑", key=f"del_{n.id}", help="Remove node"):
                            del sc.nodes[n.id]
                            sc.edges = [e for e in sc.edges
                                        if e.source != n.id and e.target != n.id]
                            st.rerun()

    # ── Tab 2: Connections ────────────────────
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
                    st.error("Source and target must be different nodes")
                else:
                    try:
                        sc.add_edge(Edge(src_id, tgt_id, edge_cap, edge_cost))
                        st.success(f"✅ Connected {src_label} → {tgt_label}")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
        else:
            st.info("Add at least 2 nodes first")

        # List existing connections
        st.divider()
        st.subheader("Current connections")
        if sc.edges:
            for e in sc.edges:
                src_name = sc.nodes[e.source].name
                tgt_name = sc.nodes[e.target].name
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{src_name}** → {tgt_name}  `cap:{e.capacity}`")
                if col2.button("🗑", key=f"del_edge_{e.source}_{e.target}"):
                    sc.remove_edge(e.source, e.target)
                    st.rerun()
        else:
            st.info("No connections yet")

    # ── Tab 3: Save / Load ────────────────────
    with tab3:
        st.subheader("Load demo data")
        if st.button("🔄 Load demo supply chain", use_container_width=True):
            st.session_state.sc = load_demo_data()
            st.session_state.disruption_result = None
            st.session_state.highlight_path = []
            st.session_state.disrupted_edge = None
            st.rerun()

        st.divider()
        st.subheader("Import from CSV")
        st.caption("Nodes CSV columns: id, name, node_type, capacity, location")
        nodes_file = st.file_uploader("Upload nodes CSV", type="csv", key="nodes_csv")
        edges_file = st.file_uploader("Upload connections CSV", type="csv", key="edges_csv")

        if nodes_file and edges_file:
            if st.button("Import", use_container_width=True):
                try:
                    nodes_df = pd.read_csv(nodes_file)
                    edges_df = pd.read_csv(edges_file)
                    new_sc = SupplyChainGraph()
                    for _, row in nodes_df.iterrows():
                        new_sc.add_node(Node(
                            str(row["id"]), str(row["name"]),
                            str(row["node_type"]), float(row["capacity"]),
                            str(row.get("location", ""))
                        ))
                    for _, row in edges_df.iterrows():
                        new_sc.add_edge(Edge(
                            str(row["source"]), str(row["target"]),
                            float(row["capacity"]),
                            float(row.get("cost", 1.0))
                        ))
                    st.session_state.sc = new_sc
                    st.success("✅ Imported successfully!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Import failed: {ex}")

        st.divider()
        st.subheader("Export")
        data = sc.to_dict()
        nodes_df = pd.DataFrame([vars(n) for n in sc.nodes.values()])
        edges_df = pd.DataFrame([vars(e) for e in sc.edges])

        col_e1, col_e2 = st.columns(2)
        if not nodes_df.empty:
            col_e1.download_button("⬇ Nodes CSV", nodes_df.to_csv(index=False),
                                   "nodes.csv", "text/csv", use_container_width=True)
        if not edges_df.empty:
            col_e2.download_button("⬇ Edges CSV", edges_df.to_csv(index=False),
                                   "edges.csv", "text/csv", use_container_width=True)

        st.download_button("⬇ Full JSON", json.dumps(data, indent=2),
                           "supply_chain.json", "application/json",
                           use_container_width=True)


# ─────────────────────────────────────────────
# Main area — 3 tabs
# ─────────────────────────────────────────────

st.title("📦 Supply Chain Resilience Dashboard")

main_tab1, main_tab2, main_tab3 = st.tabs([
    "🗺️ Supply Chain Map",
    "⚡ Disruption Simulator",
    "🏆 Criticality Ranking",
])


# ══════════════════════════════════════════════
# TAB 1 — Supply Chain Map
# ══════════════════════════════════════════════
with main_tab1:
    if not sc.nodes:
        st.info("👈 Add nodes in the sidebar to get started, or load the demo data.")
    else:
        # Summary metrics
        plants    = [n for n in sc.nodes.values() if n.node_type == "plant"]
        warehouses= [n for n in sc.nodes.values() if n.node_type == "warehouse"]
        demands   = [n for n in sc.nodes.values() if n.node_type == "demand"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🏭 Plants",     len(plants),    delta=f"Cap: {sum(n.capacity for n in plants)}")
        m2.metric("🏢 Warehouses", len(warehouses), delta=f"Cap: {sum(n.capacity for n in warehouses)}")
        m3.metric("📦 Demand pts", len(demands),    delta=f"Total: {sum(n.capacity for n in demands)}")
        m4.metric("🔗 Connections",len(sc.edges))

        st.divider()

        # Graph options
        col_opt1, col_opt2 = st.columns([3, 1])
        with col_opt2:
            show_cap = st.checkbox("Show capacities on edges", value=True)

        # Draw the map
        fig = draw_supply_chain(
            sc,
            highlight_path=st.session_state.highlight_path,
            disrupted_edge=st.session_state.disrupted_edge,
            show_capacity=show_cap,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Legend
        col_l1, col_l2, col_l3, col_l4 = st.columns(4)
        col_l1.markdown("🟩 **Plant** — Manufacturing")
        col_l2.markdown("🔷 **Warehouse** — Storage")
        col_l3.markdown("🔴 **Demand** — End market")
        col_l4.markdown("🟡 **Gold** — Highlighted path")

        st.divider()

        # Shortest path finder
        st.subheader("🔍 Find Shortest Path")
        col_sp1, col_sp2, col_sp3 = st.columns([2, 2, 1])

        node_labels = {n.name: n.id for n in sc.nodes.values()}
        with col_sp1:
            sp_src = st.selectbox("From", list(node_labels.keys()), key="sp_src")
        with col_sp2:
            sp_tgt = st.selectbox("To",   list(node_labels.keys()), key="sp_tgt",
                                  index=min(2, len(node_labels)-1))
        with col_sp3:
            st.write("")
            st.write("")
            find = st.button("Find Path 🔍", use_container_width=True)

        if find:
            src_id = node_labels[sp_src]
            tgt_id = node_labels[sp_tgt]
            results = sc.all_shortest_paths(src_id, tgt_id, k=3)

            if results:
                st.session_state.highlight_path = results[0]["path"]
                st.rerun()
            else:
                st.warning("⚠️ No path found between these nodes")
                st.session_state.highlight_path = []

        # Show path details if highlighted
        if st.session_state.highlight_path:
            path = st.session_state.highlight_path
            names = [sc.nodes[n].name for n in path]
            st.success(f"✅ Shortest path: **{'  →  '.join(names)}**")
            if st.button("Clear highlight"):
                st.session_state.highlight_path = []
                st.rerun()

        # Demand fulfillment table
        st.divider()
        st.subheader("📊 Current Demand Fulfillment")
        if sc.edges:
            with st.spinner("Computing fulfillment..."):
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
                if val >= 90:   return "background-color: #d4edda"
                if val >= 50:   return "background-color: #fff3cd"
                return "background-color: #f8d7da"

            st.dataframe(
                df.style.applymap(color_pct, subset=["Fulfillment %"]),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("Add connections to see demand fulfillment")


# ══════════════════════════════════════════════
# TAB 2 — Disruption Simulator
# ══════════════════════════════════════════════
with main_tab2:
    st.subheader("⚡ Simulate a Connection Failure")
    st.caption("Select any connection to remove it and instantly see the impact on your supply chain")

    if not sc.edges:
        st.info("Add connections first to simulate disruptions")
    else:
        edge_options = {
            f"{sc.nodes[e.source].name}  →  {sc.nodes[e.target].name}  (cap: {e.capacity})":
            (e.source, e.target)
            for e in sc.edges
        }

        col_d1, col_d2 = st.columns([3, 1])
        with col_d1:
            chosen_edge_label = st.selectbox(
                "Connection to disrupt", list(edge_options.keys()),
                key="disrupt_edge_select"
            )
        with col_d2:
            st.write("")
            st.write("")
            simulate_btn = st.button("⚡ Simulate", use_container_width=True, type="primary")

        if simulate_btn:
            src, tgt = edge_options[chosen_edge_label]
            with st.spinner("Analyzing disruption impact..."):
                result = sc.simulate_disruption(src, tgt)
            st.session_state.disruption_result = result
            st.session_state.disrupted_edge = (src, tgt)
            st.rerun()

        if st.session_state.disruption_result:
            result = st.session_state.disruption_result

            # ── Resilience score + headline ────────
            st.divider()
            col_g, col_h = st.columns([1, 2])
            with col_g:
                st.subheader("Resilience Score")
                st.plotly_chart(
                    draw_resilience_gauge(result["resilience_score"]),
                    use_container_width=True,
                )
            with col_h:
                st.subheader(f"Impact of removing: `{result['removed_edge']}`")
                score = result["resilience_score"]
                if score >= 70:
                    st.success(f"✅ **Low risk.** Your supply chain remains largely intact (score: {score}%)")
                elif score >= 40:
                    st.warning(f"⚠️ **Moderate risk.** Some demand points are affected (score: {score}%)")
                else:
                    st.error(f"🚨 **Critical risk!** Major supply disruption (score: {score}%)")

                # Impact summary cards
                for d_id, imp in result["impact"].items():
                    if imp["drop_pct"] > 0:
                        sev = imp["severity"]
                        sev_color = {
                            "critical": "🔴", "high": "🟠",
                            "medium": "🟡", "none": "🟢"
                        }.get(sev, "⚪")
                        st.write(
                            f"{sev_color} **{imp['demand_name']}**: "
                            f"{imp['before_pct']}% → {imp['after_pct']}%  "
                            f"_(−{imp['drop_pct']}%, lost {imp['lost_units']} units)_"
                        )

            # ── Impact chart ───────────────────────
            st.divider()
            st.subheader("📊 Before vs After Fulfillment")
            st.plotly_chart(
                draw_impact_chart(result["impact"]),
                use_container_width=True,
            )

            # ── Alt paths ─────────────────────────
            st.divider()
            st.subheader("🔄 Alternate Supply Routes")
            if result["alt_paths"]:
                for d_id, paths in result["alt_paths"].items():
                    d_name = sc.nodes[d_id].name
                    with st.expander(f"📦 {d_name} — {len(paths)} alternate route(s) found"):
                        for i, p in enumerate(paths, 1):
                            route_str = " → ".join(p["path"])
                            st.write(f"**Route {i}** (cost: {p['cost']}):  `{route_str}`")

                            # Highlight button
                            if st.button(f"Show on map ↗", key=f"show_path_{d_id}_{i}"):
                                # find node IDs for this path
                                name_to_id = {n.name: nid for nid, n in sc.nodes.items()}
                                st.session_state.highlight_path = [
                                    name_to_id[name] for name in p["path"]
                                    if name in name_to_id
                                ]
                                st.switch_page = "map"  # switch to tab 1
                                st.rerun()
            else:
                st.error("❌ No alternate routes found — this is a single point of failure!")

            if st.button("🔄 Reset disruption"):
                st.session_state.disruption_result = None
                st.session_state.disrupted_edge = None
                st.session_state.highlight_path = []
                st.rerun()


# ══════════════════════════════════════════════
# TAB 3 — Criticality Ranking
# ══════════════════════════════════════════════
with main_tab3:
    st.subheader("🏆 Critical Connection Ranking")
    st.caption(
        "Stress-tests every connection: which ones cause the most damage if removed? "
        "Use this to prioritize which links to make redundant first."
    )

    if not sc.edges:
        st.info("Add connections first")
    else:
        if st.button("🔍 Run Full Stress Test", type="primary", use_container_width=False):
            with st.spinner(f"Testing all {len(sc.edges)} connections..."):
                ranking = sc.rank_critical_edges()
            st.session_state["ranking"] = ranking

        if "ranking" in st.session_state:
            ranking = st.session_state["ranking"]

            # Chart
            st.plotly_chart(
                draw_criticality_chart(ranking),
                use_container_width=True,
            )

            # Table
            st.subheader("Detailed breakdown")
            rows = []
            sev_icons = {
                "critical": "🔴 Critical",
                "high":     "🟠 High",
                "medium":   "🟡 Medium",
                "low":      "🟢 Low",
            }
            for r in ranking:
                rows.append({
                    "Connection": r["label"],
                    "Avg Fulfillment Drop": f"{r['avg_fulfillment_drop']}%",
                    "Resilience Score": f"{r['resilience_score']}%",
                    "Severity": sev_icons.get(r["severity"], r["severity"]),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Recommendations
            st.divider()
            st.subheader("💡 Recommendations")
            critical = [r for r in ranking if r["severity"] == "critical"]
            high     = [r for r in ranking if r["severity"] == "high"]
            safe     = [r for r in ranking if r["severity"] == "low"]

            if critical:
                st.error(
                    f"**🚨 {len(critical)} critical connection(s)** — add redundant paths immediately:\n\n" +
                    "\n".join(f"- {r['label']}" for r in critical)
                )
            if high:
                st.warning(
                    f"**⚠️ {len(high)} high-risk connection(s)** — plan backup routes:\n\n" +
                    "\n".join(f"- {r['label']}" for r in high)
                )
            if safe:
                st.success(
                    f"**✅ {len(safe)} low-risk connection(s)** — safely redundant:\n\n" +
                    "\n".join(f"- {r['label']}" for r in safe)
                )
