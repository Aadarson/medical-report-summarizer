import os
import re
from pathlib import Path
import pytesseract
from PIL import Image
import pdfplumber

# If you set TESSERACT_CMD in .env, use it
TESSERACT_CMD = os.environ.get("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
PDF_EXT = {'.pdf'}

def extract_text_from_file(path: str) -> str:
    path = Path(path)
    ext = path.suffix.lower()
    text = ""

    if ext in PDF_EXT:
        # First try extracting selectable text
        try:
            with pdfplumber.open(path) as pdf:
                pages_text = []
                for p in pdf.pages:
                    t = p.extract_text() or ""
                    pages_text.append(t)
                text = "\n".join(pages_text).strip()
        except Exception as e:
            print("pdfplumber text extract failed:", e)
            text = ""

        # If text empty, OCR each page image
        if not text.strip():
            try:
                with pdfplumber.open(path) as pdf:
                    page_texts = []
                    for p in pdf.pages:
                        pil = p.to_image(resolution=200).original  # PIL image
                        page_texts.append(pytesseract.image_to_string(pil))
                    text = "\n".join(page_texts)
            except Exception as e:
                print("pdf OCR fallback failed:", e)

    elif ext in IMAGE_EXT:
        try:
            img = Image.open(path)
            text = pytesseract.image_to_string(img)
        except Exception as e:
            print("image OCR failed:", e)
            text = ""
    else:
        # try as plain text file
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            print("text read failed:", e)
            text = ""

    # Normalize
    text = re.sub(r"\r\n|\r", "\n", text)
    return text
