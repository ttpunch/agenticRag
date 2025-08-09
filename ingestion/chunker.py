# ingestion/chunker.py
import re

def sentence_split(text):
    # naive sentence splitter — can replace with nltk/spacy if desired
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(text, chunk_size=800, overlap=100, prefer_sentence_boundary=True):
    """
    Create overlapping chunks. If prefer_sentence_boundary is True, try to avoid
    splitting sentences by accumulating sentences until chunk_size.
    """
    if not prefer_sentence_boundary:
        chunks = []
        start = 0
        n = len(text)
        while start < n:
            end = min(start + chunk_size, n)
            chunks.append(text[start:end].strip())
            start = max(0, end - overlap)
        return chunks

    sentences = sentence_split(text)
    chunks = []
    current = []
    current_len = 0
    for s in sentences:
        s_len = len(s) + 1
        if current_len + s_len <= chunk_size:
            current.append(s)
            current_len += s_len
        else:
            if current:
                chunks.append(" ".join(current).strip())
            # start new chunk with current sentence (if it is huge, we still include it)
            current = [s]
            current_len = s_len
    if current:
        chunks.append(" ".join(current).strip())

    # Add overlap by joining tail of previous chunk to head of next if needed.
    if overlap > 0 and len(chunks) > 1:
        out = []
        for i, c in enumerate(chunks):
            if i == 0:
                out.append(c)
                continue
            prev = out[-1]
            # ensure overlap characters exist:
            if len(prev) > overlap:
                # overlap_tail = last N chars of prev
                overlap_tail = prev[-overlap:]
                new_chunk = overlap_tail + " " + c
            else:
                new_chunk = prev + " " + c
            out.append(new_chunk)
        return out
    return chunks
