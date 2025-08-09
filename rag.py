# rag.py
from vectorstore.qdrant_client import QdrantWrapper
from embeddings import EmbeddingClient
from llm_client import call_llm
from config.settings import TOP_K

class RAGPipeline:
    def __init__(self, qdrant: QdrantWrapper, embedder: EmbeddingClient):
        self.qdrant = qdrant
        self.embedder = embedder

    def answer(self, query: str, top_k=TOP_K):
        q_emb = self.embedder.embed_texts([query])[0]
        hits = self.qdrant.search(q_emb, top_k=top_k)
        # build context
        context_parts = []
        for h in hits:
            payload = h["payload"] or {}
            src = payload.get("source", "unknown")
            chunk_idx = payload.get("chunk_index", -1)
            # get text stored? if you stored text in payload, use it; here we didn't store text to avoid big payloads
            # For demo, include metadata only. Best: store chunk text in payload under 'text' during ingest.
            text = payload.get("text", "[text not stored in payload]")
            context_parts.append(f"Source: {src} (chunk:{chunk_idx})\n{text}")

        context = "\n\n---\n\n".join(context_parts)
        prompt = f"""You are an assistant. Use the following retrieved document chunks to answer the user query.

Context:
{context}

User question:
{query}

Answer concisely and cite source chunks by 'Source: filename (chunk:n)' when relevant.
"""
        resp = call_llm(prompt, max_tokens=512, temperature=0.0)
        return {"answer": resp, "retrieved": hits}
