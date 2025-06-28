# helpers/labels.py
import json
import os

def load_labels(file_path="config/labels.json"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Label file not found at {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
