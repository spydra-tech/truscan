"""
Vulnerable workflow automation using LLM.
Demonstrates real-world vulnerable patterns.
"""

from openai import OpenAI
from anthropic import Anthropic
import subprocess
import os


class VulnerableWorkflow:
    """Workflow class with multiple vulnerabilities."""
    
    def __init__(self):
        self.openai_client = OpenAI()
        self.anthropic_client = Anthropic()
    
    def automate_task(self, task_description: str):
        """VULNERABLE: Automate task using LLM-generated code."""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Write code to: {task_description}"}]
        )
        code = response.choices[0].message.content
        # CRITICAL: Executing untrusted code
        exec(code)
    
    def run_automated_command(self, goal: str):
        """VULNERABLE: Run command suggested by LLM."""
        response = self.anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=100,
            messages=[{"role": "user", "content": f"Command to achieve: {goal}"}]
        )
        command = response.content[0].text
        # CRITICAL: Command injection
        subprocess.run(command, shell=True)
    
    def process_data_with_llm(self, data: str):
        """VULNERABLE: Process data using LLM-generated code."""
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Process this data: {data}"}]
        )
        processing_code = response.choices[0].message.content
        # CRITICAL: Code injection
        eval(processing_code)
    
    def compile_and_run(self, specification: str):
        """VULNERABLE: Compile and run LLM-generated code."""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Code for: {specification}"}]
        )
        code_str = response.choices[0].message.content
        # CRITICAL: Compiling untrusted code
        compiled = compile(code_str, "<workflow>", "exec")
        exec(compiled)
    
    def execute_system_task(self, task: str):
        """VULNERABLE: Execute system task from LLM."""
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"System command for: {task}"}]
        )
        sys_command = response.choices[0].message.content
        # CRITICAL: System command injection
        os.system(sys_command)


def main():
    """Example usage - DO NOT USE IN PRODUCTION."""
    workflow = VulnerableWorkflow()
    
    # All of these are vulnerable
    workflow.automate_task("process files")
    workflow.run_automated_command("backup data")
    workflow.process_data_with_llm("user data")
    workflow.compile_and_run("analyze results")
    workflow.execute_system_task("cleanup temp files")


if __name__ == "__main__":
    main()
