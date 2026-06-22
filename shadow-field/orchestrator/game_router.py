"""Game-specific router using shadow-field deltas."""
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
import time

from shadow_field.core.system import UnifiedRuntimeDeltaSystem
from shadow_field.core.tuner import ModelID


class RouteTarget(Enum):
    ONLINE = "online"
    LOCAL = "local"
    HYBRID = "hybrid"


@dataclass
class RoutingDecision:
    target: RouteTarget
    confidence: float  # 0.0–1.0
    reason: str
    offload_ratio: float  # 0.0 = all online, 1.0 = all local
    context_delta: Optional[Dict] = None


class GameRouter:
    """
    Routes game generation between online and local LLMs
    based on shadow-field delta telemetry.
    """
    
    def __init__(
        self,
        online_model: str = "claude",
        local_model: str = "llama3",
        threshold_tension: float = 0.6,
        threshold_curvature: float = 0.5,
        threshold_stability: float = 0.4,
        min_online_tokens: int = 100,
        min_local_tokens: int = 50,
    ):
        # Shadow-field system for telemetry
        self.delta_system = UnifiedRuntimeDeltaSystem(
            harness_id="game-router",
            model_id=ModelID.COPILOT  # will be overridden per call
        )
        
        # Thresholds
        self.threshold_tension = threshold_tension
        self.threshold_curvature = threshold_curvature
        self.threshold_stability = threshold_stability
        
        # Token budgets
        self.min_online_tokens = min_online_tokens
        self.min_local_tokens = min_local_tokens
        
        # State
        self._last_decision: Optional[RoutingDecision] = None
        self._game_state_hash: int = 0
        self._narrative_tension: float = 0.5
        
    def observe_game_turn(
        self,
        game_state: Dict[str, Any],
        player_action: str,
        narrative_context: str,
        world_state: Dict[str, Any],
    ) -> RoutingDecision:
        """
        Observe a game turn and decide routing.
        Motion = combined game state + player action + narrative.
        """
        # Build motion vector from game state
        motion = {
            "game_state": game_state,
            "player_action": player_action,
            "narrative_context": narrative_context,
            "world_state": world_state,
            "state_hash": hash(str(game_state) + str(world_state)),
            "action_complexity": len(player_action.split()),
            "narrative_length": len(narrative_context),
            "timestamp": time.time(),
        }
        
        # Ingest to shadow field
        packet = self.delta_system.ingest_with_features(motion)
        
        if not packet:
            # First turn — default to online for narrative setup
            return RoutingDecision(
                target=RouteTarget.ONLINE,
                confidence=1.0,
                reason="initialization",
                offload_ratio=0.0,
            )
        
        # Extract metrics
        tension = packet.tension_delta
        curvature = packet.curvature_delta
        stability = packet.stability_trend
        
        # Decision logic
        return self._route_from_deltas(tension, curvature, stability, motion)
    
    def _route_from_deltas(
        self,
        tension: float,
        curvature: float,
        stability: float,
        motion: Dict
    ) -> RoutingDecision:
        """Core routing logic based on delta telemetry."""
        
        # CASE 1: High narrative tension + high curvature = ONLINE
        # Story branching, creative writing, character moments
        if tension > self.threshold_tension and curvature > self.threshold_curvature:
            return RoutingDecision(
                target=RouteTarget.ONLINE,
                confidence=min(1.0, (tension + curvature) / 1.5),
                reason="narrative complexity (tension + curvature)",
                offload_ratio=0.1,  # 10% to local (state tracking only)
            )
        
        # CASE 2: Low stability = LOCAL
        # Game mechanics, inventory, combat math, state recalculation
        if stability < self.threshold_stability:
            return RoutingDecision(
                target=RouteTarget.LOCAL,
                confidence=min(1.0, (1.0 - stability) / 0.5),
                reason="state inconsistency (low stability)",
                offload_ratio=0.9,  # 90% to local
            )
        
        # CASE 3: High tension + low curvature = HYBRID
        # Online handles narrative framing, local handles mechanics
        if tension > self.threshold_tension and curvature < self.threshold_curvature * 0.5:
            return RoutingDecision(
                target=RouteTarget.HYBRID,
                confidence=0.8,
                reason="narrative pressure, mechanical stability",
                offload_ratio=0.5,  # 50/50 split
                context_delta={
                    "online": "narrative_flow",
                    "local": "game_mechanics"
                }
            )
        
        # CASE 4: Routine = LOCAL
        # Exploration, movement, simple interactions
        if tension < self.threshold_tension * 0.5:
            return RoutingDecision(
                target=RouteTarget.LOCAL,
                confidence=0.9,
                reason="routine gameplay (low tension)",
                offload_ratio=0.8,
            )
        
        # DEFAULT: HYBRID
        return RoutingDecision(
            target=RouteTarget.HYBRID,
            confidence=0.7,
            reason="balanced state (default)",
            offload_ratio=0.4,
        )
    
    def estimate_token_savings(self, decision: RoutingDecision) -> Dict[str, float]:
        """Estimate token savings from offload decision."""
        # Rough heuristic: online tokens ~3x more expensive than local
        base_tokens = 500  # typical generation
        online_ratio = 1.0 - decision.offload_ratio
        
        online_tokens = base_tokens * online_ratio
        local_tokens = base_tokens * decision.offload_ratio
        
        return {
            "online_tokens": online_tokens,
            "local_tokens": local_tokens,
            "online_cost_savings": online_tokens * 3,  # cost multiplier
            "local_cost": local_tokens * 0.1,  # local is cheap
            "total_estimated_cost": (online_tokens * 3) + (local_tokens * 0.1),
            "savings_percent": (1 - ((online_tokens + local_tokens) / base_tokens)) * 100,
            "decision": decision.reason,
        }
    
    def reset_game_session(self):
        """Reset telemetry for a new game session."""
        self.delta_system.reset()
        self._last_decision = None
        self._game_state_hash = 0