import threading
import queue
import json
from typing import List, Dict
from models.content import SelectedContent
from utils.logger import setup_logger

logger = setup_logger("Collector")

class Collector(threading.Thread):
    def __init__(self, input_queue: queue.Queue, total_steps: int):
        super().__init__()
        self.input_queue = input_queue
        self.total_steps = total_steps
        self.results: Dict[str, SelectedContent] = {}
        self.running = True

    def run(self):
        logger.info("Collector started.")
        processed_count = 0
        
        while self.running:
            try:
                item = self.input_queue.get(timeout=1)
                if item is None:
                    break
                
                if isinstance(item, SelectedContent):
                    self.results[item.step_id] = item
                    processed_count += 1
                    logger.info(f"Collected result for {item.step_id}. ({processed_count}/{self.total_steps})")
                    
                    if processed_count >= self.total_steps:
                        logger.info("All steps collected.")
                        self.running = False
                
                self.input_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in Collector: {e}")
        
        logger.info("Collector stopped.")

    def get_results(self) -> List[SelectedContent]:
        # Return results sorted by step_id (assuming step_0, step_1...)
        # We can sort by the integer part of the ID
        try:
            sorted_keys = sorted(self.results.keys(), key=lambda x: int(x.split('_')[1]))
            return [self.results[k] for k in sorted_keys]
        except Exception:
            return list(self.results.values())

    def generate_report(self):
        results = self.get_results()
        print("\n" + "="*50)
        print("FINAL TRAVEL GUIDE ITINERARY")
        print("="*50 + "\n")
        
        for result in results:
            candidate = result.chosen_candidate
            print(f"Step: {result.step_id}")
            print(f"Selected Content: [{candidate.type.upper()}] {candidate.title}")
            print(f"Description: {candidate.description}")
            if candidate.url:
                print(f"URL: {candidate.url}")
            print(f"Reasoning: {result.judge_reasoning}")
            print("-" * 30)
