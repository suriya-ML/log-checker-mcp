#!/usr/bin/env python3
"""
Log Analyzer MCP Server
Simplified MCP server exposing 3 core log analysis tools:
- fetch_local_logs: Fetch and chunk local log files
- store_chunks_as_vectors: Vectorize log chunks with caching
- query_SFlogs: Query vectorized logs with semantic search

For GitHub deployment and use with MCP clients like Claude Desktop
"""

import os
import json
import sys
import time
import re
import math
import hashlib
import threading
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import configuration
from config import Config

# Import utility modules
from utils.logging_utils import get_logger, setup_logger
from utils.file_utils import (
    ensure_directory, load_json, save_json, save_chunk_txt
)
from utils.embeddings import (
    embed_text, embed_texts, convert_to_python_types, get_embedding_dimension
)
from utils.chunking_utils import (
    iter_local_logs, chunk_text, chunks_chars_mem
)
from utils.error_extraction import (
    extract_error_events_universal, universal_severity_rank
)
from utils.faiss_utils import (
    FAISSIndex, create_faiss_index_from_vectors, cosine_similarity_faiss
)

# Set up logger
logger = get_logger(__name__)

# Initialize embedding model on first use (lazy loading)
logger.info(f"Using local embedding model: {Config.EMBED_MODEL_NAME}")


# ---------------------------------------------------------------------------
# Embedding Cache Manager
# ---------------------------------------------------------------------------

class EmbeddingCache:
    """Persistent cache for text embeddings with content-based hashing"""
    
    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            cache_dir = os.path.join(Config.LOG_FOLDER, ".embedding_cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.cache_dir / "embeddings.json"
        self.stats_file = self.cache_dir / "stats.json"
        
        self.cache = self._load_cache()
        self.stats = self._load_stats()
        
    def _load_cache(self) -> Dict[str, List[float]]:
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                return load_json(str(self.cache_file), default={})
            except Exception as e:
                logger.warning(f"Error loading cache: {e}")
        return {}
    
    def _load_stats(self) -> Dict:
        """Load statistics from disk"""
        default_stats = {
            "total_hits": 0,
            "total_misses": 0,
            "total_saves": 0,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        if self.stats_file.exists():
            try:
                return load_json(str(self.stats_file), default=default_stats)
            except Exception as e:
                logger.warning(f"Error loading stats: {e}")
        
        return default_stats
    
    def _save_cache(self):
        """Persist cache to disk"""
        try:
            save_json(self.cache, str(self.cache_file))
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _save_stats(self):
        """Persist statistics to disk"""
        try:
            self.stats["last_updated"] = datetime.now().isoformat()
            save_json(self.stats, str(self.stats_file))
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
    
    def get_hash(self, text: str) -> str:
        """Generate content-based hash for text"""
        content = text[:8000].strip()
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache if exists"""
        cache_key = self.get_hash(text)
        if cache_key in self.cache:
            self.stats["total_hits"] = self.stats.get("total_hits", 0) + 1
            return self.cache[cache_key]
        else:
            self.stats["total_misses"] = self.stats.get("total_misses", 0) + 1
            return None
    
    def set(self, text: str, embedding: List[float]):
        """Store embedding in cache"""
        cache_key = self.get_hash(text)
        self.cache[cache_key] = embedding
        self.stats["total_saves"] = self.stats.get("total_saves", 0) + 1
    
    def save(self):
        """Persist cache and stats to disk"""
        self._save_cache()
        self._save_stats()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_hits = self.stats.get("total_hits", 0)
        total_misses = self.stats.get("total_misses", 0)
        total_requests = total_hits + total_misses
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        cache_size_mb = 0
        if self.cache_file.exists():
            cache_size_mb = self.cache_file.stat().st_size / (1024 * 1024)
        
        return {
            "cache_size": len(self.cache),
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size_mb": round(cache_size_mb, 2)
        }


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a_np = np.array(a)
    b_np = np.array(b)
    return float(cosine_similarity_faiss(a_np, b_np))


def is_summarization_query(query: str) -> bool:
    """Check if query is asking for a summary"""
    summary_keywords = [
        "summarize", "summary", "overview", "what happened",
        "give me a summary", "summarise", "sum up", "recap",
        "walk me through", "key events", "aggregate",
        "overall", "root cause", "rca", "all errors", "list errors"
    ]
    return any(k in query.lower() for k in summary_keywords)


# ---------------------------------------------------------------------------
# MCP Server Implementation
# ---------------------------------------------------------------------------

app = Server("log-analyzer-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="fetch_local_logs",
            description="Fetch logs from local folder; chunk with overlap & save. "
                       "Parameters: input_folder (optional, defaults to ./logs), "
                       "chunk_size (default: 4096), overlap (default: 1024)",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_folder": {
                        "type": "string",
                        "description": "Path to folder containing log files"
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Size of each chunk in characters",
                        "default": Config.DEFAULT_CHUNK_SIZE
                    },
                    "overlap": {
                        "type": "integer",
                        "description": "Overlap between chunks in characters",
                        "default": Config.DEFAULT_OVERLAP
                    }
                }
            }
        ),
        Tool(
            name="store_chunks_as_vectors",
            description="Vectorize log chunks with enhanced metadata extraction and caching. "
                       "Uses local sentence-transformers for embeddings. Extracts timeframes, classes, methods, errors. "
                       "Builds FAISS index for fast similarity search.",
            inputSchema={
                "type": "object",
                "properties": {
                    "use_cache": {
                        "type": "boolean",
                        "description": "Whether to use embedding cache",
                        "default": True
                    },
                    "clear_cache": {
                        "type": "boolean",
                        "description": "Whether to clear cache before starting",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="query_SFlogs",
            description="Query vectorized logs with comprehensive hybrid retrieval. "
                       "Supports semantic search with error analysis, metadata extraction, "
                       "and intelligent clustering. Returns detailed analysis with error patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query to search logs"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "fetch_local_logs":
            result = await fetch_local_logs(
                input_folder=arguments.get("input_folder"),
                chunk_size=arguments.get("chunk_size", Config.DEFAULT_CHUNK_SIZE),
                overlap=arguments.get("overlap", Config.DEFAULT_OVERLAP)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "store_chunks_as_vectors":
            result = await store_chunks_as_vectors(
                use_cache=arguments.get("use_cache", True),
                clear_cache=arguments.get("clear_cache", False)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "query_SFlogs":
            query = arguments.get("query")
            if not query:
                return [TextContent(type="text", text=json.dumps({"error": "Query parameter required"}))]
            
            result = await query_SFlogs(query=query)
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


# ---------------------------------------------------------------------------
# Tool Implementations
# ---------------------------------------------------------------------------

async def fetch_local_logs(
    input_folder: Optional[str] = None,
    chunk_size: int = Config.DEFAULT_CHUNK_SIZE,
    overlap: int = Config.DEFAULT_OVERLAP
) -> str:
    """Fetch and chunk local log files"""
    src_root = os.path.expanduser(input_folder or Config.LOG_FOLDER)
    if not os.path.exists(src_root):
        return f"❌ Input folder not found: {src_root}"

    output_dir = Config.LOG_FOLDER
    ensure_directory(output_dir)

    saved_chunks: List[str] = []
    total_files = 0
    total_chunks = 0

    for rel_path, abs_path in iter_local_logs(src_root):
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            
            chunks = chunks_chars_mem(text, chunk_size, overlap)
            
            for i, chunk in enumerate(chunks, 1):
                out_path = save_chunk_txt(chunk, rel_path, output_dir, i)
                saved_chunks.append(out_path)
            
            total_files += 1
            total_chunks += len(chunks)
            
        except Exception as e:
            logger.warning(f"Error processing {abs_path}: {e}")

    return f"""✅ Local logs processed
Source: {src_root}
Output: {output_dir}
Files: {total_files}, Chunks: {total_chunks}"""


async def store_chunks_as_vectors(
    use_cache: bool = True,
    clear_cache: bool = False
) -> str:
    """Vectorize log chunks with enhanced metadata extraction and caching"""
    
    chunk_paths = [Config.LOG_FOLDER]
    
    # Initialize cache
    cache = EmbeddingCache() if use_cache else None
    
    if clear_cache and cache:
        logger.info("Clearing embedding cache...")
        cache.clear()
        cache = EmbeddingCache()
    
    # Collect chunks with metadata extraction
    logger.info("Collecting chunk files with metadata extraction...")
    all_chunks = []
    for p in chunk_paths:
        for file in Path(p).rglob("*.txt"):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                
                if not text.strip():
                    continue
                
                # Extract metadata from chunk content
                metadata = {
                    "path": str(file),
                    "filename": file.name,
                    "text": text
                }
                
                # Extract timeframes
                timeframes = re.findall(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', text)
                if timeframes:
                    metadata["timeframe_start"] = timeframes[0]
                    metadata["timeframe_end"] = timeframes[-1] if len(timeframes) > 1 else timeframes[0]
                
                # Extract class names
                classes = re.findall(
                    r'\b([A-Z][a-zA-Z0-9_]*(?:Handler|Controller|Service|Trigger|Helper|Manager|Util|Utils|Batch|Queueable))\b',
                    text
                )
                if classes:
                    metadata["classes"] = list(set(classes))[:10]
                
                # Extract method signatures
                methods = re.findall(r'\b([a-z][a-zA-Z0-9_]*)\s*\(', text)
                if methods:
                    metadata["methods"] = list(set(methods))[:10]
                
                # Extract error types
                error_events = extract_error_events_universal(text, str(file))
                if error_events:
                    metadata["error_types"] = list(set(ev["error_type"] for ev in error_events))
                    metadata["has_errors"] = True
                else:
                    metadata["has_errors"] = False
                
                all_chunks.append(metadata)
                
            except Exception as e:
                logger.warning(f"Error reading {file}: {e}")

    if not all_chunks:
        return "[WARNING] No chunks found"

    total_chunks = len(all_chunks)
    logger.info(f"Found {total_chunks} chunks with metadata")
    
    # Check cache
    cached_chunks = []
    chunks_to_embed = []
    
    if cache:
        logger.info("Checking cache...")
        for chunk in tqdm(all_chunks, desc="Cache lookup", file=sys.stderr):
            embedding = cache.get(chunk["text"])
            if embedding is not None:
                chunk["vector"] = convert_to_python_types(embedding)
                cached_chunks.append(chunk)
            else:
                chunks_to_embed.append(chunk)
        
        cache_stats = cache.get_stats()
        logger.info(f"Cache hit: {len(cached_chunks)}/{total_chunks} ({len(cached_chunks)/total_chunks*100:.1f}%)")
    else:
        chunks_to_embed = all_chunks

    # If all cached, save and return
    if not chunks_to_embed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(Config.LOG_FOLDER, f"vectors_{timestamp}.json")
        save_json(cached_chunks, out_path)
        return f"[SUCCESS] All {total_chunks:,} chunks from cache: {out_path}"
    
    # Parallel embedding
    def embed_batch(batch_chunks: List[Dict], batch_id: int):
        for chunk in batch_chunks:
            try:
                # Use local sentence-transformers model
                embedding = embed_text(
                    chunk["text"][:8000],
                    model_name=Config.EMBED_MODEL_NAME,
                    normalize=True
                )
                embedding_list = convert_to_python_types(embedding)
                chunk["vector"] = embedding_list
                
                if cache:
                    cache.set(chunk["text"], embedding_list)
                
            except Exception as e:
                logger.error(f"Embedding failed for batch {batch_id}: {e}")
                return batch_id, [], str(e)
        
        return batch_id, batch_chunks, None

    # Process in parallel
    BATCH_SIZE = 1
    MAX_WORKERS = 5
    batches = [(chunks_to_embed[i:i + BATCH_SIZE], i // BATCH_SIZE) 
               for i in range(0, len(chunks_to_embed), BATCH_SIZE)]
    
    newly_embedded = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(embed_batch, batch, batch_id): batch_id 
                  for batch, batch_id in batches}
        
        with tqdm(total=len(batches), desc="Embedding", file=sys.stderr) as pbar:
            for future in as_completed(futures):
                _, batch_chunks, error = future.result()
                if error is None:
                    newly_embedded.extend(batch_chunks)
                pbar.update(1)

    elapsed = time.time() - start_time
    
    # Save
    if cache:
        cache.save()
    
    all_embedded = cached_chunks + newly_embedded
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(Config.LOG_FOLDER, f"vectors_{timestamp}.json")
    save_json(all_embedded, out_path)
    
    # Build FAISS index for efficient similarity search
    logger.info("Building FAISS index...")
    try:
        vectors = [chunk["vector"] for chunk in all_embedded]
        metadata = [{k: v for k, v in chunk.items() if k != "vector"} for chunk in all_embedded]
        
        faiss_index = create_faiss_index_from_vectors(
            vectors,
            metadata,
            index_type=Config.FAISS_INDEX_TYPE
        )
        
        # Save FAISS index
        index_path = os.path.join(Config.LOG_FOLDER, f"faiss_index_{timestamp}")
        faiss_index.save(index_path)
        
        # Save reference to latest index
        latest_index_path = os.path.join(Config.LOG_FOLDER, "faiss_index_latest")
        faiss_index.save(latest_index_path)
        
        logger.info(f"✅ FAISS index saved to {index_path}")
        
        faiss_stats = faiss_index.get_stats()
        return f"""✅ Vectorization complete
Total: {total_chunks:,}
Cached: {len(cached_chunks):,}
Newly embedded: {len(newly_embedded):,}
Time: {elapsed:.1f}s
Output: {out_path}
FAISS Index: {faiss_stats['index_type']} with {faiss_stats['total_vectors']:,} vectors"""
    except Exception as e:
        logger.warning(f"FAISS index creation failed: {e}")
        return f"""✅ Vectorization complete (FAISS indexing failed)
Total: {total_chunks:,}
Cached: {len(cached_chunks):,}
Newly embedded: {len(newly_embedded):,}
Time: {elapsed:.1f}s
Output: {out_path}"""


async def query_SFlogs(query: str) -> str:
    """Query vectorized logs with comprehensive hybrid retrieval"""
    from collections import defaultdict
    
    query = query.strip()
    if not query:
        return json.dumps({"error": "Query cannot be empty"})

    # Load latest vectors
    folder = Path(Config.LOG_FOLDER)
    json_files = sorted(folder.glob("vectors_*.json"), key=os.path.getmtime, reverse=True)
    if not json_files:
        return json.dumps({"error": "No vector JSON found"})
    
    data = load_json(str(json_files[0]), default=[])
    if not data:
        return json.dumps({"error": "Vector JSON is empty"})

    logger.info(f"🔍 Query: '{query}' | Total chunks: {len(data)}")

    # Embed query with local model
    try:
        q_vec = embed_text(
            query,
            model_name=Config.EMBED_MODEL_NAME,
            normalize=True
        )
        q_vec_list = q_vec.tolist()
    except Exception as e:
        return json.dumps({"error": f"Embedding failed: {e}"})

    # Query analysis
    query_lower = query.lower()
    is_summary = is_summarization_query(query)
    is_all_errors = any(k in query_lower for k in ["all errors", "all unique", "list errors"])
    
    q_words = set(re.findall(r"\w+", query_lower))
    
    # Try to use FAISS index for efficient search
    retrieved = []
    try:
        latest_index_path = os.path.join(Config.LOG_FOLDER, "faiss_index_latest")
        
        if os.path.exists(latest_index_path + ".faiss"):
            logger.info("Using FAISS index for similarity search...")
            faiss_index = FAISSIndex()
            faiss_index.load(latest_index_path)
            
            # Adaptive top-k for FAISS
            top_k = Config.FAISS_TOP_K if is_all_errors or is_summary else 75
            
            # Search with FAISS
            results, distances = faiss_index.search(q_vec, k=top_k)
            
            # Enhance with lexical matching
            for result in results:
                txt = result.get("text", "")
                txt_lower = txt.lower()
                words_in_chunk = set(re.findall(r"\w+", txt_lower))
                lex = len(q_words & words_in_chunk) / max(len(q_words), 1)
                
                # Combine FAISS similarity with lexical match
                sem = result["similarity"]
                score = 0.6 * sem + 0.25 * lex if is_all_errors or is_summary else 0.7 * sem + 0.2 * lex
                
                retrieved.append({
                    "score": float(score),
                    "path": result.get("path"),
                    "chunk": txt,
                    "semantic": float(sem),
                    "lexical": float(lex)
                })
            
            # Filter by score threshold
            score_threshold = 0.15 if is_all_errors or is_summary else 0.20
            retrieved = [r for r in retrieved if r["score"] >= score_threshold]
            
            if len(retrieved) < 10:
                retrieved = results[:min(50, len(results))]
                retrieved = [{
                    "score": r["similarity"],
                    "path": r.get("path"),
                    "chunk": r.get("text", ""),
                    "semantic": r["similarity"],
                    "lexical": 0.0
                } for r in retrieved]
            
            logger.info(f"✅ FAISS retrieved {len(retrieved)} chunks")
        else:
            raise FileNotFoundError("FAISS index not found")
    
    except Exception as e:
        # Fallback to traditional cosine similarity
        logger.warning(f"FAISS search failed, using fallback: {e}")
        scored = []
        for entry in data:
            vec = entry.get("vector", [])
            txt = entry.get("text", "")
            if not vec:
                continue

            sem = cosine_similarity(q_vec_list, vec)
            txt_lower = txt.lower()
            words_in_chunk = set(re.findall(r"\w+", txt_lower))
            lex = len(q_words & words_in_chunk) / max(len(q_words), 1)
            
            score = 0.6 * sem + 0.25 * lex if is_all_errors or is_summary else 0.7 * sem + 0.2 * lex

            scored.append({
                "score": float(score),
                "path": entry.get("path"),
                "chunk": txt,
                "semantic": float(sem),
                "lexical": float(lex)
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        
        top_k = min(150 if is_all_errors or is_summary else 75, len(scored))
        score_threshold = 0.15 if is_all_errors or is_summary else 0.20
        
        retrieved = [r for r in scored[:top_k] if r["score"] >= score_threshold]
        
        if len(retrieved) < 10 and len(scored) > 10:
            retrieved = scored[:min(50, len(scored))]
        
        logger.info(f"✅ Retrieved {len(retrieved)} chunks (fallback method)")

    # Extract errors from all retrieved chunks
    all_events = []
    metadata = {
        "timeframes": set(),
        "classes": set(),
        "methods": set()
    }
    
    for r in retrieved:
        events = extract_error_events_universal(r["chunk"], r.get("path"))
        all_events.extend(events)
        
        chunk_text = r["chunk"]
        
        # Extract metadata
        timeframes = re.findall(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', chunk_text)
        metadata["timeframes"].update(timeframes[:5])
        
        classes = re.findall(
            r'\b([A-Z][a-zA-Z0-9_]*(?:Handler|Controller|Service|Trigger|Helper|Manager))\b',
            chunk_text
        )
        metadata["classes"].update(classes[:10])
        
        methods = re.findall(r'\b([a-z][a-zA-Z0-9_]*)\s*\(', chunk_text)
        metadata["methods"].update(methods[:10])

    logger.info(f"🔍 Extracted {len(all_events)} error events")

    # No errors found - return relevant chunks
    if not all_events:
        compact = []
        for r in retrieved[:50]:
            compact.append({
                "path": r["path"],
                "chunk": r["chunk"][:15000],
                "score": r["score"]
            })
        
        result = {
            "query": query,
            "results": compact,
            "metadata": {
                "timeframes": sorted(list(metadata["timeframes"]))[:20],
                "classes": sorted(list(metadata["classes"])),
                "methods": sorted(list(metadata["methods"])),
                "total_chunks_analyzed": len(retrieved)
            },
            "message": "No errors found in matching log chunks. Showing relevant excerpts."
        }
        
        return json.dumps(convert_to_python_types(result), indent=2)

    # Cluster errors
    clusters = {}
    for ev in all_events:
        fp = ev["fingerprint"]
        if fp not in clusters:
            clusters[fp] = {
                "events": [],
                "error_type": ev["error_type"],
                "paths": set(),
                "messages": set()
            }
        clusters[fp]["events"].append(ev)
        if ev.get("path"):
            clusters[fp]["paths"].add(ev["path"])
        if ev.get("message"):
            clusters[fp]["messages"].add(ev["message"][:200])

    logger.info(f"📊 Clustered into {len(clusters)} unique error patterns")

    # Rank clusters
    cluster_list = []
    for fp, info in clusters.items():
        evs = info["events"]
        exemplar = evs[0]
        freq = len(evs)
        sev = universal_severity_rank(info["error_type"], exemplar.get("message", ""))
        
        cluster_list.append({
            "fingerprint": fp,
            "error_type": info["error_type"],
            "freq": freq,
            "severity": sev,
            "exemplar": exemplar,
            "paths": list(info["paths"])[:5],
            "unique_messages": len(info["messages"])
        })

    cluster_list.sort(key=lambda c: (c["severity"], c["freq"]), reverse=True)

    # Select representative examples
    selected = []
    budget = 35000 if is_all_errors or is_summary else 25000
    total = 0

    for c in cluster_list:
        paths_str = ", ".join(c["paths"]) if c["paths"] else "Unknown"
        snip = f"""[{c['error_type']} x{c['freq']} | Severity: {c['severity']}]
Files: {paths_str}
{c['exemplar']['excerpt']}
---"""
        
        if total + len(snip) > budget:
            remaining = len(cluster_list) - len(selected)
            if remaining > 0:
                selected.append({
                    "path": "summary",
                    "chunk": f"\n... and {remaining} more error patterns not shown",
                    "score": 0.5
                })
            break
        
        selected.append({"path": c["exemplar"].get("path", "unknown"), "chunk": snip, "score": 1.0})
        total += len(snip)

    logger.info(f"✅ Selected {len(selected)} error patterns")

    # Generate structured error analysis
    result = {
        "query": query,
        "error_patterns": selected,
        "error_analysis": {
            "total_errors": len(all_events),
            "unique_error_patterns": len(clusters),
            "clusters": [{
                "error_type": c["error_type"],
                "count": c["freq"],
                "severity": c["severity"],
                "affected_files": len(c["paths"])
            } for c in cluster_list],
            "metadata": {
                "timeframes": sorted(list(metadata["timeframes"]))[:20],
                "classes": sorted(list(metadata["classes"])),
                "methods": sorted(list(metadata["methods"]))
            },
            "retrieval_stats": {
                "chunks_analyzed": len(retrieved),
                "total_chunks": len(data),
                "coverage_percentage": round(len(retrieved) / len(data) * 100, 2)
            }
        }
    }
    
    return json.dumps(convert_to_python_types(result), indent=2)


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

async def async_main():
    """Async entry point for the MCP server"""
    # Ensure configuration is valid
    if not Config.validate():
        logger.error("Configuration validation failed. Please check your .env file.")
        sys.exit(1)
    
    # Ensure required folders exist
    Config.ensure_folders()
    
    logger.info("Starting Log Analyzer MCP Server...")
    logger.info(f"Log folder: {Config.LOG_FOLDER}")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    """Main entry point for the MCP server (sync wrapper)"""
    import asyncio
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
