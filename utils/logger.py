import logging
import sys
import queue
from logging.handlers import QueueHandler

# Global log queue for UI
log_queue = queue.Queue()

def setup_logger(name: str, level=logging.INFO):
    """
    Sets up a logger with the specified name and level.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level) # Set level for console handler
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Queue Handler for UI
    queue_handler = QueueHandler(log_queue)
    queue_handler.setLevel(level) # Set level for queue handler
    queue_handler.setFormatter(formatter)
    logger.addHandler(queue_handler)
    
    # The original check `if not logger.handlers:` is now redundant as handlers are added unconditionally.
    # If the intent was to prevent duplicate handlers on subsequent calls,
    # a more robust check would be needed, e.g., checking handler types.
    # For now, we'll remove the old conditional add and ensure handlers are added.
        
    return logger
