# qdrant_client_wrapper.py
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
import numpy as np
from config.settings import QDRANT_URL, QDRANT_COLLECTION, QDRANT_API_KEY

class QdrantWrapper:
    def __init__(self, url=QDRANT_URL, api_key=QDRANT_API_KEY, collection=QDRANT_COLLECTION):
        # when running in Docker on same host, use 'localhost'
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection = collection

    def create_collection(self, vector_size, distance=rest.Distance.COSINE):
        # create if not exists
        try:
            self.client.get_collection(self.collection)
        except Exception:
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config=rest.VectorParams(size=vector_size, distance=distance),
            )

    def upsert(self, ids, vectors, payloads):
        # ids: list[str|int], vectors: list[list[float]], payloads: list[dict]
        self.client.upsert(
            collection_name=self.collection,
            points= [
                rest.PointStruct(id=i, vector=v, payload=p) for i, v, p in zip(ids, vectors, payloads)
            ]
        )

    def search(self, vector, top_k=5, filter=None):
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            query_filter=filter
        )
        # hits: list of PointResults
        results = []
        for h in hits:
            results.append({
                "id": h.id,
                "score": h.score,
                "payload": h.payload,
            })
        return results
