import json
from pathlib import Path

RANGE_FILE = Path(__file__).resolve().parent / "reference_ranges.json"
REFERENCE_RANGES = {}
if RANGE_FILE.exists():
    REFERENCE_RANGES = json.loads(RANGE_FILE.read_text(encoding="utf-8"))

def interpret_values(values: dict) -> dict:
    out = {}
    for name, data in values.items():
        val = data.get("value")
        ref = REFERENCE_RANGES.get(name)
        status = "unknown"
        note = ""
        if ref and isinstance(val, (int, float)):
            low = ref.get("low")
            high = ref.get("high")
            if low is not None and high is not None:
                if val < low:
                    status = "low"
                    note = ref.get("low_note", "Lower than expected range.")
                elif val > high:
                    status = "high"
                    note = ref.get("high_note", "Higher than expected range.")
                else:
                    status = "normal"
                    note = ref.get("normal_note", "")
            else:
                status = "reference missing"
        else:
            status = "no reference"
        out[name] = {
            "value": val,
            "range": ref if ref else None,
            "status": status,
            "note": note
        }
    return out
