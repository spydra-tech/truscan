"""
LangChain Agent Excessive Agency Vulnerabilities (LLM08)

This file demonstrates excessive agency vulnerabilities in LangChain agents.
Agents with dangerous tools (PythonREPLTool, ShellTool) can execute arbitrary code/commands.

Vulnerabilities:
1. Agents with PythonREPLTool
2. Agents with ShellTool
3. Agents with both dangerous tools
4. Agent execution with user input
"""

from langchain.agents import initialize_agent, AgentExecutor
from langchain.agents.agent_toolkits import create_python_agent
from langchain.tools import PythonREPLTool, ShellTool
from langchain.llms import OpenAI
from flask import request

# ============================================================================
# VULNERABLE: Agent with PythonREPLTool
# ============================================================================
def vulnerable_agent_python_repl():
    """VULNERABLE: Agent initialized with PythonREPLTool."""
    llm = OpenAI(temperature=0)
    
    # VULNERABLE: Agent with PythonREPLTool - allows arbitrary Python execution
    agent = initialize_agent(
        tools=[PythonREPLTool()],
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    
    user_input = request.args.get('query')
    result = agent.run(user_input)
    # Attacker can inject: "Execute: import os; os.system('rm -rf /')"
    
    return result


# ============================================================================
# VULNERABLE: Agent with ShellTool
# ============================================================================
def vulnerable_agent_shell_tool():
    """VULNERABLE: Agent initialized with ShellTool."""
    llm = OpenAI(temperature=0)
    
    # VULNERABLE: Agent with ShellTool - allows arbitrary shell command execution
    agent = initialize_agent(
        tools=[ShellTool()],
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    
    user_input = request.args.get('command')
    result = agent.run(user_input)
    # Attacker can inject: "Run: rm -rf /"
    
    return result


# ============================================================================
# VULNERABLE: Agent with both dangerous tools
# ============================================================================
def vulnerable_agent_both_tools():
    """VULNERABLE: Agent with both PythonREPLTool and ShellTool."""
    llm = OpenAI(temperature=0)
    
    # VULNERABLE: Agent with both dangerous tools - maximum risk
    agent = initialize_agent(
        tools=[PythonREPLTool(), ShellTool()],
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    
    user_input = request.json.get('input')
    result = agent.run(user_input)
    # Attacker has full system access via both Python and shell
    
    return result


# ============================================================================
# VULNERABLE: AgentExecutor with dangerous tools
# ============================================================================
def vulnerable_agent_executor():
    """VULNERABLE: AgentExecutor with dangerous tools."""
    llm = OpenAI(temperature=0)
    tools = [PythonREPLTool(), ShellTool()]
    
    # VULNERABLE: AgentExecutor with dangerous tools
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )
    
    user_input = request.args.get('query')
    result = agent_executor.run(user_input)
    
    return result


# ============================================================================
# VULNERABLE: Agent with user input via invoke
# ============================================================================
def vulnerable_agent_invoke():
    """VULNERABLE: Agent execution with user input via invoke."""
    llm = OpenAI(temperature=0)
    agent = initialize_agent(
        tools=[PythonREPLTool()],
        llm=llm,
        agent="zero-shot-react-description"
    )
    
    user_input = request.json.get('input')
    
    # VULNERABLE: User input via invoke
    result = agent.invoke({"input": user_input})
    
    return result


# ============================================================================
# SAFE: Agent with safe tools only
# ============================================================================
def safe_agent_usage():
    """SAFE: Agent with only safe, whitelisted tools."""
    llm = OpenAI(temperature=0)
    
    # SAFE: Only use safe tools (e.g., search, calculator)
    from langchain.tools import DuckDuckGoSearchRun, Calculator
    
    agent = initialize_agent(
        tools=[DuckDuckGoSearchRun(), Calculator()],  # Safe tools only
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    
    user_input = request.args.get('query')
    
    # Still validate input
    if len(user_input) > 1000:
        raise ValueError("Input too long")
    
    result = agent.run(user_input)
    
    return result
