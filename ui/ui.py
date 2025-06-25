import streamlit as st
import streamlit as st
import layout.charts as charts

from datetime import datetime
from logic.logic import calculate_position_size
from helpers.helpers import confidence_message

def session_config_panel():
    st.header("Step 1: Session Configuration")
    st.number_input("Account Balance (£)", key="balance", min_value=0.0, step=100.0, format="%.2f")
    st.number_input("Risk per Trade (%)", key="risk_percent", min_value=0.0, max_value=100.0, step=0.1, format="%.2f")
    st.number_input("Max Open Risk (%)", key="max_open_risk", min_value=0.0, max_value=100.0, step=0.1, format="%.2f")
    st.number_input("Max Exposure (%)", key="max_exposure", min_value=0.0, max_value=100.0, step=1.0, format="%.2f")
    st.markdown("---")


def render_trade_setup():
    st.header("Step 2: Trade Setup")

    st.subheader("Trade Inputs")
    col1, col2 = st.columns(2)
    entry = col1.number_input("Target Market Price", min_value=0.0, format="%.4f")
    stop = col2.number_input("Target Stop Loss", min_value=0.0, format="%.4f")

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
        max_exposure = (st.session_state.max_exposure/ 100) * balance
        exposure_pct = (projected_exposure / balance) * 100

        st.markdown("### 📈 Exposure Summary")
        st.write(f"Projected Exposure: £{projected_exposure:,.2f} / £{max_exposure:,.2f} ({exposure_pct:.2f}%)")

        if projected_exposure > max_exposure:
            st.error("❌ This trade would exceed your max allowed exposure.")
        elif contribution_pct > 20:
            st.warning("⚠️ This is above your soft confidence threshold (20%)")
            
        # --- R-Multiple Chart ---
        st.markdown("### 📊 R-Multiple Analysis")

        fig = charts.plot_r_multiple_analysis(st.session_state.prospective_trade, balance)
        st.plotly_chart(fig, use_container_width=True)

def render_trade_logger():
    st.markdown("### 📝 Trade Journal Logging")

    if "trade_logged" not in st.session_state:
        st.session_state.trade_logged = False
    if "trade_decision" not in st.session_state:
        st.session_state.trade_decision = None

    # Disable buttons after log
    enter_disabled = st.session_state.trade_logged
    missed_disabled = st.session_state.trade_logged

    col1, col2, col3 = st.columns([2, 2, 3])

    with col1:
        if st.button("📥 Enter Trade", use_container_width=True, disabled=enter_disabled):
            st.session_state.trade_logged = True
            st.session_state.trade_decision = "entered"

    with col2:
        if st.button("❌ Missed Trade", use_container_width=True, disabled=missed_disabled):
            st.session_state.trade_logged = True
            st.session_state.trade_decision = "missed"

    with col3:
        st.time_input("🕒 Trade Time", value=datetime.now().time(), key="trade_time", disabled=st.session_state.trade_logged)

    if st.session_state.trade_logged:
        decision = "ENTERED" if st.session_state.trade_decision == "entered" else "MISSED"
        st.success(f"Trade marked as **{decision}** at {st.session_state.trade_time.strftime('%H:%M:%S')}")

