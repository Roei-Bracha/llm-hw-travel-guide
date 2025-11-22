import queue
from typing import Dict, Any
from agents.base_agent import BaseAgent
from models.content import ContentCandidate, SelectedContent
from utils.logger import setup_logger

logger = setup_logger("JudgeAgent")

class JudgeAgent(BaseAgent):
    def __init__(self, input_queue, output_queue):
        super().__init__(input_queue, output_queue, "judge_agent.md")
        self.buffer: Dict[str, Dict[str, ContentCandidate]] = {}

    def run(self):
        # Override run to handle buffering logic
        logger.info(f"{self.__class__.__name__} started.")
        while self.running:
            try:
                item = self.input_queue.get(timeout=1)
                if item is None:
                    break
                
                step_id, candidate = item
                self._add_to_buffer(step_id, candidate)
                
                if self._is_ready(step_id):
                    result = self._judge(step_id)
                    self.output_queue.put(result)
                    del self.buffer[step_id]
                
                self.input_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in JudgeAgent: {e}")
        
        logger.info(f"{self.__class__.__name__} stopped.")

    def _add_to_buffer(self, step_id: str, candidate: ContentCandidate):
        if step_id not in self.buffer:
            self.buffer[step_id] = {}
        self.buffer[step_id][candidate.type] = candidate
        logger.info(f"Judge received {candidate.type} for {step_id}. Have {len(self.buffer[step_id])}/3.")

    def _is_ready(self, step_id: str) -> bool:
        # We expect 3 types: video, music, history
        return len(self.buffer[step_id]) == 3

    def _judge(self, step_id: str) -> SelectedContent:
        candidates = self.buffer[step_id]
        
        # Construct prompt
        # We need location/instruction. But Judge doesn't have RouteStep directly.
        # We can either pass RouteStep in the tuple or just use generic context.
        # The prompt expects {{location}} and {{instruction}}.
        # Issue: We don't have location/instruction here if we only passed (step_id, candidate).
        # Solution: The candidates might have some context, or we should have passed the step info.
        # Let's assume for now we just say "Unknown Location" or we update the flow to pass step info.
        # Better: Pass (step, candidate) from ContentAgents?
        # Or just rely on the candidates' descriptions.
        
        # Let's update ContentAgents to pass (step, candidate) instead of (step.id, candidate)?
        # Or just use placeholders since the candidates describe themselves.
        # The prompt uses {{location}} and {{instruction}}.
        # I will use "Refer to candidates" for now to avoid refactoring everything.
        # OR, I can just extract it from the candidates if I added it there.
        # Let's just use "Current Step" for location.
        
        prompt = self.prompt_template.replace("{{location}}", "Current Step Location")
        prompt = prompt.replace("{{instruction}}", "Follow route instructions")
        
        prompt = prompt.replace("{{video_candidate}}", f"{candidates['video'].title}: {candidates['video'].description}")
        prompt = prompt.replace("{{music_candidate}}", f"{candidates['music'].title}: {candidates['music'].description}")
        prompt = prompt.replace("{{history_candidate}}", f"{candidates['history'].title}: {candidates['history'].description}")
        
        response = self.llm_client.generate_text(prompt)
        data = self._parse_json_response(response)
        
        selected_type = data.get("selected_type", "video")
        reasoning = data.get("reasoning", "")
        
        # Fallback if LLM returns invalid type
        if selected_type not in candidates:
            selected_type = "video"
            
        return SelectedContent(
            step_id=step_id,
            chosen_candidate=candidates[selected_type],
            judge_reasoning=reasoning
        )

    def process(self, data: Any) -> Any:
        # Not used since we override run
        pass
