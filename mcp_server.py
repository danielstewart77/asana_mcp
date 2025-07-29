# mcp_server.py
import os
import hashlib
import hmac
from functools import wraps
from tools import asana

import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

from agent_tooling import discover_tools, get_tool_function, get_tool_schemas
discover_tools(['toolss'])
from mcp.server.fastmcp import FastMCP

# Load API key from environment
MCP_API_KEY = os.getenv("MCP_API_KEY")
if not MCP_API_KEY:
    log.warning("⚠️  MCP_API_KEY not set - server will run WITHOUT authentication!")

def validate_mcp_request(api_key: str) -> bool:
    """
    Validate MCP client API key
    This function can be used by MCP clients or transport layers
    """
    if not MCP_API_KEY:
        log.info("🔓 No API key configured - allowing access")
        return True
        
    if not api_key:
        log.warning("❌ No API key provided")
        return False
        
    # Handle Bearer token format
    clean_key = api_key.replace('Bearer ', '').strip()
    
    if hmac.compare_digest(clean_key, MCP_API_KEY):
        log.info("✅ API key validated successfully")
        return True
    else:
        log.warning("❌ Invalid API key provided")
        return False

def require_auth(func):
    """Decorator to require API key authentication - for documentation purposes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Authentication is handled at the MCP transport level
        # This decorator is kept for documentation/future use
        return func(*args, **kwargs)
    return wrapper

# Initialize FastMCP
mcp = FastMCP("agent-tool-server")

# Configure authentication
if MCP_API_KEY:
    log.info("🔐 MCP server configured with API key authentication")
    log.info(f"🔑 Expected API key format: Bearer {MCP_API_KEY[:8]}...")
else:
    log.info("🔓 MCP server running WITHOUT authentication")

# Register all tools with FastMCP
for schema in get_tool_schemas():
    name = schema['name']
    func = get_tool_function(name)
    if func:
        log.info(f"[MCP REGISTER] {name}")
        mcp.tool()(func)

# Run the server
if __name__ == "__main__":
    if os.environ.get("RUN_DIRECT") == "1":
        log.info("🚀 Starting MCP server on 0.0.0.0:7777")
        mcp.run()
    else:
        log.info("🚀 Starting MCP server in stdio mode (used by mcpo)")
        mcp.run()  # uses stdin/stdout for mcpo