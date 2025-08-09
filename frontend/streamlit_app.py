# frontend/streamlit_app.py
import streamlit as st
import requests
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import base64
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from streamlit_extras.badges import badge

# Page configuration
st.set_page_config(
    page_title="Agentic RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
def load_css():
    st.markdown("""
    <style>
        /* Main container */
        .main {
            background-color: #f8f9fa;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #2c3e50;
            color: white;
        }
        
        /* Buttons */
        .stButton>button {
            border-radius: 20px;
            border: 1px solid #4CAF50;
            background-color: #4CAF50;
            color: white;
            font-weight: 500;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #45a049;
            border-color: #45a049;
        }
        
        /* Text input */
        .stTextInput>div>div>input {
            border-radius: 20px;
            padding: 10px 15px;
        }
        
        /* Chat messages */
        .user-message {
            background-color: #e3f2fd;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 5px 0;
            max-width: 80%;
            margin-left: auto;
        }
        
        .bot-message {
            background-color: #f1f1f1;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 5px 0;
            max-width: 80%;
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from config.settings import LLM_COMPLETION_PATH, QDRANT_URL, QDRANT_COLLECTION
from auth.jwt_auth import authenticate_user, decode_token, get_current_user
from vectorstore.qdrant_client import QdrantWrapper
from embeddings import EmbeddingClient
from ingestion.ingest_manager import ingest_path
from rag import RAGPipeline

# UI helpers
def init_state():
    logger.info("Initializing application state")
    if "jwt" not in st.session_state:
        st.session_state.jwt = None
        logger.debug("Initialized jwt in session state")
    if "username" not in st.session_state:
        st.session_state.username = None
        logger.debug("Initialized username in session state")

def login_form():
    logger.info("Rendering login form")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Welcome Back 👋</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #7f8c8d; margin-bottom: 30px;'>Sign in to access your documents</p>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            username = st.text_input("👤 Username", key="username_input")
            password = st.text_input("🔑 Password", type="password", key="password_input")
            
            col1, col2 = st.columns([1, 2])
            with col2:
                if st.button("Sign In", use_container_width=True):
                    logger.info(f"Login attempt for user: {username}")
                    try:
                        token = authenticate_user(username, password)
                        if token:
                            st.session_state.jwt = token
                            st.session_state.username = username
                            logger.info(f"Successfully logged in user: {username}")
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            logger.warning(f"Failed login attempt for user: {username}")
                            st.error("❌ Invalid username or password")
                    except Exception as e:
                        logger.error(f"Error during login: {str(e)}", exc_info=True)
                        st.error(f"⚠️ An error occurred: {str(e)}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; margin-top: 20px; color: #7f8c8d;'>Don't have an account? Contact admin</p>", unsafe_allow_html=True)

def logout():
    logger.info("Logging out user")
    st.session_state.jwt = None
    st.session_state.username = None
    logger.info("Session cleared, rerunning app")
    st.experimental_rerun()

def show_upload_ui(qdrant, embedder):
    st.subheader("Upload document(s) for ingestion")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, type=["pdf","txt","csv","xlsx","xls","png","jpg","jpeg","tiff"])
    if uploaded_files:
        out_dir = "tmp_uploads"
        os.makedirs(out_dir, exist_ok=True)
        cnt = 0
        for f in uploaded_files:
            dest = os.path.join(out_dir, f.name)
            # stream to disk
            with open(dest, "wb") as wf:
                wf.write(f.read())
            cnt += ingest_path(dest, qdrant, embedder)
        st.success(f"Ingested {cnt} chunks from {len(uploaded_files)} files")

def chat_ui(rag_pipeline):
    logger.info("Rendering chat UI")
    
    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your document assistant. How can I help you today?"}
        ]
    
    # Display chat messages
    st.markdown("<h2 style='color: #2c3e50; margin-bottom: 20px;'>Chat with your documents</h2>", unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    # Sidebar for document management
    with st.sidebar:
        st.markdown("### 🔍 Document Management")
        
        # Upload section
        with st.expander("📤 Upload Documents", expanded=False):
            uploaded_files = st.file_uploader("Choose files", 
                                           accept_multiple_files=True, 
                                           type=["pdf", "txt", "csv", "xlsx", "xls", "png", "jpg", "jpeg", "tiff"])
            
            if uploaded_files:
                st.session_state.uploaded_files = uploaded_files
                process_button = st.button("Process Documents", type="primary")
                
                if process_button:
                    with st.spinner("Processing documents..."):
                        out_dir = "tmp_uploads"
                        os.makedirs(out_dir, exist_ok=True)
                        cnt = 0
                        for f in st.session_state.uploaded_files:
                            dest = os.path.join(out_dir, f.name)
                            with open(dest, "wb") as wf:
                                wf.write(f.read())
                            cnt += ingest_path(dest, rag_pipeline.qdrant, rag_pipeline.embedder)
                        st.success(f"✅ Processed {cnt} chunks from {len(st.session_state.uploaded_files)} files")
                        st.rerun()
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Clear Chat History"):
            st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared. How can I assist you now?"}]
            st.rerun()
            
        if st.button("ℹ️ About"):
            st.session_state.messages.append({"role": "assistant", "content": "I'm an AI assistant that can help you with your documents. You can upload documents and ask me questions about them!"})
            st.rerun()
    
    # Display chat messages
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        start_time = datetime.now()
                        resp = rag_pipeline.answer(prompt)
                        duration = (datetime.now() - start_time).total_seconds()
                        logger.info(f"Query processed in {duration:.2f} seconds")
                        
                        # Display answer
                        answer = resp.get("answer", "I couldn't find an answer in the documents.")
                        st.markdown(answer)
                        
                        # Add sources if available
                        if "retrieved" in resp and resp["retrieved"]:
                            with st.expander("📚 Sources"):
                                for i, r in enumerate(resp["retrieved"][:3], 1):  # Show top 3 sources
                                    payload = r.get("payload", {})
                                    src = payload.get("source", "Unknown source")
                                    text = payload.get("text", "")
                                    st.markdown(f"**Source {i}:** `{src}`")
                                    st.caption(text[:200] + ("..." if len(text) > 200 else ""))
                        
                        # Add to chat history
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}"
                        st.error(error_msg)
                        logger.error(f"Error processing query: {str(e)}", exc_info=True)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

def main():
    logger.info("=== Starting Streamlit application ===")
    
    # Load custom CSS
    load_css()
    
    # Initialize app state
    init_state()
    
    # Set page title
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }
        .stApp {
            background-color: #f8f9fa;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if not st.session_state.jwt:
        logger.info("No active session, showing login form")
        login_form()
        return

    # token is present: decode for UI info
    try:
        user = get_current_user(st.session_state.jwt)
        logger.info(f"User session active for: {user}")
        
        col1, col2 = st.columns([8,1])
        col1.markdown(f"**Signed in as:** {user}")
        if col2.button("Logout"):
            logger.info("User initiated logout")
            logout()

        # instantiate backend clients
        logger.info("Initializing backend services...")
        try:
            qdrant = QdrantWrapper()
            logger.info("Qdrant client initialized successfully")
            
            embedder = EmbeddingClient()
            logger.info("Embedding client initialized successfully")
            
            rag_pipeline = RAGPipeline(qdrant, embedder)
            logger.info("RAG pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing backend services: {str(e)}", exc_info=True)
            st.error(f"Failed to initialize backend services: {str(e)}")
            return
            
    except Exception as e:
        logger.error(f"Error in user session handling: {str(e)}", exc_info=True)
        st.error("Session error. Please log in again.")
        st.session_state.jwt = None
        st.session_state.username = None
        logger.info("Session cleared due to error, rerunning app")
        st.rerun()
        return

    try:
        logger.info("Rendering main application UI")
        st.sidebar.header("Actions")
        
        if st.sidebar.button("Upload & Ingest"):
            logger.info("Upload & Ingest button clicked")
            show_upload_ui(qdrant, embedder)

        if st.sidebar.button("Run quick demo ingest (sample txt)"):
            logger.info("Demo ingest button clicked")
            sample_path = "sample_docs/demo.txt"
            if os.path.exists(sample_path):
                logger.info(f"Ingesting sample file: {sample_path}")
                ingest_path(sample_path, qdrant, embedder)
                st.sidebar.success("Sample ingested")
            else:
                logger.warning(f"Sample file not found: {sample_path}")
                st.sidebar.warning("Create sample_docs/demo.txt first")
        
        logger.info("Rendering chat UI")
        chat_ui(rag_pipeline)
        
    except Exception as e:
        logger.error(f"Error in main application UI: {str(e)}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
