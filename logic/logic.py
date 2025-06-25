from datetime import datetime
import os
import csv

def calculate_position_size(risk_amount, entry_price, stop_loss_price, max_capital):
    sl_distance = abs(entry_price - stop_loss_price)
    if sl_distance == 0:
        return 0, 0, 0

    ideal_size = risk_amount / sl_distance
    capital_required = ideal_size * entry_price

    if capital_required > max_capital:
        capped_size = max_capital / entry_price
        risk_at_capped = capped_size * sl_distance
        return capped_size, max_capital, risk_at_capped
    else:
        return ideal_size, capital_required, risk_amount

def log_trade(trade_data: dict, session_data: dict, decision: str):
    row = {
        "date": str(datetime.date.today()),
        "time": trade_data.get("time", ""),
        "decision": decision,
        "entry": trade_data["entry"],
        "stop": trade_data["stop"],
        "direction": trade_data["direction"],
        "position_size": trade_data["position_size"],
        "risk": trade_data["risk"],
        "capital_used": trade_data["capital_used"],
        "r_multiple": trade_data.get("r_multiple", ""),
        "take_profit": trade_data.get("take_profit", ""),
        "account_balance": session_data["balance"],
        "risk_per_trade": session_data["risk_per_trade"],
        "max_open_risk": session_data["max_open_risk"],
        "max_exposure": session_data["max_exposure"]
    }

    filepath = os.path.join("data", "trades.csv")
    file_exists = os.path.isfile(filepath)

    with open(filepath, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
