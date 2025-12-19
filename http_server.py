from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
from server import (
    analyze_logs_tool,
    fetch_logs_tool,
    list_recent_logs_tool,
    # Import other tools from your MCP server
)

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "log-checker-mcp"}), 200

@app.route('/api/mcp/tools', methods=['GET'])
def list_tools():
    """List available MCP tools"""
    return jsonify({
        "tools": [
            {
                "name": "analyze_logs",
                "description": "Analyze Salesforce debug logs for errors and patterns",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "log_id": {"type": "string"},
                        "analysis_type": {"type": "string"}
                    }
                }
            },
            {
                "name": "fetch_logs",
                "description": "Fetch Salesforce debug logs",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "org_id": {"type": "string"},
                        "limit": {"type": "number"}
                    }
                }
            }
        ]
    }), 200

@app.route('/api/mcp/execute', methods=['POST'])
def execute_tool():
    """Execute MCP tool"""
    try:
        data = request.json
        tool_name = data.get('tool_name')
        arguments = data.get('arguments', {})
        
        # Route to appropriate tool
        result = None
        if tool_name == 'analyze_logs':
            result = asyncio.run(analyze_logs_tool(**arguments))
        elif tool_name == 'fetch_logs':
            result = asyncio.run(fetch_logs_tool(**arguments))
        elif tool_name == 'list_recent_logs':
            result = asyncio.run(list_recent_logs_tool(**arguments))
        else:
            return jsonify({"error": f"Unknown tool: {tool_name}"}), 400
            
        return jsonify({
            "success": True,
            "tool": tool_name,
            "result": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### Step 1.2: Create Heroku Configuration Files

**`Procfile`:**
```
web: gunicorn http_server:app --timeout 600 --workers 3
```

**`requirements.txt`:**
```
Flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
requests==2.31.0
# Add your existing MCP dependencies
```

**`runtime.txt`:**
```
python-3.11.7
