# ingestion/pdf_parser.py
import pdfplumber

def parse_pdf(path):
    """
    Extract text from each page and return a single combined string.
    You can also return page-wise texts if you want to store page metadata.
    """
    texts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            texts.append(txt)
    return "\n\n".join(texts)
