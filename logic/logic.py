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
