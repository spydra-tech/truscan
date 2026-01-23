"""
LangChain PythonREPLChain Code Execution Vulnerabilities

This file demonstrates PythonREPLChain vulnerabilities.
PythonREPLChain executes Python code in a REPL, making it extremely dangerous with user input.

Vulnerabilities:
1. PythonREPLChain with user input
2. PythonREPLChain output to eval/exec
"""

from langchain.chains import PythonREPLChain
from langchain.llms import OpenAI
from flask import request

# ============================================================================
# VULNERABLE: PythonREPLChain with user input
# ============================================================================
def vulnerable_python_repl_user_input():
    """VULNERABLE: PythonREPLChain execution with user-controlled input."""
    llm = OpenAI(temperature=0)
    
    # VULNERABLE: PythonREPLChain with user input
    repl_chain = PythonREPLChain(llm=llm)
    
    user_query = request.args.get('query')
    result = repl_chain.run(user_query)
    # Attacker can inject: "import os; os.system('rm -rf /')"
    
    return result


# ============================================================================
# VULNERABLE: PythonREPLChain with invoke
# ============================================================================
def vulnerable_python_repl_invoke():
    """VULNERABLE: PythonREPLChain invoke with user input."""
    llm = OpenAI(temperature=0)
    repl_chain = PythonREPLChain(llm=llm)
    
    user_query = request.json.get('query')
    
    # VULNERABLE: User input via invoke
    result = repl_chain.invoke({"query": user_query})
    
    return result


# ============================================================================
# VULNERABLE: PythonREPLChain output to eval
# ============================================================================
def vulnerable_python_repl_to_eval():
    """VULNERABLE: PythonREPLChain output passed to eval/exec."""
    llm = OpenAI(temperature=0)
    repl_chain = PythonREPLChain(llm=llm)
    
    # Get REPL output
    repl_output = repl_chain.run("print('Hello')")
    
    # VULNERABLE: Execute REPL output as code (double execution!)
    result = eval(repl_output)
    
    # VULNERABLE: Also with exec
    exec(repl_output)
    
    return result


# ============================================================================
# SAFE: Never use PythonREPLChain with user input
# ============================================================================
def safe_python_repl_usage():
    """SAFE: PythonREPLChain should never be used with user input."""
    # If PythonREPLChain is absolutely necessary, use it only with:
    # 1. Hardcoded, trusted queries
    # 2. Strictly validated and sanitized input
    # 3. Sandboxed execution environment
    
    llm = OpenAI(temperature=0)
    repl_chain = PythonREPLChain(llm=llm)
    
    # SAFE: Only use with hardcoded queries
    result = repl_chain.run("print('Hello World')")  # Hardcoded, safe
    
    # NEVER use with user input, even if "validated"
    # There's no safe way to use PythonREPLChain with untrusted input
    
    return result
