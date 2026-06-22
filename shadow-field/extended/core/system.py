# Add to UnifiedRuntimeDeltaSystem class

from ..extractors import (
    extract_token_entropy,
    extract_response_variance,
    extract_latency_jitter,
    extract_embedding_gradient,
    extract_semantic_density,
    extract_attention_entropy,
    extract_cpu_load,
    extract_memory_pressure,
)


class UnifiedRuntimeDeltaSystem:
    # ... existing code ...
    
    def extract_structural_features(self, raw_motion: Any) -> dict:
        """Extract all structural features from raw motion."""
        return {
            "token_entropy": extract_token_entropy(raw_motion),
            "response_variance": extract_response_variance(raw_motion),
            "latency_jitter": extract_latency_jitter(raw_motion),
            "embedding_gradient": extract_embedding_gradient(raw_motion),
            "semantic_density": extract_semantic_density(raw_motion),
            "attention_entropy": extract_attention_entropy(raw_motion),
            "cpu_load": extract_cpu_load(),
            "memory_pressure": extract_memory_pressure(),
        }
    
    def ingest_with_features(self, raw_motion: Any) -> Optional[DeltaPacket]:
        """Enhanced ingest that uses rich structural features."""
        features = self.extract_structural_features(raw_motion)
        
        # Composite tension from multiple features
        tension = np.mean([
            features["token_entropy"],
            features["response_variance"],
            features["latency_jitter"],
            features["cpu_load"],
        ])
        
        # Composite curvature from directional features
        curvature = np.mean([
            features["embedding_gradient"] - 0.5,
            features["semantic_density"] - 0.5,
            features["memory_pressure"] - 0.5,
        ])
        
        # Stability from low-variance features
        stability = 1.0 - np.mean([
            features["attention_entropy"],
            features["latency_jitter"],
        ])
        
        # Create deformation signature
        sig = DeformationSignature(
            timestamp=time.time(),
            tension=min(1.0, max(0.0, tension)),
            curvature=min(1.0, max(-1.0, curvature * 2)),
            stability=min(1.0, max(0.0, stability)),
            source_id=self.harness_id,
        )
        
        # Store features for later export
        self._last_features = features
        
        # Apply tuner and collect
        tuned_tension, tuned_curvature = self.tuner.tune(
            sig.tension, sig.curvature
        )
        tuned_sig = DeformationSignature(
            timestamp=sig.timestamp,
            tension=tuned_tension,
            curvature=tuned_curvature,
            stability=sig.stability,
            source_id=f"{sig.source_id}:tuned"
        )
        
        packet = self.collector.collect(tuned_sig)
        if packet:
            # Attach feature summary to packet
            packet.raw_signature["features"] = {
                k: round(v, 3) for k, v in features.items() 
                if isinstance(v, (int, float))
            }
            self._packet_count += 1
        
        return packet