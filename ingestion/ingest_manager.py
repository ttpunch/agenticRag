# ingestion/ingest_manager.py
import os
from pathlib import Path
from .txt_parser import parse_txt
from .pdf_parser import parse_pdf
from .csv_parser import parse_csv
from .xlsx_parser import parse_xlsx
from .image_parser import parse_image
from .chunker import chunk_text
from vectorstore.qdrant_client import QdrantWrapper
from embeddings import EmbeddingClient
import uuid
from tqdm import tqdm

# Import from central config
from config.settings import CHUNK_SIZE as DEFAULT_CHUNK_SIZE, CHUNK_OVERLAP as DEFAULT_OVERLAP

EXT_TO_PARSER = {
    ".txt": parse_txt,
    ".pdf": parse_pdf,
    ".csv": parse_csv,
    ".xlsx": parse_xlsx,
    ".xls": parse_xlsx,
    ".png": parse_image,
    ".jpg": parse_image,
    ".jpeg": parse_image,
    ".tif": parse_image,
    ".tiff": parse_image,
}

def parse_file(path):
    ext = Path(path).suffix.lower()
    parser = EXT_TO_PARSER.get(ext)
    if not parser:
        raise ValueError(f"No parser for extension: {ext}")
    # image parser may need different signature; we keep it simple
    return parser(path)

def ingest_path(path, qdrant: QdrantWrapper, embedder: EmbeddingClient, 
                chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP,
                collection=None, store_text_in_payload=True):
    """
    Ingests a single file path (file or directory). Returns number of chunks inserted.
    """
    p = Path(path)
    if p.is_dir():
        return ingest_folder(str(p), qdrant, embedder, chunk_size, overlap,
                             collection, store_text_in_payload)

    # parse file to text
    try:
        text = parse_file(str(p))
    except Exception as e:
        print(f"[ingest] Failed to parse {path}: {e}")
        return 0

    if not text or not text.strip():
        print(f"[ingest] No text extracted from {path}")
        return 0

    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap, prefer_sentence_boundary=True)

    # embed and upsert in batches
    batch_size = 64
    total = 0
    qdrant.create_collection(vector_size=embedder.model.get_sentence_embedding_dimension() if hasattr(embedder.model, "get_sentence_embedding_dimension") else 384)
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        vectors = embedder.embed_texts(batch_chunks)
        ids = [str(uuid.uuid4()) for _ in batch_chunks]
        payloads = []
        for j, chunk_text_ in enumerate(batch_chunks):
            payload = {
                "source": p.name,
                "abs_path": str(p.resolve()),
                "chunk_index": i + j,
            }
            if store_text_in_payload:
                payload["text"] = chunk_text_
            else:
                # alternatively store pointer to file + chunk index (you can store external S3 key)
                payload["text_pointer"] = {"file": str(p.resolve()), "chunk_index": i + j}
            payloads.append(payload)
        qdrant.upsert(ids, vectors, payloads)
        total += len(ids)

    print(f"[ingest] Inserted {total} chunks from {p.name}")
    return total

def ingest_folder(folder_path, qdrant: QdrantWrapper, embedder: EmbeddingClient,
                  chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP,
                  collection=None, store_text_in_payload=True):
    """
    Ingest all supported files in a folder (non-recursive).
    """
    p = Path(folder_path)
    if not p.exists():
        print("Folder not found:", folder_path)
        return 0
    total_chunks = 0
    for child in p.iterdir():
        if child.is_file() and child.suffix.lower() in EXT_TO_PARSER:
            try:
                total_chunks += ingest_path(str(child), qdrant, embedder, chunk_size, overlap,
                                            collection, store_text_in_payload)
            except Exception as e:
                print(f"Error ingesting {child}: {e}")
    return total_chunks
