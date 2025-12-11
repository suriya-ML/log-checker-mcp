# Deployment Guide for Log Analyzer MCP Server

## Quick Start: Deploy to GitHub & Use as MCP Server

### Step 1: Push to GitHub

```bash
# Navigate to your project
cd "c:\Users\V0411759\Documents\AI TEST\log-analyzer-mcp"

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Local FAISS-based log analyzer MCP server"

# Create repo on GitHub, then add remote
git remote add origin https://github.com/YOUR-USERNAME/log-analyzer-mcp.git
git branch -M main
git push -u origin main
```

### Step 2: Configure Claude Desktop

**Location:** `C:\Users\YOUR-USERNAME\AppData\Roaming\Claude\claude_desktop_config.json`

#### Option A: Local Development (Best for Testing)

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp",
      "env": {
        "LOG_FOLDER": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp\\logs",
        "EMBED_MODEL": "all-MiniLM-L6-v2"
      }
    }
  }
}
```

#### Option B: Using uvx (Best for Production)

```bash
# First install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then configure Claude:
```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/YOUR-USERNAME/log-analyzer-mcp.git",
        "log-analyzer-mcp"
      ],
      "env": {
        "LOG_FOLDER": "C:\\path\\to\\your\\logs"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. Look for 🔌 icon - your tools should appear

## Installation from GitHub

### For End Users

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/log-analyzer-mcp.git
cd log-analyzer-mcp

# Install dependencies (NO AWS credentials needed!)
pip install -r requirements.txt

# Test the server
python server.py
```

## Claude Desktop Configuration by Platform

### Windows

**Config file:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "C:\\Users\\YOUR-USERNAME\\log-analyzer-mcp",
      "env": {
        "LOG_FOLDER": "C:\\path\\to\\logs",
        "EMBED_MODEL": "all-MiniLM-L6-v2"
      }
    }
  }
}
```

### macOS

**Config file:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python3",
      "args": ["-m", "server"],
      "cwd": "/Users/YOUR-USERNAME/log-analyzer-mcp",
      "env": {
        "LOG_FOLDER": "/path/to/logs",
        "EMBED_MODEL": "all-MiniLM-L6-v2"
      }
    }
  }
}
```

### Linux

**Config file:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python3",
      "args": ["-m", "server"],
      "cwd": "/home/YOUR-USERNAME/log-analyzer-mcp",
      "env": {
        "LOG_FOLDER": "/path/to/logs",
        "EMBED_MODEL": "all-MiniLM-L6-v2"
      }
    }
  }
}
```

## Testing the MCP Server

### 1. Test Locally

```bash
# Navigate to project
cd log-analyzer-mcp

# Run the server
python server.py

# Should see:
# Starting Log Analyzer MCP Server...
# Using local embedding model: all-MiniLM-L6-v2
```

### 2. Test with Claude Desktop

1. Configure Claude Desktop (see configurations above)
2. **Restart Claude Desktop completely**
3. Open a new conversation
4. Look for 🔌 icon - should show "log-analyzer" server
5. Test: "Use fetch_local_logs to process logs from ./logs"

### 3. Available Tools in Claude

Once configured, these tools appear:
- **fetch_local_logs** - Process log files into chunks
- **store_chunks_as_vectors** - Create embeddings & FAISS index
- **query_SFlogs** - Semantic search with error analysis

## Troubleshooting

### "Server not found" or "Connection refused"

**Check:**
1. Config file path is correct
2. `cwd` path is absolute (not relative)
3. Python is in PATH
4. Dependencies installed: `pip list | grep faiss`

**Solution:**
```bash
# Verify Python path
where python  # Windows
which python3  # Mac/Linux

# Use full path in config
"command": "C:\\Python311\\python.exe"  # Windows example
```

### "Module 'server' not found"

**Solution:** Use `-m server` instead of `server.py`
```json
"args": ["-m", "server"]  // Correct
```

### "Model download fails"

**First run downloads ~90MB model**

**Solution:** Pre-download:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### "FAISS not installed"

**Solution:**
```bash
pip install faiss-cpu
```

### Claude Desktop logs

**Check logs for errors:**
- **Windows:** `%APPDATA%\Claude\logs\`
- **macOS:** `~/Library/Logs/Claude/`
- **Linux:** `~/.config/Claude/logs/`

## Sharing Your MCP Server

### Public Repository (Recommended)

Once pushed to GitHub, others can use:

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/YOUR-USERNAME/log-analyzer-mcp.git",
        "log-analyzer-mcp"
      ]
    }
  }
}
```

**Users just need:**
1. Install uv: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Add config above
3. Restart Claude

### Adding to MCP Servers List

Consider submitting to [MCP Servers repository](https://github.com/modelcontextprotocol/servers) for community discoverability.

## Best Practices

### 1. Version Your Releases

```bash
git tag -a v1.0.0 -m "Initial release: Local FAISS-based log analyzer"
git push origin v1.0.0
```

Users can pin to version:
```json
"git+https://github.com/YOUR-USERNAME/log-analyzer-mcp.git@v1.0.0"
```

### 2. Add Comprehensive README

Include in your `README.md`:
- Quick start guide
- Claude Desktop configuration example
- Available tools and their parameters
- Configuration options
- Troubleshooting section

### 3. Use .gitignore

```
# .gitignore
.env
logs/
*.faiss
*.metadata
*.pyc
__pycache__/
.venv/
*.egg-info/
.embedding_cache/
```

### 4. Document Environment Variables

```markdown
## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| LOG_FOLDER | Path to log files | ./logs |
| EMBED_MODEL | Embedding model name | all-MiniLM-L6-v2 |
| FAISS_INDEX_TYPE | Index type | IVFFlat |
| FAISS_NLIST | Number of clusters | 100 |
```

## Production Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] README.md with setup instructions
- [ ] .gitignore configured
- [ ] Version tagged (v1.0.0)
- [ ] Tested locally with `python server.py`
- [ ] Tested in Claude Desktop
- [ ] Documentation complete
- [ ] Shared with team

## Quick Reference

### Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/log-analyzer-mcp.git
git push -u origin main
```

### Claude Config (Windows)
```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "C:\\path\\to\\log-analyzer-mcp"
    }
  }
}
```

### Test Tools
```
"Use fetch_local_logs to process logs"
"Use store_chunks_as_vectors to create embeddings"
"Use query_SFlogs to find authentication errors"
```

Your local FAISS-powered log analyzer is ready for GitHub and Claude Desktop! 🚀

### Issue: "Module not found"

```bash
pip install -r requirements.txt --upgrade
```

### Issue: "AWS credentials not found"

```bash
# Verify .env file exists and contains credentials
cat .env

# Test AWS access
python -c "import boto3; print(boto3.client('bedrock-runtime', region_name='us-east-2').list_foundation_models())"
```

### Issue: "MCP server not responding"

1. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`
2. Verify server.py runs without errors
3. Check Python version (3.9+)

## Updating the Server

### Pull Latest Changes

```bash
cd log-analyzer-mcp
git pull origin main
pip install -r requirements.txt --upgrade
```

### Update Claude Desktop Config

Restart Claude Desktop after any configuration changes.

## Support

For issues:
1. Check GitHub Issues
2. Review logs in Claude Desktop
3. Test with MCP Inspector
4. Verify AWS credentials and permissions
