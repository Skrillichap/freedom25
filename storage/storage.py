import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TRADES_CSV = os.path.join(DATA_DIR, 'trades.csv')

def save_trade(trade_dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    df = pd.DataFrame([trade_dict])
    if not os.path.exists(TRADES_CSV):
        df.to_csv(TRADES_CSV, index=False)
    else:
        df.to_csv(TRADES_CSV, mode='a', header=False, index=False)
