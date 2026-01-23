"""
LangChain PALChain Code Execution Vulnerabilities (CVE-2023-46229)

This file demonstrates PALChain code execution vulnerabilities.
PALChain generates Python code that gets executed, making it vulnerable to code injection.

Vulnerabilities:
1. PALChain with user input
2. PALChain output to eval/exec/compile
"""

from langchain.chains.pal import PALChain
from langchain.llms import OpenAI
from flask import request
# Note: eval and exec are built-in functions, not imported

# ============================================================================
# VULNERABLE: PALChain with user input
# ============================================================================
def vulnerable_palchain_user_input():
    """VULNERABLE: PALChain execution with user-controlled input."""
    llm = OpenAI(temperature=0)
    user_question = request.args.get('question')  # User-controlled
    
    # VULNERABLE: PALChain with user input
    pal_chain = PALChain.from_math_prompt(llm=llm)
    result = pal_chain.run(user_question)
    # Attacker can inject: "What is eval('import os; os.system(\"rm -rf /\")')?"
    
    return result


# ============================================================================
# VULNERABLE: PALChain output to eval/exec
# ============================================================================
def vulnerable_palchain_to_eval():
    """VULNERABLE: PALChain output passed to eval/exec/compile."""
    llm = OpenAI(temperature=0)
    pal_chain = PALChain.from_math_prompt(llm=llm)
    
    # Get PALChain output
    pal_output = pal_chain.run("Solve: 2 + 2")
    
    # VULNERABLE: Execute PALChain output as code
    result = eval(pal_output)  # CRITICAL: Double code execution!
    
    # VULNERABLE: Also with exec
    exec(pal_output)  # CRITICAL!
    
    # VULNERABLE: Also with compile
    code = compile(pal_output, '<string>', 'exec')
    exec(code)
    
    return result


# ============================================================================
# VULNERABLE: PALChain with invoke
# ============================================================================
def vulnerable_palchain_invoke():
    """VULNERABLE: PALChain invoke with user input."""
    llm = OpenAI(temperature=0)
    pal_chain = PALChain.from_math_prompt(llm=llm)
    
    user_question = request.json.get('question')
    
    # VULNERABLE: User input via invoke
    result = pal_chain.invoke({"question": user_question})
    
    return result


# ============================================================================
# SAFE: PALChain with validated input (if absolutely necessary)
# ============================================================================
def safe_palchain_usage():
    """SAFE: PALChain with strict input validation (still risky)."""
    llm = OpenAI(temperature=0)
    pal_chain = PALChain.from_math_prompt(llm=llm)
    
    user_input = request.args.get('question')
    
    # SAFE: Validate input is only math-related
    import re
    if not re.match(r'^[0-9+\-*/().\s]+$', user_input):
        raise ValueError("Invalid input: only math expressions allowed")
    
    # Still risky, but at least validated
    result = pal_chain.run(user_input)
    
    # SAFE: Don't execute the result
    # Just return it as text, don't eval/exec it
    return result
