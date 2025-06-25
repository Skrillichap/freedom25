import os
import csv
from datetime import datetime

def frange(start, stop, step):
    while start <= stop:
        yield round(start, 10)
        start += step

def infer_direction(entry, stop_loss):
    return "Long" if stop_loss < entry else "Short"

def calculate_ideal_position_size(monetary_risk, sl_distance):
    if sl_distance == 0:
        return 0
    return monetary_risk / sl_distance

def capital_required(position_size, price):
    return position_size * price

def log_trade_entry(trade_data, balance=10000):
    file_path = "data/trades.csv"
    headers = [
        "ID", "Date", "Time", "Instrument",
        "Actual Entry", "Actual Stop", "Target TP",
        "Capital Allocation (%)", "Position Size",
        "£ Used", "£ Risk", "R-Multiple"
    ]

    # Generate unique trade ID
    date_str = datetime.now().strftime("%d%m%Y")
    time_str = trade_data["entry_time"].replace(":", "")
    trade_count = 1

    if os.path.exists(file_path):
        with open(file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            trade_count = sum(1 for row in reader if row.get("Date") == trade_data["entry_date"]) + 1

    trade_id = f"{date_str}-{time_str}-{trade_count:05d}"

    # Extract actuals
    actual_entry = float(trade_data["actual_entry"])
    actual_stop = float(trade_data["actual_stop"])
    target_tp = float(trade_data["target_tp"])
    contribution_pct = float(trade_data["contribution_pct"])

    # Use recalculated values with actual inputs
    capital_used = round(balance * (contribution_pct / 100), 2)
    sl_distance = abs(actual_entry - actual_stop)
    position_size = round(capital_used / sl_distance, 2)
    risk = round(sl_distance * position_size, 2)
    r_multiple = round(abs(target_tp - actual_entry) / sl_distance, 2)

    row = [
        trade_id,
        trade_data["entry_date"],
        trade_data["entry_time"],
        "PLACEHOLDER",
        actual_entry,
        actual_stop,
        target_tp,
        contribution_pct,
        position_size,
        capital_used,
        risk,
        r_multiple
    ]

    # Write header if new or empty file
    write_headers = not os.path.exists(file_path) or os.stat(file_path).st_size == 0

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_headers:
            writer.writerow(headers)
        writer.writerow(row)