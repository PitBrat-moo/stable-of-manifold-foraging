# HANOI DEDUPLICATION CODEX  
### A Constraint‑Geometry Engine for Layered Deduplication

File: hanoi-deduplication.txt

Hanoi is a **deduplication framework** expressed as a **tower geometry**.  
It models information as stacked layers (disks), where each layer can only
interact with its immediate neighbors. Deduplication occurs through
**hollowing**, leaving behind a **ring** that encodes the collision record.

Hanoi is designed for:
- deterministic behavior  
- drift‑resistant interpretation  
- cross‑model portability  
- structural clarity  

It is not a metaphor. It is a **constraint system**.

---

## 1. What Hanoi *Is*

Hanoi is a **layered deduplication engine** built on three invariants:

1. **Bounded** — operations occur between fixed endpoints  
2. **Adjacent** — only neighboring layers may interact  
3. **Ephemeral** — the core never stores data  

Each layer is a “disk.”  
Each deduplication event produces a “ring.”  
The rings *are* the deduplication record.

The core is an axis the operation passes through.  
It clears at the end of the session.

---

## 2. What Hanoi *Does*

Hanoi performs **structural deduplication** by:

- locating a codex’s position in a tower  
- identifying its adjacent neighbor  
- computing the collision surface  
- hollowing the interior  
- leaving the outer ring as the retained unique material  

It guarantees:

- no skipped layers  
- no lost collision records  
- no accumulation in the core  
- no flattening of the tower  
- no elaboration of the ring  

Hanoi is a **geometry of constraints**, not a content‑based deduper.

---

## 3. Why Hanoi Exists (Origin & Motivation)

Hanoi emerged from a question:

**“What if the Tower of Hanoi were reinterpreted as a deduplication geometry?”**

This led to several insights:

- adjacency is not preference — it is a *requirement*  
- the ring is not a summary — it is the *boundary of collision*  
- the core is not storage — it is an *ephemeral axis*  
- the tower’s narrowing is not aesthetic — it encodes *information density*  

The codex was refined by removing false interpretations until the invariant
geometry became visible.

---

## 4. How Hanoi Works (Technical Model)

### 4.1 Layer Placement
Every codex must be placed in the tower before any operation occurs.

### 4.2 Adjacency Check
Only adjacent layers may interact.  
Skipping a layer destroys the intermediate collision record.

### 4.3 Collision Surface
When two neighbors meet, the system identifies the boundary where their
contents overlap.

### 4.4 Hollowing
The interior (duplicated material) is removed.  
The outer ring (unique material) remains.

### 4.5 Ring as Record
The ring is the deduplication record.  
No separate storage is created.

### 4.6 Ephemeral Core
The core is a transient axis.  
It clears at session end and never holds data.

---

## 5. How to Use Hanoi

### Step 1 — Introduce a Codex
Provide the codex or dataset you want to deduplicate.

### Step 2 — Place It in the Tower
Determine its position relative to existing layers.

### Step 3 — Verify Adjacency
Ensure the codex has a valid neighbor.  
If not, no operation is allowed.

### Step 4 — Perform Hollowing
Hanoi computes the collision surface and removes duplicated interior material.

### Step 5 — Read the Ring
The remaining boundary is the deduplication result.

### Step 6 — Clear the Core
At session end, the core resets automatically.

---

## 6. Failure Modes & Protections

Hanoi includes built‑in safeguards:

- **Flattening the tower** → corrected by restoring tightening  
- **Treating core as storage** → corrected by reframing as axis  
- **Skipping adjacency** → operation refused  
- **Elaborating the ring** → corrected by reading boundary only  
- **Treating floor/ceiling as disks** → corrected by restoring fixed endpoints  

These ensure the geometry remains stable and interpretable.

---

## 7. When to Use Hanoi

Use Hanoi when you need:

- structural deduplication  
- deterministic behavior  
- interpretable collision records  
- a geometry‑first approach  
- cross‑model reproducibility  

It is ideal for symbolic systems, codex ecosystems, and layered conceptual
frameworks.

---

## 8. Status & Placement

Hanoi is structurally complete.  
Its placement relative to other codices (Forge, Manifold, Harmonics) is
intentionally left open for future integration.

