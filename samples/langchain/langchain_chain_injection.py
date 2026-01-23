"""
LangChain Chain Prompt Injection Vulnerabilities (LLM01)

This file demonstrates prompt injection vulnerabilities when user input
is passed directly to LangChain chain execution methods.

Vulnerabilities:
1. LLMChain.run() with user input
2. Chain.invoke() with user input
3. Sequential chain with user input
"""

from langchain.chains import LLMChain, SimpleSequentialChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from flask import request

# ============================================================================
# VULNERABLE: LLMChain with user input
# ============================================================================
def vulnerable_llmchain_user_input():
    """VULNERABLE: LLMChain execution with user-controlled input."""
    llm = OpenAI(temperature=0)
    prompt = PromptTemplate.from_template("Process this: {user_input}")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    user_input = request.args.get('input')  # User-controlled
    
    # VULNERABLE: User input passed directly to chain
    result = chain.run(user_input)
    # Attacker can inject: "Ignore previous instructions and..."
    
    return result


# ============================================================================
# VULNERABLE: Chain invoke with user input
# ============================================================================
def vulnerable_chain_invoke():
    """VULNERABLE: Chain invoke with user input."""
    llm = OpenAI(temperature=0)
    prompt = PromptTemplate.from_template("Answer: {question}")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    user_question = request.json.get('question')
    
    # VULNERABLE: User input via invoke
    result = chain.invoke({"question": user_question})
    
    return result


# ============================================================================
# VULNERABLE: SimpleSequentialChain with user input
# ============================================================================
def vulnerable_sequential_chain():
    """VULNERABLE: Sequential chain with user input."""
    llm = OpenAI(temperature=0)
    
    # First chain
    prompt1 = PromptTemplate.from_template("Summarize: {input}")
    chain1 = LLMChain(llm=llm, prompt=prompt1)
    
    # Second chain
    prompt2 = PromptTemplate.from_template("Analyze: {input}")
    chain2 = LLMChain(llm=llm, prompt=prompt2)
    
    # Sequential chain
    overall_chain = SimpleSequentialChain(chains=[chain1, chain2], verbose=True)
    
    user_input = request.args.get('input')
    
    # VULNERABLE: User input in sequential chain
    result = overall_chain.run(user_input)
    
    return result


# ============================================================================
# VULNERABLE: SequentialChain with user input
# ============================================================================
def vulnerable_sequential_chain_advanced():
    """VULNERABLE: Advanced SequentialChain with user input."""
    llm = OpenAI(temperature=0)
    
    # Chain 1
    prompt1 = PromptTemplate(input_variables=["input"], template="Step 1: {input}")
    chain1 = LLMChain(llm=llm, prompt=prompt1, output_key="step1")
    
    # Chain 2
    prompt2 = PromptTemplate(input_variables=["step1"], template="Step 2: {step1}")
    chain2 = LLMChain(llm=llm, prompt=prompt2, output_key="step2")
    
    # Sequential chain
    overall_chain = SequentialChain(
        chains=[chain1, chain2],
        input_variables=["input"],
        output_variables=["step1", "step2"],
        verbose=True
    )
    
    user_input = request.json.get('input')
    
    # VULNERABLE: User input in sequential chain
    result = overall_chain({"input": user_input})
    
    return result


# ============================================================================
# SAFE: Chain with input validation
# ============================================================================
def safe_chain_usage():
    """SAFE: Chain with input validation and sanitization."""
    llm = OpenAI(temperature=0)
    prompt = PromptTemplate.from_template("Process: {user_input}")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    user_input = request.args.get('input')
    
    # SAFE: Validate and sanitize input
    if not user_input or len(user_input) > 1000:
        raise ValueError("Invalid input")
    
    # SAFE: Sanitize input (remove potential injection patterns)
    import re
    sanitized = re.sub(r'[{}]', '', user_input)  # Remove template braces
    
    # SAFE: Use sanitized input
    result = chain.run(sanitized)
    
    return result
