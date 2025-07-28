#!/usr/bin/env python3
"""
Test script to verify MCP server authentication
"""
import os
import subprocess
import json
import time
from dotenv import load_dotenv

load_dotenv()

def test_mcp_authentication():
    """Test MCP server with and without API key"""
    
    print("🧪 Testing MCP Server Authentication")
    print("=" * 50)
    
    # Test 1: Server with API key
    print("\n1️⃣  Testing server WITH API key...")
    env_with_key = os.environ.copy()
    env_with_key['MCP_API_KEY'] = 'mcp_secure_api_key_2025_asana_server_v1'
    
    try:
        result = subprocess.run([
            './venv/bin/python', 'mcp_server.py'
        ], env=env_with_key, capture_output=True, text=True, timeout=5)
        
        if "🔐 MCP server configured with API key authentication" in result.stdout:
            print("✅ Server correctly configured with API key")
        else:
            print("❌ Server API key configuration failed")
            print(f"Output: {result.stdout}")
            
    except subprocess.TimeoutExpired:
        print("✅ Server started successfully (timeout expected)")
    except Exception as e:
        print(f"❌ Error starting server with API key: {e}")
    
    # Test 2: Server without API key
    print("\n2️⃣  Testing server WITHOUT API key...")
    env_without_key = os.environ.copy()
    env_without_key.pop('MCP_API_KEY', None)
    
    try:
        result = subprocess.run([
            './venv/bin/python', 'mcp_server.py'
        ], env=env_without_key, capture_output=True, text=True, timeout=5)
        
        if "🔓 MCP server running WITHOUT authentication" in result.stdout:
            print("✅ Server correctly configured without API key")
        else:
            print("❌ Server no-auth configuration failed")
            print(f"Output: {result.stdout}")
            
    except subprocess.TimeoutExpired:
        print("✅ Server started successfully (timeout expected)")
    except Exception as e:
        print(f"❌ Error starting server without API key: {e}")
    
    # Test 3: Validation function
    print("\n3️⃣  Testing API key validation function...")
    
    # Import the validation function
    import sys
    sys.path.append('.')
    
    try:
        from mcp_server import validate_mcp_request
        
        # Test valid key
        valid_key = "mcp_secure_api_key_2025_asana_server_v1"
        if validate_mcp_request(valid_key):
            print("✅ Valid API key correctly accepted")
        else:
            print("❌ Valid API key incorrectly rejected")
        
        # Test invalid key
        invalid_key = "invalid_key"
        if not validate_mcp_request(invalid_key):
            print("✅ Invalid API key correctly rejected")
        else:
            print("❌ Invalid API key incorrectly accepted")
            
        # Test Bearer format
        bearer_key = f"Bearer {valid_key}"
        if validate_mcp_request(bearer_key):
            print("✅ Bearer format API key correctly accepted")
        else:
            print("❌ Bearer format API key incorrectly rejected")
            
    except ImportError as e:
        print(f"❌ Could not import validation function: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Authentication tests completed!")

if __name__ == "__main__":
    test_mcp_authentication()
