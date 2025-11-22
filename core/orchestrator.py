import threading
import queue
from typing import List
from agents.content_agents import YouTubeAgent, MusicAgent, HistoryAgent
from agents.judge_agent import JudgeAgent
from utils.logger import setup_logger

logger = setup_logger("Orchestrator")

class Orchestrator:
    def __init__(self, task_queue: queue.Queue, collector_queue: queue.Queue):
        self.task_queue = task_queue
        self.collector_queue = collector_queue
        
        # Internal queues
        self.yt_queue = queue.Queue()
        self.music_queue = queue.Queue()
        self.history_queue = queue.Queue()
        self.judge_queue = queue.Queue()
        
        # Agents
        self.agents = []

    def start(self):
        logger.info("Starting Orchestrator...")
        
        # Initialize Agents
        self.agents.append(YouTubeAgent(self.yt_queue, self.judge_queue))
        self.agents.append(MusicAgent(self.music_queue, self.judge_queue))
        self.agents.append(HistoryAgent(self.history_queue, self.judge_queue))
        self.agents.append(JudgeAgent(self.judge_queue, self.collector_queue))
        
        # Start Agents
        for agent in self.agents:
            agent.start()
            
        # Process Task Queue
        self._distribute_tasks()
        
        # Wait for completion
        self._shutdown()

    def _distribute_tasks(self):
        logger.info("Distributing tasks to agents...")
        while True:
            item = self.task_queue.get()
            if item is None:
                break
            
            # Fan-out to content agents
            self.yt_queue.put(item)
            self.music_queue.put(item)
            self.history_queue.put(item)
            
            self.task_queue.task_done()
        
        logger.info("Task distribution complete.")

    def _shutdown(self):
        logger.info("Shutting down agents...")
        
        # Stop Content Agents
        self.yt_queue.put(None)
        self.music_queue.put(None)
        self.history_queue.put(None)
        
        # Wait for Content Agents to finish
        # We assume the first 3 are content agents
        for agent in self.agents[:3]:
            agent.join()
            
        # Stop Judge Agent
        self.judge_queue.put(None)
        self.agents[3].join()
        
        logger.info("Orchestrator stopped.")
