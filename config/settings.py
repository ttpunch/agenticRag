# config/settings.py - Complete configuration for agentic_rag
import os

# Qdrant Configuration
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "docker")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "multimodal_documents")

# LLM Configuration
LLM_BASE = os.environ.get("LLM_BASE", "http://localhost:12434/engines")
LLM_ENGINE = os.environ.get("LLM_ENGINE", "v1")
LLM_COMPLETION_PATH = f"{LLM_BASE}/{LLM_ENGINE}"
LLM_API_KEY = os.environ.get("LLM_API_KEY", "docker")
LLM_MODEL = os.environ.get("LLM_MODEL", "ai/qwen3:8B-Q4_K_M")

# Embedding Configuration
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Text Processing Configuration
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "512"))    # characters per chunk
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "50"))  # characters overlap
TOP_K = int(os.environ.get("TOP_K", "5"))                   # retrieval top k

# JWT Authentication Configuration
JWT_SECRET = os.environ.get("RAG_JWT_SECRET", "replace-this-with-secure-secret")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXP_SECONDS = int(os.environ.get("RAG_JWT_EXP", str(60 * 60 * 8)))  # default 8 hours

# Frontend Configuration
STREAMLIT_PORT = int(os.environ.get("STREAMLIT_PORT", "8501"))

# Database Configuration
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "rag_db")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password")
