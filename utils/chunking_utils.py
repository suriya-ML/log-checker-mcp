"""
Text chunking utilities for log and code files
Supports character, word, and line-based chunking with memory and streaming modes
"""
import os
from typing import List, Generator, Tuple, TextIO
from collections import deque
from config import Config
LOG_EXTENSIONS = Config.LOG_EXTENSIONS

def validate_chunker(size: int, overlap: int) -> None:
    """
    Validate chunking parameters
    
    Args:
        size: Chunk size 
        overlap: Overlap between chunks
    
    Raises:
        ValueError: If parameters are invalid
    """
    if size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= size:
        raise ValueError("overlap must be < chunk_size")


def iter_local_logs(folder_path: str) -> Generator[Tuple[str, str], None, None]:
    """Yield (relative_path, absolute_path) for each eligible log under folder_path."""
    base = os.path.abspath(os.path.expanduser(folder_path))
    for root, _, files in os.walk(base):
        for f in files:
            if f.lower().endswith(LOG_EXTENSIONS):
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, base)
                yield rel_path, abs_path


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Simple text chunking by characters
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# ---------------------------------------------------------------------------
# Memory-based chunking (loads entire text into memory)
# ---------------------------------------------------------------------------

def chunks_chars_mem(text: str, size: int, overlap: int) -> List[str]:
    """
    Chunk text by characters in memory
    
    Args:
        text: Text to chunk
        size: Chunk size in characters
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    validate_chunker(size, overlap)
    step = size - overlap
    out = []
    i = 0
    n = len(text)
    while i < n:
        out.append(text[i:i+size])
        if i + size >= n:
            break
        i += step
    return out


def chunks_words_mem(text: str, size: int, overlap: int) -> List[str]:
    """
    Chunk text by words in memory
    
    Args:
        text: Text to chunk
        size: Chunk size in words
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    validate_chunker(size, overlap)
    words = text.split()
    step = size - overlap
    out = []
    i, n = 0, len(words)
    while i < n:
        out.append(" ".join(words[i:i+size]))
        if i + size >= n:
            break
        i += step
    return out


def chunks_lines_mem(text: str, size: int, overlap: int) -> List[str]:
    """
    Chunk text by lines in memory
    
    Args:
        text: Text to chunk
        size: Chunk size in lines
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    validate_chunker(size, overlap)
    lines = text.splitlines(keepends=True)
    step = size - overlap
    out = []
    i, n = 0, len(lines)
    while i < n:
        out.append("".join(lines[i:i+size]))
        if i + size >= n:
            break
        i += step
    return out


# ---------------------------------------------------------------------------
# Streaming chunking (for large files)
# ---------------------------------------------------------------------------

def stream_chunks_chars(f: TextIO, size: int, overlap: int, read_size: int = 65536) -> Generator[str, None, None]:
    """
    Stream chunks by characters from file
    
    Args:
        f: File object to read from
        size: Chunk size in characters
        overlap: Overlap between chunks
        read_size: Buffer size for reading
    
    Yields:
        Text chunks
    """
    validate_chunker(size, overlap)
    step = size - overlap
    buf = ""
    while True:
        data = f.read(read_size)
        if not data:
            break
        buf += data
        while len(buf) >= size:
            yield buf[:size]
            buf = buf[step:]
    if buf:
        yield buf


def stream_chunks_words(f: TextIO, size: int, overlap: int, read_size: int = 65536) -> Generator[str, None, None]:
    """
    Stream chunks by words from file
    
    Args:
        f: File object to read from
        size: Chunk size in words
        overlap: Overlap between chunks
        read_size: Buffer size for reading
    
    Yields:
        Text chunks
    """
    validate_chunker(size, overlap)
    step = size - overlap
    token_buf: List[str] = []
    carry = ""
    while True:
        data = f.read(read_size)
        if not data:
            break
        data = carry + data
        parts = data.split()
        ends_with_space = bool(data) and data[-1].isspace()
        if not ends_with_space:
            if parts:
                carry = parts.pop()
            else:
                carry = data
        else:
            carry = ""
        token_buf.extend(parts)
        while len(token_buf) >= size:
            chunk_tokens = token_buf[:size]
            yield " ".join(chunk_tokens)
            token_buf = token_buf[step:]
    if carry:
        token_buf.append(carry)
    if token_buf:
        yield " ".join(token_buf)


def stream_chunks_lines(f: TextIO, size: int, overlap: int) -> Generator[str, None, None]:
    """
    Stream chunks by lines from file
    
    Args:
        f: File object to read from
        size: Chunk size in lines
        overlap: Overlap between chunks
    
    Yields:
        Text chunks
    """
    validate_chunker(size, overlap)
    step = size - overlap
    window: deque[str] = deque()
    for line in f:
        window.append(line)
        if len(window) == size:
            yield "".join(window)
            for _ in range(step):
                if window:
                    window.popleft()
    if window:
        yield "".join(window)
