# Shadow-Field Delta System v1.0

Co-variant, codex-safe behavioral telemetry field with model-aware auto-tuning.

## Quick Start

```bash
# Development
pip install -e .[dev,serve,monitoring]
shadow-field serve --port 8080

# Docker
docker-compose up -d

# Architecture
- ShadowField: Non-intersecting deformation observer

- Bridle: Governor with damping and smoothing

- DeltaCollector: Bounded second-order telemetry buffer

- AutoTuner: Model-aware threshold adaptation

- UnifiedRuntimeDeltaSystem: Composition root

# API Endpoints (FastAPI)
| Endpoint | Method | Description |
|----------|--------|-------------------------------|
| /health | GET	| Health check |
| /ingest | POST | Ingest raw motion (any JSON) |
| /deltas | GET	| Export delta log (JSON) |
| /status | GET	| System status + metrics |
| /models | GET	| List available model traits |
| /tune | POST | Update model traits dynamically |

# Deployment

# Build and run all services
docker-compose up -d

# Scale model instances
docker-compose up -d --scale shadow-field=5

# Monitoring
- Prometheus: http://localhost:9090

- Grafana: http://localhost:3000 (admin/shadow)

# Integration with Stability Layer Codex
The system is designed as a passive observer:

1. Receive structural motion signals (not raw codex content)

2. Extract second-order deformation features

3. Produce model-aware deltas

4. Store only telemetry (never semantics)

5. Export logs for cross-model comparison

# Testing
pytest tests/ -v --cov=shadow_field

# Extended
Real Extraction Implemention:
extended/core/system.py

# License
MIT



