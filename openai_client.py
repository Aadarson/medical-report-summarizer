import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file (make sure it's in backend/ or project root)
load_dotenv()

# Try both .env and system env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found. Please set it in your .env file or environment.")

# Initialize client
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_summary_with_openai(values: dict, interpreted: dict) -> Optional[str]:
    """
    Use OpenAI to generate a patient-friendly medical summary.
    Handles both known reference ranges and unknown values.
    """
    try:
        tests_text = []
        for test, info in interpreted.items():
            value = info.get("value", "N/A")
            status = info.get("status", "unknown")
            note = info.get("note", "")
            rng = info.get("range", {})

            if rng:
                ref_range = f"{rng.get('low','?')} - {rng.get('high','?')} {rng.get('units','')}".strip()
            else:
                ref_range = "Not available"

            tests_text.append(f"{test}: {value} (Normal range: {ref_range}) → {status}. {note}")

        # Add raw values too (covers cases where reference was missing entirely)
        raw_text = []
        for test, val in values.items():
            if test not in interpreted:  # not mapped / no ref
                raw_text.append(f"{test}: {val} (Reference not available)")

        structured_text = "\n".join(tests_text + raw_text)

        prompt = f"""
        Convert the following lab results into a simple, clear medical summary
        for patients in plain English:

        {structured_text}

        Please include:
        - An overall impression (e.g., mostly normal, or some concerns).
        - Bullet points for abnormal values (explain what it means in everyday language).
        - For results without reference ranges, explain what the test generally measures and
          suggest why consulting a doctor is useful.
        - Keep tone reassuring, not alarming.
        - Always advise consulting a doctor.
        - Use bullet points and short sentences.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful medical explainer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5,
        )

        summary = response.choices[0].message.content.strip()

        # Format for frontend display
        summary = summary.replace("•", "<br>• ")
        summary = summary.replace("\n", "<br>")

        return summary

    except Exception as e:
        print("OpenAI call failed:", e)
        return None
