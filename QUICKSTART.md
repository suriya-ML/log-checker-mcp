# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/log-analyzer-mcp.git
cd log-analyzer-mcp
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

```bash
cp .env.example .env
```

Edit `.env`:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-2
```

### 3. Test the Server

```bash
python server.py
```

If you see "Starting Log Analyzer MCP Server..." - you're ready! Press Ctrl+C to stop.

### 4. Use with Claude Desktop

#### Find Your Config File

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

#### Add This Configuration

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": ["/full/path/to/log-analyzer-mcp/server.py"],
      "env": {
        "AWS_ACCESS_KEY_ID": "your_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret",
        "AWS_REGION": "us-east-2"
      }
    }
  }
}
```

**Important**: Use the FULL absolute path to `server.py`

### 5. Restart Claude Desktop

Completely quit and restart Claude Desktop.

### 6. Try It Out!

In Claude Desktop, try these commands:

```
1. Process some logs:
"Use fetch_local_logs to process logs from /path/to/my/logs"

2. Vectorize them:
"Use store_chunks_as_vectors to create embeddings"

3. Query them:
"Use query_SFlogs to find all NullPointerExceptions"
```

## 📁 Example Workflow

### Step 1: Prepare Your Logs

```bash
# Create a logs folder
mkdir logs

# Copy your log files there
cp /path/to/app.log logs/
cp /path/to/error.log logs/
```

### Step 2: Process Logs

In Claude:
```
Use fetch_local_logs with input_folder="./logs", chunk_size=4096, overlap=1024
```

### Step 3: Vectorize

In Claude:
```
Use store_chunks_as_vectors with use_cache=true
```

### Step 4: Query

In Claude:
```
Query logs: "What errors occurred today?"
Query logs: "Summarize all exceptions"
Query logs: "Find timeouts in UserService"
```

## 🔍 Common Use Cases

### Find All Errors
```
Use query_SFlogs with query="list all errors"
```

### Root Cause Analysis
```
Use query_SFlogs with query="what caused the NullPointerException?"
```

### Time-based Analysis
```
Use query_SFlogs with query="what happened between 10am and 11am?"
```

### Class-specific Issues
```
Use query_SFlogs with query="show errors in CustomerController"
```

## ⚡ Pro Tips

1. **First Time**: Process → Vectorize → Query (in that order)
2. **Caching**: Vectorization is cached - reprocess is instant!
3. **Large Logs**: Use smaller chunk_size (e.g., 2048) for better precision
4. **Specific Searches**: Include class names or error types in queries
5. **Summaries**: Ask for "summary" or "overview" for comprehensive analysis

## 🛠️ Troubleshooting

### "No vector JSON found"
→ Run `store_chunks_as_vectors` first

### "Input folder not found"
→ Use absolute paths or check current directory

### "AWS credentials not found"
→ Verify `.env` file has correct credentials

### MCP server not responding
→ Check Claude Desktop logs and restart the app

## 📚 Learn More

- Full documentation: [README.md](README.md)
- Deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- GitHub issues: Report problems or request features

## 💡 Example Session

```
You: "I have some application logs I need to analyze"

Claude: "I can help! First, let me process your logs."
[Uses fetch_local_logs]

You: "Now find all the errors"

Claude: "Let me vectorize the logs first, then search."
[Uses store_chunks_as_vectors]
[Uses query_SFlogs with query="all errors"]

Claude: "I found 15 unique error patterns:
1. NullPointerException (12 occurrences)
2. TimeoutException (8 occurrences)
..."
```

That's it! You're ready to analyze logs with AI! 🎉
