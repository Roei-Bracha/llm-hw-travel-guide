from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class RouteStep:
    id: str
    instruction: str
    distance: str
    duration: str
    start_location: Dict[str, float]  # {lat: float, lng: float}
    end_location: Dict[str, float]    # {lat: float, lng: float}
    html_instructions: str
    address: Optional[str] = None
