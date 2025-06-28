import os
import csv
from datetime import datetime

def frange(start, stop, step):
    while start <= stop:
        yield round(start, 10)
        start += step

def infer_direction(entry, stop):
    return "Long" if stop < entry else "Short"

def calculate_trade_details(entry, stop, contribution_pct, balance, target_tp=None, monetary_risk=None):
    direction = infer_direction(entry, stop)
    sl_distance = abs(entry - stop)
    contribution_pct = float(contribution_pct)
    capital_allocation = round(balance * (contribution_pct / 100), 2)

    position_size = round(capital_allocation / entry, 2) if entry != 0 else 0
    capital_used = round(position_size * entry, 2)
    risk = round(sl_distance * position_size, 2)

    r_multiple = None
    if target_tp is not None and sl_distance > 0:
        r_multiple = round(abs(target_tp - entry) / sl_distance, 2)

    return {
        "direction": direction,
        "sl_distance": sl_distance,
        "position_size": position_size,
        "capital_used": capital_used,
        "risk": risk,
        "r_multiple": r_multiple
    }

def log_trade_entry(trade_data, balance=10000):
    file_path = "data/trades.csv"
    headers = [
        "ID", "Date", "Time", "Instrument",
        "Actual Entry", "Actual Stop", "Target TP",
        "Capital Allocation (%)", "Position Size",
        "£ Used", "£ Risk", "R-Multiple"
    ]

    # Generate unique ID
    date_str = datetime.now().strftime("%d%m%Y")
    time_str = trade_data["entry_time"].replace(":", "")
    trade_count = 1

    if os.path.exists(file_path):
        with open(file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            trade_count = sum(1 for row in reader if row.get("Date") == trade_data["entry_date"]) + 1

    trade_id = f"{date_str}-{time_str}-{trade_count:05d}"

    # Calculate values
    calc = calculate_trade_details(
        entry=float(trade_data["actual_entry"]),
        stop=float(trade_data["actual_stop"]),
        contribution_pct=float(trade_data["contribution_pct"]),
        balance=balance,
        target_tp=float(trade_data["target_tp"])
    )

    row = [
        trade_id,
        trade_data["entry_date"],
        trade_data["entry_time"],
        "PLACEHOLDER",
        trade_data["actual_entry"],
        trade_data["actual_stop"],
        trade_data["target_tp"],
        trade_data["contribution_pct"],
        calc["position_size"],
        calc["capital_used"],
        calc["risk"],
        calc["r_multiple"]
    ]

    write_headers = not os.path.exists(file_path) or os.stat(file_path).st_size == 0

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_headers:
            writer.writerow(headers)
        writer.writerow(row)

def update_trade_row(trade_id: str, updates: dict, file_path="data/trades.csv"):
    """Update existing trade row identified by trade_id with new fields."""
    import csv
    import os
    import tempfile

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist")

    updated = False
    temp_fd, temp_path = tempfile.mkstemp()
    os.close(temp_fd)

    with open(file_path, "r", newline="", encoding="utf-8") as infile, \
         open(temp_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or []
        
        # Ensure all update keys are in the header
        for k in updates.keys():
            if k not in fieldnames:
                fieldnames.append(k)

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if row.get("ID") == trade_id:
                row.update(updates)
                updated = True
            writer.writerow(row)

    os.replace(temp_path, file_path)

    if not updated:
        raise ValueError(f"Trade ID {trade_id} not found in {file_path}")
