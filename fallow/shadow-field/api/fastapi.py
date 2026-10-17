"""FastAPI server for shadow-field delta system."""
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Optional, List
from loguru import logger
import time
import json

from shadow_field.core.system import UnifiedRuntimeDeltaSystem
from shadow_field.core.tuner import ModelID, ModelTraits
from shadow_field.integration.stability_layer import StabilityLayerBinding, StabilityLayerConfig
from shadow_field.integration.model_surface import ModelSurfaceAdapter, SurfaceConfig, SurfaceType
from shadow_field.integration.observability import MetricsCollector, TraceExporter


# Pydantic models for API
class IngestRequest(BaseModel):
    motion: Any
    metadata: Optional[dict] = Field(default_factory=dict)
    model_id: Optional[str] = "copilot"


class TuneRequest(BaseModel):
    sensitivity: Optional[float] = None
    damping_factor: Optional[float] = None
    noise_floor: Optional[float] = None
    curvature_bias: Optional[float] = None


class CompareRequest(BaseModel):
    surface_a: str
    surface_b: str


app = FastAPI(title="Shadow-Field Delta System v1.0", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
systems = {}
collector = MetricsCollector()
tracer = TraceExporter()


@app.on_event("startup")
async def startup():
    """Initialize system instances for all models."""
    global systems
    
    for model in ModelID:
        system = UnifiedRuntimeDeltaSystem(
            harness_id=f"harness-{model.value}",
            model_id=model,
        )
        systems[model.value] = system
        logger.info(f"Initialized system for {model.value}")
    
    # Create stability layer binding
    stability_config = StabilityLayerConfig(codex_id="primary-stability")
    stability_binding = StabilityLayerBinding(stability_config, systems["copilot"])
    systems["_stability"] = stability_binding
    
    logger.info("Shadow-Field Delta System v1.0 ready")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "systems": list(systems.keys()),
        "timestamp": time.time()
    }


@app.post("/ingest/{model_id}")
async def ingest(
    model_id: str,
    request: IngestRequest
):
    """Ingest raw motion and collect delta packet."""
    system = systems.get(model_id.lower())
    if not system:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    start = time.time()
    
    # Trace the ingest
    with tracer.create_span("api_ingest", {
        "model_id": model_id,
        "motion_hash": hash(str(request.motion)) % 1000000,
    }):
        packet = system.ingest_with_features(request.motion)
        
        if packet:
            collector.record_packet(packet, model_id)
            collector.record_buffer_size(len(system.collector._buffer), model_id)
            
            latency = time.time() - start
            collector.record_latency(latency, model_id)
        
        return {
            "status": "ok",
            "packet": packet.__dict__ if packet else None,
            "latency": latency,
            "buffer_size": len(system.collector._buffer),
        }


@app.get("/deltas/{model_id}")
async def get_deltas(
    model_id: str,
    limit: Optional[int] = 100
):
    """Export delta log for a model."""
    system = systems.get(model_id.lower())
    if not system:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    logs = system.get_log()
    return {
        "model_id": model_id,
        "count": len(logs),
        "deltas": logs[-limit:],
        "status": system.status(),
    }


@app.get("/status")
async def status():
    """Overall system status."""
    return {
        "systems": {
            name: system.status() 
            for name, system in systems.items() 
            if not name.startswith("_")
        },
        "metrics": {
            "total_packets": collector.packets_collected._value.get(),
        },
        "timestamp": time.time(),
    }


@app.post("/tune/{model_id}")
async def tune(
    model_id: str,
    request: TuneRequest
):
    """Update model traits dynamically."""
    system = systems.get(model_id.lower())
    if not system:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    traits = system.tuner.traits
    if request.sensitivity is not None:
        traits.sensitivity = request.sensitivity
    if request.damping_factor is not None:
        traits.damping_factor = request.damping_factor
    if request.noise_floor is not None:
        traits.noise_floor = request.noise_floor
    if request.curvature_bias is not None:
        traits.curvature_bias = request.curvature_bias
    
    system.tuner.update_traits(traits)
    
    return {
        "status": "ok",
        "model_id": model_id,
        "traits": traits.__dict__,
    }


@app.get("/models")
async def list_models():
    """List all available model surfaces."""
    return {
        "models": [
            {
                "id": m.value,
                "default_traits": ModelTraits.default_for(m).__dict__,
                "active": m.value in systems,
            }
            for m in ModelID
        ]
    }


@app.post("/compare")
async def compare(request: CompareRequest):
    """Compare two model surfaces."""
    surface_a = systems.get(request.surface_a.lower())
    surface_b = systems.get(request.surface_b.lower())
    
    if not surface_a or not surface_b:
        raise HTTPException(
            status_code=404, 
            detail="One or both surfaces not found"
        )
    
    # Create adapters for comparison
    adapter_a