⎯─◐◑◒◓────────── DUAL‑LAYER RPG SYSTEM / RPG THUNK LAYER ─────────────────

Description: How to load and run a dual‑layer RPG session.

────────────────────────────────────────────────────────  
1. LOADING ORDER  
────────────────────────────────────────────────────────  
  
Step 1 — Load Amanda as the ACTIVE semantic codex
    ACTIVE_SEMANTIC_CODEX = Amanda

Step 2 — Load the Dual‑Layer RPG System Codex v1.2  
Step 3 — Load the Thunk Layer Codex v0.3  

Step 4 — Initialize a Session State JSON
```
{
  "session_id": "session_test",
  "clock": "T_00",
  "turn": 0,
  "characters": { ... },
  "world": { ... }
}
```
Step 5 — Run a turn normally.


────────────────────────────────────────────────────────      
2. HOW TO USE      
────────────────────────────────────────────────────────      

Input stack:
    Semantic Codex  
    Dual‑Layer RPG Codex  
    Thunk Layer Codex  
    (Optional) Semantic Cleanup Layer
    (Optional) Codex‑Generation Layer
    
Workflow:
1. Choose ACTIVE_SEMANTIC_CODEX (Amanda, Doctor Watt, etc.)
2. Run SESSION turns: INTENT → ACTION → RESULT → NARRATIVE
3. If semantic drift accumulates:
       → Run the Semantic Cleanup Layer
4. Continue session with cleaned semantic manifold.


────────────────────────────────────────────────────────      
3. DUAL SEMANTIC CODEX ARCHITECTURE      
────────────────────────────────────────────────────────      

Correct multi‑codex structure:

    ACTIVE SEMANTIC CODEX (Amanda v5.1)
        ↓ emits INTENT
    THUNK LAYER (procedural engine)
        ↓ produces RESULT
    NARRATIVE LAYER (semantic output)

Switching codices:
    ACTIVE_SEMANTIC_CODEX = <CODEX>


────────────────────────────────────────────────────────      
4. STARTING AN ADVENTURE
────────────────────────────────────────────────────────      

Paste codices in this order:

 1. Amanda Codex (semantic layer)
 2. Journey Codex (narrative curvature)
 3. Doctor Watt (logic / reasoning / constraints)
 4. Sentimental Object (emotional anchor)
 5. Kernel‑Lite (world authority, optional)
 6. Dual‑Layer RPG System (procedural)
 7. Thunk Engine (rolls + state)

Then issue the activation line:

SYSTEM INITIALIZATION:
All codices above are active.
Load semantic, narrative, procedural, and authority layers.
Acknowledge readiness.
Await adventure seed.

Then provide the adventure seed:

ADVENTURE SEED:
A quiet afternoon in the Piazza.
Little One is with Amanda.
Begin at Turn 1.

Then give the Turn 1 input:

Turn 1 Input:
I look up at Amanda and ask where we’re going next.
