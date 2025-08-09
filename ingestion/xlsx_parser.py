# ingestion/xlsx_parser.py
import pandas as pd

def parse_xlsx(path, sheet_name=None, max_chars_per_row=2000):
    df = pd.read_excel(path, sheet_name=sheet_name, dtype=str, keep_default_na=False)
    rows = []
    for i, row in df.iterrows():
        text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
        if len(text) > max_chars_per_row:
            text = text[:max_chars_per_row] + "..."
        rows.append(f"Row {i}: {text}")
    return "\n".join(rows)
