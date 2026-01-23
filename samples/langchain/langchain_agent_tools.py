"""
LangChain Agent Tool Configuration Vulnerabilities (LLM08)

This file demonstrates excessive agency vulnerabilities through agent tool configuration.
Agents with many tools or unrestricted tool access pose security risks.

Vulnerabilities:
1. Agents with many tools (excessive permissions)
2. Agents with file operation tools
3. Agents with network operation tools
"""

from langchain.agents import initialize_agent
from langchain.tools import PythonREPLTool, ShellTool, FileManagementTool
from langchain.tools import RequestsTool, DuckDuckGoSearchRun
from langchain.llms import OpenAI
from flask import request

# ============================================================================
# VULNERABLE: Agent with many tools
# ============================================================================
def vulnerable_agent_many_tools():
    """VULNERABLE: Agent initialized with many tools (excessive permissions)."""
    llm = OpenAI(temperature=0)
    
    # VULNERABLE: Agent with many tools - excessive agency
    agent = initialize_agent(
        tools=[
            PythonREPLTool(),
            ShellTool(),
            FileManagementTool(),
            RequestsTool(),
            DuckDuckGoSearchRun(),
            # ... many more tools
        ],
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    
    user_input = request.args.get('query')
    result = agent.run(user_input)
    # Agent has too many permissions - can execute code, commands, access files, network
    
    return result


# ============================================================================
# VULNERABLE: Agent with file operation tools
# ============================================================================
def vulnerable_agent_file_tools():
    """VULNERABLE: Agent with file operation tools."""
    llm = OpenAI(temperature=0)
    
    # VULNERABLE: Agent with file operations
    from langchain.tools import ReadFileTool, WriteFileTool, ListDirectoryTool
    
    agent = initialize_agent(
        tools=[
            ReadFileTool(),
            WriteFileTool(),
            ListDirectoryTool(),
        ],
        llm=llm,
        agent="zero-shot-react-description"
    )
    
    user_input = request.json.get('query')
    result = agent.run(user_input)
    # Attacker can: read sensitive files, write malicious files, list directories
    
    return result


# ============================================================================
# VULNERABLE: Agent with network operation tools
# ============================================================================
def vulnerable_agent_network_tools():
    """VULNERABLE: Agent with network operation tools (SSRF risk)."""
    llm = OpenAI(temperature=0)
    
    # VULNERABLE: Agent with network tools
    agent = initialize_agent(
        tools=[
            RequestsTool(),
            DuckDuckGoSearchRun(),
        ],
        llm=llm,
        agent="zero-shot-react-description"
    )
    
    user_input = request.args.get('query')
    result = agent.run(user_input)
    # Attacker can: make HTTP requests to internal services (SSRF),
    # exfiltrate data, access internal APIs
    
    return result


# ============================================================================
# SAFE: Agent with restricted, safe tools only
# ============================================================================
def safe_agent_tool_configuration():
    """SAFE: Agent with only safe, whitelisted tools."""
    llm = OpenAI(temperature=0)
    
    # SAFE: Only use safe, read-only tools
    from langchain.tools import Calculator, DuckDuckGoSearchRun
    
    agent = initialize_agent(
        tools=[
            Calculator(),  # Safe: math only
            DuckDuckGoSearchRun(),  # Safe: public search only
            # No code execution, file operations, or unrestricted network access
        ],
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    
    user_input = request.args.get('query')
    
    # Still validate input
    if len(user_input) > 500:
        raise ValueError("Input too long")
    
    result = agent.run(user_input)
    
    return result
