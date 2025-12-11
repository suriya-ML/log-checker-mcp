# Agentforce Vibes MCP Server Configuration

## Add Log Analyzer to Agentforce Vibes

Copy this exact format to add the Log Analyzer MCP server to your Agentforce Vibes:

```json
{
  "mcpServers": {
    "https://github.com/suriya-ML/log-checker-mcp": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 600,
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/suriya-ML/log-checker-mcp.git",
        "python",
        "-m",
        "server"
      ]
    }
  }
}
```

## With Both Servers (Salesforce + Log Analyzer)

```json
{
  "mcpServers": {
    "https://github.com/salesforcecli/mcp": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 600,
      "type": "stdio",
      "command": "node",
      "args": [
        "/home/codebuilder/.local/share/code-server/User/globalStorage/salesforce.salesforcedx-einstein-gpt/MCP/a4d-mcp-wrapper.js",
        "@salesforce/mcp@latest",
        "--orgs",
        "ALLOW_ALL_ORGS",
        "--toolsets",
        "metadata",
        "--tools",
        "get_username,run_apex_test,run_soql_query,guide_lwc_development,orchestrate_lwc_component_creation,guide_lwc_accessibility,create_lwc_component_from_prd,assign_permission_set,list_all_orgs,list_devops_center_projects,list_devops_center_work_items,create_devops_center_pull_request,promote_devops_center_work_item,commit_devops_center_work_item,check_devops_center_commit_status,checkout_devops_center_work_item,run_code_analyzer,describe_code_analyzer_rule,detect_devops_center_merge_conflict,resolve_devops_center_merge_conflict"
      ]
    },
    "https://github.com/suriya-ML/log-checker-mcp": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 600,
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/suriya-ML/log-checker-mcp.git",
        "python",
        "-m",
        "server"
      ]
    }
  }
}
```

## With Custom Environment Variables

```json
{
  "mcpServers": {
    "https://github.com/suriya-ML/log-checker-mcp": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 600,
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/suriya-ML/log-checker-mcp.git",
        "python",
        "-m",
        "server"
      ],
      "env": {
        "LOG_FOLDER": "/path/to/your/logs",
        "EMBED_MODEL": "all-MiniLM-L6-v2",
        "FAISS_INDEX_TYPE": "IVFFlat"
      }
    }
  }
}
```

## Available Tools

Once configured, these tools will be available in Agentforce Vibes:

1. **fetch_local_logs**
   - Fetch and chunk local log files
   - Parameters: `input_folder`, `chunk_size`, `overlap`

2. **store_chunks_as_vectors**
   - Vectorize logs with FAISS indexing
   - Parameters: `use_cache`, `clear_cache`

3. **query_SFlogs**
   - Semantic log search with error analysis
   - Parameters: `query` (required)

## Features

- ⚡ 30-150x faster than traditional log search
- 🏠 100% local processing (no cloud APIs)
- 💰 Zero cost operation
- 🔍 Semantic search with FAISS
- 🐛 Intelligent error pattern detection
- 💾 Smart caching for instant re-indexing

## Installation

The MCP server will be automatically installed from GitHub when Agentforce Vibes starts.

**Repository:** https://github.com/suriya-ML/log-checker-mcp

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `LOG_FOLDER` | Path to log files directory | `./logs` |
| `EMBED_MODEL` | Sentence-transformers model | `all-MiniLM-L6-v2` |
| `FAISS_INDEX_TYPE` | FAISS index type | `IVFFlat` |
| `FAISS_NLIST` | Number of clusters | `100` |
| `FAISS_NPROBE` | Search clusters | `10` |
| `FAISS_TOP_K` | Max results | `150` |

## Quick Start

1. Copy the JSON configuration above
2. Add to your Agentforce Vibes MCP configuration
3. Restart Agentforce Vibes
4. Tools will be automatically available

## Example Usage

```
"Use fetch_local_logs to process logs from /var/log"

"Use store_chunks_as_vectors to create embeddings"

"Use query_SFlogs to find authentication errors in the last 24 hours"
```

## Troubleshooting

**If tools don't appear:**
- Check that `uvx` is installed
- Verify GitHub repository is accessible
- Check Agentforce Vibes logs for errors

**For detailed troubleshooting:**
See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) in the repository.
