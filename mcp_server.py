# mcp_server.py
import os
from functools import wraps
from tools import asana_functions

import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

from agent_tooling import discover_tools, get_tool_function, get_tool_schemas
discover_tools(['tools'])
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("agent-tool-server")

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
    log.info("🚀 Starting MCP server directly")
    log.info("⚠️  Note: FastMCP only supports stdio mode, not HTTP")
    log.info("💡 For HTTP API access, use MCPO wrapper")
    mcp.run()