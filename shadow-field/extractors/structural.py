"""Structural feature extractors for LLM motion."""
import math
import numpy as np
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class StructuralFeatures:
    """Second-order structural features extracted from system motion."""
    token_entropy: float
    response_variance: float
    latency_jitter: float
    embedding_gradient: float
    semantic_density: float
    attention_entropy: float
    coherence: float
    timestamp: float


def extract_token_entropy(response: Any) -> float:
    """
    Extract entropy from token distribution.
    High entropy = exploratory, low entropy = deterministic.
    """
    if hasattr(response, 'tokens'):
        tokens = response.tokens
    elif isinstance(response, (list, tuple)) and len(response) > 0:
        tokens = response
    else:
        # Fallback: use string representation
        s = str(response)
        freq = {}
        for ch in s[:1000]:
            freq[ch] = freq.get(ch, 0) + 1
        total = sum(freq.values())
        entropy = -sum((v/total) * math.log2(v/total) for v in freq.values())
        return min(1.0, entropy / 8.0)
    
    # Compute entropy of token IDs or strings
    freq = {}
    for t in tokens[:1000]:
        freq[t] = freq.get(t, 0) + 1
    total = sum(freq.values())
    entropy = -sum((v/total) * math.log2(v/total) for v in freq.values())
    return min(1.0, entropy / 12.0)  # Normalize to [0,1]


def extract_response_variance(response: Any) -> float:
    """
    Variance in response structure.
    High variance = unstable/creative, low = stable/predictable.
    """
    s = str(response)
    if len(s) < 2:
        return 0.5
    
    # Use length variance across chunks
    chunk_size = min(50, len(s) // 10)
    chunks = [s[i:i+chunk_size] for i in range(0, len(s), chunk_size)]
    lengths = [len(c) for c in chunks]
    
    if len(lengths) < 2:
        return 0.5
    
    variance = np.var(lengths) / (max(lengths) ** 2)
    return min(1.0, variance)


def extract_latency_jitter(response: Any) -> float:
    """
    Response timing jitter (if timing data available).
    """
    if hasattr(response, 'timing'):
        timings = response.timing
        if len(timings) > 1:
            jitter = np.std(np.diff(timings))
            return min(1.0, jitter / 1000.0)  # Normalize to ms
    
    # Fallback: use response length stability as proxy
    s = str(response)
    if len(s) < 10:
        return 0.5
    
    # Check for repeated patterns as timing proxy
    pattern = s[:20]
    count = s.count(pattern)
    stability = min(1.0, count / (len(s) / 20))
    return 1.0 - stability  # Invert: more repeats = less jitter


def extract_embedding_gradient(response: Any) -> float:
    """
    Rate of change in embedding space.
    High gradient = rapid semantic shifts.
    """
    # This requires actual embedding access; provide placeholder
    if hasattr(response, 'embedding_delta'):
        return min(1.0, abs(response.embedding_delta) / 10.0)
    
    # Fallback: use string hashing as embedding proxy
    s = str(response)
    if len(s) < 2:
        return 0.5
    
    # Approximate gradient via sequential hashing
    chunks = [s[i:i+20] for i in range(0, min(len(s), 100), 20)]
    if len(chunks) < 2:
        return 0.5
    
    deltas = []
    for i in range(len(chunks)-1):
        h1 = hash(chunks[i]) % 100
        h2 = hash(chunks[i+1]) % 100
        deltas.append(abs(h1 - h2) / 100.0)
    
    return min(1.0, np.mean(deltas))


def extract_semantic_density(response: Any) -> float:
    """
    Information density / novelty.
    """
    s = str(response)
    if len(s) < 10:
        return 0.5
    
    # Unique words ratio as density proxy
    words = s.split()
    if len(words) < 2:
        return 0.5
    
    unique = len(set(words))
    density = unique / len(words)
    
    # Also consider rare/uncommon words
    # (simplified: length > 7 as "complex")
    complex_words = sum(1 for w in words if len(w) > 7)
    complexity = min(1.0, complex_words / len(words) * 2)
    
    return min(1.0, (density + complexity) / 2)


def extract_attention_entropy(response: Any) -> float:
    """
    Entropy of attention distribution (if available).
    """
    if hasattr(response, 'attention_weights'):
        weights = response.attention_weights
        if len(weights) > 1:
            probs = np.array(weights) / sum(weights)
            entropy = -sum(p * np.log2(p + 1e-10) for p in probs)
            return min(1.0, entropy / np.log2(len(weights)))
    
    # Fallback: use response structure as proxy
    s = str(response)
    if len(s) < 10:
        return 0.5
    
    # Entropy of character distribution
    freq = {}
    for ch in s[:1000]:
        freq[ch] = freq.get(ch, 0) + 1
    total = sum(freq.values())
    entropy = -sum((v/total) * math.log2(v/total) for v in freq.values())
    return min(1.0, entropy / 8.0)