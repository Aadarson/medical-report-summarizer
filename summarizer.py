from parser import parse_text

def summarize_text(text):
    """
    Generate a summary from parsed text
    """
    parsed_data = parse_text(text)
    summary = {}

    if parsed_data["medications"]:
        summary["medications"] = parsed_data["medications"]
    if parsed_data["observed_values"]:
        summary["observed_values"] = parsed_data["observed_values"]

    return summary
