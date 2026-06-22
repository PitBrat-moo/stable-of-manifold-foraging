from typing import Optional, Any
from .field import ShadowField, DeformationSignature
from .bridle import Bridle, BridleConfig
from .collector import DeltaCollector, DeltaPacket
from .tuner import AutoTuner, ModelID, ModelTraits


class UnifiedRuntimeDeltaSystem:
    """
    Composition root:
    ShadowField + Bridle + Collector + AutoTuner
    Safe, codex-agnostic telemetry harness.
    """
    
    def __init__(
        self,
        harness_id: str = "primary",
        model_id: ModelID = ModelID.COPILOT,
        collector_max_size: int = 1000,
        bridle_config: Optional[BridleConfig] = None,
        model_traits: Optional[ModelTraits] = None,
    ):
        self.harness_id = harness_id
        self.model_id = model_id
        
        # Components
        self.bridle = Bridle(bridle_config or BridleConfig())
        self.field = ShadowField(harness_id, self.bridle)
        self.collector = DeltaCollector(collector_max_size, model_id.value)
        self.tuner = AutoTuner(model_id, model_traits)
        
        # State
        self._active = True
        self._packet_count = 0
        
    def ingest(self, raw_motion: Any) -> Optional[DeltaPacket]:
        """Main entry point: raw motion -> tuned delta packet."""
        if not self._active:
            return None
        
        # 1. Observe via field (deformation signature)
        sig = self.field.observe(raw_motion)
        if sig is None:
            return None
        
        # 2. Apply auto-tuner (model-aware adjustment)
        tuned_tension, tuned_curvature = self.tuner.tune(
            sig.tension, sig.curvature
        )
        # Reconstruct tuned signature
        tuned_sig = DeformationSignature(
            timestamp=sig.timestamp,
            tension=tuned_tension,
            curvature=tuned_curvature,
            stability=sig.stability,
            source_id=f"{sig.source_id}:tuned"
        )
        
        # 3. Collect delta
        packet = self.collector.collect(tuned_sig)
        if packet:
            self._packet_count += 1
        
        return packet
    
    def get_log(self):
        return self.collector.export_log()
    
    def to_json(self) -> str:
        return self.collector.to_json()
    
    def reset(self):
        self.field.clear()
        self.collector.clear()
        self._packet_count = 0
    
    def status(self) -> dict:
        return {
            "harness_id": self.harness_id,
            "model_id": self.model_id.value,
            "active": self._active,
            "packet_count": self._packet_count,
            "buffer_size": len(self.collector._buffer),
            "tuner_traits": self.tuner.traits.__dict__,
        }