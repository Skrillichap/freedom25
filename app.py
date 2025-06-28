import streamlit as st
import config.config as config
import ui.ui as ui
import layout.layout as layout
from datetime import datetime

# Init Streamlit session state
config.initialize_session_state()
if "initialized" not in st.session_state:
    initial = config.get_initial_session_state()
    for k, v in initial.items():
        st.session_state[k] = v
    st.session_state.initialized = True

# Page config
st.set_page_config(page_title="Freedom 25", layout="wide")
st.title("🧮 Freedom 25 — Trade Journal")

# Step 1: Session-wide config
ui.session_config_panel()
layout.show_session_metrics()

# Init active trades container
if "active_trades" not in st.session_state:
    st.session_state.active_trades = {}

# Add new trade button
if st.button("➕ Start New Trade"):
    now = datetime.now()
    date_str = now.strftime("%d%m%Y")
    time_str = now.strftime("%H%M")
    count = len(st.session_state.active_trades) + 1
    trade_id = f"{date_str}-{time_str}-{count:05d}"

    st.session_state.active_trades[trade_id] = {
        "stage": 2,
        "collapsed": {
            "step2": False,
            "step3": True,
            "step4": True
        },
        "data": {}
    }

    # Collapse session config on first trade
    st.session_state.session_config_collapsed = True

# Render trades in tabs
if st.session_state.active_trades:
    trade_ids = list(st.session_state.active_trades.keys())
    tabs = st.tabs([f"{i+1}" for i in range(len(trade_ids))])

    for i, tid in enumerate(trade_ids):
        trade_state = st.session_state.active_trades[tid]
        with tabs[i]:
            st.markdown(f"#### Working on: {tid}")
            ui.render_trade_setup(trade_state, tid)
            ui.render_trade_logger(trade_state, tid)
            ui.render_trade_live_log(trade_state, tid)


# Save session snapshot
config.save_snapshot({
    "balance": st.session_state.balance,
    "risk_percent": st.session_state.risk_percent,
    "max_open_risk": st.session_state.max_open_risk,
    "max_exposure": st.session_state.max_exposure
})

