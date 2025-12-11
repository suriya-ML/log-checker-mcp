"""
FAISS utilities for efficient vector storage and similarity search
Provides index management, search, and persistence for log analyzer
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path

try:
    import faiss
except ImportError:
    raise ImportError("FAISS not installed. Run: pip install faiss-cpu")

from utils.logging_utils import get_logger

logger = get_logger(__name__)


class FAISSIndex:
    """
    FAISS index manager for efficient vector search
    Supports multiple index types and persistent storage
    """
    
    def __init__(
        self,
        dimension: int = 1024,
        index_type: str = "IVFFlat",
        nlist: int = 100,
        nprobe: int = 10
    ):
        """
        Initialize FAISS index
        
        Args:
            dimension: Vector dimensionality
            index_type: Type of FAISS index ('Flat', 'IVFFlat', 'IVFPQ', 'HNSW')
            nlist: Number of clusters for IVF indexes
            nprobe: Number of clusters to visit during search (IVF only)
        """
        self.dimension = dimension
        self.index_type = index_type
        self.nlist = nlist
        self.nprobe = nprobe
        self.index = None
        self.metadata = []
        self.is_trained = False
        
        logger.info(f"Initializing FAISS index: type={index_type}, dimension={dimension}")
    
    def _create_index(self) -> faiss.Index:
        """Create appropriate FAISS index based on type"""
        if self.index_type == "Flat":
            # Exact search using L2 distance
            index = faiss.IndexFlatL2(self.dimension)
            logger.info("Created Flat index (exact search)")
            
        elif self.index_type == "IVFFlat":
            # Inverted file with exact post-verification
            quantizer = faiss.IndexFlatL2(self.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.dimension, self.nlist)
            logger.info(f"Created IVFFlat index (nlist={self.nlist})")
            
        elif self.index_type == "IVFPQ":
            # Inverted file with product quantization (more memory efficient)
            quantizer = faiss.IndexFlatL2(self.dimension)
            m = 8  # Number of sub-quantizers
            bits = 8  # Bits per sub-vector
            index = faiss.IndexIVFPQ(quantizer, self.dimension, self.nlist, m, bits)
            logger.info(f"Created IVFPQ index (nlist={self.nlist}, m={m})")
            
        elif self.index_type == "HNSW":
            # Hierarchical Navigable Small World graph
            index = faiss.IndexHNSWFlat(self.dimension, 32)
            logger.info("Created HNSW index (M=32)")
            
        else:
            logger.warning(f"Unknown index type: {self.index_type}, using Flat")
            index = faiss.IndexFlatL2(self.dimension)
        
        return index
    
    def build(self, vectors: np.ndarray, metadata: List[Dict]) -> None:
        """
        Build FAISS index from vectors
        
        Args:
            vectors: numpy array of shape (n_samples, dimension)
            metadata: List of metadata dicts corresponding to each vector
        """
        if vectors.shape[0] != len(metadata):
            raise ValueError("Number of vectors must match metadata length")
        
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} doesn't match index dimension {self.dimension}")
        
        # Ensure float32 format (FAISS requirement)
        vectors = vectors.astype('float32')
        
        # Create index
        self.index = self._create_index()
        
        # Train index if needed
        if self.index_type in ["IVFFlat", "IVFPQ"]:
            logger.info(f"Training index on {len(vectors)} vectors...")
            self.index.train(vectors)
            self.is_trained = True
            
            # Set nprobe for search
            self.index.nprobe = self.nprobe
            logger.info(f"Index trained, nprobe set to {self.nprobe}")
        
        # Add vectors to index
        logger.info(f"Adding {len(vectors)} vectors to index...")
        self.index.add(vectors)
        
        # Store metadata
        self.metadata = metadata
        
        logger.info(f"✅ FAISS index built successfully with {self.index.ntotal} vectors")
    
    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        return_distances: bool = True
    ) -> Tuple[List[Dict], Optional[np.ndarray]]:
        """
        Search for k nearest neighbors
        
        Args:
            query_vector: Query vector of shape (dimension,) or (1, dimension)
            k: Number of nearest neighbors to return
            return_distances: Whether to return distances
        
        Returns:
            Tuple of (results, distances) where results is list of metadata dicts
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty or not built")
            return [], None
        
        # Ensure correct shape and type
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        query_vector = query_vector.astype('float32')
        
        # Limit k to available vectors
        k = min(k, self.index.ntotal)
        
        # Search
        distances, indices = self.index.search(query_vector, k)
        
        # Get results with metadata
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.metadata):  # Valid index
                result = self.metadata[idx].copy()
                if return_distances:
                    # Convert L2 distance to similarity score (higher is better)
                    # Using exponential decay: similarity = exp(-distance)
                    result["distance"] = float(distances[0][i])
                    result["similarity"] = float(np.exp(-distances[0][i]))
                results.append(result)
        
        logger.info(f"Search returned {len(results)} results")
        
        if return_distances:
            return results, distances[0]
        return results, None
    
    def batch_search(
        self,
        query_vectors: np.ndarray,
        k: int = 10
    ) -> List[Tuple[List[Dict], np.ndarray]]:
        """
        Search for multiple queries at once
        
        Args:
            query_vectors: Query vectors of shape (n_queries, dimension)
            k: Number of nearest neighbors per query
        
        Returns:
            List of (results, distances) tuples for each query
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty or not built")
            return []
        
        query_vectors = query_vectors.astype('float32')
        k = min(k, self.index.ntotal)
        
        distances, indices = self.index.search(query_vectors, k)
        
        all_results = []
        for query_idx in range(len(query_vectors)):
            results = []
            for i, idx in enumerate(indices[query_idx]):
                if idx >= 0 and idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result["distance"] = float(distances[query_idx][i])
                    result["similarity"] = float(np.exp(-distances[query_idx][i]))
                    results.append(result)
            all_results.append((results, distances[query_idx]))
        
        return all_results
    
    def save(self, filepath: str) -> None:
        """
        Save FAISS index and metadata to disk
        
        Args:
            filepath: Path to save the index (without extension)
        """
        if self.index is None:
            raise ValueError("No index to save")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_file = str(filepath.with_suffix('.faiss'))
        faiss.write_index(self.index, index_file)
        logger.info(f"Saved FAISS index to {index_file}")
        
        # Save metadata and config
        metadata_file = str(filepath.with_suffix('.metadata'))
        with open(metadata_file, 'wb') as f:
            pickle.dump({
                'metadata': self.metadata,
                'dimension': self.dimension,
                'index_type': self.index_type,
                'nlist': self.nlist,
                'nprobe': self.nprobe,
                'is_trained': self.is_trained
            }, f)
        logger.info(f"Saved metadata to {metadata_file}")
    
    def load(self, filepath: str) -> None:
        """
        Load FAISS index and metadata from disk
        
        Args:
            filepath: Path to load the index from (without extension)
        """
        filepath = Path(filepath)
        
        index_file = str(filepath.with_suffix('.faiss'))
        metadata_file = str(filepath.with_suffix('.metadata'))
        
        if not os.path.exists(index_file) or not os.path.exists(metadata_file):
            raise FileNotFoundError(f"Index files not found: {filepath}")
        
        # Load FAISS index
        self.index = faiss.read_index(index_file)
        logger.info(f"Loaded FAISS index from {index_file} ({self.index.ntotal} vectors)")
        
        # Load metadata and config
        with open(metadata_file, 'rb') as f:
            data = pickle.load(f)
            self.metadata = data['metadata']
            self.dimension = data['dimension']
            self.index_type = data['index_type']
            self.nlist = data.get('nlist', 100)
            self.nprobe = data.get('nprobe', 10)
            self.is_trained = data.get('is_trained', False)
        
        # Set nprobe if IVF index
        if self.index_type in ["IVFFlat", "IVFPQ"] and hasattr(self.index, 'nprobe'):
            self.index.nprobe = self.nprobe
        
        logger.info(f"Loaded metadata for {len(self.metadata)} vectors")
    
    def get_stats(self) -> Dict:
        """Get statistics about the index"""
        if self.index is None:
            return {"status": "not_built"}
        
        return {
            "status": "ready",
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "is_trained": self.is_trained,
            "nlist": self.nlist if self.index_type in ["IVFFlat", "IVFPQ"] else None,
            "nprobe": self.nprobe if self.index_type in ["IVFFlat", "IVFPQ"] else None
        }


def cosine_similarity_faiss(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors using FAISS
    
    Args:
        vec1: First vector
        vec2: Second vector
    
    Returns:
        Cosine similarity score (0 to 1)
    """
    # Normalize vectors
    vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
    vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)
    
    # Cosine similarity is dot product of normalized vectors
    return float(np.dot(vec1_norm, vec2_norm))


def create_faiss_index_from_vectors(
    vectors: List[List[float]],
    metadata: List[Dict],
    index_type: str = "IVFFlat",
    dimension: int = None
) -> FAISSIndex:
    """
    Helper function to create and build FAISS index from vector list
    
    Args:
        vectors: List of vectors
        metadata: List of metadata dicts
        index_type: Type of FAISS index
        dimension: Vector dimension (auto-detected if None)
    
    Returns:
        Built FAISSIndex object
    """
    vectors_array = np.array(vectors, dtype='float32')
    
    if dimension is None:
        dimension = vectors_array.shape[1]
    
    # Choose appropriate parameters based on dataset size
    n_vectors = len(vectors)
    if n_vectors < 1000:
        # Small dataset: use flat index for exact search
        index_type = "Flat"
        nlist = None
        nprobe = None
    elif n_vectors < 10000:
        # Medium dataset: use IVFFlat with fewer clusters
        nlist = min(100, n_vectors // 10)
        nprobe = min(10, nlist)
    else:
        # Large dataset: use IVFFlat with more clusters
        nlist = min(1000, n_vectors // 50)
        nprobe = min(20, nlist)
    
    logger.info(f"Creating FAISS index for {n_vectors} vectors (dim={dimension}, type={index_type})")
    
    faiss_index = FAISSIndex(
        dimension=dimension,
        index_type=index_type,
        nlist=nlist or 100,
        nprobe=nprobe or 10
    )
    
    faiss_index.build(vectors_array, metadata)
    
    return faiss_index
