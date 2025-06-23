import plotly.graph_objects as go
import logic.logic as logic
import logic.trade as trade

def plot_r_multiple_analysis(trade_data, balance):
    entry = trade_data["entry"]
    stop = trade_data["stop"]
    position_size = trade_data["position_size"]
    sl_distance = abs(entry - stop)
    direction = trade_data["direction"]

    r_values = list(trade.frange(1.0, 5.0, 0.2))
    data = []

    for r in r_values:
        if direction == "Long":
            tp = entry + (r * sl_distance)
        else:
            tp = entry - (r * sl_distance)

        profit = abs(tp - entry) * position_size
        profit_pct = (profit / balance) * 100

        data.append({
            "R": r,
            "TP": round(tp, 4),
            "Profit": round(profit, 2),
            "Profit %": round(profit_pct, 2)
        })

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[d["R"] for d in data],
        y=[d["Profit"] for d in data],
        name="Profit (£)",
        mode="lines+markers",
        yaxis="y1",
        hovertemplate="R: %{x}<br>Profit: £%{y:.2f}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=[d["R"] for d in data],
        y=[d["Profit %"] for d in data],
        name="Profit (% Balance)",
        mode="lines+markers",
        yaxis="y2",
        hovertemplate="R: %{x}<br>Profit: %{y:.2f}%<extra></extra>"
    ))

    fig.update_layout(
        title="📈 R-Multiple vs Profit",
        xaxis=dict(title="R-Multiple"),
        yaxis=dict(title="Profit (£)", side="left"),
        yaxis2=dict(title="Profit (% Balance)", overlaying="y", side="right"),
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(x=0.5, xanchor="center", orientation="h", y=-0.3),
        height=400
    )

    return fig
