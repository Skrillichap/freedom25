import streamlit as st
from logic.logic import calculate_position_size
from helpers.helpers import confidence_message

def session_config_panel():
    st.header("Step 1: Session Configuration")
    st.number_input("Account Balance (£)", key="balance", min_value=0.0, step=100.0, format="%.2f")
    st.number_input("Risk per Trade (%)", key="risk_percent", min_value=0.0, max_value=100.0, step=0.1, format="%.2f")
    st.number_input("Max Exposure (%)", key="max_exposure_pct", min_value=0.0, max_value=100.0, step=1.0, format="%.2f")
    st.markdown("---")

def render_trade_setup():
    st.header("Step 2: Trade Setup")

    st.subheader("Trade Inputs")
    col1, col2 = st.columns(2)
    entry = col1.number_input("Current Market Price", min_value=0.0, format="%.4f")
    stop = col2.number_input("Planned Stop Loss", min_value=0.0, format="%.4f")

    contribution_pct = st.slider("Capital Allocation (% of balance)", 0, 25, 10, 1)
    st.caption(confidence_message(contribution_pct))

    if entry > 0 and stop > 0:
        balance = st.session_state.balance
        max_capital = (contribution_pct / 100.0) * balance
        risk = st.session_state.monetary_risk

        size, capital_used, actual_risk = calculate_position_size(risk, entry, stop, max_capital)
        direction = "Long" if stop < entry else "Short"

        st.session_state.prospective_trade = {
            "entry": entry,
            "stop": stop,
            "contribution_pct": contribution_pct,
            "direction": direction,
            "position_size": size,
            "capital_used": capital_used,
            "risk": actual_risk
        }

        st.markdown("---")
        st.subheader("🧮 Calculated Trade Details")
        col1, col2 = st.columns(2)
        col1.metric("📉 Direction", direction)
        col2.metric("📊 Position Size", f"{size:,.2f} units")

        col1.metric("💸 Capital Used", f"£{capital_used:,.2f} ({(capital_used / balance * 100):.2f}%)")
        col2.metric("⚠️ Risk", f"£{actual_risk:,.2f} ({(actual_risk / balance * 100):.2f}%)")

        total_exposure = sum(t["capital_used"] for t in st.session_state.open_trades)
        projected_exposure = total_exposure + capital_used
        max_exposure = (st.session_state.max_exposure_pct / 100) * balance
        exposure_pct = (projected_exposure / balance) * 100

        st.markdown("### 📈 Exposure Summary")
        st.write(f"Projected Exposure: £{projected_exposure:,.2f} / £{max_exposure:,.2f} ({exposure_pct:.2f}%)")

        if projected_exposure > max_exposure:
            st.error("❌ This trade would exceed your max allowed exposure.")
        elif contribution_pct > 20:
            st.warning("⚠️ This is above your soft confidence threshold (20%)")
