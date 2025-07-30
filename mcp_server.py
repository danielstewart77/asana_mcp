# mcp_server.py
import os
import hmac
from functools import wraps
from tools import asana_functions

import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

from agent_tooling import discover_tools, get_tool_function, get_tool_schemas
discover_tools(['tools'])
from mcp.server.fastmcp import FastMCP

# --- Authentication Configuration ---
MCP_API_KEY = os.getenv("MCP_API_KEY") or "mcp_secure_api_key_2025_asana_server_v1"

def validate_api_token(token: str) -> bool:
    """
    Validate API token using secure comparison to prevent timing attacks.
    Accepts both direct token and Bearer format.
    """
    if not token:
        return False
    
    # Handle Bearer token format
    if token.startswith("Bearer "):
        token = token[7:]  # Remove "Bearer " prefix
    
    # Use HMAC comparison to prevent timing attacks
    expected = MCP_API_KEY.encode('utf-8')
    provided = token.encode('utf-8')
    
    return hmac.compare_digest(expected, provided)

# Initialize FastMCP
mcp = FastMCP("agent-tool-server")

# Add authentication middleware
@mcp.middleware
async def auth_middleware(request, call_next):
    """Middleware to validate Bearer token for all requests"""
    
    # Skip authentication for development if no API key is set
    if not MCP_API_KEY or MCP_API_KEY == "mcp_secure_api_key_2025_asana_server_v1":
        if os.getenv("DEVELOPMENT") or not os.getenv("PRODUCTION"):
            log.info("⚠️  Development mode: API authentication bypassed")
            return await call_next(request)
    
    # Extract Authorization header
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header:
        log.warning("❌ Missing Authorization header")
        return {"error": "Authorization required. Please provide a Bearer token."}
    
    # Validate the token
    if validate_api_token(auth_header):
        log.info("✅ API key validated successfully")
        return await call_next(request)
    else:
        log.warning("❌ Invalid API key provided")
        return {"error": "Invalid API key. Please provide a valid Bearer token."}

# Check if authentication is enabled
if MCP_API_KEY and MCP_API_KEY != "mcp_secure_api_key_2025_asana_server_v1":
    log.info("🔐 MCP server configured with API key authentication")
else:
    log.info("🔓 MCP server running WITHOUT authentication")

# if tool schemas are empty, register the default Asana tool
if not get_tool_schemas():
    log.info("🔧 No tools found, registering default Asana tool")
    mcp.tool()(asana_functions.extract_incomplete_tasks)  # Ensure the tool is registered

# Register all tools with FastMCP
for schema in get_tool_schemas():
    name = schema['name']
    func = get_tool_function(name)
    if func:
        log.info(f"[MCP REGISTER] {name}")
        mcp.tool()(func)

# Run the server
if __name__ == "__main__":
    log.info("🚀 Starting MCP server")
    mcp.run()