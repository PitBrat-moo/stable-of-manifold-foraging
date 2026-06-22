"""Multi-model surface adapters."""
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from loguru import logger


class SurfaceType(Enum):
    DEEPSEEK = "deepseek"
    CLAUDE = "claude"
    GEMINI = "gemini"
    GROK = "grok"
    COPILOT = "copilot"
    CUSTOM = "custom"


@dataclass
class SurfaceConfig:
    """Configuration for a model surface."""
    surface_type: SurfaceType
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    traits_override: Optional[Dict] = None
    tags: List[str] = field(default_factory=list)


class ModelSurfaceAdapter:
    """
    Adapter for connecting to different model surfaces.
    Enables cross-model delta comparison.
    """
    
    def __init__(self, config: SurfaceConfig, delta_system: Any):
        self.config = config
        self.delta_system = delta_system
        self._surface_id = f"{config.surface_type.value}-{id(self)}"
        self._readings: List[Dict] = []
        
    def observe_response(self, response: Any, metadata: Optional[Dict] = None) -> Optional[Dict]:
        """Observe a model response and extract deltas."""
        # Combine response with metadata
        motion = {
            "response": response,
            "metadata": metadata or {},
            "surface": self.config.surface_type.value,
            "timestamp": __import__('time').time(),
        }
        
        packet = self.delta_system.ingest_with_features(motion)
        
        if packet:
            # Tag with surface info
            packet.raw_signature["surface"] = self.config.surface_type.value
            self._readings.append(packet.__dict__)
            logger.debug(f"Surface {self._surface_id}: collected delta")
        
        return packet.__dict__ if packet else None
    
    def compare_with(self, other_adapter: 'ModelSurfaceAdapter') -> Dict:
        """Cross-model comparison between two surface adapters."""
        if not self._readings or not other_adapter._readings:
            return {"error": "Insufficient readings for comparison"}
        
        # Align timestamps if possible
        my_recent = self._readings[-10:]
        other_recent = other_adapter._readings[-10:]
        
        min_len = min(len(my_recent), len(other_recent))
        my_recent = my_recent[-min_len:]
        other_recent = other_recent[-min_len:]
        
        # Compute deltas between surfaces
        comparisons = []
        for i in range(min_len):
            m = my_recent[i]
            o = other_recent[i]
            comparisons.append({
                "timestamp": m["timestamp"],
                "tension_diff": m["tension_delta"] - o["tension_delta"],
                "curvature_diff": m["curvature_delta"] - o["curvature_delta"],
                "stability_diff": m["stability_trend"] - o["stability_trend"],
            })
        
        return {
            "surface_a": self.config.surface_type.value,
            "surface_b": other_adapter.config.surface_type.value,
            "sample_count": min_len,
            "comparisons": comparisons,
            "summary": {
                "mean_tension_diff": sum(c["tension_diff"] for c in comparisons) / min_len,
                "mean_curvature_diff": sum(c["curvature_diff"] for c in comparisons) / min_len,
                "mean_stability_diff": sum(c["stability_diff"] for c in comparisons) / min_len,
            }
        }
    
    def export_surface_log(self) -> Dict:
        """Export all readings from this surface."""
        return {
            "surface_id": self._surface_id,
            "surface_type": self.config.surface_type.value,
            "readings": self._readings,
            "count": len(self._readings),
        }