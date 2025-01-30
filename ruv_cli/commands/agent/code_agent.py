import os
import json
import requests
from typing import Optional, Tuple
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from .base_agent import BaseAgent

# Load environment variables from .env file
load_dotenv(".env")

class CodeAgent(BaseAgent):
    """Agent for code generation and execution"""
    def __init__(self, name: str = "CodeAgent"):
        super().__init__(name=name)
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not self.openrouter_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        
    def log(self, message: str):
        """Print a log message with agent name prefix"""
        print(f"[{self.name}] {message}")
        
    def run(self, code: str) -> Tuple[bool, str]:
        """Execute code in sandbox and return success status and output"""
        try:
            # Get E2B API key
            api_key = os.getenv("E2B_API_KEY")
            if not api_key:
                raise RuntimeError("E2B_API_KEY not set in environment")
            
            # Create sandbox with E2B
            sandbox = Sandbox(
                api_key=api_key,
                template="code-interpreter-v1"
            )
            self.log("Creating sandbox...")
            
            # Execute code
            self.log("Executing code in sandbox...")
            result = sandbox.run_code(code)
            self.log("✓ Code execution successful")
            self.log(f"Result: {result}")
            return True, str(result)
                
        except Exception as e:
            error_msg = str(e)
            self.log(f"Execution failed: {error_msg}")
            return False, error_msg

    def generate_code(self, prompt: str, error_context: Optional[str] = None) -> Optional[str]:
        """Generate Python code using Claude 3.5 Sonnet"""
        try:
            # Prepare the system prompt
            system_prompt = """You are a Python code generator specializing in algorithms and data structures.
Generate only executable Python code without any explanation or markdown formatting.
If provided with an error context, analyze the error and fix the code accordingly.
Focus on writing robust, efficient code that handles edge cases and includes test cases."""

            # Prepare the user prompt
            user_prompt = prompt
            if error_context:
                user_prompt = f"""Previous code generated an error:
{error_context}

Please fix the code and generate a corrected version that handles this error.
Original request: {prompt}"""

            # Make request to OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3-sonnet:beta",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"API request failed: {response.text}")
                
            result = response.json()
            if not result.get("choices"):
                raise RuntimeError("No code generated")
                
            code = result["choices"][0]["message"]["content"].strip()
            return code
            
        except Exception as e:
            self.log(f"Code generation failed: {str(e)}")
            return None

def run_code(user_query: str) -> bool:
    """Generate and execute Python code based on user query using ReACT loop"""
    if not user_query:
        print("[ERROR] No query provided for code agent.")
        return False
        
    try:
        agent = CodeAgent()
        max_attempts = 1
        attempt = 0
        error_context = None
        
        while attempt < max_attempts:
            attempt += 1
            agent.log(f"Attempt {attempt}/{max_attempts}")
            
            # Generate code
            code = agent.generate_code(user_query, error_context)
            if not code:
                return False
                
            agent.log(f"Generated Code:\n{code}")
            
            # Execute code
            success, result = agent.run(code)
            if success:
                agent.log(f"Execution Result:\n{result}")
                return True
                
            # If execution failed, try again with error context
            error_context = result
            agent.log(f"Execution failed: {error_context}")
            agent.log("Retrying with error context...")
            
        agent.log("Max attempts reached. Code execution failed.")
        return False
        
    except Exception as e:
        print(f"[ERROR] Code execution failed: {str(e)}")
        return False