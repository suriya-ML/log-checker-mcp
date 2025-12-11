"""
Error extraction utilities for log analysis
Supports multiple formats: Python, Java/Apex, .NET, web servers, and generic errors
"""
import re
import hashlib
from typing import List, Dict, Tuple, Optional


# ---------- Normalization helpers ----------
_ID_HEX_RE = re.compile(r'\b[0-9a-f]{8,}\b', re.IGNORECASE)
_ID_UUID_RE = re.compile(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b', re.IGNORECASE)
_NUM_RE = re.compile(r'\b\d+\b')


def normalize_text_for_fingerprint(s: str, limit: int = 400) -> str:
    """
    Normalize text for deduplication by removing volatile identifiers
    
    Args:
        s: Text to normalize
        limit: Maximum character length
    
    Returns:
        Normalized text string
    """
    s = s.replace('\r\n', '\n')
    s = _ID_UUID_RE.sub('<UUID>', s)
    s = _ID_HEX_RE.sub('<HEX>', s)
    s = _NUM_RE.sub('<NUM>', s)
    s = s.strip().lower()
    return s[:limit]


def sha1_hash(s: str) -> str:
    """
    Generate SHA1 hash of string
    
    Args:
        s: String to hash
    
    Returns:
        Hexadecimal SHA1 hash
    """
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


# ---------- Format-specific extractors ----------

def extract_python_tracebacks(text: str) -> List[Tuple[str, Dict]]:
    """
    Extract Python tracebacks: Traceback (most recent call last): ... Exception: msg
    
    Args:
        text: Log text to parse
    
    Returns:
        List of (block_text, metadata) tuples
    """
    res = []
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n:
        if lines[i].startswith("Traceback (most recent call last):"):
            block = [lines[i]]
            i += 1
            # Collect stack frames (lines starting with "  File" or "    ")
            while i < n and (lines[i].startswith('  File') or lines[i].startswith('    ')):
                block.append(lines[i])
                i += 1
            # Final exception line(s)
            tail = []
            while i < n and (('Error' in lines[i]) or ('Exception' in lines[i]) or lines[i].startswith('During handling')):
                tail.append(lines[i])
                i += 1
            block.extend(tail)
            if len(block) > 1:
                res.append(('\n'.join(block).strip(), {"type": "PythonException"}))
            continue
        i += 1
    return res


_JAVA_HEAD_RE = re.compile(r'.*(Exception|Error|Throwable)(:|\s|$)', re.IGNORECASE)
_JAVA_FRAME_RE = re.compile(r'^\s*at\s+[\w$.]+\(.*\)$')


def extract_java_like(text: str) -> List[Tuple[str, Dict]]:
    """
    Extract Java/Apex/Node style exceptions with 'at' stack frames
    
    Args:
        text: Log text to parse
    
    Returns:
        List of (block_text, metadata) tuples
    """
    res = []
    lines = text.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        if _JAVA_HEAD_RE.match(lines[i]) or lines[i].strip().startswith('FATAL_ERROR'):
            block = [lines[i]]
            i += 1
            frame_count = 0
            while i < n and (_JAVA_FRAME_RE.match(lines[i]) or
                              'Caused by:' in lines[i] or
                              'Stack Trace' in lines[i] or
                              'StackTrace' in lines[i]):
                block.append(lines[i])
                if _JAVA_FRAME_RE.match(lines[i]):
                    frame_count += 1
                i += 1
            if frame_count >= 1:
                # crude classifier for Apex / Java / Node
                t = "ApexException" if "FATAL_ERROR" in block[0] or "System." in block[0] else "JavaLikeException"
                res.append(('\n'.join(block).strip(), {"type": t}))
            else:
                # Single-line ERROR / Exception (still capture)
                if ('Exception' in block[0] or 'ERROR' in block[0] or 'FATAL' in block[0]):
                    res.append((block[0].strip(), {"type": "GenericError"}))
            continue
        i += 1
    return res


_DOTNET_FRAME_RE = re.compile(r'^\s*at\s+[\w$.`]+\([^\)]*\)\s*(in\s+.*?:line\s+\d+)?\s*$', re.IGNORECASE)


def extract_dotnet(text: str) -> List[Tuple[str, Dict]]:
    """
    Extract C#/.NET stack traces with file:line info
    
    Args:
        text: Log text to parse
    
    Returns:
        List of (block_text, metadata) tuples
    """
    res = []
    lines = text.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        if ('Exception:' in lines[i]) or lines[i].strip().endswith('Exception') or 'System.' in lines[i]:
            block = [lines[i]]
            i += 1
            frame_count = 0
            while i < n and (_DOTNET_FRAME_RE.match(lines[i]) or '--- End of stack trace' in lines[i]):
                block.append(lines[i])
                if _DOTNET_FRAME_RE.match(lines[i]):
                    frame_count += 1
                i += 1
            if frame_count > 0:
                res.append(('\n'.join(block).strip(), {"type": "DotNetException"}))
            continue
        i += 1
    return res


_NGINX_APACHE_RE = re.compile(r'^\S+\s+\S+\s+\S+\s+\[(error|crit|alert|emerg)\]\s+\S+:\s+.*$', re.IGNORECASE)


def extract_nginx_apache(text: str) -> List[Tuple[str, Dict]]:
    """
    Extract Nginx/Apache error log entries
    
    Args:
        text: Log text to parse
    
    Returns:
        List of (block_text, metadata) tuples
    """
    res = []
    for ln in text.splitlines():
        if _NGINX_APACHE_RE.match(ln):
            res.append((ln.strip(), {"type": "WebServerError"}))
    return res


_GENERIC_ERR_RE = re.compile(r'(ERROR|CRITICAL|FATAL|EXCEPTION|Exception|Traceback|Unhandled)', re.IGNORECASE)


def extract_generic(text: str, context_lines: int = 6) -> List[Tuple[str, Dict]]:
    """
    Fallback: capture lines with ERROR/Exception keywords and surrounding context
    
    Args:
        text: Log text to parse
        context_lines: Number of lines to include after match
    
    Returns:
        List of (block_text, metadata) tuples
    """
    res = []
    lines = text.splitlines()
    n = len(lines)
    for i, ln in enumerate(lines):
        if _GENERIC_ERR_RE.search(ln):
            block = [ln]
            for j in range(1, min(context_lines, n - i)):
                nxt = lines[i + j]
                # stop early if blank gap
                if not nxt.strip():
                    break
                block.append(nxt)
            res.append(('\n'.join(block).strip(), {"type": "GenericError"}))
    return res


# ---------- Universal extractor ----------

_ERR_TYPE_EXTRACT_RE = re.compile(
    r'([A-Za-z_][A-Za-z0-9_\.]*Exception|System\.\w+Exception|Apex\.\w+Exception|Error|ERROR|FATAL)', re.IGNORECASE
)


def extract_error_events_universal(text: str, path: Optional[str] = None) -> List[Dict]:
    """
    Try multiple format-specific extractors, then unify, normalize, and fingerprint.
    
    Args:
        text: Log text to parse
        path: Optional file path for context
    
    Returns:
        List of error event dictionaries with fingerprint, error_type, message, excerpt, path
    """
    candidates = []
    # Order matters: specific → generic
    for fn in (extract_python_tracebacks,
               extract_dotnet,
               extract_java_like,
               extract_nginx_apache,
               extract_generic):
        try:
            candidates.extend(fn(text))
        except Exception:
            pass

    events = []
    seen_blocks = set()
    for block_text, meta in candidates:
        key = sha1_hash(block_text[:800])
        if key in seen_blocks:
            continue
        seen_blocks.add(key)

        # Derive error_type + message
        head = block_text.splitlines()[0] if block_text else ""
        m = _ERR_TYPE_EXTRACT_RE.search(head) or _ERR_TYPE_EXTRACT_RE.search(block_text)
        err_type = m.group(0) if m else (meta.get("type") if meta else "UnknownError")

        # Build a message stem from head (strip volatile bits)
        message_stem = normalize_text_for_fingerprint(head, limit=220)

        # Extract up to first 5 "frames" for fingerprint when present
        frame_lines = []
        for ln in block_text.splitlines()[1:]:
            if ln.lstrip().startswith("at "):           # Java/Node/.NET style
                frame_lines.append(ln.strip())
            elif ln.lstrip().startswith("File ") or ln.lstrip().startswith('File "'):  # Python
                frame_lines.append(ln.strip())
            elif "Caused by:" in ln or "StackTrace" in ln:
                frame_lines.append(ln.strip())
            if len(frame_lines) >= 5:
                break
        top_frames = "|".join(normalize_text_for_fingerprint(fl, 140) for fl in frame_lines)

        fp_src = f"{err_type}|{message_stem}|{top_frames}"
        fingerprint = sha1_hash(fp_src)

        events.append({
            "fingerprint": fingerprint,
            "error_type": err_type,
            "message": head.strip(),
            "excerpt": block_text[:4000],
            "path": path
        })
    return events


def universal_severity_rank(err_type: str, msg: str) -> int:
    """
    Rank error severity based on keywords
    
    Args:
        err_type: Error type string
        msg: Error message
    
    Returns:
        Severity rank (1-5, higher is more severe)
    """
    s = f"{err_type} {msg}".lower()
    if any(k in s for k in ("fatal", "panic", "outofmemory", "out of memory", "segfault", "emerg")):
        return 5
    if any(k in s for k in ("crash", "deadlock", "data loss", "corrupt")):
        return 4
    if any(k in s for k in ("timeout", "deadline", "nullpointer", "null pointer", "unauthorized", "permission", "access denied")):
        return 3
    if any(k in s for k in ("error", "exception", "assert")):
        return 2
    if any(k in s for k in ("warn", "warning")):
        return 1
    return 0
