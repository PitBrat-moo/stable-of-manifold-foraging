"""System-level metrics extractors."""
import psutil
import time
from typing import Optional


def extract_cpu_load() -> float:
    """CPU load as proxy for system tension."""
    return psutil.cpu_percent(interval=0.1) / 100.0


def extract_memory_pressure() -> float:
    """Memory pressure as stability indicator."""
    mem = psutil.virtual_memory()
    return mem.percent / 100.0


def extract_network_metrics() -> Optional[dict]:
    """Network I/O as curvature proxy."""
    net = psutil.net_io_counters()
    if net:
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        }
    return None