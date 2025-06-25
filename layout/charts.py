import plotly.graph_objects as go
import logic.trade as trade

def plot_r_multiple_analysis(trade_data, balance):
    entry = trade_data["entry"]
    stop = trade_data["stop"]
    position_size = trade_data["position_size"]
    sl_distance = abs(entry - stop)
    direction = trade_data["direction"]

    # Finer resolution for smooth curve tracking
    r_values = list(trade.frange(1.0, 5.0, 0.01))
    tp_values = []
    profits = []
    profit_pcts = []

    for r in r_values:
        tp = entry + (r * sl_distance) if direction == "Long" else entry - (r * sl_distance)
        tp_values.append(round(tp, 4))
        profit = abs(tp - entry) * position_size
        profits.append(profit)
        profit_pcts.append((profit / balance) * 100)

    fig = go.Figure()

    # Core profit trace
    fig.add_trace(go.Scatter(
        x=r_values,
        y=profits,
        mode="lines",
        name="Profit (£)",
        yaxis="y1",
        xaxis="x1",
        customdata=list(zip(tp_values, profit_pcts)),
        hovertemplate=(
            "R: %{x:.2f}<br>"
            "TP: £%{customdata[0]:.2f}<br>"
            "£ Profit: £%{y:.2f}<br>"
            "Profit: %{customdata[1]:.2f}%<extra></extra>"
        ),
        line=dict(color="dodgerblue")
    ))

    # Dummy top X for TP
    fig.add_trace(go.Scatter(
        x=r_values,
        y=[None] * len(tp_values),
        mode="lines",
        xaxis="x2",
        showlegend=False
    ))

    # Dummy right Y for % return
    fig.add_trace(go.Scatter(
        x=[None] * len(profit_pcts),
        y=profits,
        mode="lines",
        yaxis="y2",
        showlegend=False
    ))

    # Layout with 4 axes and full hover tracking
    fig.update_layout(
        title="📈 R-Multiple Analysis",
        height=450,
        margin=dict(t=60, b=50, l=60, r=60),

        # 👇 This is what gives you full dynamic crosshair tracking
        hovermode="closest",  
        spikedistance=-1,
        xaxis=dict(
            title="R-Multiple",
            tickmode='linear',
            tick0=1,
            dtick=0.5,
            side="bottom",
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            showline=True,
            showgrid=True
        ),
        xaxis2=dict(
            title="Take Profit (£)",
            overlaying="x",
            side="top",
            tickvals=r_values[::50],
            ticktext=[f"{tp:.2f}" for tp in tp_values[::50]],
            showgrid=False,
            showline=True
        ),
        yaxis=dict(
            title="Profit (£)",
            side="left",
            showspikes=True,
            spikemode="across",
            showline=True,
            showgrid=True
        ),
        yaxis2=dict(
            title="Profit (% Balance)",
            overlaying="y",
            side="right",
            tickvals=profits[::50],
            ticktext=[f"{p:.2f}%" for p in profit_pcts[::50]],
            showgrid=False,
            showline=True
        ),
        legend=dict(
            x=0.5,
            xanchor="center",
            y=-0.3,
            orientation="h"
        )
    )

    return fig
