import os
import json

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SNAPSHOT_PATH = os.path.join(CONFIG_DIR, 'snapshot.json')

def load_snapshot():
    if not os.path.exists(SNAPSHOT_PATH):
        return {
            "balance": 0.0,
            "risk_percent": 1.0,
            "max_exposure_pct": 50.0
        }
    with open(SNAPSHOT_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_snapshot(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(SNAPSHOT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def get_initial_session_state():
    snapshot = load_snapshot()
    return {
        "balance": snapshot.get("balance", 0.0),
        "risk_percent": snapshot.get("risk_percent", 1.0),
        "max_exposure_pct": snapshot.get("max_exposure_pct", 50.0),
        "monetary_risk": 0.0,
        "open_risk": 0.0,
        "max_open_risk": 3.0,
        "trades": [],
        "trade_counter": 0,
        "open_trades": [],
        "prospective_trade": None,
    }

def initialize_session_state():
    import streamlit as st
    defaults = get_initial_session_state()
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
