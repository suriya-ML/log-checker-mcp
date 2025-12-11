#!/bin/bash
# GitHub Setup Script for Log Analyzer MCP Server

echo "🚀 Setting up Log Analyzer MCP Server for GitHub..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git repository
echo "📦 Initializing git repository..."
git init

# Add all files
echo "📝 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Log Analyzer MCP Server

Features:
- fetch_local_logs: Process and chunk log files
- store_chunks_as_vectors: Vectorize with AWS Bedrock
- query_SFlogs: Semantic log search and analysis

Includes:
- Full documentation (README, QUICKSTART, DEPLOYMENT)
- Configuration examples
- Utility modules for log processing
- AWS Bedrock integration
- Embedding cache for performance
"

echo ""
echo "✅ Repository initialized!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Run these commands (replace YOUR_USERNAME and REPO_NAME):"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/log-analyzer-mcp.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Your MCP server will be live on GitHub!"
echo ""
echo "📖 See DEPLOYMENT.md for detailed deployment instructions"
