import argparse
import queue
import sys
from core.mapper import RouteFinder
from core.scheduler import Scheduler
from core.orchestrator import Orchestrator
from core.collector import Collector
from utils.logger import setup_logger

logger = setup_logger("Main")

def main():
    parser = argparse.ArgumentParser(description="Agent-Based Travel Guide")
    parser.add_argument("start", help="Start address")
    parser.add_argument("destination", help="Destination address")
    parser.add_argument("--limit", type=int, help="Limit the number of steps to process", default=None)
    args = parser.parse_args()

    logger.info(f"Starting trip from '{args.start}' to '{args.destination}'")

    # 1. Get Route
    try:
        mapper = RouteFinder()
        steps = mapper.get_route(args.start, args.destination)
    except Exception as e:
        logger.error(f"Failed to get route: {e}")
        sys.exit(1)

    if not steps:
        logger.error("No route found.")
        sys.exit(1)

    logger.info(f"Route found with {len(steps)} steps.")

    if args.limit and args.limit > 0:
        logger.info(f"Limiting processing to first {args.limit} steps.")
        steps = steps[:args.limit]

    # 2. Initialize Queues
    task_queue = queue.Queue()
    collector_queue = queue.Queue()

    # 3. Initialize Components
    scheduler = Scheduler(task_queue)
    orchestrator = Orchestrator(task_queue, collector_queue)
    collector = Collector(collector_queue, total_steps=len(steps))

    # 4. Schedule Tasks
    scheduler.schedule_steps(steps)

    # 5. Start Execution
    collector.start()
    orchestrator.start() # Blocks until agents are done

    # 6. Wait for Collector
    collector.join()
    
    # 7. Final Report
    collector.generate_report()

if __name__ == "__main__":
    main()
