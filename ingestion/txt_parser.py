# ingestion/txt_parser.py
def parse_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
