"""
LangChain Agent File Operation Vulnerabilities (LLM08)

This file demonstrates file operation vulnerabilities when agents have
access to file system tools without proper restrictions.

Vulnerabilities:
1. Agents with unrestricted file operation tools
2. File operations with user input
"""

from langchain.agents import initialize_agent
from langchain.tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from langchain.llms import OpenAI
from flask import request

# ============================================================================
# VULNERABLE: Agent with unrestricted file tools
# ============================================================================
def vulnerable_agent_file_operations():
    """VULNERABLE: Agent with unrestricted file operation tools."""
    llm = OpenAI(temperature=0)
    
    # VULNERABLE: Agent with file tools - no restrictions
    agent = initialize_agent(
        tools=[
            ReadFileTool(),
            WriteFileTool(),
            ListDirectoryTool(),
        ],
        llm=llm,
        agent="zero-shot-react-description"
    )
    
    user_input = request.args.get('query')
    result = agent.run(user_input)
    # Attacker can:
    # - Read /etc/passwd, .env files, config files
    # - Write malicious files anywhere
    # - List sensitive directories
    
    return result


# ============================================================================
# SAFE: Agent with restricted file operations
# ============================================================================
def safe_agent_file_operations():
    """SAFE: Agent with restricted file operation tools."""
    llm = OpenAI(temperature=0)
    
    # SAFE: Create restricted file tools (sandboxed to specific directory)
    from pathlib import Path
    
    # Restrict to a specific directory
    allowed_dir = Path("/tmp/sandbox")
    allowed_dir.mkdir(exist_ok=True)
    
    # Create custom restricted tools (would need custom implementation)
    # For now, just don't use file tools with user input
    
    # SAFE: Use agent without file tools, or with read-only access to safe directories
    from langchain.tools import DuckDuckGoSearchRun
    
    agent = initialize_agent(
        tools=[DuckDuckGoSearchRun()],  # No file operations
        llm=llm,
        agent="zero-shot-react-description"
    )
    
    user_input = request.args.get('query')
    result = agent.run(user_input)
    
    return result
