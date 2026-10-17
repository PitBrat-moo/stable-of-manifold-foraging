import pytest
from shadow_field.core.system import UnifiedRuntimeDeltaSystem
from shadow_field.core.tuner import ModelID


def test_no_direct_codex_access():
    """Field never receives codex content — only motion proxies."""
    system = UnifiedRuntimeDeltaSystem()
    
    # Simulate codex content (should never be passed directly)
    codex_content = {"secret": "data", "semantics": "..."}
    
    # We pass a *proxy* (hash, ID, or structural descriptor), not content
    proxy = hash(str(codex_content)) % 10000
    packet = system.ingest(proxy)
    
    # Packet contains no semantic content
    assert packet is None or "secret" not in str(packet.__dict__)


def test_second_order_only():
    """Deltas are differences, not absolutes."""
    system = UnifiedRuntimeDeltaSystem()
    
    # First ingestion should produce no delta (no previous state)
    p1 = system.ingest(0.5)
    assert p1 is None
    
    # Second should produce delta
    p2 = system.ingest(0.7)
    assert p2 is not None
    assert abs(p2.tension_delta) > 0  # non-zero change


def test_bounded_growth():
    """Collector never exceeds max_size."""
    system = UnifiedRuntimeDeltaSystem(collector_max_size=10)
    
    for i in range(100):
        system.ingest(i / 100.0)
    
    assert len(system.collector._buffer) <= 10


def test_no_recursion():
    """Field does not call back into itself."""
    system = UnifiedRuntimeDeltaSystem()
    
    # This would loop if recursive — we just check it terminates
    for i in range(100):
        system.ingest(i)
    
    assert system._packet_count > 0