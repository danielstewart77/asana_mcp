# Secured MCP Server for Asana Tools

This MCP (Model Context Protocol) server provides secure access to Asana tools with API key authentication.

## 🔐 Security Features

- **API Key Authentication**: Server requires a valid API key for access
- **Bearer Token Support**: Accepts both direct keys and Bearer token format
- **Secure Validation**: Uses HMAC comparison to prevent timing attacks
- **Environment-based Configuration**: API key stored securely in environment variables

## 📋 Setup

### 1. Environment Configuration

Make sure your `.env` file contains:
```bash
MCP_API_KEY=mcp_secure_api_key_2025_asana_server_v1
ASANA_PAT=your_asana_personal_access_token
OPENAI_API_KEY=your_openai_api_key
```

### 2. Docker Deployment

The server runs in Docker with the API key automatically loaded:

```bash
# Build and run with docker-compose
docker-compose up -d --build
```

### 3. Local Development

```bash
# Install dependencies
./venv/bin/pip install -r requirements.txt

# Run server with authentication
./venv/bin/python mcp_server.py
```

## 🔌 Client Configuration

### MCP Client Configuration (Secure Method)

**NEVER put API keys directly in configuration files!** Instead:

1. **Use the template**: Copy `mcp_client_config.template.json` to your MCP client config directory
2. **Environment variables**: The MCP client will read `MCP_API_KEY` from your environment
3. **Local config**: Create a local config file (gitignored) if needed

**Template file** (`mcp_client_config.template.json`):
```json
{
  "mcpServers": {
    "asana-server": {
      "command": "mcpo",
      "args": ["--port", "7777", "--", "./venv/bin/python", "mcp_server.py"],
      "env": {
        "MCP_API_KEY": "${MCP_API_KEY}"
      },
      "transport": {
        "type": "stdio"
      }
    }
  }
}
```

### MCP Client Setup

```bash
# 1. Copy template to your MCP client config location
cp mcp_client_config.template.json ~/.mcp/config.json

# 2. MCP_API_KEY will be read from environment automatically
# Make sure your .env file contains:
# MCP_API_KEY=mcp_secure_api_key_2025_asana_server_v1

# 3. Start your MCP client (e.g., Claude Desktop, etc.)
```

### HTTP Client (if using HTTP transport)

```bash
# Example cURL request
curl -H "Authorization: Bearer mcp_secure_api_key_2025_asana_server_v1" \
     -H "Content-Type: application/json" \
     -d '{"method": "list_tools", "params": {}}' \
     http://asana.sparktobloom.com:7777
```

## 🧪 Testing Authentication

Run the authentication test script:

```bash
./venv/bin/python test_auth.py
```

This will test:
- ✅ Server startup with API key
- ✅ Server startup without API key
- ✅ API key validation function
- ✅ Bearer token format support

## 🔧 Available Tools

The MCP server exposes the following Asana tools:

- `extract_incomplete_tasks()`: Fetch incomplete/overdue tasks from all projects
- Additional tools from `agent_tooling` package

## 🚀 Production Deployment

### Via Docker Compose

The included `docker-compose.yml` automatically:
- Builds the container with all dependencies
- Loads environment variables from `.env`
- Exposes the server through Traefik proxy
- Enables automatic restarts

### Security Considerations

1. **API Key Rotation**: Regularly update the `MCP_API_KEY` value
2. **HTTPS Only**: Always use HTTPS in production (handled by Traefik)
3. **Network Security**: Restrict access using firewall rules
4. **Logging**: Monitor authentication attempts in server logs
5. **⚠️ NEVER commit API keys**: Always use `.env` files or environment variables
6. **Config Files**: Never put secrets in JSON config files - use templates with env vars

## 📊 Monitoring

Server logs include authentication events:
- `🔐 MCP server configured with API key authentication` - Server started with auth
- `✅ API key validated successfully` - Successful authentication
- `❌ Invalid API key provided` - Failed authentication attempt
- `🔓 No API key configured` - Server running without auth

## 🆘 Troubleshooting

### Common Issues

1. **"Missing API key" errors**: Ensure `MCP_API_KEY` is set in environment
2. **"Invalid API key" errors**: Verify the key matches exactly (case-sensitive)
3. **Server won't start**: Check that all dependencies are installed in the virtual environment

### Testing Connection

```bash
# Test if server is responding
curl -H "Authorization: Bearer mcp_secure_api_key_2025_asana_server_v1" \
     http://localhost:7777/health
```

### Disable Authentication (Development Only)

To temporarily disable authentication:
```bash
# Remove or comment out MCP_API_KEY in .env
# MCP_API_KEY=mcp_secure_api_key_2025_asana_server_v1
```

The server will start without authentication and log:
`🔓 MCP server running WITHOUT authentication`
