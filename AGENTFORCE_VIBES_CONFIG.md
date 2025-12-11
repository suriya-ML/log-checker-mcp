# MCP Server Configuration for Agentforce Vibes

## Your Log Analyzer MCP Server Configuration

Add this to your Agentforce Vibes remote MCP servers:

```json
{
  "name": "Log Analyzer FAISS",
  "description": "Local FAISS-powered log analysis with semantic search, error detection, and pattern clustering. 100% local, no cloud APIs, 30-150x faster than traditional search.",
  "url": "git+https://github.com/suriya-ML/log-checker-mcp.git",
  "type": "uvx",
  "config": {
    "command": "uvx",
    "args": [
      "--from",
      "git+https://github.com/suriya-ML/log-checker-mcp.git",
      "log-analyzer-mcp"
    ],
    "env": {
      "LOG_FOLDER": "/path/to/logs"
    }
  },
  "tools": [
    {
      "name": "fetch_local_logs",
      "description": "Fetch and chunk local log files with configurable size and overlap",
      "parameters": {
        "input_folder": "Path to folder containing log files (optional)",
        "chunk_size": "Size of each chunk in characters (default: 4096)",
        "overlap": "Overlap between chunks in characters (default: 1024)"
      }
    },
    {
      "name": "store_chunks_as_vectors",
      "description": "Vectorize log chunks with local embeddings and build FAISS index for fast similarity search",
      "parameters": {
        "use_cache": "Whether to use embedding cache (default: true)",
        "clear_cache": "Whether to clear cache before starting (default: false)"
      }
    },
    {
      "name": "query_SFlogs",
      "description": "Query vectorized logs with semantic search, hybrid retrieval, and intelligent error analysis",
      "parameters": {
        "query": "Natural language query to search logs (required)"
      }
    }
  ],
  "features": [
    "Semantic log search with FAISS",
    "30-150x faster than traditional search",
    "Intelligent error pattern detection",
    "Local sentence-transformers embeddings",
    "Smart caching for instant re-indexing",
    "Hybrid semantic + lexical retrieval",
    "No cloud APIs required",
    "Zero cost operation"
  ],
  "requirements": {
    "python": ">=3.9",
    "packages": [
      "mcp>=0.9.0",
      "sentence-transformers>=2.2.0",
      "numpy>=1.24.0",
      "faiss-cpu>=1.7.4",
      "torch>=2.0.0"
    ]
  }
}
```

## Compact Version (Minimal)

```json
{
  "name": "Log Analyzer FAISS",
  "url": "git+https://github.com/suriya-ML/log-checker-mcp.git",
  "command": "uvx",
  "args": ["--from", "git+https://github.com/suriya-ML/log-checker-mcp.git", "log-analyzer-mcp"]
}
```

## For Python-based Remote MCP Configuration

```python
mcp_server = {
    "name": "log-analyzer-faiss",
    "repository": "https://github.com/suriya-ML/log-checker-mcp.git",
    "type": "git",
    "runner": "uvx",
    "description": "FAISS-powered log analysis with semantic search",
    "tools": ["fetch_local_logs", "store_chunks_as_vectors", "query_SFlogs"],
    "env": {
        "LOG_FOLDER": "/default/log/path"
    }
}
```

## For REST API Configuration

```json
{
  "mcpServer": {
    "id": "log-analyzer-faiss",
    "name": "Log Analyzer FAISS",
    "repository": "https://github.com/suriya-ML/log-checker-mcp.git",
    "branch": "main",
    "type": "uvx",
    "enabled": true,
    "autoUpdate": true,
    "config": {
      "env": {
        "LOG_FOLDER": "${USER_LOG_FOLDER}"
      }
    },
    "capabilities": {
      "tools": true,
      "resources": false,
      "prompts": false
    }
  }
}
```

## For YAML Configuration

```yaml
name: log-analyzer-faiss
description: Local FAISS-powered log analysis with semantic search
repository: https://github.com/suriya-ML/log-checker-mcp.git
type: uvx
runner:
  command: uvx
  args:
    - --from
    - git+https://github.com/suriya-ML/log-checker-mcp.git
    - log-analyzer-mcp
environment:
  LOG_FOLDER: /path/to/logs
tools:
  - name: fetch_local_logs
    description: Fetch and chunk local log files
  - name: store_chunks_as_vectors
    description: Vectorize logs with FAISS indexing
  - name: query_SFlogs
    description: Semantic log search with error analysis
features:
  - semantic_search
  - faiss_indexing
  - error_detection
  - local_processing
  - zero_cost
```

## For Agentforce Registry Format

```json
{
  "serverDefinition": {
    "identifier": "suriya-ML/log-checker-mcp",
    "displayName": "Log Analyzer FAISS",
    "description": "Local FAISS-powered log analysis with semantic search, error detection, and pattern clustering. 30-150x faster than traditional search.",
    "category": "analytics",
    "tags": ["logs", "faiss", "semantic-search", "error-detection", "local"],
    "author": "suriya-ML",
    "license": "MIT",
    "repository": {
      "type": "github",
      "url": "https://github.com/suriya-ML/log-checker-mcp"
    },
    "installation": {
      "type": "uvx",
      "package": "git+https://github.com/suriya-ML/log-checker-mcp.git"
    },
    "runtime": {
      "type": "python",
      "minVersion": "3.9"
    },
    "configuration": {
      "required": [],
      "optional": [
        {
          "name": "LOG_FOLDER",
          "type": "string",
          "description": "Path to log files directory",
          "default": "./logs"
        },
        {
          "name": "EMBED_MODEL",
          "type": "string",
          "description": "Sentence-transformers model name",
          "default": "all-MiniLM-L6-v2"
        },
        {
          "name": "FAISS_INDEX_TYPE",
          "type": "string",
          "description": "FAISS index type",
          "default": "IVFFlat",
          "enum": ["Flat", "IVFFlat", "IVFPQ", "HNSW"]
        }
      ]
    },
    "tools": [
      {
        "name": "fetch_local_logs",
        "description": "Fetch and chunk local log files with configurable chunk size and overlap",
        "inputSchema": {
          "type": "object",
          "properties": {
            "input_folder": {
              "type": "string",
              "description": "Path to folder containing log files"
            },
            "chunk_size": {
              "type": "integer",
              "description": "Size of each chunk in characters",
              "default": 4096
            },
            "overlap": {
              "type": "integer",
              "description": "Overlap between chunks in characters",
              "default": 1024
            }
          }
        }
      },
      {
        "name": "store_chunks_as_vectors",
        "description": "Vectorize log chunks with local embeddings and build FAISS index",
        "inputSchema": {
          "type": "object",
          "properties": {
            "use_cache": {
              "type": "boolean",
              "description": "Whether to use embedding cache",
              "default": true
            },
            "clear_cache": {
              "type": "boolean",
              "description": "Whether to clear cache before starting",
              "default": false
            }
          }
        }
      },
      {
        "name": "query_SFlogs",
        "description": "Query vectorized logs with semantic search and error analysis",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "Natural language query to search logs"
            }
          },
          "required": ["query"]
        }
      }
    ],
    "metrics": {
      "performance": "30-150x faster than traditional search",
      "cost": "$0 (100% local)",
      "privacy": "Complete (no cloud APIs)"
    }
  }
}
```

## Quick Copy-Paste for Most Systems

```json
{
  "name": "log-analyzer-faiss",
  "url": "git+https://github.com/suriya-ML/log-checker-mcp.git",
  "type": "uvx",
  "description": "FAISS-powered log analysis with semantic search"
}
```

## Environment Variables (Optional)

```bash
LOG_FOLDER=/path/to/logs
EMBED_MODEL=all-MiniLM-L6-v2
FAISS_INDEX_TYPE=IVFFlat
FAISS_NLIST=100
FAISS_NPROBE=10
FAISS_TOP_K=150
```

Choose the format that matches your Agentforce Vibes configuration system!
