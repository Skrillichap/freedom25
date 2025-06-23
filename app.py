import streamlit as st
from config.config import initialize_session_state, get_initial_session_state, save_snapshot
from ui.ui import session_config_panel, render_trade_setup
from layout.layout import show_session_metrics

# Init Streamlit session state
initialize_session_state()
if "initialized" not in st.session_state:
    initial = get_initial_session_state()
    for k, v in initial.items():
        st.session_state[k] = v
    st.session_state.initialized = True

# Page config
st.set_page_config(page_title="Freedom 25", layout="centered")
st.title("🧮 Freedom 25 — Trade Journal")

# UI rendering
session_config_panel()
show_session_metrics()
render_trade_setup()

# Save snapshot
save_snapshot({
    "balance": st.session_state.balance,
    "risk_percent": st.session_state.risk_percent,
    "max_exposure_pct": st.session_state.max_exposure_pct
})
