"""Adventure game using shadow-field router."""
from shadow_field.orchestrator.game_router import GameRouter, RouteTarget
from local_llm import LocalModelClient
from online_client import OnlineModelClient
import json


class AdventureGame:
    """
    In-context adventure game that offloads intelligently.
    Runs on ANY model via hybrid routing.
    """
    
    def __init__(self):
        self.router = GameRouter(
            online_model="claude",
            local_model="llama3",
            threshold_tension=0.6,
            threshold_curvature=0.5,
            threshold_stability=0.4,
        )
        self.local = LocalModelClient()  # e.g., llama-cpp-python
        self.online = OnlineModelClient()  # e.g., Anthropic/OpenAI
        
        # Game state
        self.world_state = {"location": "tavern", "inventory": [], "quests": []}
        self.narrative_context = "You are an adventurer in a fantasy world."
        self.turn_history = []
        
    def process_turn(self, player_action: str):
        """Main game loop."""
        # 1. Observe the turn
        decision = self.router.observe_game_turn(
            game_state=self.world_state,
            player_action=player_action,
            narrative_context=self.narrative_context,
            world_state=self.world_state,
        )
        
        # 2. Route based on decision
        if decision.target == RouteTarget.ONLINE:
            response = self._online_generate(player_action)
            self.narrative_context += "\n" + response
            self.world_state = self._extract_state_from_response(response)
            
        elif decision.target == RouteTarget.LOCAL:
            response = self._local_generate(player_action)
            # Local handles mechanics, narrative is minimal
            self.world_state = self._update_mechanics(response)
            
        else:  # HYBRID
            # Split generation
            narrative_part = self._online_generate_narrative(player_action)
            mechanics_part = self._local_generate_mechanics(player_action)
            response = self._merge_responses(narrative_part, mechanics_part)
            self.narrative_context += "\n" + narrative_part
            self.world_state = self._apply_mechanics(mechanics_part)
        
        # 3. Log delta for tuning
        self.turn_history.append({
            "action": player_action,
            "decision": decision.reason,
            "offload_ratio": decision.offload_ratio,
            "response": response[:100] + "...",
        })
        
        # 4. Estimate savings (for monitoring)
        savings = self.router.estimate_token_savings(decision)
        print(f"[ROUTER] {decision.reason} | Offload: {decision.offload_ratio:.0%} | Savings: {savings['savings_percent']:.0f}%")
        
        return response
    
    def _online_generate(self, action: str) -> str:
        """Call online model (Claude/Gemini/Grok)."""
        # Actual implementation uses API
        prompt = f"{self.narrative_context}\n\nPlayer: {action}\n\nNarrator:"
        return self.online.generate(prompt, max_tokens=300)
    
    def _local_generate(self, action: str) -> str:
        """Call local LLM for mechanics."""
        prompt = f"""Game state: {json.dumps(self.world_state)}
        Player action: {action}
        Update game state, inventory, and mechanics."""
        return self.local.generate(prompt, max_tokens=100)
    
    def _online_generate_narrative(self, action: str) -> str:
        """Online handles narrative framing only."""
        prompt = f"{self.narrative_context}\n\nPlayer: {action}\n\nNarrator (story only, no mechanics):"
        return self.online.generate(prompt, max_tokens=150)
    
    def _local_generate_mechanics(self, action: str) -> str:
        """Local handles mechanics only."""
        prompt = f"Game state: {json.dumps(self.world_state)}\nAction: {action}\nUpdate mechanics:"
        return self.local.generate(prompt, max_tokens=50)
    
    def _merge_responses(self, narrative: str, mechanics: str) -> str:
        """Merge hybrid responses."""
        return f"{narrative}\n\n[Mechanics: {mechanics}]"
    
    def _extract_state_from_response(self, response: str) -> dict:
        """Extract world state from narrative response."""
        # In practice: use structured extraction or regex
        # For demo: return existing state
        return self.world_state
    
    def _update_mechanics(self, mechanics_response: str) -> dict:
        """Update world state from mechanics response."""
        # Parse mechanics JSON or structured output
        # For demo: return existing state
        return self.world_state
    
    def _apply_mechanics(self, mechanics_part: str) -> dict:
        """Apply mechanics changes to world state."""
        # Parse and apply
        return self.world_state