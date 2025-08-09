# embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingClient:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts):
        """
        texts: list[str]
        returns: list[list[float]] floats as lists
        """
        embs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        # normalize (optional, often helps)
        norms = (embs**2).sum(axis=1, keepdims=True) ** 0.5
        norms[norms == 0] = 1.0
        embs = embs / norms
        return embs.tolist()
