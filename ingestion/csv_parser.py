# ingestion/csv_parser.py
import pandas as pd

def parse_csv(path, max_chars_per_row=2000):
    """
    For CSVs, create a text summary per row or join important columns.
    Returning a single string by joining rows can be okay for smaller CSVs.
    """
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    rows = []
    for i, row in df.iterrows():
        # Simple row-to-text conversion. Improve by selecting specific columns.
        text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
        if len(text) > max_chars_per_row:
            text = text[:max_chars_per_row] + "..."
        rows.append(f"Row {i}: {text}")
    return "\n".join(rows)
