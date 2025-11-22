import abc
import os
import subprocess
from config import Config
from utils.logger import setup_logger

logger = setup_logger("LLMClient")

class BaseLLMClient(abc.ABC):
    @abc.abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

class MockLLMClient(BaseLLMClient):
    def generate_text(self, prompt: str) -> str:
        logger.info(f"Mock LLM received prompt: {prompt[:50]}...")
        return "This is a mock response from the LLM."

class ClaudeCLIClient(BaseLLMClient):
    def generate_text(self, prompt: str) -> str:
        logger.info(f"Claude CLI received prompt length: {len(prompt)}")
        
        try:
            # We assume 'claude' is in the PATH.
            # The user said "The agents will run using commend lines that will tell claude code to run agents."
            # We'll pass the prompt via stdin or argument. 
            # Let's try passing as argument first, but for long prompts stdin is safer.
            # However, typical CLI usage might be `claude "prompt"`
            
            # Let's try to echo the prompt into claude if it supports reading from stdin
            # or just pass it as an argument.
            # Given "claude code", it might be `claude` command.
            
            # Let's assume `claude -p "prompt"` or just `claude "prompt"`
            # But for safety with special characters, passing via stdin is best if supported.
            # If not, we'll use a temporary file.
            
            # Strategy: Write prompt to a temp file and cat it to claude?
            # Or just subprocess.run(['claude', prompt])
            
            # Let's assume the command is simply `claude` and it takes the prompt as an argument.
            # NOTE: If the prompt is very long, this might hit shell limits.
            # A safer way if `claude` accepts stdin:
            # process = subprocess.Popen(['claude'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # stdout, stderr = process.communicate(input=prompt)
            
            # Since I don't know the exact `claude` CLI flags, I will assume it accepts input as the first argument
            # similar to `llm` CLI tools.
            
            # User said: "The agents will run using commend lines that will tell claude code to run agents."
            # This implies I should construct a command line.
            
            # Prepare environment with API key
            env = os.environ.copy()
            if Config.LLM_API_KEY:
                env["ANTHROPIC_API_KEY"] = Config.LLM_API_KEY
            
            # Run claude with the prompt
            # User instructions: use -p for print mode and --dangerously-skip-permissions for headless
            
            result = subprocess.run(
                ['claude', '--dangerously-skip-permissions', '-p', prompt], 
                capture_output=True, 
                text=True,
                timeout=120, # Increased timeout for safety
                env=env
            )
            
            if result.returncode != 0:
                logger.error(f"Claude CLI Error: {result.stderr}")
                return f"Error calling Claude CLI: {result.stderr}"
                
            return result.stdout.strip()
            
        except FileNotFoundError:
            logger.error("Claude CLI tool not found. Please ensure 'claude' is installed and in PATH.")
            return "Error: 'claude' executable not found."
        except Exception as e:
            logger.error(f"Error executing Claude CLI: {e}")
            return f"Error: {e}"

def get_llm_client() -> BaseLLMClient:
    # Default to ClaudeCLIClient as per new requirements
    # But we can check LLM_PROVIDER if we want to keep flexibility
    provider = Config.LLM_PROVIDER.lower()
    
    if provider == "mock":
        return MockLLMClient()
    
    # Default to Claude CLI
    return ClaudeCLIClient()
