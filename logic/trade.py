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
