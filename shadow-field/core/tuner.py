from enum import Enum
from typing import Dict, Optional


class ModelID(Enum):
    DEEPSEEK = "deepseek"
    CLAUDE = "claude"
    GEMINI = "gemini"
    GROK = "grok"
    COPILOT = "copilot"


@dataclass
class ModelTraits:
    """Model-specific behavioral tuning parameters."""
    sensitivity: float       # 0.0–1.0 (how responsive to motion)
    damping_factor: float    # 0.0–1.0 (inertia)
    noise_floor: float       # 0.0–1.0 (minimum detectable change)
    curvature_bias: float    # -1.0 to 1.0 (preferred arc direction)
    
    @classmethod
    def default_for(cls, model_id: ModelID) -> 'ModelTraits':
        """Known trait profiles — tune empirically."""
        profiles = {
            ModelID.DEEPSEEK: cls(0.7, 0.4, 0.05, 0.1),
            ModelID.CLAUDE: cls(0.8, 0.3, 0.03, -0.05),
            ModelID.GEMINI: cls(0.6, 0.5, 0.08, 0.2),
            ModelID.GROK: cls(0.9, 0.2, 0.02, -0.1),
            ModelID.COPILOT: cls(0.5, 0.6, 0.1, 0.0),
        }
        return profiles.get(model_id, cls(0.7, 0.4, 0.05, 0.0))


class AutoTuner:
    """
    Model-aware adaptive threshold modulator.
    Adjusts field sensitivity based on active model traits.
    """
    
    def __init__(self, model_id: ModelID, traits: Optional[ModelTraits] = None):
        self.model_id = model_id
        self.traits = traits or ModelTraits.default_for(model_id)
        self._history: list[float] = []
        
    def tune(self, raw_tension: float, raw_curvature: float) -> tuple[float, float]:
        """
        Apply model-specific scaling to tension and curvature.
        Returns (adjusted_tension, adjusted_curvature).
        """
        # Apply sensitivity + noise floor
        tension = max(self.traits.noise_floor, 
                      raw_tension * self.traits.sensitivity)
        
        # Apply damping (inertia)
        if self._history:
            avg_tension = sum(self._history[-5:]) / min(5, len(self._history))
            tension = tension * (1 - self.traits.damping_factor) + avg_tension * self.traits.damping_factor
        
        # Apply curvature bias
        curvature = raw_curvature + self.traits.curvature_bias * 0.1
        
        # Clip
        tension = min(1.0, max(0.0, tension))
        curvature = min(1.0, max(-1.0, curvature))
        
        self._history.append(tension)
        if len(self._history) > 100:
            self._history.pop(0)
            
        return tension, curvature
    
    def update_traits(self, new_traits: ModelTraits):
        self.traits = new_traits