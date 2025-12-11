# 🚀 Quick Start: Use from GitHub

Your MCP server is now live at: **https://github.com/suriya-ML/log-checker-mcp**

## For You (Using Your Own Server)

### Option 1: Direct from GitHub (Recommended)

**Install uv:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/suriya-ML/log-checker-mcp.git",
        "log-analyzer-mcp"
      ],
      "env": {
        "LOG_FOLDER": "C:\\path\\to\\your\\logs"
      }
    }
  }
}
```

**Config Location:** `C:\Users\YOUR-USERNAME\AppData\Roaming\Claude\claude_desktop_config.json`

### Option 2: Local Development

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": ["-u", "-m", "server"],
      "cwd": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "LOG_FOLDER": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp\\logs"
      }
    }
  }
}
```

## For Others (Using Your Published Server)

Anyone can use your server with:

```powershell
# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/suriya-ML/log-checker-mcp.git",
        "log-analyzer-mcp"
      ]
    }
  }
}
```

That's it! uvx automatically:
- Clones the repo
- Installs dependencies
- Runs the server
- Updates on restart

## After Configuration

1. **Restart Claude Desktop** completely
2. **Look for 🔌 icon**
3. **Test:** "List available MCP tools"

Should show:
- ✅ `fetch_local_logs`
- ✅ `store_chunks_as_vectors`
- ✅ `query_SFlogs`

## Features

- 🚀 **100% Local** - No cloud APIs, no costs
- ⚡ **FAISS-powered** - 30-150x faster than traditional search
- 🔍 **Semantic Search** - Find logs by meaning, not just keywords
- 🐛 **Error Analysis** - Intelligent error pattern detection
- 💾 **Smart Caching** - Instant re-indexing

## Example Usage

```
"Use fetch_local_logs to process logs from C:\logs"

"Use store_chunks_as_vectors to create embeddings"

"Use query_SFlogs to find authentication errors"
```

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues.

**Quick fix checklist:**
- [ ] uv installed: `uv --version`
- [ ] Config in correct location
- [ ] Claude Desktop restarted completely
- [ ] Check logs: `%APPDATA%\Claude\logs\`

## Repository

**GitHub:** https://github.com/suriya-ML/log-checker-mcp

**Updates:** Automatic on Claude Desktop restart (when using uvx)

---

**Your log analyzer is production-ready!** 🎉
