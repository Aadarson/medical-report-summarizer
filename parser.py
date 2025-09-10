import re

# Define common medical keywords for extraction
MEDICAL_KEYWORDS = [
    'blood pressure', 'glucose', 'hb', 'cholesterol', 'uric acid',
    'hba1c', 'medication', 'mg', 'dose', 'observed value'
]

def parse_text(text):
    """
    Parse text to extract medical measurements and medications
    """
    text_lower = text.lower()
    medications = re.findall(r'\d+\.?\d*\s*mg', text_lower)
    observed_values = []

    for keyword in MEDICAL_KEYWORDS:
        matches = re.findall(rf'{keyword}[:\s]*[0-9/.\-]*', text_lower)
        observed_values.extend(matches)

    return {
        "medications": medications,
        "observed_values": observed_values
    }
