import streamlit as st
import streamlit as st
import layout.charts as charts
import logic.trade as trade

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
    st.subheader("📥 Trade Logger")

    if st.button("📥 Enter Trade"):
        # Lock in the live values at the moment of click
        live_data = st.session_state.prospective_trade.copy()

        st.session_state.trade_log_snapshot = {
            "contribution_pct": live_data.get("contribution_pct"),
            "position_size": live_data.get("position_size"),
            "capital_used": live_data.get("capital_used"),
            "risk": live_data.get("risk")
        }

        st.session_state.trade_ready_to_log = True
        st.success("Trade marked for logging. Input exact trade data below.")

    if st.session_state.get("trade_ready_to_log"):
        col1, col2 = st.columns(2)
        with col1:
            actual_entry = st.number_input("📈 Actual Entry Price", format="%.4f")
            actual_stop = st.number_input("📉 Actual Stop Loss", format="%.4f")
        with col2:
            target_tp = st.number_input("🎯 Target Take Profit", format="%.4f")
            entry_time = st.text_input("🕒 Time of Entry (HH:MM)", value="09:30")

        confirm = st.button("✅ Confirm and Log Trade")

        if confirm:
            snapshot = st.session_state.trade_log_snapshot

            trade_data = {
                "entry_date": str(datetime.now().date()),
                "entry_time": entry_time,
                "actual_entry": actual_entry,
                "actual_stop": actual_stop,
                "target_tp": target_tp,
                "contribution_pct": snapshot["contribution_pct"],
                "position_size": snapshot["position_size"],
                "capital_used": snapshot["capital_used"],
                "risk": snapshot["risk"]
            }

            try:
                trade.log_trade_entry(trade_data)
                st.success("✅ Trade logged successfully.")
                st.session_state.trade_ready_to_log = False
                del st.session_state.trade_log_snapshot
            except Exception as e:
                st.error(f"❌ Failed to log trade: {e}")