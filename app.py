import streamlit as st
import config.config as config
import ui.ui as ui
import layout.layout as layout
import logic.trade as trade
from datetime import datetime

# Init Streamlit session state
config.initialize_session_state()
if "initialized" not in st.session_state:
    initial = config.get_initial_session_state()
    for k, v in initial.items():
        st.session_state[k] = v
    st.session_state.initialized = True

# Page config
st.set_page_config(page_title="Freedom 25", layout="centered")
st.title("🧮 Freedom 25 — Trade Journal")

# UI rendering
ui.session_config_panel()
layout.show_session_metrics()
ui.render_trade_setup()
ui.render_trade_logger()


# Save snapshot
config.save_snapshot({
    "balance": st.session_state.balance,
    "risk_percent": st.session_state.risk_percent,
    "max_open_risk": st.session_state.max_open_risk,
    "max_exposure": st.session_state.max_exposure
})