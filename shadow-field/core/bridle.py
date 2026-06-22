from dataclasses import dataclass
from typing import Optional


@dataclass
class BridleConfig:
    max_tension: float = 0.9
    min_tension: float = 0.05
    curvature_limit: float = 0.8
    smoothing_alpha: float = 0.3  # IIR low-pass


class Bridle:
    """
    Governor — modulates intensity and shapes arcs.
    Prevents runaway motion and reduces volatility.
    """
    
    def __init__(self, config: Optional[BridleConfig] = None):
        self.config = config or BridleConfig()
        self._prev_tension = 0.5
        self._prev_curvature = 0.0
        
    def modulate(self, sig: 'DeformationSignature') -> 'DeformationSignature':
        """Apply damping and smoothing to a deformation signature."""
        # Clamp tension
        tension = min(self.config.max_tension, max(self.config.min_tension, sig.tension))
        
        # Smooth tension (low-pass)
        tension = (self.config.smoothing_alpha * tension + 
                   (1 - self.config.smoothing_alpha) * self._prev_tension)
        
        # Limit curvature
        curvature = max(-self.config.curvature_limit, 
                        min(self.config.curvature_limit, sig.curvature))
        
        # Store for next cycle
        self._prev_tension = tension
        self._prev_curvature = curvature
        
        return DeformationSignature(
            timestamp=sig.timestamp,
            tension=tension,
            curvature=curvature,
            stability=sig.stability,
            source_id=sig.source_id
        )