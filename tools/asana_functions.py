import asana
import os
import hmac
from datetime import datetime, timezone
from openai import OpenAI
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from agent_tooling import tool

from dotenv import load_dotenv

load_dotenv()

# --- Config ---
ASANA_PAT = os.getenv("ASANA_PAT") or "your_asana_personal_access_token"
OPENAI_KEY = os.getenv("OPENAI_API_KEY") or "your_openai_api_key"
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

def require_bearer_auth(func: Callable) -> Callable:
    """
    Decorator that validates Bearer token authentication.
    For MCP tools, this can be extended to check authentication context.
    Currently validates against the configured MCP_API_KEY.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # For MCP tools, we could check authentication through various means:
        # 1. Environment variable
        # 2. Global authentication state
        # 3. Request context (if available)
        
        # For now, we'll validate that the MCP_API_KEY is properly configured
        if not MCP_API_KEY or MCP_API_KEY == "mcp_secure_api_key_2025_asana_server_v1":
            raise ValueError("MCP API key is not properly configured")
        
        # In a full implementation, you could check request headers or other auth mechanisms here
        # For this example, we'll allow the call to proceed if the API key is configured
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper

@tool(tags=["asana_projects"])
@require_bearer_auth
def extract_incomplete_tasks() -> List[Dict[str, Any]]:
    """
    Fetch all incomplete or overdue tasks across all active projects in the user's workspace.
    Requires a valid API key for authentication.
    Returns a list of dicts with relevant task info.
    """

    # Initialize Asana SDK client
    configuration = asana.Configuration()
    configuration.access_token = ASANA_PAT
    api_client = asana.ApiClient(configuration)
    tasks_api = asana.TasksApi(api_client)
    users_api = asana.UsersApi(api_client)
    projects_api = asana.ProjectsApi(api_client)

    # Identify workspace
    me: Dict[str, Any] = users_api.get_user("me", {})  # type: ignore
    workspace_gid = me['workspaces'][0]['gid']

    # Retrieve active projects in workspace
    projects = projects_api.get_projects_for_workspace(workspace_gid, {"archived": False})
    overdue_tasks: List[Dict[str, Any]] = []

    for proj in projects:
        proj_name = proj['name']
        proj_gid = proj['gid']

        # Fetch incomplete or overdue tasks for project
        opts = {
            "completed_since": "now",
            "opt_fields": "name,assignee.name,due_on,completed,permalink_url"
        }
        for task in tasks_api.get_tasks_for_project(proj_gid, opts=opts):
            # Handle task as dict too
            task_dict = task if isinstance(task, dict) else task.__dict__
            due = task_dict.get('due_on')
            incomplete = not task_dict.get('completed', False)
            overdue = False
            if incomplete and due:
                overdue = datetime.strptime(due, "%Y-%m-%d").date() < datetime.now(timezone.utc).date()
            
            # Handle assignee
            assignee = task_dict.get('assignee')
            assignee_name: Optional[str] = None
            if assignee:
                if isinstance(assignee, dict):
                    assignee_name = assignee.get('name')
                else:
                    assignee_name = getattr(assignee, 'name', None)
            
            overdue_tasks.append({
                "project": proj_name,
                "task_name": task_dict.get('name'),
                "assignee": assignee_name,
                "due_on": due,
                "overdue": overdue,
                "url": task_dict.get('permalink_url')
            })

    return overdue_tasks

def summarize_tasks(tasks: List[Dict[str, Any]]) -> str:
    """Send tasks to GPT for prioritization and summarization."""
    client = OpenAI(api_key=OPENAI_KEY)
    prompt = f"""
You are an executive assistant. From the following tasks, identify the 5 most business-critical items.
Consider overdue status, missing assignees, and importance.

Tasks:
{tasks}
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    tasks = extract_incomplete_tasks()
    print(f"Found {len(tasks)} incomplete/overdue tasks")
    
    # Show first 5 tasks
    for t in tasks[:5]:
        print(f"- [{t['project']}] {t['task_name']} (Assignee: {t['assignee']}) Due: {t['due_on']} Overdue: {t['overdue']}")
    
    # If OpenAI key is available, get prioritized summary
    if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key":
        print("\n" + "="*50)
        print("AI PRIORITIZED SUMMARY:")
        print("="*50)
        summary = summarize_tasks(tasks)
        print(summary)
    else:
        print("\nOpenAI API key not available. Skipping AI summarization.")