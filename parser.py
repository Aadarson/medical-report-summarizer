import re
import json
from pathlib import Path

# ----------------------------
# Load reference ranges safely
# ----------------------------
RANGE_FILE = Path(__file__).resolve().parent / "reference_ranges.json"
REFERENCE_RANGES = {}

if RANGE_FILE.exists():
    try:
        with RANGE_FILE.open(encoding="utf-8-sig") as f:
            REFERENCE_RANGES = json.load(f)
        print("Loaded reference ranges:", len(REFERENCE_RANGES), "tests")  # optional debug
    except json.JSONDecodeError as e:
        print(f"Error loading JSON: {e}")
else:
    print(f"Reference file not found: {RANGE_FILE}")

# ----------------------------
# Regex patterns for parsing
# ----------------------------
NUMBER_PATTERN = r"-?\d{1,3}(?:[\,\.]\d+)?"
LINE_PATTERN = re.compile(
    rf"(?P<name>[A-Za-z0-9\-\s\/\(\)\.]+?)\s*[:\t\s]\s*(?P<value>{NUMBER_PATTERN})\b",
    re.IGNORECASE
)

# ----------------------------
# Parsing function
# ----------------------------
def parse_key_values(text: str) -> dict:
    values = {}
    if not text:
        return values

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = LINE_PATTERN.search(line)
        if m:
            name = m.group("name").strip()
            name_norm = " ".join(name.split())  # normalize spaces
            val_raw = m.group("value").replace(",", ".")
            try:
                val = float(val_raw)
            except ValueError:
                continue
            values[name_norm] = {"value": val}

    # Normalize keys to reference names using exact match or aliases
    lower_map = {k.lower(): k for k in REFERENCE_RANGES.keys()}
    final = {}

    for k, v in values.items():
        key_l = k.lower()
        canonical = None

        # 1) Exact match
        if key_l in lower_map:
            canonical = lower_map[key_l]
        else:
            # 2) Match aliases
            for ref_name, ref_info in REFERENCE_RANGES.items():
                aliases = [a.lower() for a in ref_info.get("aliases", [])]
                if key_l in aliases:
                    canonical = ref_name
                    break
            # 3) Partial / substring match
            if not canonical:
                for ref_name, ref_info in REFERENCE_RANGES.items():
                    ref_l = ref_name.lower()
                    if ref_l in key_l or key_l in ref_l:
                        canonical = ref_name
                        break

        final_name = canonical if canonical else k
        final[final_name] = v

    return final
