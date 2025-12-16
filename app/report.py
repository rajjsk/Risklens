import json
from pathlib import Path

def save_report(report: dict, out_dir: str, basename: str):
    """
    Saves the contract analysis report as a JSON file
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out_json = Path(out_dir)/f"{basename}_report.json"
    with open(out_json, 'w') as f:
        json.dump(report, f, indent=2)
    return str(out_json)
