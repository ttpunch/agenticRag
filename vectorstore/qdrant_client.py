# vectorstore/qdrant_client.py
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from config.settings import QDRANT_URL, QDRANT_COLLECTION, QDRANT_API_KEY

class QdrantWrapper:
    def __init__(self, url=QDRANT_URL, api_key=QDRANT_API_KEY, collection=QDRANT_COLLECTION):
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection = collection

    def create_collection(self, vector_size, distance=rest.Distance.COSINE):
        try:
            self.client.get_collection(self.collection)
        except Exception:
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config=rest.VectorParams(size=vector_size, distance=distance),
            )

    def upsert(self, ids, vectors, payloads):
        """
        payloads: list of dicts (each may contain 'text', 'source', 'chunk_index', etc.)
        """
        points = []
        for i, v, p in zip(ids, vectors, payloads):
            points.append(rest.PointStruct(id=i, vector=v, payload=p))
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, vector, top_k=5, filter=None, with_payload=True):
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            query_filter=filter,
            with_payload=with_payload
        )
        results = []
        for h in hits:
            results.append({"id": h.id, "score": h.score, "payload": h.payload})
        return results
