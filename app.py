import streamlit as st
from config.config import initialize_session_state, get_initial_session_state, save_snapshot
import ui.ui as ui
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
ui.session_config_panel()
show_session_metrics()
ui.render_trade_setup()
ui.render_trade_logger()


# Save snapshot
save_snapshot({
    "balance": st.session_state.balance,
    "risk_percent": st.session_state.risk_percent,
    "max_open_risk": st.session_state.max_open_risk,
    "max_exposure": st.session_state.max_exposure
})

