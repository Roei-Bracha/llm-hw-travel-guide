import threading
import queue
import os
import json
from typing import Any, Dict, Optional
from utils.llm_client import get_llm_client
from utils.brave_client import BraveSearchClient
from utils.logger import setup_logger

logger = setup_logger("BaseAgent")

class BaseAgent(threading.Thread):
    def __init__(self, input_queue: queue.Queue, output_queue: queue.Queue, prompt_file: str):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.llm_client = get_llm_client()
        self.search_client = BraveSearchClient()
        self.prompt_template = self._load_prompt(prompt_file)
        self.running = True

    def _load_prompt(self, filename: str) -> str:
        path = os.path.join("agents", "prompts", filename)
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {path}")
            return ""

    def run(self):
        logger.info(f"{self.__class__.__name__} started.")
        while self.running:
            try:
                # Timeout allows checking self.running periodically
                item = self.input_queue.get(timeout=1)
                if item is None: # Sentinel to stop
                    break
                
                result = self.process(item)
                if result:
                    self.output_queue.put(result)
                
                self.input_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in {self.__class__.__name__}: {e}")
        
        logger.info(f"{self.__class__.__name__} stopped.")

    def process(self, data: Any) -> Any:
        """
        To be implemented by subclasses.
        """
        raise NotImplementedError

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Helper to parse JSON from LLM response.
        Handles potential markdown code blocks.
        """
        try:
            # Find the first '{' and last '}'
            start = response.find('{')
            end = response.rfind('}')
            
            if start != -1 and end != -1:
                json_str = response[start:end+1]
                return json.loads(json_str)
            
            # Fallback: try to parse the whole string if no braces found (unlikely for valid JSON)
            return json.loads(response.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response}")
            return {}
