"""Observability integration (Prometheus, OpenTelemetry)."""
from typing import Optional, Dict, Any
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


class MetricsCollector:
    """Prometheus metrics collector for shadow-field."""
    
    def __init__(self, namespace: str = "shadow_field"):
        self.namespace = namespace
        
        # Metrics
        self.packets_collected = Counter(
            f"{namespace}_packets_total",
            "Total packets collected",
            ["model_id"]
        )
        self.tension_gauge = Gauge(
            f"{namespace}_tension",
            "Current tension value",
            ["model_id"]
        )
        self.curvature_gauge = Gauge(
            f"{namespace}_curvature",
            "Current curvature value",
            ["model_id"]
        )
        self.stability_gauge = Gauge(
            f"{namespace}_stability",
            "Current stability value",
            ["model_id"]
        )
        self.buffer_size = Gauge(
            f"{namespace}_buffer_size",
            "Current collector buffer size",
            ["model_id"]
        )
        self.latency_hist = Histogram(
            f"{namespace}_ingest_latency_seconds",
            "Ingest operation latency",
            ["model_id"]
        )
    
    def record_packet(self, packet: Any, model_id: str):
        """Record a delta packet to Prometheus."""
        self.packets_collected.labels(model_id=model_id).inc()
        self.tension_gauge.labels(model_id=model_id).set(packet.tension_delta)
        self.curvature_gauge.labels(model_id=model_id).set(packet.curvature_delta)
        self.stability_gauge.labels(model_id=model_id).set(packet.stability_trend)
    
    def record_buffer_size(self, size: int, model_id: str):
        self.buffer_size.labels(model_id=model_id).set(size)
    
    def record_latency(self, seconds: float, model_id: str):
        self.latency_hist.labels(model_id=model_id).observe(seconds)
    
    def export(self) -> str:
        return generate_latest()


class TraceExporter:
    """OpenTelemetry trace exporter for distributed tracing."""
    
    def __init__(self, endpoint: Optional[str] = None):
        self.provider = TracerProvider()
        if endpoint:
            exporter = OTLPSpanExporter(endpoint=endpoint)
            processor = BatchSpanProcessor(exporter)
            self.provider.add_span_processor(processor)
        
        trace.set_tracer_provider(self.provider)
        self.tracer = trace.get_tracer("shadow-field-delta-system")
    
    def create_span(self, name: str, attributes: Optional[Dict] = None):
        """Create a trace span for tracking operations."""
        return self.tracer.start_as_current_span(
            name,
            kind=SpanKind.INTERNAL,
            attributes=attributes or {}
        )
    
    def trace_ingest(self, system, raw_motion: Any) -> Optional[Any]:
        """Trace the full ingest pipeline."""
        with self.create_span("ingest", {
            "harness_id": system.harness_id,
            "model_id": system.model_id.value,
        }) as span:
            
            # Add motion summary as attribute (safe, non-content)
            motion_hash = hash(str(raw_motion)) % 1000000
            span.set_attribute("motion_hash", motion_hash)
            
            # Execute ingest
            result = system.ingest_with_features(raw_motion)
            
            if result:
                span.set_attribute("packet_tension", result.tension_delta)
                span.set_attribute("packet_curvature", result.curvature_delta)
                span.set_attribute("packet_stability", result.stability_trend)
            
            return result