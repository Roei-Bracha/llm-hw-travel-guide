import requests
import json
import os
import hashlib
from typing import List, Dict, Any, Optional
from config import Config
from models.step import RouteStep
from utils.logger import setup_logger

logger = setup_logger("RouteFinder")

class RouteFinder:
    def __init__(self):
        if not Config.ORS_API_KEY:
            logger.error("ORS_API_KEY is not set.")
            raise ValueError("ORS_API_KEY is required.")
        
        self.api_key = Config.ORS_API_KEY
        self.base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        self.cache_dir = "cache"
        self.cache_file = os.path.join(self.cache_dir, "route_cache.json")
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load cache
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Cache file is corrupted. Starting with empty cache.")
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _get_cache_key(self, origin: str, destination: str) -> str:
        # Create a unique key based on origin and destination
        key_str = f"{origin.lower()}|{destination.lower()}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _geocode(self, address: str) -> Optional[List[float]]:
        """
        Helper to geocode an address using ORS Geocoding API.
        Returns [lon, lat].
        """
        # Note: ORS Geocoding is a separate endpoint. 
        # For simplicity, we'll assume the user might provide coordinates or we use a simple geocoder.
        # However, ORS directions endpoint takes coordinates, not address strings directly.
        # To keep it simple and free, we will use the ORS Geocoding API if needed, 
        # OR we can ask the user to provide coordinates? 
        # The requirements said "Start address" and "Destination address".
        # So we MUST geocode.
        
        geocode_url = "https://api.openrouteservice.org/geocode/search"
        params = {
            "api_key": self.api_key,
            "text": address,
            "size": 1
        }
        try:
            response = requests.get(geocode_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['features']:
                    # ORS returns [lon, lat]
                    return data['features'][0]['geometry']['coordinates']
        except Exception as e:
            logger.error(f"Geocoding failed for {address}: {e}")
        
        return None

    def get_route(self, origin: str, destination: str) -> List[RouteStep]:
        """
        Fetches the route from ORS API or cache.
        """
        cache_key = self._get_cache_key(origin, destination)
        
        if cache_key in self.cache:
            logger.info(f"Route found in cache for {origin} -> {destination}")
            route_data = self.cache[cache_key]
        else:
            logger.info(f"Fetching route from ORS for {origin} -> {destination}")
            
            # Geocode origin and destination
            start_coords = self._geocode(origin)
            end_coords = self._geocode(destination)
            
            if not start_coords or not end_coords:
                logger.error("Failed to geocode origin or destination.")
                return []
            
            try:
                # Request driving directions
                # ORS expects [[start_lon, start_lat], [end_lon, end_lat]]
                params = {
                    "api_key": self.api_key,
                    "start": f"{start_coords[0]},{start_coords[1]}",
                    "end": f"{end_coords[0]},{end_coords[1]}"
                }
                
                # Using GET request for simplicity
                response = requests.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"ORS API Error: {response.text}")
                    return []
                
                route_data = response.json()
                
                # Update cache
                self.cache[cache_key] = route_data
                self._save_cache()
                
            except Exception as e:
                logger.error(f"Error fetching route: {e}")
                return []

        return self.parse_route(route_data)

    def parse_route(self, route_json: Dict[str, Any]) -> List[RouteStep]:
        """
        Parses the ORS route JSON into a list of RouteStep objects.
        """
        steps: List[RouteStep] = []
        
        if not route_json or 'features' not in route_json:
            return steps
            
        # ORS returns a GeoJSON FeatureCollection
        feature = route_json['features'][0]
        properties = feature.get('properties', {})
        segments = properties.get('segments', [])
        
        if not segments:
            return steps
            
        # We assume single segment for simple A to B routes
        segment = segments[0]
        
        # Geometry coordinates for the entire route
        geometry = feature['geometry']['coordinates']
        
        for i, step_data in enumerate(segment.get('steps', [])):
            # Generate a unique ID for the step
            step_id = f"step_{i}"
            
            instruction = step_data.get('instruction', '')
            distance = f"{step_data.get('distance', 0)} m"
            duration = f"{step_data.get('duration', 0)} s"
            
            # ORS gives way_points indices into the geometry array
            # start_index = step_data.get('way_points', [0, 0])[0]
            # end_index = step_data.get('way_points', [0, 0])[1]
            
            # Let's just take the location of the maneuver
            # The 'way_points' are indices into the geometry coordinates list
            way_points = step_data.get('way_points', [])
            if way_points:
                start_idx = way_points[0]
                end_idx = way_points[-1]
                
                start_coord = geometry[start_idx] # [lon, lat]
                end_coord = geometry[end_idx]     # [lon, lat]
                
                start_loc = {"lat": start_coord[1], "lng": start_coord[0]}
                end_loc = {"lat": end_coord[1], "lng": end_coord[0]}
            else:
                start_loc = {}
                end_loc = {}

            step = RouteStep(
                id=step_id,
                instruction=instruction,
                distance=distance,
                duration=duration,
                start_location=start_loc,
                end_location=end_loc,
                html_instructions=instruction, # ORS sends plain text usually
                address=None 
            )
            steps.append(step)
            
        return steps
