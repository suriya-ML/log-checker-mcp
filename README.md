# Log Analyzer MCP Server

A Model Context Protocol (MCP) server that provides powerful log analysis capabilities using AWS Bedrock for semantic search and AI-powered analysis.

## Features

- **fetch_local_logs**: Fetch and chunk local log files with configurable chunk size and overlap
- **store_chunks_as_vectors**: Vectorize log chunks with enhanced metadata extraction and intelligent caching
- **query_SFlogs**: Query vectorized logs with hybrid semantic/lexical search, error clustering, and comprehensive analysis

## Prerequisites

- Python 3.9 or higher
- AWS account with Bedrock access
- AWS credentials with permissions for Bedrock Runtime

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/log-analyzer-mcp.git
cd log-analyzer-mcp
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-2
```

## Usage

### Running the Server Locally

```bash
python server.py
```

### Configuring with Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": ["/absolute/path/to/log-analyzer-mcp/server.py"],
      "env": {
        "AWS_ACCESS_KEY_ID": "your_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret",
        "AWS_REGION": "us-east-2"
      }
    }
  }
}
```

### Available Tools

#### 1. fetch_local_logs

Fetch and chunk log files from a local directory.

**Parameters:**
- `input_folder` (optional): Path to folder containing log files (default: ./logs)
- `chunk_size` (optional): Size of each chunk in characters (default: 4096)
- `overlap` (optional): Overlap between chunks in characters (default: 1024)

**Example:**
```
Use fetch_local_logs to process logs from /path/to/logs with chunk_size 5000
```

#### 2. store_chunks_as_vectors

Vectorize log chunks with AWS Bedrock embeddings and intelligent caching.

**Parameters:**
- `use_cache` (optional): Whether to use embedding cache (default: true)
- `clear_cache` (optional): Clear cache before starting (default: false)

**Features:**
- Extracts timeframes, class names, method names, error types
- Parallel processing for fast vectorization
- Persistent caching to avoid re-embedding

**Example:**
```
Use store_chunks_as_vectors to vectorize the logs
```

#### 3. query_SFlogs

Query vectorized logs with semantic search and comprehensive analysis.

**Parameters:**
- `query` (required): Natural language query

**Features:**
- Hybrid semantic + lexical search
- Automatic error clustering and deduplication
- Severity ranking and frequency analysis
- Metadata extraction (timeframes, classes, methods)
- AI-powered summarization

**Examples:**
```
Query logs: "What NullPointerExceptions occurred?"
Query logs: "Summarize all errors"
Query logs: "Show timeout issues in UserHandler"
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `AWS_REGION` | AWS region | us-east-2 |
| `AWS_CONNECT_TIMEOUT` | Connection timeout (seconds) | 60 |
| `AWS_READ_TIMEOUT` | Read timeout (seconds) | 300 |
| `BEDROCK_EMBED_MODEL_ID` | Embedding model | amazon.titan-embed-text-v2:0 |
| `BEDROCK_NOVA_MODEL_ID` | Analysis model | amazon.nova-premier-v1:0 |
| `LOG_FOLDER` | Default log folder | ./logs |
| `DEFAULT_CHUNK_SIZE` | Default chunk size | 4096 |
| `DEFAULT_OVERLAP` | Default overlap | 1024 |

## Architecture

```
log-analyzer-mcp/
├── server.py              # Main MCP server implementation
├── config.py              # Configuration management
├── utils/                 # Utility modules
│   ├── logging_utils.py   # Logging configuration
│   ├── file_utils.py      # File operations
│   ├── bedrock_utils.py   # AWS Bedrock integration
│   ├── chunking_utils.py  # Text chunking
│   └── error_extraction.py # Error pattern extraction
├── logs/                  # Log storage (created automatically)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## How It Works

### 1. Log Processing Pipeline

```
Raw Logs → Chunking → Metadata Extraction → Vectorization → Storage
```

- **Chunking**: Split logs into overlapping chunks for better context preservation
- **Metadata Extraction**: Extract timeframes, class names, methods, error types
- **Vectorization**: Generate embeddings using AWS Bedrock
- **Caching**: Store embeddings for fast re-processing

### 2. Query Pipeline

```
Query → Embedding → Hybrid Search → Error Clustering → AI Analysis → Results
```

- **Hybrid Search**: Combine semantic similarity with lexical matching
- **Error Clustering**: Group similar errors using fingerprinting
- **Ranking**: Sort by severity and frequency
- **AI Analysis**: Generate comprehensive summaries with AWS Bedrock

## Performance

- **Parallel Processing**: Up to 5 concurrent embedding requests
- **Intelligent Caching**: 70-90% cache hit rate on repeated processing
- **Adaptive Retrieval**: Dynamic top-k based on query type
- **Token Optimization**: Smart budget management for AI analysis

## Troubleshooting

### Common Issues

**"No vector JSON found"**
- Run `store_chunks_as_vectors` first to vectorize your logs

**"Bedrock authentication failed"**
- Verify your AWS credentials in `.env`
- Ensure your AWS account has Bedrock access enabled

**"No chunks found"**
- Check that log files exist in the configured folder
- Verify file extensions (.log, .txt) are correct

### Logging

Logs are written to stderr for MCP compatibility. To debug:

```bash
python server.py 2> debug.log
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/log-analyzer-mcp/issues)
- Documentation: [Wiki](https://github.com/yourusername/log-analyzer-mcp/wiki)

## Roadmap

- [ ] Support for additional embedding models
- [ ] Real-time log streaming
- [ ] Web UI for visualization
- [ ] Multi-language support
- [ ] Enhanced error pattern detection
- [ ] Integration with monitoring tools

## Acknowledgments

Built with:
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - AI/ML capabilities
- [Anthropic Claude](https://www.anthropic.com/) - AI analysis
