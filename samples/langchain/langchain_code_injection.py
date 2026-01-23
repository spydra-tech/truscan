"""
LangChain Chain Output Code Injection Vulnerabilities (LLM02)

This file demonstrates code injection vulnerabilities when LangChain chain output
is passed to dangerous sinks like eval(), exec(), or compile().

Vulnerabilities:
1. Chain output to eval/exec/compile
2. LLMChain output to code execution
3. Sequential chain output to code execution
"""

from langchain.chains import LLMChain, SimpleSequentialChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from flask import request

# ============================================================================
# VULNERABLE: LLMChain output to eval
# ============================================================================
def vulnerable_chain_output_to_eval():
    """VULNERABLE: LLMChain output passed to eval()."""
    llm = OpenAI(temperature=0)
    prompt = PromptTemplate.from_template("Generate Python code for: {task}")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    task = request.args.get('task')
    chain_output = chain.run(task)
    
    # VULNERABLE: Execute chain output as code
    result = eval(chain_output)  # CRITICAL: Code injection!
    # Attacker can make LLM generate: "import os; os.system('rm -rf /')"
    
    return result


# ============================================================================
# VULNERABLE: Chain output to exec
# ============================================================================
def vulnerable_chain_output_to_exec():
    """VULNERABLE: Chain output passed to exec()."""
    llm = OpenAI(temperature=0)
    prompt = PromptTemplate.from_template("Write code to: {instruction}")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    instruction = request.json.get('instruction')
    chain_output = chain.run(instruction)
    
    # VULNERABLE: Execute chain output
    exec(chain_output)  # CRITICAL: Code injection!
    
    return chain_output


# ============================================================================
# VULNERABLE: Chain output to compile
# ============================================================================
def vulnerable_chain_output_to_compile():
    """VULNERABLE: Chain output passed to compile()."""
    llm = OpenAI(temperature=0)
    prompt = PromptTemplate.from_template("Create a function: {description}")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    description = request.args.get('description')
    chain_output = chain.run(description)
    
    # VULNERABLE: Compile and execute chain output
    code = compile(chain_output, '<string>', 'exec')
    exec(code)  # CRITICAL: Code injection!
    
    return code


# ============================================================================
# VULNERABLE: Sequential chain output to eval
# ============================================================================
def vulnerable_sequential_chain_to_eval():
    """VULNERABLE: Sequential chain output passed to eval()."""
    llm = OpenAI(temperature=0)
    
    # First chain
    prompt1 = PromptTemplate.from_template("Analyze: {input}")
    chain1 = LLMChain(llm=llm, prompt=prompt1, output_key="analysis")
    
    # Second chain
    prompt2 = PromptTemplate.from_template("Generate code based on: {analysis}")
    chain2 = LLMChain(llm=llm, prompt=prompt2)
    
    # Sequential chain
    overall_chain = SimpleSequentialChain(chains=[chain1, chain2], verbose=True)
    
    user_input = request.json.get('input')
    chain_output = overall_chain.run(user_input)
    
    # VULNERABLE: Execute sequential chain output
    result = eval(chain_output)  # CRITICAL: Code injection!
    
    return result


# ============================================================================
# SAFE: Chain output validation and safe parsing
# ============================================================================
def safe_chain_output_handling():
    """SAFE: Chain output handled safely without code execution."""
    llm = OpenAI(temperature=0)
    prompt = PromptTemplate.from_template("Generate JSON for: {task}")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    task = request.args.get('task')
    chain_output = chain.run(task)
    
    # SAFE: Parse as JSON instead of executing as code
    import json
    try:
        result = json.loads(chain_output)  # Safe parsing
    except json.JSONDecodeError:
        # Handle invalid JSON
        result = {"error": "Invalid output format"}
    
    # SAFE: Use structured output, never eval/exec/compile
    return result
