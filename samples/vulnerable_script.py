#!/usr/bin/env python3
"""
Vulnerable script that uses LLM output unsafely.
This demonstrates multiple vulnerability patterns.
"""

import openai
import subprocess
import os
import sys


def main():
    """Main function with multiple vulnerabilities."""
    
    # Vulnerability 1: Direct eval of LLM output
    print("Getting code from LLM...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Write a Python function"}]
    )
    code = response.choices[0].message.content
    eval(code)  # VULNERABLE
    
    # Vulnerability 2: Exec with LLM output
    print("Getting more code...")
    response2 = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate Python code"
    )
    more_code = response2.choices[0].text
    exec(more_code)  # VULNERABLE
    
    # Vulnerability 3: Subprocess with shell=True
    print("Getting command...")
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "What command should I run?"}]
    )
    cmd = resp.choices[0].message.content
    subprocess.call(cmd, shell=True)  # VULNERABLE
    
    # Vulnerability 4: os.system with LLM output
    print("Getting system command...")
    response3 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Generate a system command"}]
    )
    sys_cmd = response3.choices[0].message.content
    os.system(sys_cmd)  # VULNERABLE
    
    # Vulnerability 5: subprocess.Popen
    print("Getting Popen command...")
    response4 = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Create a subprocess command"}]
    )
    popen_cmd = response4.choices[0].message.content
    subprocess.Popen(popen_cmd, shell=True)  # VULNERABLE
    
    # Vulnerability 6: Compile LLM output
    print("Compiling LLM code...")
    response5 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Write compiled code"}]
    )
    compile_code = response5.choices[0].message.content
    compile(compile_code, "<script>", "exec")  # VULNERABLE


if __name__ == "__main__":
    main()
