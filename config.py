"""
Configuration module for Log Analyzer MCP Server
FAISS-based vector search with local embeddings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration management with environment variables"""
    
    # ========================================================================
    # EMBEDDING MODEL CONFIGURATION
    # ========================================================================
    # Local embedding model (sentence-transformers)
    EMBED_MODEL_NAME = os.environ.get('EMBED_MODEL', 'all-MiniLM-L6-v2')
    EMBED_DIMENSION = int(os.environ.get('EMBED_DIMENSION', '384'))  # Dimension for all-MiniLM-L6-v2
    
    # ========================================================================
    # LOG ANALYZER CONFIGURATION
    # ========================================================================
    # Get base directory (project root)
    _BASE_DIR = Path(__file__).parent.absolute()
    
    # File paths - use relative paths by default
    LOG_FOLDER = os.environ.get('LOG_FOLDER', str(_BASE_DIR / 'logs'))
    
    # Log file extensions to process
    LOG_EXTENSIONS = ('.log', '.txt', '.out', '.err')
    
    # Ensure folders exist
    @classmethod
    def ensure_folders(cls):
        """Create required folders if they don't exist"""
        Path(cls.LOG_FOLDER).mkdir(parents=True, exist_ok=True)
    
    # Chunking parameters
    MAX_CHARS_PER_CHUNK = int(os.environ.get('MAX_CHARS_PER_CHUNK', '5000'))
    DEFAULT_CHUNK_SIZE = int(os.environ.get('DEFAULT_CHUNK_SIZE', '4096'))
    DEFAULT_OVERLAP = int(os.environ.get('DEFAULT_OVERLAP', '1024'))
    
    # ========================================================================
    # FAISS CONFIGURATION
    # ========================================================================
    # FAISS index type: 'Flat' (exact), 'IVFFlat' (fast), 'IVFPQ' (memory efficient), 'HNSW' (graph-based)
    FAISS_INDEX_TYPE = os.environ.get('FAISS_INDEX_TYPE', 'IVFFlat')
    
    # IVF parameters
    FAISS_NLIST = int(os.environ.get('FAISS_NLIST', '100'))  # Number of clusters for IVF
    FAISS_NPROBE = int(os.environ.get('FAISS_NPROBE', '10'))  # Clusters to search
    
    # Search parameters
    FAISS_TOP_K = int(os.environ.get('FAISS_TOP_K', '150'))  # Default top-k results
    
    # Index persistence
    FAISS_INDEX_PATH = os.environ.get(
        'FAISS_INDEX_PATH',
        str(_BASE_DIR / 'logs' / 'faiss_index')
    )
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        # All configuration is optional with sensible defaults
        return True
