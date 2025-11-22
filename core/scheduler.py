import queue
from typing import List
from models.step import RouteStep
from utils.logger import setup_logger

logger = setup_logger("Scheduler")

class Scheduler:
    def __init__(self, task_queue: queue.Queue):
        self.task_queue = task_queue

    def schedule_steps(self, steps: List[RouteStep]):
        """
        Enqueues all route steps into the task queue.
        """
        logger.info(f"Scheduling {len(steps)} steps...")
        for step in steps:
            self.task_queue.put(step)
        
        # Add None sentinel to indicate end of tasks?
        # Or Orchestrator handles it.
        # Typically, we might want to signal end of input.
        # But since we have multiple agents consuming, we need to be careful.
        # The Orchestrator will likely consume these steps and spawn agents.
        # So one sentinel for the Orchestrator is enough.
        self.task_queue.put(None)
        logger.info("Scheduling complete.")
