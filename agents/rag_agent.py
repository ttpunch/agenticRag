# agents/rag_agent.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import RAGPipeline
from qdrant_client_wrapper import QdrantWrapper
from embeddings import EmbeddingClient

def rag_agent(state):
    """
    RAG agent that processes queries using the RAG pipeline.
    Expects state to contain 'query' and 'authorized' keys.
    Returns state with 'rag_result' added.
    """
    query = state.get("query", "")
    if not query:
        return {**state, "error": "missing_query", "rag_result": None}
    
    if not state.get("authorized", False):
        return {**state, "error": "unauthorized", "rag_result": None}
    
    try:
        # Initialize RAG components
        qdrant = QdrantWrapper()
        embedder = EmbeddingClient()
        rag_pipeline = RAGPipeline(qdrant, embedder)
        
        # Process the query
        result = rag_pipeline.answer(query)
        
        return {**state, "rag_result": result}
        
    except Exception as e:
        return {**state, "error": f"rag_error: {str(e)}", "rag_result": None} 