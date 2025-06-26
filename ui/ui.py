import streamlit as st
import layout.charts as charts
import logic.trade as trade
from datetime import datetime
from helpers.helpers import confidence_message
from logic.trade import calculate_trade_details

def session_config_panel():
    expanded = not st.session_state.get("session_config_collapsed", False)

    with st.expander("⚙️ Session Configuration", expanded=expanded):
        st.number_input("Account Balance (£)", key="balance", min_value=0.0, step=100.0, format="%.2f")
        st.number_input("Risk per Trade (%)", key="risk_percent", min_value=0.0, max_value=100.0, step=0.1, format="%.2f")
        st.number_input("Max Open Risk (%)", key="max_open_risk", min_value=0.0, max_value=100.0, step=0.1, format="%.2f")
        st.number_input("Max Exposure (%)", key="max_exposure", min_value=0.0, max_value=100.0, step=1.0, format="%.2f")
        st.markdown("---")

def render_trade_setup(trade_state: dict, trade_id: str):
    expanded = not trade_state["collapsed"].get("step2", False)
    with st.expander("📌 Step 2: Trade Setup", expanded=expanded):
        col1, col2 = st.columns(2)
        entry = col1.number_input(f"Target Market Price ({trade_id})", min_value=0.0, format="%.4f", key=f"{trade_id}_entry")
        stop = col2.number_input(f"Target Stop Loss ({trade_id})", min_value=0.0, format="%.4f", key=f"{trade_id}_stop")
        contribution_pct = st.slider(f"Capital Allocation (% of balance) ({trade_id})", 0, 25, 10, 1, key=f"{trade_id}_contribution")

        st.caption(confidence_message(contribution_pct))

        trade_state["data"]["entry"] = entry
        trade_state["data"]["stop"] = stop
        trade_state["data"]["contribution_pct"] = contribution_pct

        if entry > 0 and stop > 0:
            balance = st.session_state.balance
            details = calculate_trade_details(
                entry=entry,
                stop=stop,
                contribution_pct=contribution_pct,
                balance=balance,
                monetary_risk=st.session_state.monetary_risk
            )
            trade_state["data"].update(details)

            st.markdown("### 🧮 Calculated Trade Details")
            col1, col2 = st.columns(2)
            col1.metric("📉 Direction", details["direction"])
            col2.metric("📊 Position Size", f"{details['position_size']:,.2f} units")
            col1.metric("💸 Capital Used", f"£{details['capital_used']:,.2f}")
            col2.metric("⚠️ Risk", f"£{details['risk']:,.2f}")

            total_exposure = sum(t.get("capital_used", 0) for t in st.session_state.active_trades.values())
            projected_exposure = total_exposure + details["capital_used"]
            max_exposure = (st.session_state.max_exposure / 100) * balance
            exposure_pct = (projected_exposure / balance) * 100

            st.markdown("### 📈 Exposure Summary")
            st.write(f"Projected Exposure: £{projected_exposure:,.2f} / £{max_exposure:,.2f} ({exposure_pct:.2f}%)")

            if projected_exposure > max_exposure:
                st.error("❌ This trade would exceed your max allowed exposure.")
            elif contribution_pct > 20:
                st.warning("⚠️ This is above your soft confidence threshold (20%)")

            st.markdown("### 📊 R-Multiple Analysis")
            fig = charts.plot_r_multiple_analysis(trade_state["data"], balance)
            st.plotly_chart(fig, use_container_width=True)

    trade_state["collapsed"]["step2"] = not expanded

def render_trade_logger(trade_state: dict, trade_id: str):
    expanded = not trade_state["collapsed"].get("step3", True)
    with st.expander("📝 Step 3: Log Trade Entry", expanded=expanded):
        if st.button("📥 Enter Trade", key=f"{trade_id}_enter"):
            trade_state["ready_to_log"] = True
            st.success("Trade marked for logging. Input execution details below.")

        if trade_state.get("ready_to_log"):
            col1, col2 = st.columns(2)
            with col1:
                actual_entry = st.number_input(f"📈 Actual Entry Price ({trade_id})", format="%.4f", key=f"{trade_id}_actual_entry")
                actual_stop = st.number_input(f"📉 Actual Stop Loss ({trade_id})", format="%.4f", key=f"{trade_id}_actual_stop")
            with col2:
                target_tp = st.number_input(f"🎯 Target Take Profit ({trade_id})", format="%.4f", key=f"{trade_id}_tp")
                entry_time = st.text_input(f"🕒 Time of Entry (HH:MM) ({trade_id})", value="09:30", key=f"{trade_id}_time")

            if st.button("✅ Confirm and Log Trade", key=f"{trade_id}_confirm"):
                data = trade_state["data"]
                trade_data = {
                    "entry_date": str(datetime.now().date()),
                    "entry_time": entry_time,
                    "actual_entry": actual_entry,
                    "actual_stop": actual_stop,
                    "target_tp": target_tp,
                    "contribution_pct": data.get("contribution_pct", 0)
                }

                try:
                    trade.log_trade_entry(trade_data, balance=st.session_state.balance)
                    st.success("✅ Trade logged successfully.")
                    trade_state["ready_to_log"] = False
                except Exception as e:
                    st.error(f"❌ Failed to log trade: {e}")

    trade_state["collapsed"]["step3"] = not expanded
