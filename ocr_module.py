import easyocr

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

def extract_text(image_path):
    """
    Extracts text from image using EasyOCR
    """
    try:
        results = reader.readtext(image_path, detail=0)
        text = " ".join(results)
        return text
    except Exception as e:
        print(f"Error extracting text from {image_path}: {e}")
        return ""
