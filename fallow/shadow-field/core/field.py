from dataclasses import dataclass
from typing import Any, Optional, Callable
import time
import uuid


@dataclass
class DeformationSignature:
    """Second-order deformation imprint — safe, non-semantic."""
    timestamp: float
    tension: float       # 0.0–1.0 (structural stress)
    curvature: float     # -1.0 to 1.0 (arc direction)
    stability: float     # 0.0–1.0 (local coherence)
    source_id: str       # model or component identifier


class ShadowField:
    """
    Co-variant, non-intersecting behavioral field.
    Tracks system motion via deformation, not content.
    Klein-adjacent: no inside/outside distinction for telemetry.
    """
    
    def __init__(self, harness_id: str, bridle: Optional['Bridle'] = None):
        self.harness_id = harness_id
        self.bridle = bridle
        self._deformation_history: list[DeformationSignature] = []
        self._active = True
        self._field_id = uuid.uuid4().hex[:8]
        
    def observe(self, raw_motion: Any) -> Optional[DeformationSignature]:
        """
        Observe system motion -> produce deformation signature.
        No direct content access — only structural proxies.
        """
        if not self._active:
            return None
            
        # Extract second-order features (deformation, not semantics)
        tension = self._extract_tension(raw_motion)
        curvature = self._extract_curvature(raw_motion)
        stability = self._extract_stability(raw_motion)
        
        sig = DeformationSignature(
            timestamp=time.time(),
            tension=tension,
            curvature=curvature,
            stability=stability,
            source_id=self.harness_id
        )
        
        # Apply bridle if present
        if self.bridle:
            sig = self.bridle.modulate(sig)
        
        self._deformation_history.append(sig)
        return sig
    
    def _extract_tension(self, motion: Any) -> float:
        # Placeholder: structural delta magnitude
        # In practice: gradient norm, rate of change, divergence
        return min(1.0, abs(hash(str(motion)) % 1000) / 1000.0)
    
    def _extract_curvature(self, motion: Any) -> float:
        # Placeholder: directional change
        return (hash(str(motion)) % 200 - 100) / 100.0
    
    def _extract_stability(self, motion: Any) -> float:
        # Placeholder: local variance inverse
        return 0.5 + 0.5 * (hash(str(motion)) % 100) / 100.0
    
    def get_recent(self, n: int = 10) -> list[DeformationSignature]:
        return self._deformation_history[-n:]
    
    def clear(self):
        self._deformation_history.clear()