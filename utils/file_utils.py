"""
File and directory utilities
"""
import os
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from .logging_utils import get_logger

logger = get_logger(__name__)


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, create if it doesn't
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {dir_path}")
    return dir_path


def clean_directory(path: str, create_after: bool = True) -> None:
    """
    Remove all contents of a directory
    
    Args:
        path: Directory path
        create_after: Whether to recreate the directory after cleaning
    """
    dir_path = Path(path)
    
    if dir_path.exists():
        shutil.rmtree(dir_path)
        logger.info(f"Cleaned directory: {dir_path}")
    
    if create_after:
        dir_path.mkdir(parents=True, exist_ok=True)


def load_json(file_path: str, default: Any = None) -> Any:
    """
    Load JSON from file with error handling
    
    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid
    
    Returns:
        Parsed JSON data or default value
    """
    path = Path(file_path)
    
    if not path.exists():
        logger.warning(f"JSON file not found: {file_path}")
        return default
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return default
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return default


def save_json(data: Any, file_path: str, indent: int = 2) -> bool:
    """
    Save data as JSON to file
    
    Args:
        data: Data to save
        file_path: Path to save to
        indent: JSON indentation level
    
    Returns:
        True if successful, False otherwise
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.debug(f"Saved JSON to: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in bytes or None if file doesn't exist
    """
    path = Path(file_path)
    
    if not path.exists():
        return None
    
    return path.stat().st_size


def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> list:
    """
    List files in a directory
    
    Args:
        directory: Directory path
        pattern: File pattern (e.g., "*.txt")
        recursive: Whether to search recursively
    
    Returns:
        List of file paths
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        logger.warning(f"Directory not found: {directory}")
        return []
    
    if recursive:
        return [str(p) for p in dir_path.rglob(pattern) if p.is_file()]
    else:
        return [str(p) for p in dir_path.glob(pattern) if p.is_file()]


def ensure_dir(path: str) -> None:
    """
    Ensure a directory exists (simple version for compatibility)
    
    Args:
        path: Directory path
    """
    os.makedirs(path, exist_ok=True)


def save_chunk_txt(chunk: str, rel_source: str, outdir: str, idx: int) -> str:
    """
    Save a text chunk to file
    
    Args:
        chunk: Text content to save
        rel_source: Relative path of source file
        outdir: Output directory
        idx: Chunk index
    
    Returns:
        Path to saved chunk file
    """
    stem, _ = os.path.splitext(rel_source)
    subdir = os.path.join(outdir, os.path.dirname(stem))
    ensure_dir(subdir)
    out_name = f"{os.path.basename(stem)}__chunk{idx:04d}.txt"
    out_path = os.path.join(subdir, out_name)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(chunk)
    return out_path


def append_jsonl(jsonl_path: str, source_rel: str, chunk_idx: int, unit: str, content: str) -> None:
    """
    Append a record to JSONL file
    
    Args:
        jsonl_path: Path to JSONL file
        source_rel: Relative source path
        chunk_idx: Chunk index
        unit: Chunking unit (chars, words, lines)
        content: Chunk content
    """
    ensure_dir(os.path.dirname(jsonl_path) or ".")
    with open(jsonl_path, "a", encoding="utf-8") as j:
        rec = {
            "source": source_rel,
            "chunk_index": chunk_idx,
            "unit": unit,
            "length": len(content),
            "content": content,
        }
        j.write(json.dumps(rec, ensure_ascii=False) + "\n")
