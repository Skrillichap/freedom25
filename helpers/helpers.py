import streamlit as st
from datetime import datetime

def generate_trade_id():
    return datetime.now().strftime("%d%m%Y_%H%M%S")

def calculate_monetary_risk(balance, risk_percent):
    return (risk_percent / 100.0) * balance

def confidence_message(percent):
    if percent <= 5:
        return "🟢 Cautious – exploratory setup"
    elif percent <= 10:
        return "🟡 Low conviction – testing waters"
    elif percent <= 15:
        return "🟠 Moderate confidence – solid reasoning"
    elif percent <= 20:
        return "🔴 High confidence – well-researched"
    else:
        return "🔥 Extreme conviction – ensure tight risk!"
    
