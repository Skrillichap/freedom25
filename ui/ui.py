import streamlit as st
import layout.charts as charts
import logic.trade as trade
from datetime import datetime
from helpers.helpers import confidence_message
from logic.trade import calculate_trade_details
from helpers.labels import load_labels

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
            col1.metric(
                "💸 Capital Used", 
                f"£{details['capital_used']:,.2f} ({(details['capital_used'] / balance * 100):.2f}%)"
            )
            col2.metric(
                "⚠️ Risk", 
                f"£{details['risk']:,.2f} ({(details['risk'] / balance * 100):.2f}% / {st.session_state.risk_percent:.2f}%)"
            )

            # Exposure Summary
            total_exposure = sum(t.get("capital_used", 0) for t in st.session_state.active_trades.values())
            projected_exposure = total_exposure + details["capital_used"]
            max_exposure = (st.session_state.max_exposure / 100) * balance
            exposure_pct = (projected_exposure / balance) * 100

            st.markdown("### 📈 Exposure Summary")
            st.write(
                f"Projected Exposure: £{projected_exposure:,.2f} / £{max_exposure:,.2f} "
                f"({exposure_pct:.2f}% / {st.session_state.max_exposure:.2f}%)"
            )

            # Ideal Leverage
            actual_rpt = (details["risk"] / balance) * 100
            max_rpt = st.session_state.risk_percent

            if actual_rpt > 0:
                ideal_leverage = max_rpt / actual_rpt
                ideal_leverage_display = f"{ideal_leverage:.1f}×"
            else:
                ideal_leverage_display = "N/A"

            st.markdown("### 📏 Ideal Leverage")
            st.write(
                f"{ideal_leverage_display} to fully utilise your max risk per trade ({max_rpt:.2f}%)"
            )

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
                target_tp = st.number_input(f"🎯 Target Take Profit ({trade_id})", format="%.4f", key=f"{trade_id}_tp")
            with col2:
                actual_stop = st.number_input(f"📉 Actual Stop Loss ({trade_id})", format="%.4f", key=f"{trade_id}_actual_stop")
                entry_time = st.text_input(f"🕒 Time of Entry (HH:MM) ({trade_id})", value="09:30", key=f"{trade_id}_time")

            if st.button("✅ Confirm and Log Trade", key=f"{trade_id}_confirm"):
                data = trade_state["data"]
                capital_used = data.get("capital_used", 0)
                position_size = data.get("position_size", 0)
                balance = st.session_state.balance
                risk_percent = st.session_state.risk_percent

                sl_distance = abs(actual_entry - actual_stop)
                actual_risk = sl_distance * position_size if sl_distance > 0 else 0
                actual_rpt = (actual_risk / balance) * 100 if balance else 0
                ideal_leverage = risk_percent / actual_rpt if actual_rpt > 0 else 0

                trade_data = {
                    "entry_date": str(datetime.now().date()),
                    "entry_time": entry_time,
                    "actual_entry": actual_entry,
                    "actual_stop": actual_stop,
                    "target_tp": target_tp,
                    "contribution_pct": data.get("contribution_pct", 0),
                    "instrument": st.session_state.get(f"{trade_id}_instrument", "PLACEHOLDER"),
                    "balance": balance,
                    "position_size": position_size,
                    "capital_used": capital_used,
                    "risk": actual_risk,
                    "max_rpt": risk_percent,
                    "actual_rpt": actual_rpt,
                    "divergence": actual_rpt - risk_percent,
                    "ideal_leverage": round(ideal_leverage, 2)
                }

                try:
                    trade_id_logged = trade.log_trade_entry(trade_data)
                    trade_state["data"]["trade_id"] = trade_id_logged
                    trade_state["ready_to_log"] = False
                    trade_state["collapsed"]["step3"] = True
                    st.success(f"✅ Trade logged successfully (ID: {trade_id_logged})")
                except Exception as e:
                    st.error(f"❌ Failed to log trade: {e}")

    trade_state["collapsed"]["step3"] = not expanded


def render_trade_live_log(trade_state: dict, trade_id: str):
    expanded = not trade_state["collapsed"].get("step4", False)

    trade_id = trade_state["data"].get("trade_id")
    if not trade_id:
        st.warning("⚠️ Trade ID not found. Please log entry first in Step 3.")
        return

    with st.expander("📘 Step 4: Mid-Trade Notes", expanded=expanded):
        st.markdown("Use this section to document your mindset, strategy, and instrument.")

        col1, col2 = st.columns(2)
        labels = load_labels()

        mood_full = col1.selectbox(
            "😶 Mood", [""] + labels.get("moods", []),
            key=f"{trade_id}_mood"
        )
        mood = mood_full.split(" ", 1)[-1] if mood_full else ""
        strategy = col2.selectbox(
            "📐 Strategy", [""] + labels.get("strategies", []),
            key=f"{trade_id}_strategy"
        )
        instrument = st.text_input(
            "🎯 Instrument", key=f"{trade_id}_instrument"
        )
        notes = st.text_area(
            "📝 Notes", height=150, key=f"{trade_id}_notes"
        )

        submitted = st.button("🗂️ Save Mid-Trade Log", key=f"{trade_id}_log_live")

        if submitted:
            try:
                from logic.trade import update_trade_row
                update_trade_row(trade_id, {
                    "Mood": mood,
                    "Strategy": strategy,
                    "Instrument": instrument,
                    "Notes": notes
                })
                st.success("✅ Mid-trade details saved.")
                trade_state["collapsed"]["step4"] = True
            except Exception as e:
                st.error(f"❌ Failed to update trade log: {e}")

    # Preserve collapsed state
    trade_state["collapsed"]["step4"] = not expanded

def render_trade_exit_log(trade_state: dict, session_trade_id: str):
    expanded = not trade_state["collapsed"].get("step5", False)

    # Use trade ID from CSV (from Step 3)
    csv_trade_id = trade_state["data"].get("trade_id")
    if not csv_trade_id:
        st.warning("⚠️ Trade ID not found. Please log the entry in Step 3 first.")
        return

    with st.expander("✅ Step 5: Finalise Trade", expanded=expanded):
        st.markdown("Enter final trade outcomes including exit and reflections.")

        labels = load_labels()

        col1, col2 = st.columns(2)
        with col1:
            exit_price = st.number_input(f"📉 Exit Price ({csv_trade_id})", format="%.4f", key=f"{csv_trade_id}_exit_price")
            exit_time = st.text_input(f"⏱️ Exit Time (HH:MM)", value="16:00", key=f"{csv_trade_id}_exit_time")
        with col2:
            exit_reason = st.selectbox("🚪 Exit Reason", [""] + labels.get("exit_reasons", []), key=f"{csv_trade_id}_exit_reason")
            result = st.selectbox("📊 Result", ["Profit", "Loss", "Break-even"], key=f"{csv_trade_id}_result")

        col_notes1, col_notes2 = st.columns(2)
        what_went_well = col_notes1.text_area("✅ What went well?", height=120, key=f"{csv_trade_id}_went_well")
        what_to_improve = col_notes2.text_area("🔁 What would you do differently?", height=120, key=f"{csv_trade_id}_improve")
        closing_notes = st.text_area("📘 Closing Notes", height=100, key=f"{csv_trade_id}_closing_notes")

        if st.button("💾 Finalise and Save Trade", key=f"{csv_trade_id}_save_final"):
            try:
                # Get required details
                actual_entry = float(trade_state["data"].get("actual_entry", 0))
                position_size = float(trade_state["data"].get("position_size", 0))
                pnl = (float(exit_price) - actual_entry) * position_size if result == "Profit" else (float(exit_price) - actual_entry) * position_size
                r_multiple = abs(pnl / trade_state["data"].get("risk", 1)) if trade_state["data"].get("risk", 0) != 0 else 0
                r_multiple = round(r_multiple, 2)

                trade.update_trade_row(csv_trade_id, {
                    "Exit Price": exit_price,
                    "Exit Time": exit_time,
                    "Exit Reason": exit_reason,
                    "Result": result,
                    "P/L": round(pnl, 2),
                    "Final R-Multiple": r_multiple,
                    "What Went Well": what_went_well,
                    "What to Improve": what_to_improve,
                    "Closing Notes": closing_notes
                })
                st.success(f"✅ Trade finalised and saved successfully (ID: {csv_trade_id})")
                trade_state["collapsed"]["step5"] = True

            except Exception as e:
                st.error(f"❌ Failed to finalise trade: {e}")

    trade_state["collapsed"]["step5"] = not expanded

