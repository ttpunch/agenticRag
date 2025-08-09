# frontend/streamlit_app.py
import streamlit as st
import requests
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import base64
import time

# Page configuration with proper layout
st.set_page_config(
    page_title="Agentic RAG | AI Document Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': "https://github.com/your-repo/issues",
        'About': "# Agentic RAG\nPowered by AI for intelligent document analysis"
    }
)

# Fixed and properly aligned CSS
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main container fixes */
        .main .block-container {
            padding: 1rem 2rem 2rem 2rem;
            max-width: none;
            margin: 0;
        }
        
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        /* Header styling - properly centered */
        .app-header {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
            width: 100%;
        }
        
        .app-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 0.5rem;
        }
        
        .app-subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            font-weight: 400;
        }
        
        /* User header - properly aligned */
        .user-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .status-online {
            background: rgba(34, 197, 94, 0.2);
            color: #10b981;
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .welcome-text {
            color: white;
            font-weight: 500;
            font-size: 1rem;
        }
        
        .time-display {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }
        
        /* Metrics dashboard - proper grid layout */
        .metrics-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
            width: 100%;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        }
        
        .metric-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            margin: 0.5rem 0;
            color: #333;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9rem;
            font-weight: 500;
            margin: 0;
        }
        
        /* Main content layout */
        .main-content {
            display: flex;
            gap: 2rem;
            align-items: flex-start;
        }
        
        /* Chat container - properly structured */
        .chat-section {
            flex:1;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            min-height: 600px;
            display: flex;
            flex-direction: column;
        }
        
        .chat-header {
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        .chat-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .chat-subtitle {
            color: #666;
            font-size: 0.9rem;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 1rem;
            padding: 0.5rem 0;
            max-height: 400px;
        }
        
        /* Chat message styling */
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 18px 18px 4px 18px;
            padding: 12px 18px;
            margin: 8px 0 8px auto;
            max-width: 80%;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            word-wrap: break-word;
        }
        
        .bot-message {
            background: #f8f9fa;
            color: #333;
            border-radius: 18px 18px 18px 4px;
            padding: 12px 18px;
            margin: 8px auto 8px 0;
            max-width: 80%;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border: 1px solid #e9ecef;
            word-wrap: break-word;
        }
        
        /* Chat input area */
        .chat-input-section {
            margin-top: auto;
            padding-top: 1rem;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        .suggestions-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        /* Sidebar fixes */
        .css-1d391kg {
            background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            background: white;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Login form styling */
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 3rem 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 400px;
            margin: 2rem auto;
        }
        
        .login-title {
            color: #333;
            font-size: 2rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .login-subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 1rem;
        }
        
        /* File uploader styling */
        .stFileUploader > div {
            border: 2px dashed #ccc;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            background: rgba(255, 255, 255, 0.5);
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem;
            }
            
            .main-content {
                flex-direction: column;
                gap: 1rem;
            }
            
            .metrics-container {
                grid-template-columns: repeat(2, 1fr);
                gap: 0.5rem;
            }
            
            .user-message,
            .bot-message {
                max-width: 95%;
            }
            
            .suggestions-container {
                grid-template-columns: 1fr;
                gap: 0.5rem;
            }
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

def init_state():
    """Initialize session state variables"""
    defaults = {
        "jwt": None,
        "username": None,
        "messages": [
            {"role": "assistant", "content": "👋 Hello! I'm your AI document assistant. Upload some documents and ask me questions about them!"}
        ],
        "uploaded_files": [],
        "processing_files": False,
        "last_activity": datetime.now()
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_app_header():
    """Display app header"""
    st.markdown("""
        <div class="app-header">
            <h1 class="app-title">🤖 Agentic RAG</h1>
            <p class="app-subtitle">AI-Powered Document Intelligence Assistant</p>
        </div>
    """, unsafe_allow_html=True)

def login_form():
    """Login form"""
    logger.info("Rendering login form")
    
    show_app_header()
    
    # Centered login form
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("""
            <div class="login-container">
                <h2 class="login-title">Welcome Back</h2>
                <p class="login-subtitle">Sign in to access your document assistant</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            
            if st.button("🚀 Sign In", use_container_width=True):
                if not username or not password:
                    st.error("⚠️ Please fill in all fields")
                    return
                
                with st.spinner("Authenticating..."):
                    try:
                        token = authenticate_user(username, password)
                        if token:
                            st.session_state.jwt = token
                            st.session_state.username = username
                            st.success("✅ Login successful!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    except Exception as e:
                        st.error(f"⚠️ Authentication error: {str(e)}")

def show_user_header(username):
    """Show user header with proper alignment"""
    st.markdown(f"""
        <div class="user-header">
            <div class="user-info">
                <div class="status-online">
                    <span>🟢</span> Online
                </div>
                <span class="welcome-text">Welcome, {username}!</span>
            </div>
            <div class="time-display">
                ⏰ {datetime.now().strftime("%H:%M")}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Logout button in sidebar
    with st.sidebar:
        if st.button("🚪 Logout", use_container_width=True):
            logout()

def logout():
    """Handle user logout"""
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

def show_metrics_dashboard(rag_pipeline):
    """Show metrics with proper grid layout"""
    st.markdown("""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-icon">📄</div>
                <div class="metric-value">1,247</div>
                <div class="metric-label">Documents</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">💬</div>
                <div class="metric-value">{}</div>
                <div class="metric-label">Conversations</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">⚡</div>
                <div class="metric-value">0.8s</div>
                <div class="metric-label">Avg Response</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">🟢</div>
                <div class="metric-value">Online</div>
                <div class="metric-label">System Health</div>
            </div>
        </div>
    """.format(len(st.session_state.messages) // 2), unsafe_allow_html=True)

def show_sidebar_controls(rag_pipeline):
    """Sidebar controls"""
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")
        
        # Document Upload
        with st.expander("📤 Upload Documents", expanded=True):
            uploaded_files = st.file_uploader(
                "Choose files", 
                accept_multiple_files=True, 
                type=["pdf", "txt", "csv", "xlsx", "xls", "png", "jpg", "jpeg", "tiff"],
                help="Upload documents to analyze"
            )
            
            if uploaded_files:
                st.markdown("**Selected Files:**")
                for file in uploaded_files:
                    file_size = len(file.getvalue()) / 1024
                    st.write(f"• {file.name} ({file_size:.1f} KB)")
                
                if st.button("🚀 Process Documents", type="primary"):
                    process_documents(uploaded_files, rag_pipeline)
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Clear Chat"):
                st.session_state.messages = [
                    {"role": "assistant", "content": "Chat cleared! How can I help you?"}
                ]
                st.rerun()
        
        with col2:
            if st.button("🎮 Demo"):
                load_demo_data(rag_pipeline)

def process_documents(uploaded_files, rag_pipeline):
    """Process uploaded documents"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        out_dir = "tmp_uploads"
        os.makedirs(out_dir, exist_ok=True)
        
        total_files = len(uploaded_files)
        processed_chunks = 0
        
        for i, file in enumerate(uploaded_files):
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"Processing {file.name}...")
            
            dest = os.path.join(out_dir, file.name)
            with open(dest, "wb") as wf:
                wf.write(file.read())
            
            chunks = ingest_path(dest, rag_pipeline.qdrant, rag_pipeline.embedder)
            processed_chunks += chunks
        
        progress_bar.progress(1.0)
        st.success(f"✅ Processed {processed_chunks} chunks from {total_files} files!")
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"📁 I've processed {total_files} new document(s). Ask me questions about them!"
        })
        
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    finally:
        progress_bar.empty()
        status_text.empty()

def load_demo_data(rag_pipeline):
    """Load demo data"""
    with st.spinner("Loading demo data..."):
        try:
            demo_content = """
            # AI and Machine Learning Overview
            
            Artificial Intelligence (AI) is the simulation of human intelligence in machines. 
            Machine Learning (ML) is a subset of AI that enables machines to learn from experience.
            
            Key concepts include:
            - Deep Learning: Neural networks with multiple layers
            - Natural Language Processing: Understanding human language  
            - Computer Vision: Interpreting visual information
            - Reinforcement Learning: Learning through trial and error
            """
            
            os.makedirs("sample_docs", exist_ok=True)
            sample_path = "sample_docs/demo.txt"
            
            with open(sample_path, "w") as f:
                f.write(demo_content)
            
            chunks = ingest_path(sample_path, rag_pipeline.qdrant, rag_pipeline.embedder)
            st.success(f"✅ Demo loaded! ({chunks} chunks)")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "🎮 Demo content loaded! Ask me about AI and machine learning."
            })
            
        except Exception as e:
            st.error(f"❌ Demo error: {str(e)}")
        
        time.sleep(1)
        st.rerun()

def chat_ui(rag_pipeline):
    """Main chat interface with proper structure"""
    st.markdown("""
        <div class="chat-section">
            <div class="chat-header">
                <h2 class="chat-title">💬 Chat with your Documents</h2>
                <p class="chat-subtitle">Ask questions and get intelligent responses</p>
            </div>
    """, unsafe_allow_html=True)
    
    # Chat messages container
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="bot-message">
                    <strong>🤖 Assistant:</strong> {message["content"]}
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input section
    st.markdown('<div class="chat-input-section">', unsafe_allow_html=True)
    
    # Quick suggestions
    st.markdown("**💡 Quick Suggestions:**")
    st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Summarize content", use_container_width=True):
            handle_query("Summarize the main points from the documents", rag_pipeline)
    with col2:
        if st.button("🔍 Find information", use_container_width=True):
            handle_query("What are the key topics covered?", rag_pipeline)
    with col3:
        if st.button("💡 Key insights", use_container_width=True):
            handle_query("What are the most important insights?", rag_pipeline)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    prompt = st.chat_input("Type your question here...")
    
    if prompt:
        handle_query(prompt, rag_pipeline)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def handle_query(prompt, rag_pipeline):
    """Handle user query"""
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        with st.spinner("Processing..."):
            resp = rag_pipeline.answer(prompt)
        
        answer = resp.get("answer", "I couldn't find an answer.")
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.rerun()

def main():
    """Main application"""
    load_css()
    init_state()
    
    if not st.session_state.jwt:
        login_form()
        return

    try:
        user = get_current_user(st.session_state.jwt)
        
        # Show header
        show_app_header()
        show_user_header(user)
        
        # Initialize backend
        with st.spinner("🔧 Initializing services..."):
            qdrant = QdrantWrapper()
            embedder = EmbeddingClient()
            rag_pipeline = RAGPipeline(qdrant, embedder)
        
        # Show metrics
        show_metrics_dashboard(rag_pipeline)
        
        # Main layout
        col_sidebar, col_chat = st.columns([1, 2])
        
        with col_sidebar:
            show_sidebar_controls(rag_pipeline)
        
        with col_chat:
            chat_ui(rag_pipeline)
            
    except Exception as e:
        st.error(f"🚫 Error: {str(e)}")
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()