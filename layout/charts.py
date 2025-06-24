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
    tp_values = []
    profits = []
    profit_pcts = []

    for r in r_values:
        if direction == "Long":
            tp = entry + (r * sl_distance)
        else:
            tp = entry - (r * sl_distance)

        tp_values.append(round(tp, 4))
        profit = abs(tp - entry) * position_size
        profits.append(profit)
        profit_pcts.append((profit / balance) * 100)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=r_values,
        y=profits,
        mode="lines+markers",
        name="Profit (£)",
        hovertemplate="R: %{x}<br>TP: %{customdata}<br>£%{y:.2f}<extra></extra>",
        customdata=tp_values
    ))

    fig.update_layout(
        title="📈 R-Multiple Analysis",
        xaxis=dict(
            title="R-Multiple",
            tickmode='linear',
            tick0=1,
            dtick=0.5,
            side="bottom"
        ),
        xaxis2=dict(
            title="Take Profit (TP)",
            overlaying="x",
            side="top",
            tickvals=r_values,
            ticktext=[f"{tp:.2f}" for tp in tp_values],
            showgrid=False
        ),
        yaxis=dict(
            title="Profit (£)",
            side="left"
        ),
        yaxis2=dict(
            title="Profit (% Balance)",
            overlaying="y",
            side="right",
            showgrid=False,
            tickvals=profits,
            ticktext=[f"{p:.2f}%" for p in profit_pcts]
        ),
        height=400,
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(x=0.5, xanchor="center", y=-0.25, orientation="h")
    )

    return fig