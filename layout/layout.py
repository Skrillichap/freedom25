import streamlit as st
from helpers.helpers import calculate_monetary_risk

def show_session_metrics():
    balance = st.session_state.get("balance", 0.0)
    risk_percent = st.session_state.get("risk_percent", 0.0)
    monetary_risk = calculate_monetary_risk(balance, risk_percent)
    st.session_state.monetary_risk = monetary_risk

    metrics_expanded = st.session_state.get("session_metrics_expanded", True)
    with st.expander("📊 Session Metrics Overview", expanded=metrics_expanded):

        # Centered large balance value (no label)
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 4rem; font-weight: 400; color: white; letter-spacing: 0.2rem;">
                    £{int(balance):,}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Row of calculated metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🎯 Risk per Trade (%)", f"{risk_percent:.2f}%")
        col2.metric("💷 MRPT (Monetary)", f"£{monetary_risk:,.2f}")
        col3.metric("📉 Max Open Risk", f"{st.session_state.max_open_risk:.2f}%")
        col4.metric("📈 Max Exposure", f"{st.session_state.max_exposure:.2f}%")

    st.session_state.session_metrics_expanded = metrics_expanded