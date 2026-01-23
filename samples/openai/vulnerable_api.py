"""
Vulnerable API endpoint that processes LLM responses unsafely.
"""

from flask import Flask, request, jsonify
from openai import OpenAI
import subprocess

app = Flask(__name__)
client = OpenAI()


@app.route("/api/execute-code", methods=["POST"])
def execute_code():
    """VULNERABLE: Execute code from LLM response."""
    data = request.json
    prompt = data.get("prompt", "")
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Write Python code: {prompt}"}]
    )
    
    code = response.choices[0].message.content
    # CRITICAL VULNERABILITY: Executing untrusted LLM output
    exec(code)
    
    return jsonify({"status": "executed"})


@app.route("/api/run-command", methods=["POST"])
def run_command():
    """VULNERABLE: Run shell command from LLM."""
    data = request.json
    task = data.get("task", "")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Generate command: {task}"}]
    )
    
    command = response.choices[0].message.content
    # CRITICAL VULNERABILITY: Command injection
    subprocess.Popen(command, shell=True)
    
    return jsonify({"status": "running"})


@app.route("/api/compile", methods=["POST"])
def compile_code():
    """VULNERABLE: Compile code from LLM."""
    from anthropic import Anthropic
    
    data = request.json
    description = data.get("description", "")
    
    anthropic = Anthropic()
    response = anthropic.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=200,
        messages=[{"role": "user", "content": f"Code: {description}"}]
    )
    
    code = response.content[0].text
    # CRITICAL VULNERABILITY: Compiling untrusted code
    compile(code, "<api>", "exec")
    
    return jsonify({"status": "compiled"})


if __name__ == "__main__":
    app.run(debug=True)
