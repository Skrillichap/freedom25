import streamlit as st
from helpers.helpers import calculate_monetary_risk

def show_session_metrics():
    balance = st.session_state.get("balance", 0.0)
    risk_percent = st.session_state.get("risk_percent", 0.0)
    monetary_risk = calculate_monetary_risk(balance, risk_percent)
    st.session_state.monetary_risk = monetary_risk

    st.subheader("🔍 Calculated Session Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Monetary Risk Per Trade", f"£{monetary_risk:,.2f}")
    col2.metric("Max Open Risk (%)", f"{st.session_state.max_open_risk:.2f}%")
    col3.metric("Max Exposure (%)", f"{st.session_state.max_exposure:.2f}%")
    st.markdown("---")
