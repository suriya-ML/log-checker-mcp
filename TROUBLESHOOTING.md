# MCP Server Troubleshooting Guide

## Error: "SSE error: Invalid content type, expected 'text/event-stream'"

This error means Claude Desktop can't communicate with the MCP server. Here's how to fix it:

### Solution 1: Fix Claude Desktop Configuration

**The issue:** Your config might have incorrect paths or Python command.

**Edit:** `C:\Users\V0411759\AppData\Roaming\Claude\claude_desktop_config.json`

**Use this configuration:**

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": [
        "-u",
        "-m",
        "server"
      ],
      "cwd": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "LOG_FOLDER": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp\\logs"
      }
    }
  }
}
```

**Key fixes:**
- Added `-u` flag for unbuffered output
- Added `PYTHONUNBUFFERED=1` environment variable
- Used absolute paths with proper escaping

### Solution 2: Verify Python Path

```powershell
# Find your Python path
where python

# Test if Python works
python --version
```

If Python is not in PATH, use full path in config:

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "C:\\Users\\V0411759\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
      "args": ["-u", "-m", "server"],
      "cwd": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp"
    }
  }
}
```

### Solution 3: Install Dependencies

```powershell
cd "c:\Users\V0411759\Documents\AI TEST\log-analyzer-mcp"
pip install -r requirements.txt
```

### Solution 4: Test Server Manually

```powershell
cd "c:\Users\V0411759\Documents\AI TEST\log-analyzer-mcp"
python -u -m server
```

**Expected output:**
```
Starting Log Analyzer MCP Server...
Using local embedding model: all-MiniLM-L6-v2
Log folder: c:\Users\V0411759\Documents\AI TEST\log-analyzer-mcp\logs
```

**If you see errors:** Check the error message and fix dependencies.

### Solution 5: Check Claude Desktop Logs

**Location:** `%APPDATA%\Claude\logs\`

**Open latest log file and look for:**
- Python errors
- Module import errors
- Path issues

### Solution 6: Simplified Config (Try This First!)

Use the startup script:

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "cmd",
      "args": [
        "/c",
        "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp\\start_server.bat"
      ]
    }
  }
}
```

### Solution 7: Use Full Python Path

Find your Python installation:

```powershell
Get-Command python | Select-Object -ExpandProperty Definition
```

Then use the full path:

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "C:\\Python311\\python.exe",
      "args": ["-u", "-m", "server"],
      "cwd": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp"
    }
  }
}
```

## Step-by-Step Fix

### Step 1: Verify Dependencies

```powershell
cd "c:\Users\V0411759\Documents\AI TEST\log-analyzer-mcp"
pip list | Select-String -Pattern "mcp|faiss|sentence"
```

**Expected output:**
```
faiss-cpu          1.7.4
mcp                0.9.0
sentence-transformers 2.2.0
```

**If missing:**
```powershell
pip install -r requirements.txt
```

### Step 2: Test Server

```powershell
python -u -m server
```

**Should NOT exit immediately.** Press Ctrl+C to stop.

### Step 3: Update Claude Config

Use this EXACT configuration:

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": [
        "-u",
        "-m",
        "server"
      ],
      "cwd": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

1. **Completely quit** Claude Desktop (check Task Manager)
2. **Wait 5 seconds**
3. **Start** Claude Desktop
4. **Check** for 🔌 icon

### Step 5: Test in Claude

```
"List available MCP tools"
```

Should show:
- fetch_local_logs
- store_chunks_as_vectors
- query_SFlogs

## Common Issues

### Issue: "Module 'server' not found"

**Fix:** Make sure you're using `-m server` not `server.py`

```json
"args": ["-u", "-m", "server"]  // Correct
```

### Issue: "No module named 'mcp'"

**Fix:**
```powershell
pip install mcp
```

### Issue: "No module named 'faiss'"

**Fix:**
```powershell
pip install faiss-cpu
```

### Issue: "No module named 'sentence_transformers'"

**Fix:**
```powershell
pip install sentence-transformers
```

### Issue: Server starts then immediately exits

**Fix:** Add unbuffered flag:
```json
"args": ["-u", "-m", "server"]
```

### Issue: "Cannot find Python"

**Fix:** Use full Python path:
```powershell
# Find Python
where python

# Use full path in config
"command": "C:\\full\\path\\to\\python.exe"
```

## Debugging Commands

### Check Python
```powershell
python --version
where python
```

### Check Dependencies
```powershell
cd "c:\Users\V0411759\Documents\AI TEST\log-analyzer-mcp"
pip list
```

### Test Import
```powershell
python -c "import mcp; import faiss; import sentence_transformers; print('OK')"
```

### View Claude Logs
```powershell
cd %APPDATA%\Claude\logs
Get-Content -Path (Get-ChildItem | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Tail 50
```

## Working Configuration Template

Copy this EXACT configuration:

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": [
        "-u",
        "-m",
        "server"
      ],
      "cwd": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp",
        "LOG_FOLDER": "c:\\Users\\V0411759\\Documents\\AI TEST\\log-analyzer-mcp\\logs"
      }
    }
  }
}
```

**File location:** `C:\Users\V0411759\AppData\Roaming\Claude\claude_desktop_config.json`

## Still Not Working?

1. **Check Claude logs:** `%APPDATA%\Claude\logs\`
2. **Verify Python works:** `python -m server`
3. **Test imports:** `python -c "import mcp"`
4. **Check paths:** All paths must use `\\` on Windows
5. **Restart everything:** Quit Claude completely, wait, restart

## Quick Fix Checklist

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Python works: `python --version`
- [ ] Server runs: `python -u -m server`
- [ ] Config uses absolute paths
- [ ] Config has `-u` flag
- [ ] Claude Desktop completely restarted
- [ ] Check Claude logs for errors

If still failing, share the Claude Desktop log file contents.
