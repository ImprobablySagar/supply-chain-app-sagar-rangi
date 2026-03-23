"""
Supply Chain Visualization
Generates interactive Plotly figures for the supply chain graph.
"""

import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import math
import pandas as pd
from core.graph_engine import SupplyChainGraph


# ─────────────────────────────────────────────
# Color scheme
# ─────────────────────────────────────────────

NODE_COLORS = {
    "plant":     "#0F6E56",   # green
    "warehouse": "#185FA5",   # blue
    "demand":    "#993C1D",   # coral
}

NODE_SYMBOLS = {
    "plant":     "square",
    "warehouse": "diamond",
    "demand":    "circle",
}

SEVERITY_COLORS = {
    "critical": "#E24B4A",
    "high":     "#EF9F27",
    "medium":   "#378ADD",
    "low":      "#1D9E75",
    "none":     "#888780",
}


# ─────────────────────────────────────────────
# Layout helpers
# ─────────────────────────────────────────────

def _auto_layout(sc: SupplyChainGraph) -> dict[str, tuple[float, float]]:
    """
    Hierarchical layout: plants (left) → warehouses (center) → demand (right).
    Falls back to spring layout if no type info.
    """
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


def _edge_trace(x0, y0, x1, y1, color, width, dash, label="", opacity=1.0):
    """Arrow-style edge as a Scatter trace."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2

    return go.Scatter(
        x=[x0, x1, None],
        y=[y0, y1, None],
        mode="lines+text",
        line=dict(color=color, width=width, dash=dash),
        opacity=opacity,
        text=["", label, ""],
        textposition="middle center",
        textfont=dict(size=9, color=color),
        hoverinfo="skip",
        showlegend=False,
    )


# ─────────────────────────────────────────────
# Main supply chain figure
# ─────────────────────────────────────────────

def draw_supply_chain(
    sc: SupplyChainGraph,
    highlight_path: list[str] = None,
    disrupted_edge: tuple[str, str] = None,
    show_capacity: bool = True,
) -> go.Figure:
    """
    Full interactive supply chain diagram.
    - highlight_path: list of node IDs to highlight in gold
    - disrupted_edge: (source, target) to mark red/dashed
    """
    pos = _auto_layout(sc)
    highlight_path = highlight_path or []
    highlight_set = set(zip(highlight_path, highlight_path[1:])) if len(highlight_path) > 1 else set()

    traces = []

    # ── Edges ──────────────────────────────────
    for edge in sc.edges:
        x0, y0 = pos[edge.source]
        x1, y1 = pos[edge.target]

        is_disrupted = (
            disrupted_edge and
            edge.source == disrupted_edge[0] and
            edge.target == disrupted_edge[1]
        )
        is_highlighted = (edge.source, edge.target) in highlight_set
        is_inactive = not edge.active or is_disrupted

        color = (
            "#E24B4A" if is_disrupted else
            "#EF9F27" if is_highlighted else
            "#B4B2A9" if is_inactive else
            "#5F5E5A"
        )
        width = 3 if is_highlighted else 2 if is_disrupted else 1.5
        dash = "dot" if is_inactive else "solid"
        opacity = 0.4 if is_inactive and not is_disrupted else 1.0

        cap_label = f"  cap:{edge.capacity}" if show_capacity else ""
        traces.append(_edge_trace(x0, y0, x1, y1, color, width, dash,
                                  label=cap_label, opacity=opacity))

        # Arrow head (small marker at target end)
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        if length > 0:
            ux, uy = dx / length, dy / length
            ax = x1 - ux * 0.07
            ay = y1 - uy * 0.07
            traces.append(go.Scatter(
                x=[ax], y=[ay], mode="markers",
                marker=dict(symbol="arrow", size=10, color=color,
                            angle=math.degrees(math.atan2(-dy, dx)) + 90),
                showlegend=False, hoverinfo="skip",
            ))

    # ── Nodes ──────────────────────────────────
    for ntype in ["plant", "warehouse", "demand"]:
        nids = [n for n, node in sc.nodes.items() if node.node_type == ntype]
        if not nids:
            continue

        xs = [pos[n][0] for n in nids]
        ys = [pos[n][1] for n in nids]
        names = [sc.nodes[n].name for n in nids]
        caps = [sc.nodes[n].capacity for n in nids]
        locs = [sc.nodes[n].location or "" for n in nids]

        in_path = [n in highlight_path for n in nids]
        colors = [
            "#EF9F27" if ip else NODE_COLORS[ntype]
            for ip in in_path
        ]
        sizes = [22 if ip else 16 for ip in in_path]

        hover = [
            f"<b>{name}</b><br>Type: {ntype}<br>"
            f"Capacity/Demand: {cap}<br>Location: {loc}"
            for name, cap, loc in zip(names, caps, locs)
        ]

        traces.append(go.Scatter(
            x=xs, y=ys,
            mode="markers+text",
            name=ntype.capitalize() + "s",
            text=names,
            textposition=(
                "middle left" if ntype == "plant" else
                "top center" if ntype == "warehouse" else
                "middle right"
            ),
            textfont=dict(size=11),
            hovertext=hover,
            hoverinfo="text",
            marker=dict(
                symbol=NODE_SYMBOLS[ntype],
                size=sizes,
                color=colors,
                line=dict(width=1.5, color="white"),
            ),
        ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=11),
        ),
        height=480,
        hovermode="closest",
    )
    return fig


# ─────────────────────────────────────────────
# Disruption impact bar chart
# ─────────────────────────────────────────────

def draw_impact_chart(impact: dict) -> go.Figure:
    """Bar chart showing before/after fulfillment per demand node."""
    names  = [v["demand_name"] for v in impact.values()]
    before = [v["before_pct"] for v in impact.values()]
    after  = [v["after_pct"]  for v in impact.values()]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Before disruption", x=names, y=before,
        marker_color="#1D9E75", opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        name="After disruption", x=names, y=after,
        marker_color="#E24B4A", opacity=0.85,
    ))

    fig.update_layout(
        barmode="group",
        yaxis=dict(title="Demand fulfillment (%)", range=[0, 110]),
        xaxis=dict(title="Demand point"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    fig.add_hline(y=100, line_dash="dot", line_color="#888780",
                  annotation_text="Full demand", annotation_position="right")
    return fig


# ─────────────────────────────────────────────
# Critical edge ranking chart
# ─────────────────────────────────────────────

def draw_criticality_chart(ranking: list[dict]) -> go.Figure:
    """Horizontal bar chart: edge criticality ranking."""
    labels = [r["label"] for r in ranking]
    drops  = [r["avg_fulfillment_drop"] for r in ranking]
    colors = [SEVERITY_COLORS[r["severity"]] for r in ranking]

    fig = go.Figure(go.Bar(
        x=drops, y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{d}%" for d in drops],
        textposition="outside",
    ))
    fig.update_layout(
        xaxis=dict(title="Avg fulfillment drop (%)", range=[0, max(drops or [10]) * 1.3]),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=max(300, len(ranking) * 40),
        margin=dict(l=10, r=60, t=10, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# Resilience score gauge
# ─────────────────────────────────────────────

def draw_resilience_gauge(score: float) -> go.Figure:
    color = (
        "#E24B4A" if score < 40 else
        "#EF9F27" if score < 70 else
        "#1D9E75"
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "steps": [
                {"range": [0,  40], "color": "#FCEBEB"},
                {"range": [40, 70], "color": "#FAEEDA"},
                {"range": [70, 100], "color": "#EAF3DE"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
