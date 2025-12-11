@echo off
REM GitHub Setup Script for Log Analyzer MCP Server (Windows)

echo.
echo Setting up Log Analyzer MCP Server for GitHub...
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed. Please install git first.
    exit /b 1
)

REM Initialize git repository
echo Initializing git repository...
git init

REM Add all files
echo Adding files to git...
git add .

REM Create initial commit
echo Creating initial commit...
git commit -m "Initial commit: Log Analyzer MCP Server" -m "Features:" -m "- fetch_local_logs: Process and chunk log files" -m "- store_chunks_as_vectors: Vectorize with AWS Bedrock" -m "- query_SFlogs: Semantic log search and analysis"

echo.
echo Repository initialized successfully!
echo.
echo Next steps:
echo 1. Create a new repository on GitHub
echo 2. Run these commands (replace YOUR_USERNAME and REPO_NAME):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/log-analyzer-mcp.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Your MCP server will be live on GitHub!
echo.
echo See DEPLOYMENT.md for detailed deployment instructions
echo.
pause
