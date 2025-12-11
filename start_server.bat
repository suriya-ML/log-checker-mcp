@echo off
REM Startup script for Log Analyzer MCP Server
REM This ensures the server runs with proper stdio communication

cd /d "%~dp0"
python -u -m server
