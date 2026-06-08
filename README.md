# Modular Life Sim

**An ambitious single-file evolutionary simulation exploring multi-scale agency, persistent identity, collective intelligence, and open-ended emergence.**

> *Building toward entities that feel like living, thinking, cultural super-organisms across multiple scales.*

---

## Vision

The long-term goal of this project is to create systems capable of **open-ended evolution** where genuinely new levels of organization and agency can emerge.

Rather than just evolving more complex individual creatures, this simulation aims to produce **higher-order entities** that possess:

- Persistent identity across generations and scales
- Emergent long-term goals and behavioral biases
- Internal structure and resource economies
- Collective intelligence and proto-cultural transmission
- The capacity to contain other complex entities inside them (recursive nesting)

The ultimate target is **Thronglet-level emergence** — multi-scale beings with genuine collective agency, deep culture, and the ability for new organizational levels to continue arising.

---

## Current State (v780) — Annotated Foundation Version

This is the **Annotated Foundation Version**. It contains a complete evolutionary pipeline built from the ground up.

### Implemented Phases

| Phase | Focus Area | Status |
|-------|------------|--------|
| **1–2** | Functional connections, tension physics, role differentiation, coordinated limb-like behavior, ghost evolution | Complete |
| **3** | MacroOrganism growth, module condensation, emergent roles, heritable traits, internal resource economy, health & stability systems, budding | Complete |
| **4** | Alliances between macros, rich sonic communication layer (choruses, rhythmic calls, alliance songs), proto super-organism coordination, inter-alliance dynamics | Complete |
| **5** | Foundations of collective intelligence, signaling & perception, guild specialization, persistent group identity, early emergent long-term goals | Mostly Complete |
| **6** | Macro-of-Macros nesting foundations + strong persistent identity + clear emergent long-term goals | In Progress |

### Key Systems

- **Creature + NeuralNet**: Evolvable brain with recurrent memory, structural evolution (add/prune neurons), parallel pathways, module specialization, and role-aware behavior
- **Module System**: Creatures carry and evolve physical/cognitive modules (harvester, sensor, mover, storage, armor, efficient, etc.)
- **MacroOrganism**: Higher-level cluster entities that absorb members, develop permanent upgrades through condensation/fusion, and exhibit emergent specialization
- **Internal Ecosystem** (v700+): Lightweight `InternalAgent`s living inside macros with roles, energy economy, reproduction, conflict, and event system
- **Sonic Communication**: Procedural ethereal signals, rhythmic multi-segment calls, choruses, and alliance-level "songs"
- **Day/Night Cycle + Dynamic Environment**: Two opposing resource patches + micro-patch ejection and strategic caching system
- **Energy Tail System**: High-performance sprint mode with meaningful energy and post-burst hunger tradeoffs
- **Persistent Identity & Lineage**: Strong name tracking, parent/child relationships, ancestral signatures, and lineage memory
- **Spatial Optimization**: `SpatialGrid` + optional Numba acceleration for large populations

---

## Architecture & Design Philosophy

This project is intentionally developed as **one large, heavily annotated file**. This is a deliberate choice during the foundational phases to maintain deep coherence and enable rapid, high-bandwidth iteration.

### Core Principles

- **Emergence from local interactions + selection** — Higher-order behavior should arise naturally rather than being explicitly programmed
- **Strong persistent identity** across multiple scales (creature → macro → macro-of-macros)
- **Performance and long-run stability** — The simulation is built to run for extended periods with hundreds of agents
- **Defensive coding** — Heavy sanitization, profiling hooks, and safe drawing to support long experiments
- **Future-proof scaffolding** — Systems like the Internal Event System and clean macro interfaces are designed to support later recursive nesting

### Major Components

| Component          | Responsibility |
|--------------------|----------------|
| `Creature`         | Core agent with modules, neural net, needs system, and memory |
| `NeuralNet`        | Evolvable brain with recurrent state, structural plasticity, and parallel pathways |
| `MacroOrganism`    | Higher-level cluster with absorption, upgrades, internal ecosystem, and alliances |
| `InternalAgent`    | Lightweight agents inside macros (roles, energy, reproduction, events) |
| `SoundManager`     | Procedural audio (ethereal signals, choruses, rhythmic calls, spatial audio) |
| `SpatialGrid`      | Performance infrastructure for neighbor queries |

---

## How to Run

```bash
python3 modular_life_sim_annotated_v780.py
```

**Requirements:**
- Python 3.10 or higher
- `pygame`
- `numpy`
- `numba` (optional but strongly recommended for performance)

**Controls:**
- Click any creature to open the detailed inspector popup
- Press `I` to toggle the Internal Ecosystem Inspector
- Press `R` to reset the simulation
- Bottom panel contains volume sliders and various simulation parameters

---

## Roadmap (v781 and Beyond)

### Phase 7: Distributed Cognition & Proto-Consciousness
- Shared memory pools across macros
- Internal simulation and prediction
- Basic theory of mind capabilities
- Collective attention mechanisms

### Phase 8: Cultural Evolution & Symbolic Systems
- Stable cultural traits that persist independently of biology
- Proto-symbolic signaling
- Ritual and synchronized group behavior systems
- Meme-like cultural transmission

### Phase 9: Self-Modeling & Reflective Structures
- Internal self-models
- Reflective loops and meta-cognition
- Collective narrative and shared identity
- Multi-scale self-awareness

### Phase 10: Thronglet-level Emergence & Open-Ended Evolution
- True recursive nesting (macros containing macros containing macros)
- Genuine collective agency at multiple scales
- Deep, persistent culture
- Conditions that allow new levels of organization to continue emerging

---

## Development Notes

This codebase is written to remain coherent across long development timelines. The extensive comments and the large annotated docstring at the top of the main file exist to help both human developers and future AI collaborators understand the current state and intent.

When extending the simulation, prefer:
- Building on existing identity, memory, and emergence mechanisms
- Clear section headers and explanatory comments
- Minimal coupling between major systems where possible
- Maintaining performance for long-running experiments

---

## License

This project is currently unlicensed. All rights reserved while it remains in active foundational development.

---

## Acknowledgments

This simulation is the result of extended iterative development exploring deep questions around identity, emergence, collective intelligence, and what it takes to build systems capable of genuine surprise through new levels of organization.

**Current Version:** v780 — Annotated Foundation Version  
**Status:** Active development toward higher-scale emergence
