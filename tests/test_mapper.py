import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.mapper import RouteFinder
from config import Config

def test_mapper():
    print("Testing RouteFinder with OpenRouteService...")
    
    if not Config.ORS_API_KEY:
        print("Error: ORS_API_KEY is not set in .env file.")
        return

    try:
        finder = RouteFinder()
        
        # Test case: New York to Boston
        origin = "New York, NY"
        destination = "Boston, MA"
        
        print(f"Fetching route from {origin} to {destination}...")
        steps = finder.get_route(origin, destination)
        
        if not steps:
            print("Failed to get route.")
            return
            
        print(f"Successfully retrieved {len(steps)} steps.")
        
        # Print first few steps
        for i, step in enumerate(steps[:5]):
            print(f"Step {i+1}: {step.instruction} ({step.distance})")
            
        # Verify cache
        cache_file = "cache/route_cache.json"
        if os.path.exists(cache_file):
            print(f"Cache file exists at {cache_file}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
                print(f"Cache contains {len(data)} entries.")
        else:
            print("Cache file was not created.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_mapper()
