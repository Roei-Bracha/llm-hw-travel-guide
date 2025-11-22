import queue
import threading
import time
from typing import Optional, List
from core.mapper import RouteFinder
from core.scheduler import Scheduler
from core.orchestrator import Orchestrator
from core.collector import Collector
from models.content import SelectedContent
from utils.logger import setup_logger

logger = setup_logger("Engine")

class TravelGuideEngine(threading.Thread):
    def __init__(self, start_location: str, destination: str, limit: Optional[int] = None):
        super().__init__()
        self.start_location = start_location
        self.destination = destination
        self.limit = limit
        self.running = True
        self.results: List[SelectedContent] = []
        self.error: Optional[str] = None
        self.is_complete = False
        
        # Queues
        self.task_queue = queue.Queue()
        self.collector_queue = queue.Queue()
        
        # Components
        self.scheduler = Scheduler(self.task_queue)
        self.orchestrator = Orchestrator(self.task_queue, self.collector_queue)
        self.collector = None # Initialized after route is found

    def run(self):
        try:
            logger.info(f"Starting engine for {self.start_location} -> {self.destination}")
            
            # 1. Get Route
            mapper = RouteFinder()
            steps = mapper.get_route(self.start_location, self.destination)
            
            if not steps:
                self.error = "No route found."
                logger.error(self.error)
                self.is_complete = True
                return

            if self.limit and self.limit > 0:
                logger.info(f"Limiting to {self.limit} steps.")
                steps = steps[:self.limit]

            # 2. Initialize Collector
            self.collector = Collector(self.collector_queue, total_steps=len(steps))
            
            # 3. Schedule
            self.scheduler.schedule_steps(steps)
            
            # 4. Start Components
            self.collector.start()
            self.orchestrator.start() # Blocks until agents are done
            
            # 5. Wait for Collector
            self.collector.join()
            
            # 6. Get Results
            self.results = self.collector.get_results()
            self.is_complete = True
            logger.info("Engine execution complete.")
            
        except Exception as e:
            self.error = str(e)
            logger.error(f"Engine error: {e}")
            self.is_complete = True

    def get_progress(self) -> float:
        if not self.collector:
            return 0.0
        # This is a rough estimate. Collector doesn't expose progress directly easily 
        # without modifying it. Let's just return 0.5 if running, 1.0 if complete.
        # Or better, let's rely on results count if we can access it safely.
        # Since Collector is a thread, accessing its state might be race-prone but 
        # for a progress bar it's acceptable.
        if self.is_complete:
            return 1.0
        
        # We can check how many results are in.
        # But Collector.results is a dict.
        try:
            current = len(self.collector.results)
            total = self.collector.total_steps
            return current / total if total > 0 else 0.0
        except:
            return 0.0
