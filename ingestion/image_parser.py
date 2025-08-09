# ingestion/image_parser.py
from PIL import Image
import pytesseract

def parse_image(path, lang=None):
    """
    path -> OCR text string.
    Make sure tesseract is installed in the system. If tesseract is not in PATH,
    set pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract" (or your path).
    """
    img = Image.open(path)
    # optionally convert to grayscale or run basic preprocessing here
    text = pytesseract.image_to_string(img, lang=lang) if lang else pytesseract.image_to_string(img)
    return text
