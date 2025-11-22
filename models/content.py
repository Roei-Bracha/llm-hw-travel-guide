from dataclasses import dataclass
from typing import Optional

@dataclass
class ContentCandidate:
    type: str  # "video", "music", "history"
    title: str
    description: str
    reasoning: str
    url: Optional[str] = None

@dataclass
class SelectedContent:
    step_id: str
    chosen_candidate: ContentCandidate
    judge_reasoning: str
