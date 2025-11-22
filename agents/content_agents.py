from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from models.content import ContentCandidate
from models.step import RouteStep
from utils.logger import setup_logger

logger = setup_logger("ContentAgents")

class ContentAgent(BaseAgent):
    def process(self, step: RouteStep) -> tuple[str, ContentCandidate]:
        location = step.address if step.address else f"{step.end_location['lat']},{step.end_location['lng']}"
        instruction = step.instruction
        
        # 1. Initial Prompt
        prompt = self.prompt_template.replace("{{location}}", str(location))
        prompt = prompt.replace("{{instruction}}", instruction)
        
        response = self.llm_client.generate_text(prompt)
        data = self._parse_json_response(response)
        
        # 2. Handle Search if needed
        if "search_query" in data:
            query = data["search_query"]
            logger.info(f"{self.__class__.__name__} searching for: {query}")
            
            results = self._perform_search(query)
            
            # 3. Follow-up Prompt with results
            results_str = "\n".join([f"- {r['title']}: {r['description']} ({r['url']})" for r in results])
            follow_up_prompt = f"{prompt}\n\nSearch Results:\n{results_str}\n\nNow select the best option based on these results."
            
            response = self.llm_client.generate_text(follow_up_prompt)
            data = self._parse_json_response(response)
            
        return (step.id, self._create_candidate(data))

    def _perform_search(self, query: str) -> List[Dict[str, str]]:
        raise NotImplementedError

    def _create_candidate(self, data: Dict[str, Any]) -> ContentCandidate:
        raise NotImplementedError

class YouTubeAgent(ContentAgent):
    def __init__(self, input_queue, output_queue):
        super().__init__(input_queue, output_queue, "youtube_agent.md")

    def _perform_search(self, query: str) -> List[Dict[str, str]]:
        return self.search_client.search_videos(query)

    def _create_candidate(self, data: Dict[str, Any]) -> ContentCandidate:
        video = data.get("selected_video", {})
        return ContentCandidate(
            type="video",
            title=video.get("title", "Unknown Video"),
            description=video.get("description", ""),
            url=video.get("url", ""),
            reasoning=video.get("reasoning", "")
        )

class MusicAgent(ContentAgent):
    def __init__(self, input_queue, output_queue):
        super().__init__(input_queue, output_queue, "music_agent.md")

    def _perform_search(self, query: str) -> List[Dict[str, str]]:
        return self.search_client.search_web(query)

    def _create_candidate(self, data: Dict[str, Any]) -> ContentCandidate:
        song = data.get("selected_song", {})
        return ContentCandidate(
            type="music",
            title=f"{song.get('title', 'Unknown')} by {song.get('artist', 'Unknown')}",
            description=song.get("description", ""),
            url=None, # Music might not have a direct URL unless found
            reasoning=song.get("reasoning", "")
        )

class HistoryAgent(ContentAgent):
    def __init__(self, input_queue, output_queue):
        super().__init__(input_queue, output_queue, "history_agent.md")

    def _perform_search(self, query: str) -> List[Dict[str, str]]:
        return self.search_client.search_web(query)

    def _create_candidate(self, data: Dict[str, Any]) -> ContentCandidate:
        story = data.get("selected_story", {})
        return ContentCandidate(
            type="history",
            title=story.get("title", "Unknown Story"),
            description=story.get("content", ""),
            url=None,
            reasoning=story.get("reasoning", "")
        )
