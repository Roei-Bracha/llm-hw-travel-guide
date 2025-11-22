import requests
import os
import json
from typing import List, Dict, Any, Optional
from config import Config
from utils.logger import setup_logger

logger = setup_logger("BraveSearchClient")

class BraveSearchClient:
    def __init__(self):
        if not Config.BRAVE_SEARCH_API_KEY:
            logger.warning("BRAVE_SEARCH_API_KEY is not set. Search functionality will fail.")
        
        self.api_key = Config.BRAVE_SEARCH_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1"
        self.cache_dir = "cache"
        self.cache_file = os.path.join(self.cache_dir, "search_cache.json")
        
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save search cache: {e}")

    def search_web(self, query: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Searches the web for the given query.
        Returns a list of dicts with 'title', 'description', 'url'.
        """
        cache_key = f"web:{query}"
        if cache_key in self.cache:
            logger.info(f"Returning cached web search results for: {query}")
            return self.cache[cache_key]

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {"q": query, "count": count}
        
        try:
            response = requests.get(f"{self.base_url}/web", headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                if 'web' in data and 'results' in data['web']:
                    for item in data['web']['results']:
                        results.append({
                            "title": item.get("title", ""),
                            "description": item.get("description", ""),
                            "url": item.get("url", "")
                        })
                
                self.cache[cache_key] = results
                self._save_cache()
                return results
            else:
                logger.error(f"Brave Search API Error: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def search_videos(self, query: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Searches for videos.
        """
        cache_key = f"video:{query}"
        if cache_key in self.cache:
            logger.info(f"Returning cached video search results for: {query}")
            return self.cache[cache_key]

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {"q": query, "count": count}
        
        try:
            response = requests.get(f"{self.base_url}/videos", headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                if 'results' in data:
                    for item in data['results']:
                        results.append({
                            "title": item.get("title", ""),
                            "description": item.get("description", ""),
                            "url": item.get("url", "")
                        })
                
                self.cache[cache_key] = results
                self._save_cache()
                return results
            else:
                logger.error(f"Brave Video Search API Error: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Video search failed: {e}")
            return []
