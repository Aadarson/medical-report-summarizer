from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil, time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your modules
try:
    from backend.ocr_module import extract_text_from_file
    from backend.parser import parse_key_values
    from backend.interpreter import interpret_values
    from backend.openai_client import generate_summary_with_openai
except ImportError:
    from ocr_module import extract_text_from_file
    from parser import parse_key_values
    from interpreter import interpret_values
    from openai_client import generate_summary_with_openai

app = FastAPI(title="Medical Report Summarizer")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

FRONTEND_DIR = BASE_DIR.parent / "frontend"

# ✅ Serve frontend static files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ✅ Serve index.html
@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

# ✅ Serve favicon.ico
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = FRONTEND_DIR / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return FileResponse(FRONTEND_DIR / "index.html")  # fallback

# Upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), prefer_ai: str = Form("true")):
    prefer_ai = prefer_ai.lower() in ("true", "1", "yes", "on")
    timestamp = int(time.time())
    dest = UPLOAD_DIR / f"{timestamp}_{file.filename}"

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text
    extracted_text = extract_text_from_file(str(dest))
    values = parse_key_values(extracted_text)
    interpreted = interpret_values(values)

    # AI summary
    summary = generate_summary_with_openai(values, interpreted) if prefer_ai else None

    # Fallback summary (patient-friendly)
    if not summary:
        lines = ["<h3>Summary of your report:</h3>", "<ul>"]
        if not interpreted:
            lines.append("<li>⚠️ No lab values could be confidently extracted.</li>")
        else:
            for test, info in interpreted.items():
                val = info.get("value", "—")
                status = info.get("status", "unknown")
                note = info.get("note", "")

                if status == "high":
                    lines.append(f"<li>{test}: {val} → High. {note or 'Above the normal range.'}</li>")
                elif status == "low":
                    lines.append(f"<li>{test}: {val} → Low. {note or 'Below the normal range.'}</li>")
                elif status == "normal":
                    lines.append(f"<li>{test}: {val} → Normal.</li>")
                else:  # unknown reference
                    lines.append(f"<li>{test}: {val} → Reference range not available. {note or 'Consult your doctor for interpretation.'}</li>")

        lines.append("</ul>")
        summary = "".join(lines)

    return JSONResponse({
        "values": values,
        "interpreted": interpreted,
        "summary": summary
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
