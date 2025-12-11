"""
Local embedding utilities using sentence-transformers
No cloud dependencies - runs entirely locally
"""

import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from utils.logging_utils import get_logger

logger = get_logger(__name__)

# Global model cache
_model_cache = {}


def get_embedding_model(model_name: str = 'all-MiniLM-L6-v2') -> SentenceTransformer:
    """
    Get or create a sentence transformer model with caching
    
    Args:
        model_name: Name of the sentence-transformers model
    
    Returns:
        SentenceTransformer model instance
    """
    if model_name not in _model_cache:
        logger.info(f"Loading embedding model: {model_name}")
        try:
            _model_cache[model_name] = SentenceTransformer(model_name)
            logger.info(f"✅ Model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    return _model_cache[model_name]


def embed_text(
    text: str,
    model_name: str = 'all-MiniLM-L6-v2',
    normalize: bool = True
) -> np.ndarray:
    """
    Generate embedding for a single text
    
    Args:
        text: Text to embed
        model_name: Name of the sentence-transformers model
        normalize: Whether to normalize the embedding
    
    Returns:
        Embedding vector as numpy array
    """
    model = get_embedding_model(model_name)
    
    # Encode text
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=normalize,
        show_progress_bar=False
    )
    
    return embedding


def embed_texts(
    texts: List[str],
    model_name: str = 'all-MiniLM-L6-v2',
    normalize: bool = True,
    batch_size: int = 32,
    show_progress: bool = True
) -> np.ndarray:
    """
    Generate embeddings for multiple texts (batch processing)
    
    Args:
        texts: List of texts to embed
        model_name: Name of the sentence-transformers model
        normalize: Whether to normalize the embeddings
        batch_size: Batch size for processing
        show_progress: Whether to show progress bar
    
    Returns:
        Array of embeddings with shape (n_texts, embedding_dim)
    """
    model = get_embedding_model(model_name)
    
    # Batch encode
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=normalize,
        batch_size=batch_size,
        show_progress_bar=show_progress
    )
    
    return embeddings


def get_embedding_dimension(model_name: str = 'all-MiniLM-L6-v2') -> int:
    """
    Get the embedding dimension for a model
    
    Args:
        model_name: Name of the sentence-transformers model
    
    Returns:
        Embedding dimension
    """
    model = get_embedding_model(model_name)
    return model.get_sentence_embedding_dimension()


def convert_to_python_types(obj):
    """
    Convert numpy types to Python native types for JSON serialization
    
    Args:
        obj: Object to convert (can be nested)
    
    Returns:
        Object with Python native types
    """
    import numpy as np
    
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_python_types(item) for item in obj]
    else:
        return obj


# Model recommendations based on use case
MODEL_RECOMMENDATIONS = {
    'fast': 'all-MiniLM-L6-v2',           # 384 dim, very fast, good quality
    'balanced': 'all-mpnet-base-v2',      # 768 dim, slower but better quality
    'quality': 'all-mpnet-base-v2',       # 768 dim, best quality
    'multilingual': 'paraphrase-multilingual-MiniLM-L12-v2',  # 384 dim, supports 50+ languages
    'code': 'sentence-transformers/all-MiniLM-L6-v2',  # Good for code and logs
}


def get_recommended_model(use_case: str = 'fast') -> str:
    """
    Get recommended model name for a use case
    
    Args:
        use_case: Use case ('fast', 'balanced', 'quality', 'multilingual', 'code')
    
    Returns:
        Model name
    """
    return MODEL_RECOMMENDATIONS.get(use_case, MODEL_RECOMMENDATIONS['fast'])
