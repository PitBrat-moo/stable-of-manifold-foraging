from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List
import json


@dataclass
class DeltaPacket:
    """Safe, second-order telemetry packet."""
    timestamp: float
    model_id: str
    tension_delta: float      # change from previous
    curvature_delta: float
    stability_trend: float    # moving average direction
    raw_signature: dict       # minimal, non-semantic


class DeltaCollector:
    """
    Bounded collector for deformation deltas.
    Second-order only — never stores content.
    """
    
    def __init__(self, max_size: int = 1000, model_id: str = "generic"):
        self.max_size = max_size
        self.model_id = model_id
        self._buffer: deque[DeltaPacket] = deque(maxlen=max_size)
        self._last_sig: Optional[DeformationSignature] = None
        
    def collect(self, sig: DeformationSignature) -> Optional[DeltaPacket]:
        """Ingest a deformation signature -> produce delta packet."""
        if self._last_sig is None:
            self._last_sig = sig
            return None  # first sample, no delta yet
        
        # Compute second-order differences
        tension_delta = sig.tension - self._last_sig.tension
        curvature_delta = sig.curvature - self._last_sig.curvature
        
        # Stability trend (simple moving slope)
        stability_trend = sig.stability - self._last_sig.stability
        
        packet = DeltaPacket(
            timestamp=sig.timestamp,
            model_id=self.model_id,
            tension_delta=round(tension_delta, 4),
            curvature_delta=round(curvature_delta, 4),
            stability_trend=round(stability_trend, 4),
            raw_signature={
                "t": round(sig.tension, 3),
                "c": round(sig.curvature, 3),
                "s": round(sig.stability, 3)
            }
        )
        
        self._buffer.append(packet)
        self._last_sig = sig
        return packet
    
    def export_log(self) -> List[dict]:
        """Export delta log for cross-model comparison."""
        return [p.__dict__ for p in self._buffer]
    
    def to_json(self) -> str:
        return json.dumps(self.export_log(), indent=2)
    
    def clear(self):
        self._buffer.clear()
        self._last_sig = None