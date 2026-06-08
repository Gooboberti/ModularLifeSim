#!/usr/bin/env python3
"""
=============================================================================
          MODULAR LIFE SIM v780 - ANNOTATED FOUNDATION VERSION
                    Very Robust Persistent Identity & Clear Long-Term Emergent Goals
=============================================================================

This is the annotated foundation version of the Modular Life Simulation.
It contains detailed explanations of the architecture, systems, and the
long-term vision so that future versions of Grok (or other developers)
can quickly understand the current state and continue development coherently.

=============================================================================
                           CURRENT STATE (v780)
=============================================================================

We have built a complete evolutionary pipeline from the bottom up:

PHASE 1-2 (v739–v745): Functional Connections
- Tension, pulling, role differentiation, bonus transfer through connections
- Coordinated limb-like behavior, ghost evolution, group identity

PHASE 3 (v746–v752): Macro Growth & Evolution
- Module condensation (mechanically powerful)
- Emergent roles, heritable traits on split, memory & migration
- Internal resource economy, health tied to stability + connections, budding

PHASE 4 (v753–v772): Groups & Meta-Structures
- Alliances with mutual benefits
- Rich sonic communication layer (choruses, call-and-response, ghost echoes, alliance songs, rituals)
- Proto super-organism coordination
- Inter-alliance dynamics + early nesting
- Ecosystem guilds + distributed memory
- Ritual & synchronized group behavior

PHASE 5 (v763–v780+): Collective Intelligence & Culture (in progress)
- Proto-signaling & cultural transmission via imitation
- Stronger guild specialization
- Persistent group identity + emergent long-term goals

PHASE 6 (v773+): Toward Thronglet Emergence (just started)
- Recursive macro-of-macros nesting
- Persistent identity and emergent goals (current focus)

=============================================================================
                        ARCHITECTURE OVERVIEW
=============================================================================

The simulation is deliberately kept in **one file** for simplicity of
workflow, while maintaining strong internal organization through clear
section headers and comments.

Main Sections:
1. Configuration & Constants          (lines ~50-200)
2. Helper Functions                   (spatial, time, food, etc.)
3. Core Data Classes                  (Module, MicroPatch, etc.)
4. Creature Class + NeuralNet         (core agent + brain)
5. SoundManager                       (ethereal signals, choruses, spatial audio)
6. MacroOrganism Class                (the key higher-level entity)
7. Global State & Initialization
8. Update Logic (physics, AI, economy, alliances, nesting, signaling)
9. Drawing / Rendering
10. Main Game Loop + Event Handling

Key Design Principles:
- Everything emerges from local interactions + selection.
- Single-file for easy iteration and sharing.
- Strong comments and section headers for maintainability.
- Performance considerations (SpatialGrid, pre-rendered surfaces, Numba where used).
- Defensive coding (safe drawing, position sanitization) to support long runs.

=============================================================================
                        FUTURE ROADMAP (v781+)
=============================================================================

A detailed future roadmap has been created in:
`future_roadmap_v781_plus.md`

High-level future phases:

Phase 7 (v791–v820): Distributed Cognition & Proto-Consciousness
- Shared memory pools, internal simulation/prediction, basic theory of mind
- Collective attention and primitive awareness

Phase 8 (v821–v860): Cultural Evolution & Symbolic Systems
- Stable cultural traits, proto-symbolic signaling, ritual systems
- Meme-like cultural evolution independent of biology

Phase 9 (v861–v900): Self-Modeling & Reflective Structures
- Internal self-models, reflective loops, collective narrative/identity
- Multi-scale self-awareness

Phase 10 (v901+): Thronglet-level Emergence & Open-Ended Evolution
- True multi-scale persistent entities with rich internal structure
- Genuine collective agency, deep culture, recursive depth
- Open-ended evolution where new levels of organization can continue emerging

The long-term vision is entities that feel like living, thinking, cultural
super-organisms with genuine collective agency across multiple scales.

=============================================================================
"""

import pygame
import random
import math
from collections import defaultdict
import numpy as np
import time
import os

# =============================================================================
# SECTION 1: CONFIGURATION & CONSTANTS
# =============================================================================

# === DEBUG FLAG ===
# Set to True to temporarily disable chorus so you can clearly hear ethereal tones
DISABLE_CHORUS = False

try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    print("Numba not available. Running without JIT acceleration.")

# =============================================================================
# SECTION 2: HELPER FUNCTIONS
# =============================================================================

# ============================================================
# CONFIG
# ============================================================
WIDTH, HEIGHT = 1320, 920
FPS = 60
CELL_SIZE = 90

# ============================================================
# HARD INTERNAL SIMULATION BOX (v653)
# ============================================================
MARGIN = 40
SIM_LEFT = MARGIN
SIM_RIGHT = WIDTH - MARGIN
SIM_TOP = MARGIN
SIM_BOTTOM = HEIGHT - 200   # Leave room for UI panel
SIM_WIDTH = SIM_RIGHT - SIM_LEFT
SIM_HEIGHT = SIM_BOTTOM - SIM_TOP
PREDATOR_VISION_RADIUS = 320
REPRODUCTION_COOLDOWN = 420
ATTACK_RANGE = 32

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Modular Life Sim v780 - Very Robust Persistent Identity & Clear Long-Term Emergent Goals")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 17)
small_font = pygame.font.SysFont("arial", 13)
tiny_font = pygame.font.SysFont("arial", 12)
title_font = pygame.font.SysFont("arial", 20)

BLACK = (18, 18, 22)
WHITE = (245, 245, 250)
LEGEND_BG = (26, 26, 30)
WASTE_COLOR = (180, 160, 100)
CARRY_COLOR = (255, 215, 60)
CARRY_GLOW_COLOR = (255, 245, 170)
SELECT_HIGHLIGHT = (255, 255, 100)
ATTACK_GLOW = (255, 80, 80)
REGEN_COLOR = (100, 255, 180)
PREPARE_COLOR = (255, 200, 80)
REPRO_MARKER_COLOR = (80, 220, 255)

FORAGER_COLOR = (110, 255, 140)
SCOUT_COLOR = (110, 175, 255)
COURIER_COLOR = (255, 195, 110)
SENSOR_COLOR = (195, 155, 255)
DESPERATE_COLOR = (255, 80, 80)
GENERALIST_COLOR = (255, 235, 180)

# Pre-rendered creature surfaces (big performance win)
CREATURE_SURFACES = {}
def get_creature_surface(role, is_desperate=False, core_size=7.0):
    key = (role, is_desperate, round(core_size, 1))
    if key in CREATURE_SURFACES:
        return CREATURE_SURFACES[key]

    size = int(core_size * 3.8)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    color = DESPERATE_COLOR if is_desperate else {
        "forager": FORAGER_COLOR, "scout": SCOUT_COLOR,
        "courier": COURIER_COLOR, "sensor": SENSOR_COLOR
    }.get(role, GENERALIST_COLOR)

    cx = cy = size // 2
    pygame.draw.circle(surf, color, (cx, cy), core_size)
    # Clean look, no outer ring

    CREATURE_SURFACES[key] = surf.convert_alpha()
    return surf

MIN_RADIUS = 48
GREEN_GLOW = 0
BLUE_GLOW = 0
generation = 0
BOTTOM_PANEL_HEIGHT = 195

selected_creature = None
start_time = time.time()
prev_time_of_day = 0.0  # kept for now in case other systems use it later

# v705: Internal ecosystem inspector toggle (press I)
show_internal_inspector = False

# v718: Basic Profiling
profiling_enabled = False
internal_update_time = 0.0
internal_draw_time = 0.0
profile_frame_count = 0
last_profile_print = 0.0

# For staggered dawn/dusk micro-patch bursts
dawn_burst_remaining = 0
dusk_burst_remaining = 0
burst_cooldown = 0

# ====================== DAY/NIGHT CYCLE ======================
DAY_NIGHT_CYCLE = 1750  # Faster cycle (~30 seconds per full day/night)
def get_time_of_day():
    return (pygame.time.get_ticks() // 16) % DAY_NIGHT_CYCLE / DAY_NIGHT_CYCLE  # 0.0 to 1.0

def is_day(t):
    """Right half of clock = Day, Left half = Night"""
    return t < 0.5

def get_day_night_tint(t):
    """Returns a subtle color shift for atmospheric day/night feel."""
    if is_day(t):
        return (255, 245, 235)  # Warm/amber during day
    else:
        return (195, 205, 255)  # Cooler during night

# ====================== NAME GENERATOR ======================
FIRST_SYLLABLES = ["Zor", "Kael", "Vex", "Nyx", "Ryn", "Syl", "Thal", "Quor", "Myr", "Lir", "Xan", "Vel", "Drak", "Sov", "Kry"]
SECOND_SYLLABLES = ["ion", "ar", "eth", "ix", "on", "us", "an", "or", "ex", "yl", "ith", "ax", "en", "os", "um"]

def generate_name():
    return random.choice(FIRST_SYLLABLES) + random.choice(SECOND_SYLLABLES)

# ====================== SPATIAL GRID ======================
class SpatialGrid:
    def __init__(self, cell_size=CELL_SIZE):
        self.cell_size = cell_size
        self.grid = defaultdict(list)

    def clear(self):
        self.grid.clear()

    def _key(self, x, y):
        return (int(x // self.cell_size), int(y // self.cell_size))

    def insert(self, obj, x, y):
        key = self._key(x, y)
        self.grid[key].append(obj)

    def query(self, x, y, radius):
        results = []
        cell_radius = int(radius // self.cell_size) + 1
        cx, cy = self._key(x, y)
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                key = (cx + dx, cy + dy)
                if key in self.grid:
                    results.extend(self.grid[key])
        return results

    def count_nearby(self, x, y, radius):
        """Faster count without building full list"""
        count = 0
        cell_radius = int(radius // self.cell_size) + 1
        cx, cy = self._key(x, y)
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                key = (cx + dx, cy + dy)
                if key in self.grid:
                    for obj in self.grid[key]:
                        if (obj.pos.x - x)**2 + (obj.pos.y - y)**2 < radius*radius:
                            count += 1
        return count

# Numba-accelerated neighbor counting (much faster for large populations)
if NUMBA_AVAILABLE:
    @njit(fastmath=True, cache=True)
    def fast_count_nearby(positions_x, positions_y, target_x, target_y, radius):
        count = 0
        r2 = radius * radius
        for i in range(len(positions_x)):
            dx = positions_x[i] - target_x
            dy = positions_y[i] - target_y
            if dx*dx + dy*dy < r2:
                count += 1
        return count
else:
    def fast_count_nearby(positions_x, positions_y, target_x, target_y, radius):
        # Fallback pure Python version
        count = 0
        r2 = radius * radius
        for i in range(len(positions_x)):
            dx = positions_x[i] - target_x
            dy = positions_y[i] - target_y
            if dx*dx + dy*dy < r2:
                count += 1
        return count

creature_grid = SpatialGrid()
patch_grid = SpatialGrid()

# Global position arrays for Numba JIT acceleration
positions_x = np.array([], dtype=np.float32)
positions_y = np.array([], dtype=np.float32)

# ====================== NEURAL NETWORK ======================
# Supports Phase 1-5 features + extensions:
# - 29 inputs (including predator density and ally density)
# - 6 outputs (including hunting_persistence for focus)
# - Weight + structural (topology) evolution
# - Reward-modulated lifetime learning
class NeuralNet:
    def __init__(self, input_size=29, h1=18, h2=16, h3=11, output_size=6):
        self.input_size = input_size
        self.h1, self.h2, self.h3 = h1, h2, h3
        self.output_size = output_size
        self.w1 = np.random.randn(input_size, h1) * 0.42
        self.b1 = np.zeros(h1)
        self.w2 = np.random.randn(h1, h2) * 0.42
        self.b2 = np.zeros(h2)
        self.w3 = np.random.randn(h2, h3) * 0.42
        self.b3 = np.zeros(h3)
        self.w4 = np.random.randn(h3, output_size) * 0.42
        self.b4 = np.zeros(output_size)

        # === Phase 1: Recurrent Core + Internal State ===
        self.recurrent_size = 10
        self.internal_state_size = 6
        self.full_input_size = input_size + self.recurrent_size + self.internal_state_size

        # === Phase 2: Structural Evolution ===
        # Importance tracking for weights (magnitude * activation impact)
        self.importance_w1 = np.zeros((input_size, h1))
        self.importance_w2 = np.zeros((h1, h2))
        self.importance_w3 = np.zeros((h2, h3))

        # Evolvable structural rates (Phase 2 Stage 2 - Option B)
        self.struct_add_chance = 0.12      # Base chance to attempt adding a new neuron
        self.struct_prune_chance = 0.12    # Base chance to attempt pruning weak connections

        # Evolvable Developmental Bias Strength (v48)
        self.developmental_bias_strength = 0.35   # How strongly new neurons are biased toward important inputs

        # Activity-Based Modulation (v52)
        self.recent_success_boost = 0.0    # Temporary boost to add_chance after recent success
        self.lineage_memory_strength = 0.0      # Accumulates across successful generations (Option A)
        self.ancestral_timbre = 0.5             # Fading ancestral signature (v135)

        # Evolvable Protection Window (v53)
        self.protection_strength = 0.65    # How strongly new neurons are protected after creation

        # === Phase 5 Summary (v73–v80) ===
        # - Proximity awareness and richer spatial perception (v73–v74)
        # - Proximity modulation + signaling foundation (v75–v76)
        # - Signal perception + interaction selection pressure (v77–v78)
        # - Local group effects + final stability (v79–v80)
        # Phase 5 lays the groundwork for collective behavior and proto-communication.

        # === Phase 5: Simple Signaling Foundation (v76) ===
        self.signal_value = 0.0

        # === Stage A: Stronger Module + Role Voice Coupling (v86) ===
        self.voice_base_freq = 880.0
        self.voice_timbre = 0.5
        self.voice_mod_depth = 0.15

        # === Heritable Emotional Sensitivities (v403) ===
        self.fear_sensitivity = 0.65
        self.loneliness_sensitivity = 0.55
        self.contentment_sensitivity = 0.60
        self.curiosity_sensitivity = 0.50
        self.aggression_sensitivity = 0.45

        # Stronger coupling with Module_B
        if hasattr(self, 'module_preference_B'):
            self.voice_timbre = np.clip(0.42 + (self.module_preference_B * 0.38), 0.12, 0.88)
            self.voice_mod_depth = np.clip(0.10 + (self.module_preference_B * 0.18), 0.05, 0.35)

        # Role-based voice bias
        if hasattr(self, 'owner') and self.owner:
            role = self.owner.get_role()
            if role == "scout":
                self.voice_base_freq = np.clip(self.voice_base_freq + 45, 700, 1100)
            elif role == "forager":
                self.voice_timbre = np.clip(self.voice_timbre - 0.08, 0.1, 0.85)

        # === Phase 4: Explicit Module Representation (v66) + Inheritance (v67) ===
        # We now treat the two parallel pathways as explicit modules
        self.module_names = ["Module_A", "Module_B"]
        self.module_usage = {"Module_A": 0.0, "Module_B": 0.0}   # Track relative usage

        # Evolvable module preference (how much this creature favors each module)
        self.module_preference_A = 0.55
        self.module_preference_B = 0.45

        # === Phase 3 Summary (v57–v65) ===
        # - Soft role modulation on hidden layers (v57)
        # - Parallel pathways with role/context routing (v58–v59)
        # - Context gating + hierarchical controller (v60–v61)
        # - Module specialization pressure (v62)
        # - Memory-module differentiated interaction (v63)
        # - Stability & final balancing (v64)
        # Phase 3 establishes the foundation for modular and hierarchical cognition.

        # === Phase 2 Stage 2 Summary (v44–v56) ===
        # - Evolvable structural rates (add/prune)
        # - Success modulation + activity-based short-term boosts
        # - Context-aware (desperate vs safe)
        # - Lineage memory + homeostatic regulation
        # - Role-aware specialization
        # - Evolvable bias strength + protection window
        # This completes the core structural evolution systems before Phase 3.

        # Lightweight GRU-style recurrent cell (slightly more conservative init for stability)
        self.w_rec = np.random.randn(input_size + self.recurrent_size, self.recurrent_size) * 0.25
        self.b_rec = np.zeros(self.recurrent_size)
        self.w_update = np.random.randn(input_size + self.recurrent_size, self.recurrent_size) * 0.25
        self.b_update = np.zeros(self.recurrent_size)
        self.w_reset = np.random.randn(input_size + self.recurrent_size, self.recurrent_size) * 0.25
        self.b_reset = np.zeros(self.recurrent_size)

        # Expanded first layer for memory-augmented forward pass
        self.w1_memory = np.random.randn(self.full_input_size, h1) * 0.42
        self.b1_memory = np.zeros(h1)

    def forward(self, inputs):
        x = np.array(inputs)
        h1 = np.tanh(np.dot(x, self.w1) + self.b1)
        h2 = np.tanh(np.dot(h1, self.w2) + self.b2)
        h3 = np.tanh(np.dot(h2, self.w3) + self.b3)
        out = np.tanh(np.dot(h3, self.w4) + self.b4)
        return out

    def mutate(self, mutation_rate=0.095, mutation_strength=0.39):
        for arr in [self.w1, self.b1, self.w2, self.b2, self.w3, self.b3, self.w4, self.b4,
                    self.w_rec, self.b_rec, self.w_update, self.b_update, self.w_reset, self.b_reset,
                    self.w1_memory, self.b1_memory,
                    self.importance_w1, self.importance_w2, self.importance_w3]:
            mask = np.random.rand(*arr.shape) < mutation_rate
            arr[mask] += np.random.randn(*arr.shape)[mask] * mutation_strength

        # === Phase 2.2: Usage-Aware Structural Evolution ===
        # Much smarter pruning: low magnitude + low lifetime importance
        if random.random() < 0.18:
            for importance, weight in [(self.importance_w1, self.w1),
                                       (self.importance_w2, self.w2),
                                       (self.importance_w3, self.w3)]:
                # Prune only if both weak and unimportant over lifetime
                prune_mask = (np.abs(weight) < 0.045) & (importance < 0.035)
                weight[prune_mask] = 0.0

        # Stronger pathway protection for high-importance connections
        # Phase 2.3: Stronger & Smarter Pathway Protection
        # Phase 2 — Final Polish (v40)
        protection_mask_w1 = self.importance_w1 > 0.38
        protection_mask_w2 = self.importance_w2 > 0.35
        protection_mask_w3 = self.importance_w3 > 0.31

        if random.random() < 0.10:
            self.w1[~protection_mask_w1] += np.random.randn(*self.w1.shape)[~protection_mask_w1] * 0.02
            self.w2[~protection_mask_w2] += np.random.randn(*self.w2.shape)[~protection_mask_w2] * 0.02
            self.w3[~protection_mask_w3] += np.random.randn(*self.w3.shape)[~protection_mask_w3] * 0.02

        # Role-Aware + Context-Aware Plasticity (v49)
        effective_prune = self.struct_prune_chance
        effective_add = self.struct_add_chance + getattr(self, 'recent_success_boost', 0.0)

        if hasattr(self, 'owner') and self.owner:
            role = self.owner.get_role()

            # Role-based modifiers (Balanced Specialization - v55/v56)
            if role == "scout":
                effective_prune = min(0.30, self.struct_prune_chance * 1.20)
                effective_add = max(0.07, self.struct_add_chance * 0.93)
            elif role == "forager":
                effective_add = min(0.34, self.struct_add_chance * 1.14)
            elif role == "generalist":
                effective_add = min(0.33, self.struct_add_chance * 1.08)
                effective_prune = min(0.27, self.struct_prune_chance * 1.08)
            elif role == "sensor":
                effective_add = min(0.30, self.struct_add_chance * 0.96)

            # Desperate creatures prune more aggressively
            if self.owner.is_desperate():
                effective_prune = min(0.30, effective_prune * 1.20)

        # Final cleanup of very low-importance connections
        if random.random() < effective_prune:
            low_imp_w1 = self.importance_w1 < 0.022
            low_imp_w2 = self.importance_w2 < 0.022
            low_imp_w3 = self.importance_w3 < 0.022
            self.w1[low_imp_w1] *= 0.88
            self.w2[low_imp_w2] *= 0.88
            self.w3[low_imp_w3] *= 0.88

        # Add new neurons
        if random.random() < effective_add:
            new_neuron_idx = random.randint(0, self.h2 - 1)

            # Base initialization
            self.w2[:, new_neuron_idx] += np.random.randn(self.h1) * 0.50
            self.w3[new_neuron_idx, :] += np.random.randn(self.h3) * 0.45

            # Developmental Bias toward currently important inputs (scaled by evolvable strength)
            if np.max(self.importance_w1) > 0.05:
                bias_strength = 0.25 + (self.developmental_bias_strength * 0.8)
                top_inputs = np.argsort(self.importance_w1.sum(axis=1))[-8:]
                for i in top_inputs:
                    if i < self.w2.shape[0]:
                        self.w2[i, new_neuron_idx] += np.random.randn() * bias_strength

            # === Developmental Protection Window (Evolvable) ===
            prot = self.protection_strength
            self.importance_w2[:, new_neuron_idx] += 0.5 * prot
            self.importance_w3[new_neuron_idx, :] += 0.5 * prot
            self.importance_w2[:, new_neuron_idx] *= (1.4 + prot * 0.6)
            self.importance_w3[new_neuron_idx, :] *= (1.4 + prot * 0.6)

    def copy(self):
        new_net = NeuralNet(self.input_size, self.h1, self.h2, self.h3, self.output_size)
        new_net.w1 = self.w1.copy()
        new_net.b1 = self.b1.copy()
        new_net.w2 = self.w2.copy()
        new_net.b2 = self.b2.copy()
        new_net.w3 = self.w3.copy()
        new_net.b3 = self.b3.copy()
        new_net.w4 = self.w4.copy()
        new_net.b4 = self.b4.copy()

        # Phase 1: Copy recurrent weights
        new_net.w_rec = self.w_rec.copy()
        new_net.b_rec = self.b_rec.copy()
        new_net.w_update = self.w_update.copy()
        new_net.b_update = self.b_update.copy()
        new_net.w_reset = self.w_reset.copy()
        new_net.b_reset = self.b_reset.copy()

        # Phase 1: Copy memory-augmented first layer
        new_net.w1_memory = self.w1_memory.copy()
        new_net.b1_memory = self.b1_memory.copy()

        # Phase 2: Copy importance tracking
        new_net.importance_w1 = self.importance_w1.copy()
        new_net.importance_w2 = self.importance_w2.copy()
        new_net.importance_w3 = self.importance_w3.copy()

        # Lineage Memory + Homeostatic Regulation (v50–v51)
        lineage_success = min(1.0, getattr(self, 'owner', None).offspring_count / 8.0) if hasattr(self, 'owner') and self.owner else 0.0
        mutation_scale = 1.0 - (lineage_success * 0.6)

        new_net.struct_add_chance = np.clip(
            self.struct_add_chance + np.random.normal(0, 0.015 * mutation_scale), 0.03, 0.35
        )
        new_net.struct_prune_chance = np.clip(
            self.struct_prune_chance + np.random.normal(0, 0.015 * mutation_scale), 0.03, 0.35
        )

        # Homeostatic pull toward moderate values (prevents runaway plasticity)
        new_net.struct_add_chance = np.clip(new_net.struct_add_chance * 0.97 + 0.12 * 0.03, 0.03, 0.35)
        new_net.struct_prune_chance = np.clip(new_net.struct_prune_chance * 0.97 + 0.12 * 0.03, 0.03, 0.35)

        # Evolvable Developmental Bias Strength
        new_net.developmental_bias_strength = np.clip(
            self.developmental_bias_strength + np.random.normal(0, 0.04), 0.1, 0.7
        )

        # Evolvable Protection Window
        new_net.protection_strength = np.clip(
            self.protection_strength + np.random.normal(0, 0.05), 0.3, 1.0
        )

        # Carry over recent success boost with slower decay (Success History)
        new_net.recent_success_boost = max(0.0, self.recent_success_boost * 0.75)

        # === Phase 4: Module Inheritance & Variation (v67) ===
        # Inherit module preferences with mutation
        new_net.module_preference_A = np.clip(
            self.module_preference_A + np.random.normal(0, 0.06), 0.15, 0.85
        )
        new_net.module_preference_B = 1.0 - new_net.module_preference_A

        # === Stage A: Inherit Evolvable Voice Traits + Early Lineage Memory ===
        new_net.voice_base_freq = np.clip(
            self.voice_base_freq + np.random.normal(0, 26), 700, 1080
        )
        new_net.voice_timbre = np.clip(
            self.voice_timbre + np.random.normal(0, 0.085), 0.1, 0.9
        )
        new_net.voice_mod_depth = np.clip(
            self.voice_mod_depth + np.random.normal(0, 0.035), 0.05, 0.38
        )

        # Inherit emotional sensitivities with mutation
        new_net.fear_sensitivity = np.clip(
            self.fear_sensitivity + np.random.normal(0, 0.06), 0.2, 1.0
        )
        new_net.loneliness_sensitivity = np.clip(
            self.loneliness_sensitivity + np.random.normal(0, 0.06), 0.2, 1.0
        )
        new_net.contentment_sensitivity = np.clip(
            self.contentment_sensitivity + np.random.normal(0, 0.06), 0.2, 1.0
        )
        new_net.curiosity_sensitivity = np.clip(
            self.curiosity_sensitivity + np.random.normal(0, 0.06), 0.2, 1.0
        )
        new_net.aggression_sensitivity = np.clip(
            self.aggression_sensitivity + np.random.normal(0, 0.06), 0.2, 1.0
        )

        return new_net

    # === Phase 1: Recurrent Core Methods ===
    def init_recurrent_state(self):
        return np.zeros(self.recurrent_size)

    def init_internal_state(self):
        return np.random.uniform(-0.25, 0.25, self.internal_state_size)

    def update_recurrent_state(self, external_inputs, prev_hidden):
        """Lightweight GRU-style recurrent update with stability guards"""
        combined = np.concatenate([external_inputs, prev_hidden])

        reset_gate = np.tanh(np.dot(combined, self.w_reset) + self.b_reset)
        update_gate = np.tanh(np.dot(combined, self.w_update) + self.b_update)

        candidate_input = np.concatenate([external_inputs, reset_gate * prev_hidden])
        candidate = np.tanh(np.dot(candidate_input, self.w_rec) + self.b_rec)

        new_hidden = (1 - update_gate) * prev_hidden + update_gate * candidate

        # Phase 1 stability: Clip and sanitize recurrent state
        new_hidden = np.clip(new_hidden, -6.0, 6.0)
        if np.any(np.isnan(new_hidden)) or np.any(np.isinf(new_hidden)):
            new_hidden = np.zeros_like(new_hidden)

        return new_hidden

    def update_importance(self, activation_h1=None, activation_h2=None, activation_h3=None):
        """
        Phase 2.1: Improved lifetime importance tracking.
        Combines weight magnitude with activation impact when available.
        """
        decay = 0.985

        # Base importance from weight magnitude
        base_w1 = np.abs(self.w1) * 0.015
        base_w2 = np.abs(self.w2) * 0.015
        base_w3 = np.abs(self.w3) * 0.015

        # If activation data is provided, boost importance for active connections
        if activation_h1 is not None:
            # Simple outer-product style contribution (lightweight)
            contrib_w1 = np.abs(np.outer(activation_h1[:self.w1.shape[0]] if len(activation_h1) >= self.w1.shape[0] else np.ones(self.w1.shape[0]), 
                                        np.ones(self.w1.shape[1]))) * 0.01
            base_w1 += contrib_w1[:self.w1.shape[0], :self.w1.shape[1]]

        self.importance_w1 = self.importance_w1 * decay + base_w1
        self.importance_w2 = self.importance_w2 * decay + base_w2
        self.importance_w3 = self.importance_w3 * decay + base_w3

    def forward_with_memory(self, external_inputs, recurrent_state, internal_state, role=None):
        """Forward pass with Parallel Pathways (Phase 3 v58).
        Introduces two parallel computation paths for h2 that can be biased by role.
        """
        full_input = np.concatenate([
            external_inputs,
            recurrent_state,
            internal_state
        ])

        h1 = np.tanh(np.dot(full_input, self.w1_memory) + self.b1_memory)

        # === Phase 3: Explicit Routing (v59) ===
        # Pathway A (standard / conservative)
        h2a = np.tanh(np.dot(h1, self.w2) + self.b2)

        # Pathway B (alternative / more expressive module)
        h2b = np.tanh(np.dot(h1, self.w2 * 0.92) + self.b2 * 1.08)

        # === Phase 4: Dynamic Module Activation (v69) ===
        # Start with inherited module preference
        dyn_weight_a = self.module_preference_A
        dyn_weight_b = self.module_preference_B

        # Role-based specialization pressure
        if role == "forager":
            dyn_weight_a = max(0.18, self.module_preference_A * 0.55)
            dyn_weight_b = 1.0 - dyn_weight_a
        elif role == "scout":
            dyn_weight_a = min(0.88, self.module_preference_A * 1.35)
            dyn_weight_b = 1.0 - dyn_weight_a
        elif role == "sensor":
            dyn_weight_a = max(0.62, self.module_preference_A * 1.1)
            dyn_weight_b = 1.0 - dyn_weight_a

        # Context-sensitive dynamic shift (desperation vs recent success)
        if hasattr(self, 'owner') and self.owner:
            if self.owner.is_desperate():
                dyn_weight_a = min(0.92, dyn_weight_a + 0.10)
                dyn_weight_b = 1.0 - dyn_weight_a
            else:
                success_boost = getattr(self, 'recent_success_boost', 0.0)
                if success_boost > 0.02:
                    dyn_weight_b = min(0.82, dyn_weight_b + success_boost * 0.55)
                    dyn_weight_a = 1.0 - dyn_weight_b

        # === Phase 5: Proximity + Signaling + Perception (v75–v77) ===
        if hasattr(self, 'owner') and self.owner:
            nearby = [c for c in creatures if c is not self and (c.pos - self.pos).length() < 170]
            nearby_count = len(nearby)

            if nearby_count >= 8:
                dyn_weight_a = min(0.95, dyn_weight_a + 0.14)
                dyn_weight_b = 1.0 - dyn_weight_a
                self.struct_add_chance = max(0.04, self.struct_add_chance * 0.96)
            elif nearby_count >= 4:
                dyn_weight_a = min(0.92, dyn_weight_a + 0.08)
                dyn_weight_b = 1.0 - dyn_weight_a

            # Update own emitted signal (forced minimum for testing)
            energy_factor = min(0.65, self.owner.energy / 100.0)
            self.signal_value = max(0.25, 0.50 + energy_factor * 0.45)
            if getattr(self, 'recent_success_boost', 0.0) > 0.0:
                self.signal_value += 0.30

            # Debug: Print signal value more frequently for testing
            if random.random() < 0.05:
                print(f"[SIGNAL] signal_value = {self.signal_value:.2f} | energy={self.owner.energy:.1f}")

            # === Stage A: Stronger Dynamic Module-Voice Coupling ===
            if hasattr(self, 'module_preference_B'):
                self.voice_timbre = np.clip(0.38 + (self.module_preference_B * 0.42), 0.12, 0.88)
                self.voice_mod_depth = np.clip(0.09 + (self.module_preference_B * 0.20), 0.05, 0.36)

            # === v77: Signal Perception & Response ===
            # Detect and react to signals from nearby creatures
            if nearby_count > 0:
                avg_neighbor_signal = sum(c.signal_value for c in nearby) / nearby_count

                # If neighbors are emitting strong signals, slightly shift toward expressive module
                if avg_neighbor_signal > 0.7:
                    dyn_weight_b = min(0.85, dyn_weight_b + 0.08)
                    dyn_weight_a = 1.0 - dyn_weight_b

            # === v80: Local Group Effects + Stability ===
            # Balanced benefits for small local groups
            if 3 <= nearby_count <= 6:
                avg_signal = sum(c.signal_value for c in nearby) / nearby_count
                if avg_signal > 0.55:
                    self.owner.energy = min(200, self.owner.energy + 0.09)  # Slightly reduced for balance

                    if hasattr(self.owner, 'reproduction_cooldown'):
                        self.owner.reproduction_cooldown = max(0, self.owner.reproduction_cooldown - 1)

        weight_a = dyn_weight_a
        weight_b = dyn_weight_b

        # === Phase 4: Cross-Module Coordination + Stability (v72) ===
        shared_signal = (h2a.mean() + h2b.mean()) * 0.04

        coord_factor = 1.0 + (h2a.mean() - h2b.mean()) * 0.10
        h2b = h2b * np.clip(coord_factor, 0.90, 1.10)

        h2a = h2a + shared_signal * 0.25
        h2b = h2b + shared_signal * 0.15

        h2 = h2a * weight_a + h2b * weight_b

        # === Phase 4: Explicit Module Tracking (v66) ===
        # Record relative usage of each module
        total = weight_a + weight_b
        if total > 0:
            self.module_usage["Module_A"] = weight_a / total
            self.module_usage["Module_B"] = weight_b / total

        # Memory-Module Interaction + Stability
        memory_influence = 1.0
        if weight_b > 0.55:
            memory_influence = 1.08

        h2 = h2 * memory_influence

        # Hierarchical Controller
        control_signal = 1.0
        if hasattr(self, 'owner') and self.owner:
            energy_factor = np.clip(self.owner.energy / 120.0, 0.75, 1.25)
            success_boost = getattr(self, 'recent_success_boost', 0.0)
            control_signal = energy_factor * (1.0 + success_boost * 0.65)
            if self.owner.is_desperate():
                control_signal *= 0.88

        h3 = np.tanh(np.dot(h2, self.w3) + self.b3) * np.clip(control_signal, 0.65, 1.35)
        out = np.tanh(np.dot(h3, self.w4) + self.b4)
        return out

# ====================== SOUND MANAGER ======================
class SoundManager:
    def __init__(self):
        self.muted = False
        self.master_volume = 0.65
        # Base volumes directly controlled by sliders (for testing/refinement)
        self.ethereal_base = 0.6
        self.chorus_base = 0.55
        self.life_event_base = 0.5
        self.last_death_time = 0
        self.last_birth_time = 0
        self.drone_channel = None
        self.drone_sound = None
        # Drone temporarily disabled for audio debugging (v90)
        # if not self.muted:
        #     self._create_ambient_drone()

    def _create_ambient_drone(self):
        try:
            sample_rate = 44100
            duration = 12.0
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples, False)
            wave = np.sin(2 * np.pi * 48 * t) * 0.55
            wave += np.sin(2 * np.pi * 48.7 * t) * 0.35
            wave += np.sin(2 * np.pi * 96 * t) * 0.12
            envelope = np.linspace(0.92, 1.0, samples) * np.linspace(1.0, 0.92, samples)
            wave = wave * envelope
            wave = (wave * 28000).astype(np.int16)
            stereo = np.column_stack((wave, wave))
            self.drone_sound = pygame.sndarray.make_sound(stereo)
            self.drone_channel = pygame.mixer.Channel(1)
            self.drone_channel.play(self.drone_sound, loops=-1)
            self.drone_channel.set_volume(self.master_volume * 0.38)
        except Exception as e:
            print("Drone creation failed:", e)

    def set_master_volume(self, vol):
        self.master_volume = max(0.0, min(1.0, vol))
        if self.drone_channel:
            self.drone_channel.set_volume(self.master_volume * 0.38)

    def toggle_mute(self):
        self.muted = not self.muted
        if self.drone_channel:
            if self.muted:
                self.drone_channel.stop()
            else:
                self.drone_channel.play(self.drone_sound, loops=-1)
                self.drone_channel.set_volume(self.master_volume * 0.38)

    def _make_pop(self, frequency=220, duration=0.18, volume=0.28, reverb=0.0):
        """Generate a short tonal pop. If reverb > 0, append a decaying echo tail for spatial feel."""
        sample_rate = 44100
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        wave = np.sin(2 * np.pi * frequency * t)
        envelope = np.linspace(0.0, 1.0, int(samples * 0.12))
        envelope = np.concatenate([envelope, np.linspace(1.0, 0.0, samples - len(envelope))])
        wave = wave * envelope * volume * 32000

        # Simple spatial reverb tail (decaying echoes)
        if reverb > 0.05:
            tail_len = int(samples * (0.35 + reverb * 0.4))
            tail = np.zeros(tail_len, dtype=np.float32)
            decay = 0.6 - reverb * 0.15
            for i in range(min(3, int(2 + reverb * 2))):  # 2-4 echoes
                offset = int((0.12 + i * 0.09) * sample_rate)
                if offset < tail_len:
                    echo_amp = (0.45 - i * 0.12) * reverb
                    echo = wave[:max(0, tail_len - offset)] * echo_amp
                    tail[offset:offset + len(echo)] += echo * (decay ** i)
            # Mix tail back in
            total_len = max(len(wave), len(tail))
            mixed = np.zeros(total_len, dtype=np.float32)
            mixed[:len(wave)] += wave
            mixed[:len(tail)] += tail * 0.7
            wave = mixed

        wave = wave.astype(np.int16)
        stereo = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(stereo)

    def play_death_pop(self):
        if self.muted: return
        now = pygame.time.get_ticks()
        if now - self.last_death_time < 40: return
        self.last_death_time = now
        try:
            sound = self._make_pop(frequency=random.randint(175, 255), duration=0.15, volume=0.38)
            sound.set_volume(self.master_volume * self.life_event_base)
            sound.play()
        except: pass

    def play_reproduce_sound(self):
        if self.muted: return
        now = pygame.time.get_ticks()
        if now - self.last_birth_time < 55: return
        self.last_birth_time = now
        try:
            sound = self._make_pop(frequency=random.randint(310, 390), duration=0.24, volume=0.22)
            sound.set_volume(self.master_volume * self.life_event_base)
            sound.play()
        except: pass

    def play_wall_bounce(self, position=None):
        """Short percussive bounce sound when a creature hits the perimeter during launch.
        Adds spatial reverb when far from center or near edges."""
        if self.muted: return
        now = pygame.time.get_ticks()
        if now - getattr(self, 'last_bounce_time', 0) < 25: return
        self.last_bounce_time = now
        try:
            freq = random.randint(520, 680)
            reverb_amt = 0.0
            vol = self.master_volume * 0.65
            if position:
                cx, cy = WIDTH // 2, HEIGHT // 2
                dist = ((position[0] - cx)**2 + (position[1] - cy)**2) ** 0.5
                vol *= max(0.35, 1.0 - (dist / (WIDTH * 0.7)))
                # More reverb when far from center or near edges
                edge_factor = min(1.0, dist / (WIDTH * 0.45))
                reverb_amt = 0.25 + edge_factor * 0.55
            sound = self._make_pop(frequency=freq, duration=0.07, volume=0.45, reverb=reverb_amt)
            sound.set_volume(vol)
            sound.play()
        except: pass

    def play_inner_launch(self, position=None, is_green=True):
        """Dramatic launch sound when a creature hits the dark inner zone and gets ejected.
        Adds spatial reverb that increases with distance from center."""
        if self.muted: return
        now = pygame.time.get_ticks()
        if now - getattr(self, 'last_launch_time', 0) < 35: return
        self.last_launch_time = now
        try:
            base = 780 if is_green else 920
            freq = random.randint(base - 60, base + 90)
            reverb_amt = 0.15
            vol = self.master_volume * 0.85
            if position:
                cx, cy = WIDTH // 2, HEIGHT // 2
                dist = ((position[0] - cx)**2 + (position[1] - cy)**2) ** 0.5
                vol *= max(0.4, 1.0 - (dist / (WIDTH * 0.65)))
                # Stronger reverb on distant launches
                reverb_amt = 0.35 + min(0.65, (dist / (WIDTH * 0.55)))
            sound = self._make_pop(frequency=freq, duration=0.18, volume=0.55, reverb=reverb_amt)
            sound.set_volume(vol)
            sound.play()
        except: pass

    # Simple cache for generated ethereal signals to reduce expensive sndarray calls
    _ethereal_cache = {}

    def play_ethereal_signal(self, signal_strength=0.6, density=0.3, avg_voice_freq=880.0, avg_timbre=0.5, avg_mod=0.15, signal_tendency=0.5, position=None, velocity=None, caller=None):
        """
        Rhythmic multi-segment vocal calls influenced by emotional state.
        
        Emotions now affect:
        - Pitch (fear → higher, contentment → lower)
        - Timbre & modulation (vengeful/curious = more expressive)
        - Number of rhythmic segments (scared/curious = more segments)
        """
        if self.muted: return
        try:
            sample_rate = 22050

            # === Emotional influence on voice ===
            emotion_pitch_shift = 0.0
            emotion_timbre_shift = 0.0
            emotion_rhythm_boost = 0.0

            if caller is not None:
                dom = getattr(caller, 'dominant_emotion', 'Content')
                if dom == "Scared":
                    emotion_pitch_shift = +55
                    # Scared: less segmentation, more continuous feel to avoid Morse-code pulsing
                    emotion_rhythm_boost = 0.12
                elif dom == "Aggression":
                    emotion_pitch_shift = +25
                    emotion_timbre_shift = +0.12
                    emotion_rhythm_boost = 0.25
                elif dom == "Curious":
                    emotion_timbre_shift = +0.08
                    emotion_rhythm_boost = 0.20
                elif dom == "Content":
                    emotion_pitch_shift = -35
                    emotion_timbre_shift = -0.06

            # Rhythmic patterning influenced by emotion (toned down to avoid morse-like pulsing)
            num_segments = 1
            base_rhythm = signal_tendency + (emotion_rhythm_boost * 0.6)  # Reduced emotional impact
            if base_rhythm > 0.62:
                if random.random() < 0.65:
                    num_segments = 2
                if base_rhythm > 0.82 and random.random() < 0.35:
                    num_segments = 3

            if num_segments > 1:
                seg_dur = 0.32
                # More organic gap variation when emotional
                gap_dur = 0.085 + random.uniform(-0.035, 0.045)
                duration = (seg_dur * num_segments) + (gap_dur * (num_segments - 1))
            else:
                duration = 0.70 + random.uniform(0.0, 0.10)

            samples = int(sample_rate * duration)

            # Phase 1: Mark that this creature recently did a rhythmic call
            if num_segments > 1 and caller is not None:
                caller.recent_rhythmic_call = 240

            # Option C Complete - Final Module Influence
            # module_preference_B has strong, clean, direct control over timbre

            pitch_shift = (avg_timbre - 0.5) * 56 + (avg_mod - 0.15) * 38 + emotion_pitch_shift
            base_freq = max(445, avg_voice_freq * 0.54) + (signal_strength * 2) + pitch_shift

            # Apply emotional timbre shift
            avg_timbre = np.clip(avg_timbre + emotion_timbre_shift, 0.1, 0.95)

            # === Simple Doppler Shift ===
            # Adjust pitch based on movement toward/away from screen center
            if velocity is not None and position is not None:
                try:
                    screen_center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
                    to_center = screen_center - pygame.math.Vector2(position)
                    if to_center.length() > 1:
                        to_center = to_center.normalize()
                        radial_velocity = pygame.math.Vector2(velocity).dot(to_center)
                        # Positive = moving toward center (higher pitch)
                        doppler_factor = 1.0 + (radial_velocity * 0.0025)  # Tuned for subtle effect
                        base_freq *= max(0.85, min(1.18, doppler_factor))
                except:
                    pass

            t = np.linspace(0, duration, samples, False)

            if num_segments > 1:
                # === Rhythmic Multi-Segment Call ===
                seg_len = int(sample_rate * 0.32)
                gap_len = int(sample_rate * 0.09)

                segments = []
                for i in range(num_segments):
                    t_seg = np.linspace(0, 0.32, seg_len, False)

                    # Slight variation per segment for organic rhythm
                    mod_freq = 1.45 + (i * 0.08)
                    mod_amount = (avg_mod * 17.0) * (0.95 + i * 0.04)

                    mod_env = np.linspace(0.3, 1.0, seg_len) * np.linspace(1.0, 0.25, seg_len)
                    mod_w = np.sin(2 * np.pi * mod_freq * t_seg) * mod_amount * mod_env

                    seg = np.sin(2 * np.pi * (base_freq + mod_w) * t_seg) * 0.50
                    segments.append(seg)

                    if i < num_segments - 1:
                        segments.append(np.zeros(gap_len))

                wave = np.concatenate(segments)
                samples = len(wave)
            else:
                # Single segment (normal vocal tone)
                mod_envelope = np.concatenate([
                    np.linspace(0.3, 1.0, int(samples * 0.25)),
                    np.linspace(1.0, 0.25, samples - int(samples * 0.25))
                ])

                expressive_factor = 0.6 + (signal_tendency * 1.1)
                mod_amount = avg_mod * 18.0 * expressive_factor
                mod_freq = 1.5 + (avg_timbre * 0.6)
                mod_wave = np.sin(2 * np.pi * mod_freq * t) * mod_amount * mod_envelope

                wave = np.sin(2 * np.pi * (base_freq + mod_wave) * t) * 0.58

                attack = int(samples * 0.10)
                release = samples - attack
                envelope = np.concatenate([
                    np.linspace(0.0, 1.0, attack),
                    np.linspace(1.0, 0.0, release)
                ])
                wave = wave * envelope

            volume = 0.22 + (density * 0.06) + (signal_strength * 0.015)

            # More aggressive limiting to reduce remaining crackling on high population
            wave = np.tanh(wave * 1.35) * 0.88
            wave = np.clip(wave, -0.92, 0.92)

            # Stronger density-based volume reduction
            effective_volume = volume * (0.82 if density > 0.55 else 0.95)
            wave = (wave * effective_volume * 6800).astype(np.int16)
            stereo = np.column_stack((wave, wave))

            snd = pygame.sndarray.make_sound(stereo)

            # === Spatial Audio (Binaural-style panning) ===
            # Calculate stereo positioning based on creature location
            base_vol = min(1.0, self.master_volume * self.ethereal_base * 4.8)

            if position is not None:
                # Simple spatial panning based on x-position relative to screen center
                try:
                    screen_center_x = WIDTH / 2
                    rel_x = (position[0] - screen_center_x) / (WIDTH / 2)   # -1.0 (left) to +1.0 (right)
                    rel_x = max(-1.0, min(1.0, rel_x))

                    # Distance-based attenuation (simple)
                    distance = abs(rel_x)
                    distance_attenuation = max(0.35, 1.0 - (distance * 0.55))

                    left_vol  = base_vol * distance_attenuation * (1.0 - max(0, rel_x) * 0.7)
                    right_vol = base_vol * distance_attenuation * (1.0 + min(0, rel_x) * 0.7)

                    # Get a free channel and apply stereo volume
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.set_volume(left_vol, right_vol)
                        channel.play(snd)
                    else:
                        snd.set_volume(base_vol)
                        snd.play()
                except:
                    snd.set_volume(base_vol)
                    snd.play()
            else:
                snd.set_volume(base_vol)
                snd.play()

            # Clean debug
            tone_desc = "bright" if avg_timbre > 0.55 else "warm" if avg_timbre > 0.3 else "soft"
            # print(f"[TONE] {tone_desc} | vol≈{volume:.2f} | sig={signal_tendency:.2f}")  # Disabled for dawn/dusk debugging

        except Exception as e:
            print(f"[AUDIO ERROR] play_ethereal_signal failed: {e}")

    def play_chorus_layer(self, signal_strength=0.6, density=0.5, avg_timbre=0.5, avg_mod=0.15):
        """Robust Audible Chorus (v154)."""
        if self.muted: return
        try:
            # Lower sample rate for performance on layered chorus sounds
            sample_rate = 22050
            duration = 2.0 + random.uniform(0.0, 0.4)
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples, False)

            wave = np.zeros(samples)
            base_freq = 585 + (signal_strength * 20)

            for i in range(8):
                detune = (i - 3.5) * 0.0038 * (avg_timbre + 0.4)
                freq = base_freq * (1.0 + i * 0.0045 + detune)
                amp = 0.09 - (i * 0.0065)
                wave += np.sin(2 * np.pi * freq * t) * amp

            if avg_mod > 0.10:
                mod_amount = (avg_mod - 0.05) * 5.5
                mod_wave = np.sin(2 * np.pi * 2.1 * t) * mod_amount
                wave = wave * (1.0 + mod_wave * 0.15)

            envelope = np.linspace(0.22, 1.0, samples) * np.linspace(1.0, 0.16, samples)
            wave = wave * envelope * 0.74

            volume = 0.40 + (density * 0.26)
            wave = (wave * volume * 14200).astype(np.int16)
            stereo = np.column_stack((wave, wave))

            snd = pygame.sndarray.make_sound(stereo)
            # Louder chorus
            snd.set_volume(min(1.0, self.master_volume * self.chorus_base * 1.4))
            snd.play()

            if not DISABLE_CHORUS:
                pass  # print(f"[CHORUS] layer | density={density:.2f}")  # Disabled for dawn/dusk debugging
        except:
            pass

    def update_background_tone(self, population):
        if self.muted or not self.drone_channel: return
        try:
            target = 0.32 + min(population / 420, 0.23)
            self.drone_channel.set_volume(self.master_volume * target)
        except: pass

sound_manager = SoundManager()

# ====================== GAME ======================
GREEN_POS = pygame.math.Vector2(WIDTH * 0.28, HEIGHT // 2 - 40)  # Further left
BLUE_POS = pygame.math.Vector2(WIDTH * 0.82, HEIGHT * 0.22)  # Further separated
GREEN_FOOD = 480.0
BLUE_FOOD = 240.0
GREEN_MAX = 520.0
BLUE_MAX = 280.0

# Controllable multiplier for wrong-patch damage (day/night mismatch)
WRONG_PATCH_DAMAGE_MULT = 1.0
POPULATION_SCALED_WRONG_PATCH = True   # When True, wrong-patch damage scales with population instead of manual slider
EFFECTIVE_WRONG_PATCH_MULT = 1.0       # The actual value used for damage this frame (either manual or pop-scaled)
MAIN_PATCH_PUSH_STRENGTH = 11.72  # Fixed. Green = full at night, Blue = full during day. Zero otherwise.
GREEN_INNER_RADIUS_RATIO = 0.37   # Inner "launch zone" as fraction of current green radius (reduced)
BLUE_INNER_RADIUS_RATIO = 0.37    # Inner "launch zone" as fraction of current blue radius (reduced)
INNER_LAUNCH_STRENGTH = 5.8       # Very strong push when inside the inner dark zone (green or blue)
GREEN_BASE_RADIUS = 120
BLUE_BASE_RADIUS = 105

# Vortex / Central Current System (v504)
VORTEX_CENTER = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
VORTEX_INTENSITY = 0.0           # Default is now 0 (user can raise with slider)
VORTEX_RADIUS = 520              # Effective range of the vortex
VORTEX_EXEMPT_RADIUS = 145       # Radius around main patches that are exempt from vortex force

# === Role Group & Inter-Role Pressure System (v519) ===
ROLE_GROUP_RADIUS = 100          # Radius to check for same-role vs different-role creatures
INTER_ROLE_DAMAGE = 0.38         # Base energy drain per frame when outnumbered by other roles
REPULSION_STRENGTH = 0.85        # How strongly creatures are pushed away from other role groups

WASTE = 0.0
waste_particles = []
energy_tails = []
micro_patches = []
deposit_flashes = []
vortex_particles = []   # Particles flowing toward center to visualize vortex
macro_organisms = []        # Phase 1: Active macro-organisms

# CarryTrail system fully removed for performance

class EnergyTail:
    """Simplified non-particle energy tail effect"""
    def __init__(self, x, y, size, life):
        self.pos = pygame.math.Vector2(x, y)
        self.size = size
        self.life = life
        self.max_life = life

    def update(self):
        self.life -= 1.2
        self.size *= 0.96

    def draw(self, s):
        if self.life <= 0: return
        alpha = max(0.1, self.life / self.max_life)
        # Simple glowing line / dash instead of many particles
        color = (int(100 * alpha), int(255 * alpha), int(255 * alpha))
        end = self.pos + pygame.math.Vector2(random.uniform(-6, 6), random.uniform(-6, 6))
        pygame.draw.line(s, color, (int(self.pos.x), int(self.pos.y)), (int(end.x), int(end.y)), 2)

class MicroPatch:
    __slots__ = (
        'pos', 'amount', 'radius', 'decay_timer', 'is_strategic',
        'persistent', 'outbound', 'has_bounced', 'pulse',
        'attraction_radius', 'vel', 'jet_speed', 'not_harvestable'
    )

    def __init__(self, x, y, amount, is_strategic=False, lifetime=None, persistent=False, outbound=False):
        self.pos = pygame.math.Vector2(x, y)
        self.amount = amount
        self.radius = max(14, min(42, amount * 1.8))
        if lifetime is not None:
            self.decay_timer = lifetime
        else:
            self.decay_timer = 999999 if persistent else (32000 if is_strategic else 16500)
            if persistent:
                self.decay_timer = 999999  # Never expire during brown phase
        self.is_strategic = is_strategic
        self.persistent = persistent
        self.outbound = outbound          # True while in special ejection phase
        self.has_bounced = False          # Becomes True after hitting a map wall
        self.pulse = 0
        self.attraction_radius = 240 if is_strategic else 200
        self.vel = pygame.math.Vector2(0, 0)
        self.jet_speed = False
        self.not_harvestable = outbound   # Unharvestable during special outbound phase

    def update(self):
        global GREEN_FOOD, BLUE_FOOD
        self.decay_timer -= 1
        self.pulse += 0.11

        if not self.persistent:
            decay_rate = 0.997 if self.is_strategic else 0.9985
            if self.decay_timer < 8000:
                self.amount = max(3.5, self.amount * decay_rate)
        self.radius = max(12, min(42, self.amount * 1.8))

        # Universal attraction: All micro-patches are slowly pulled toward nearest main patch
        if not self.persistent:
            target = GREEN_POS if self.pos.distance_to(GREEN_POS) < self.pos.distance_to(BLUE_POS) else BLUE_POS
            to_target = target - self.pos
            if to_target.length() > 6:
                self.pos += to_target.normalize() * 1.1  # Stronger pull toward main patches

        if self.persistent and self.outbound:
            # === Brown/amber ejection phase - strictly unharvestable ===
            self.not_harvestable = True

            # Minimum speed floor
            if self.vel.length() < 4.0:
                self.vel = self.vel.normalize() * 5.0 if self.vel.length() > 0.1 else pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize() * 5.5

            self.pos += self.vel

            # Simple reliable wall bounce (clamp + reverse)
            bounced = False
            if self.pos.x < 30:
                self.pos.x = 30
                self.vel.x *= -0.85
                bounced = True
            if self.pos.x > WIDTH - 30:
                self.pos.x = WIDTH - 30
                self.vel.x *= -0.85
                bounced = True
            if self.pos.y < 30:
                self.pos.y = 30
                self.vel.y *= -0.85
                bounced = True
            if self.pos.y > HEIGHT - BOTTOM_PANEL_HEIGHT - 30:
                self.pos.y = HEIGHT - BOTTOM_PANEL_HEIGHT - 30
                self.vel.y *= -0.85
                bounced = True

            if bounced:
                self.has_bounced = True
                # Convert to normal micro-patch after bouncing
                self.persistent = False
                self.outbound = False
                self.not_harvestable = False
                self.decay_timer = 26000  # Fresh lifetime after conversion

        if self.jet_speed and not (getattr(self, 'persistent', False) and getattr(self, 'outbound', False)):
            # Normal jet movement for non-brown patches
            # Fast jet movement + bounce + gradual slowdown
            self.pos += self.vel
            self.vel *= 0.985

            if self.pos.x < 30 or self.pos.x > WIDTH - 30:
                self.vel.x *= -0.7
            if self.pos.y < 30 or self.pos.y > HEIGHT - BOTTOM_PANEL_HEIGHT - 30:
                self.vel.y *= -0.7

            pull_strength = 1.4 if self.not_harvestable else 0.35
            if self.vel.length() < 2.5 or self.not_harvestable:
                target = GREEN_POS if self.pos.distance_to(GREEN_POS) < self.pos.distance_to(BLUE_POS) else BLUE_POS
                to_target = target - self.pos
                if to_target.length() > 8:
                    self.pos += to_target.normalize() * pull_strength

            if self.not_harvestable and self.vel.length() < 1.8:
                self.not_harvestable = False
        else:
            if not self.persistent:
                target = GREEN_POS if self.pos.distance_to(GREEN_POS) < self.pos.distance_to(BLUE_POS) else BLUE_POS
                to_target = target - self.pos
                if to_target.length() > 5:
                    self.pos += to_target.normalize() * 0.08

    def is_attractive(self):
        return self.amount > 8.0

    def is_expired(self):
        if self.persistent:
            return False
        return self.amount < 3.5 or self.decay_timer <= 0

    def draw(self, s):
        alpha = min(1.0, self.amount / 45)

        if getattr(self, 'outbound', False) and getattr(self, 'persistent', False):
            # Brown/amber ejection phase
            draw_radius = int(self.radius * 1.55)
            pygame.draw.circle(s, (200, 130, 35), (int(self.pos.x), int(self.pos.y)), draw_radius)
            pygame.draw.circle(s, (255, 195, 70), (int(self.pos.x), int(self.pos.y)), int(draw_radius * 0.5))
        else:
            if self.is_strategic:
                r, g, b = int(90 + 60*alpha), int(220 + 25*alpha), int(160 + 70*alpha)
                pygame.draw.circle(s, (r, g, b), (int(self.pos.x), int(self.pos.y)), int(self.radius))
                pulse_size = 10 + math.sin(self.pulse) * 3.2
                pygame.draw.circle(s, (160, 255, 230), (int(self.pos.x), int(self.pos.y)), int(self.radius + pulse_size), 2)
            else:
                r, g, b = int(70 + 75*alpha), int(205 + 35*alpha), int(135 + 45*alpha)
                pygame.draw.circle(s, (r, g, b), (int(self.pos.x), int(self.pos.y)), int(self.radius))
                pygame.draw.circle(s, (110, 255, 180), (int(self.pos.x), int(self.pos.y)), int(self.radius + 8), 1)

# =============================================================================
# SECTION 3: CORE CLASSES
# =============================================================================
# This section contains all the main entity classes:
# - Module
# - Creature (the main agent)
# - MicroPatch
# - NeuralNet
# - SoundManager
# =============================================================================

# Simple particle class for visualizing vortex flow
class VortexParticle:
    __slots__ = ('pos', 'vel')
    
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)


# =============================================================================
# v722: InternalRole System (Phase R2)
# =============================================================================
class InternalRole:
    """Represents a role an InternalAgent can have."""
    def __init__(self, name, consumption_mult=1.0, color=(200, 200, 200), bonus=""):
        self.name = name
        self.consumption_mult = consumption_mult
        self.color = color
        self.bonus = bonus

# Registry of available roles
ROLE_REGISTRY = {
    "harvester": InternalRole("harvester", consumption_mult=0.9, color=(120, 255, 140), bonus="Efficient gatherer"),
    "defender":  InternalRole("defender",  consumption_mult=1.1, color=(255, 180, 120), bonus="Protective"),
    "relay":     InternalRole("relay",     consumption_mult=1.0, color=(160, 200, 255), bonus="Communication"),
    "generalist": InternalRole("generalist", consumption_mult=1.0, color=(200, 220, 200), bonus="Balanced"),
}


# =============================================================================
# v701: Lightweight InternalAgent Class (Phase 11)
# =============================================================================
class InternalAgent:
    """
    Lightweight internal agent living inside a MacroOrganism.
    This is the foundational identity layer for the internal ecosystem.
    No neural net, no complex behavior yet — just data + basic identity.
    """
    def __init__(self, energy=50.0, role_bias="generalist", lineage_signature=None, is_core=False, role=None):
        self.energy = energy
        self.role_bias = role_bias
        self.lineage_signature = lineage_signature or {}
        self.success_score = 0.0
        self.age = 0
        self.is_core = is_core
        self.name = generate_name()

        # v722: Use proper InternalRole object
        if isinstance(role, InternalRole):
            self.role = role
        elif role and role in ROLE_REGISTRY:
            self.role = ROLE_REGISTRY[role]
        else:
            # Default based on role_bias or random
            if role_bias in ROLE_REGISTRY:
                self.role = ROLE_REGISTRY[role_bias]
            else:
                self.role = ROLE_REGISTRY["generalist"]

    def __repr__(self):
        core_str = " [CORE]" if self.is_core else ""
        role_name = self.role.name if hasattr(self.role, 'name') else str(self.role)
        return f"InternalAgent({self.name}{core_str}, energy={self.energy:.1f}, role={role_name})"


class MacroOrganism:
    """True Absorption + Permanent Upgrades (v552)
    
    v655: Foundational spring/tension forces on connections.
    This version establishes the basic physical tension system as the starting point
    for the new Connection Web / Macro of Macros roadmap.
    """
    def __init__(self, members):
        self.members = members
        self.pos = pygame.math.Vector2(0, 0)
        self.vel = pygame.math.Vector2(0, 0)
        self.core_drive = pygame.math.Vector2(0, 0)
        self.role = members[0].get_role() if members else "Unknown"
        self.creation_time = pygame.time.get_ticks()
        self.last_update = pygame.time.get_ticks()
        self.age = 0.0  # seconds lived

        # True absorption system
        self.absorption_timers = {id(m): 0.0 for m in members}
        self.upgrades = {
            "gathering": 0.0,
            "speed": 0.0,
            "energy_efficiency": 0.0,
            "signaling": 0.0
        }

        # Core members (founding) can never be truly consumed
        self.core_members = set(id(m) for m in members[:3]) if len(members) >= 3 else set(id(m) for m in members)

        # Persistent macro name based on core
        if members:
            core = members[0]
            self.core_name = getattr(core, 'name', generate_name()) + " Core"
        else:
            self.core_name = generate_name() + " Core"

        # Visual attachments on the perimeter (from consumed creatures)
        self.attached_modules = []  # [(angle, module_type, radius, tier)]
        self.module_absorption_count = {"harvester": 0, "mover": 0, "storage": 0, "sensor": 0, "armor": 0}  # v731: for fusion
        self.module_composition = {}  # For role evolution

        # Tractor beam system
        self.tractor_targets = []
        self.tractor_cooldown = 0

        # === v700: Internal Ecosystem Scaffold (Phase 11) ===
        # Minimal data structures only. No behavior or visuals yet.
        self.internal_agents = []          # List of lightweight InternalAgent objects (added in v701)
        self.internal_energy = 80.0        # Shared nutrient pool for internals
        self.internal_conflict_cooldown = 0
        self.core_genome_id = None         # Will point to the protected Core internal (v703)

        # v702: Simple conflict visual flashes
        self.conflict_flashes = []  # list of (pos, life) for drawing faint effects inside macro

        # === v704: Upward Trait Flow - Macro personality biases ===
        # These are influenced by successful internals (especially the Core)
        self.macro_voice_timbre_bias = 0.5
        self.macro_fear_sensitivity_bias = 0.65
        self.macro_module_preference_B_bias = 0.45   # How much the macro favors Module_B

        # === v711: Internal Resource Economy ===
        self.internal_nutrient_pool = 120.0   # Shared resource pool for internals

        # v714/v715: Internal stability (influenced by internal ecosystem health)
        self.internal_stability = 1.0

        # v723: Internal Event System
        self.internal_events = []   # List of {'type': str, 'data': dict}

        # v728: Placeholder for future Macro-of-Macros nesting
        self.parent_macro = None
        self.is_nested = False

        # Slight individual variation in preferred connection distance (v619)
        self.preferred_spacing_offset = random.uniform(-8, 12)

    # === v721: Extracted Internal System Methods ===
    def update_internal_economy(self, dt):
        """Handles nutrient pool consumption and macro feeding."""
        if not self.internal_agents:
            return

        total_consumption = 0.0
        for agent in self.internal_agents:
            base_consumption = 0.8 + (agent.success_score * 0.05)
            # v722: Use role's consumption multiplier
            mult = agent.role.consumption_mult if hasattr(agent.role, 'consumption_mult') else 1.0
            consumption = base_consumption * mult
            if agent.is_core:
                consumption *= 0.6
            agent.energy -= consumption
            total_consumption += consumption

        self.internal_nutrient_pool = max(0, self.internal_nutrient_pool - total_consumption * 0.6)

        # Starving internals
        for agent in self.internal_agents:
            if agent.energy < 20:
                agent.energy -= 1.2

        # Remove dead + emit events
        for agent in self.internal_agents:
            if agent.energy <= 0:
                self.emit_internal_event('internal_died', {
                    'role': agent.role.name if hasattr(agent.role, 'name') else str(agent.role),
                    'energy': agent.energy
                })
        self.internal_agents = [a for a in self.internal_agents if a.energy > 0]

        # (Auto-feeding from macro energy disabled — MacroOrganism has no 'energy' attribute)
        # This can be re-enabled later when macros track their own resources properly.

    def update_internal_reproduction(self):
        """Handles internal agent reproduction."""
        if not self.internal_agents:
            return

        new_internals = []
        for agent in self.internal_agents:
            if agent.energy > 55 and agent.success_score > 3.5 and random.random() < 0.06:
                agent.energy -= 18

                child_signature = agent.lineage_signature.copy() if agent.lineage_signature else {}
                for key in child_signature:
                    if isinstance(child_signature[key], (int, float)):
                        child_signature[key] = max(0.15, min(0.9, child_signature[key] + random.uniform(-0.07, 0.07)))

                child = InternalAgent(
                    energy=22,
                    role_bias=agent.role_bias,
                    lineage_signature=child_signature,
                    is_core=False
                )
                new_internals.append(child)
                self.emit_internal_event('internal_born', {
                    'role': child.role.name if hasattr(child.role, 'name') else str(child.role)
                })

        self.internal_agents.extend(new_internals)

    def check_module_fusion(self):
        """
        v746: Module Condensation / Fusion (Mechanically Meaningful)
        When enough modules of one type are absorbed, they now fuse into
        significantly more powerful, permanent macro-level upgrades that
        meaningfully affect the entire cluster (gathering, speed, defense, etc.).
        This is the first version where condensation has strong, observable impact.
        """
        FUSION_THRESHOLD = 7   # Slightly higher threshold for more meaningful fusions

        for mod_type, count in list(self.module_absorption_count.items()):
            if count >= FUSION_THRESHOLD:
                # v746: Much stronger, permanent macro-level upgrade
                bonus_key = f"{mod_type}_efficiency"
                current = self.upgrades.get(bonus_key, 0)
                self.upgrades[bonus_key] = current + 2.5   # Big jump per fusion

                # Also boost a general "power" stat
                self.upgrades["power"] = self.upgrades.get("power", 0) + 1.5

                # Remove more modules from shell (stronger visual condensation)
                to_remove = FUSION_THRESHOLD // 2 + 1
                removed = 0
                new_attached = []
                for data in self.attached_modules:
                    if removed < to_remove and len(data) >= 2 and data[1] == mod_type:
                        removed += 1
                        continue
                    new_attached.append(data)
                self.attached_modules = new_attached

                # Reset counter (keep remainder)
                self.module_absorption_count[mod_type] = count - FUSION_THRESHOLD

                # Stronger visual + cluster-wide effect
                if self.pos:
                    for _ in range(10):
                        fx = self.pos.x + random.uniform(-35, 35)
                        fy = self.pos.y + random.uniform(-35, 35)
                        self.conflict_flashes.append([pygame.math.Vector2(fx, fy), 30])

                    # v746: Brief cluster-wide boost when fusion occurs
                    for member in self.members:
                        member.energy = min(member.max_energy(), member.energy + 4.0)
                        if hasattr(member, 'reproduction_cooldown'):
                            member.reproduction_cooldown = max(0, member.reproduction_cooldown - 25)

    def update_internal_stability(self):
        """v751: Macro Health = Internal + Connection Stability
        Stability is now strongly influenced by BOTH internal ecosystem health
        AND external connection strength (group_stability + number of partners).
        """
        if not self.internal_agents:
            self.internal_stability = 1.0
            return

        avg_internal_energy = sum(a.energy for a in self.internal_agents) / len(self.internal_agents)
        core_stable = any(a.is_core for a in self.internal_agents)

        internal_factor = (avg_internal_energy / 55.0) * (1.15 if core_stable else 0.82)

        # v751: External connection strength contribution
        connection_factor = 1.0
        if hasattr(self, 'group_stability'):
            connection_factor += self.group_stability * 0.35
        if len(getattr(self, 'fusion_partners', [])) >= 3:
            connection_factor += 0.25

        stability = internal_factor * connection_factor
        stability = max(0.55, min(1.5, stability))

        self.internal_stability = stability

        # Apply stability to macro and members
        if hasattr(self, 'reproduction_cooldown') and stability > 1.0:
            self.reproduction_cooldown = max(0, int(self.reproduction_cooldown * (1.9 - stability)))

        if avg_internal_energy < 18 and len(self.internal_agents) > 2:
            self.internal_stability = max(0.5, self.internal_stability * 0.9)

        # v751: High stability gives small passive benefit to members
        if stability > 1.15 and self.members:
            for member in self.members:
                if random.random() < 0.15:
                    member.energy = min(member.max_energy(), member.energy + 0.4)

    def emit_internal_event(self, event_type, data=None):
        """v723: Simple event emission for internal ecosystem."""
        if data is None:
            data = {}
        self.internal_events.append({
            'type': event_type,
            'data': data,
            'frame': pygame.time.get_ticks()
        })

    # === v728: Clean Interfaces for Future Macro-of-Macros Nesting ===
    def get_internal_summary(self):
        """Returns a clean summary of the internal ecosystem state.
        Designed to be safely exposed to parent macros in the future."""
        if not self.internal_agents:
            return {
                'count': 0,
                'avg_energy': 0,
                'core_present': False,
                'roles': {}
            }

        roles = {}
        total_energy = 0
        core_present = False

        for agent in self.internal_agents:
            rname = agent.role.name if hasattr(agent.role, 'name') else str(agent.role)
            if rname not in roles:
                roles[rname] = 0
            roles[rname] += 1
            total_energy += agent.energy
            if agent.is_core:
                core_present = True

        return {
            'count': len(self.internal_agents),
            'avg_energy': total_energy / len(self.internal_agents),
            'core_present': core_present,
            'roles': roles,
            'stability': getattr(self, 'internal_stability', 1.0)
        }

    def get_core_lineage(self):
        """Returns the lineage signature of the current Core, if one exists.
        Useful for upward inheritance in nested macro scenarios."""
        for agent in self.internal_agents:
            if agent.is_core:
                return agent.lineage_signature.copy() if agent.lineage_signature else {}
        return {}

    def update(self):
        if not self.members:
            return

        total_pos = pygame.math.Vector2(0, 0)
        total_vel = pygame.math.Vector2(0, 0)
        for c in self.members:
            total_pos += c.pos
            total_vel += c.vel

        count = len(self.members)
        self.pos = total_pos / count
        self.vel = total_vel / count

        # === v747: Emergent Macro Role Specialization ===
        # Determine dominant lean based on module composition and member roles.
        # This gives macros a simple "personality" or caste over time.
        if not hasattr(self, 'specialization'):
            self.specialization = "generalist"
            self.specialization_strength = 0.0

        # === v749: Simple Macro Memory & Migration ===
        if not hasattr(self, 'remembered_locations'):
            self.remembered_locations = []  # list of (position, quality)

        # === v750: Internal Resource Economy for Macros ===
        if not hasattr(self, 'internal_biomass'):
            self.internal_biomass = 0.0

        # === v753: Alliances Between Macro Clusters ===
        if not hasattr(self, 'allies'):
            self.allies = set()  # set of macro ids we have an alliance with

        # Simple scoring
        scores = {"forager": 0, "scout": 0, "sensor": 0, "courier": 0}
        for m in self.members:
            role = m.get_role() if hasattr(m, 'get_role') else "generalist"
            if role in scores:
                scores[role] += 1

        # Boost from fused modules
        if hasattr(self, 'module_composition'):
            for mod_type, cnt in self.module_composition.items():
                if mod_type == "harvester":
                    scores["forager"] += cnt * 0.8
                elif mod_type == "mover":
                    scores["scout"] += cnt * 0.8
                elif mod_type == "sensor":
                    scores["sensor"] += cnt * 0.9

        dominant = max(scores, key=scores.get)
        total = sum(scores.values()) or 1
        strength = scores[dominant] / total

        self.specialization = dominant if strength > 0.45 else "generalist"
        self.specialization_strength = strength

        # Aggressive refresh + cleanup of fusion_partners every frame (v654)
        fresh_partners = []
        for other in macro_organisms:
            if other is not self and other.role == self.role:
                # Only connect if both are inside the hard simulation box
                if (SIM_LEFT < other.pos.x < SIM_RIGHT and SIM_TOP < other.pos.y < SIM_BOTTOM):
                    if self.pos.distance_to(other.pos) < 190:
                        fresh_partners.append(other)

        # Explicitly remove any dead/stale references (fixes dangling lines)
        self.fusion_partners = [p for p in fresh_partners if p in macro_organisms]

        # Decay timer faster if we no longer have enough close partners
        if len(fresh_partners) < 2:
            self.fusion_prep_timer = max(0, getattr(self, 'fusion_prep_timer', 0) - 4)
        else:
            self.fusion_prep_timer = min(60, getattr(self, 'fusion_prep_timer', 0) + 1)

        # v749: Occasionally record current location as "good" if stable and well-connected
        if len(self.fusion_partners) >= 2 and getattr(self, 'group_stability', 0) > 0.5:
            if random.random() < 0.03:
                self.remembered_locations.append((self.pos.copy(), 1.0))
                # Keep memory limited
                if len(self.remembered_locations) > 5:
                    self.remembered_locations.pop(0)

        # v750: Internal Resource Economy - Tax members and occasionally support them
        if self.members:
            tax_rate = 0.008
            for member in self.members:
                if member.energy > 25:
                    tax = min(0.8, member.energy * tax_rate)
                    member.energy -= tax
                    self.internal_biomass += tax * 0.7

            # Occasionally spend biomass to support members (macro "investing" in the cluster)
            if self.internal_biomass > 8 and random.random() < 0.12:
                spend = min(3.0, self.internal_biomass * 0.4)
                self.internal_biomass -= spend
                for member in self.members:
                    if random.random() < 0.6:
                        member.energy = min(member.max_energy(), member.energy + 1.2)
                        if hasattr(member, 'reproduction_cooldown'):
                            member.reproduction_cooldown = max(0, member.reproduction_cooldown - 8)

        # === v775: Persistent Group Identity & Early Emergent Goals ===
        # Nested/super-organism groups maintain stronger persistent identity.
        # High-stability groups begin showing simple long-term behavioral biases
        # (early emergent goals, e.g. preference for certain strategies or areas).

        if len(getattr(self, 'allies', [])) >= 6 and getattr(self, 'group_stability', 0) > 1.1:
            for other in macro_organisms:
                if other is self:
                    continue
                dist = self.pos.distance_to(other.pos)
                if dist < 250 and getattr(other, 'group_stability', 0) < 1.0:
                    # Strong integrative pull + resource flow
                    if random.random() < 0.05:
                        to_self = self.pos - other.pos
                        if to_self.length() > 50:
                            other.core_drive = other.core_drive * 0.5 + to_self.normalize() * 1.6

                        if self.internal_biomass > 15:
                            transfer = 0.8
                            self.internal_biomass -= transfer
                            other.internal_biomass = getattr(other, 'internal_biomass', 0) + transfer * 0.7
                            other.group_stability = min(1.4, getattr(other, 'group_stability', 1.0) + 0.03)

                    # Persistent identity inheritance (stronger and more lasting)
                    if random.random() < 0.04 and hasattr(self, 'specialization') and hasattr(other, 'specialization'):
                        if self.specialization_strength > 0.7:
                            other.specialization = self.specialization
                            other.specialization_strength = max(other.specialization_strength, self.specialization_strength * 0.7)

            # v780: Clear, strong emergent long-term goals — very consistent home range + strategic personality
            if random.random() < 0.045:
                if not hasattr(self, 'persistent_preference'):
                    self.persistent_preference = self.pos.copy()
                else:
                    # Extremely strong reinforcement of preferred area
                    self.persistent_preference = self.persistent_preference * 0.86 + self.pos * 0.14

                # Very strong, reliable pull toward persistent preference
                if hasattr(self, 'persistent_preference'):
                    to_pref = self.persistent_preference - self.pos
                    if to_pref.length() > 35:
                        self.core_drive = self.core_drive * 0.55 + to_pref.normalize() * 1.45

        # === v753: Alliance Formation & Mutual Benefits ===
        self.allies.clear()
        for other in macro_organisms:
            if other is self or other.role != self.role:
                continue
            dist = self.pos.distance_to(other.pos)
            if dist < 220 and getattr(other, 'group_stability', 0) > 0.6 and getattr(self, 'group_stability', 0) > 0.6:
                # Form alliance
                self.allies.add(id(other))
                other.allies.add(id(self))

                # Mutual stability bonus
                bonus = 0.04
                self.group_stability = min(1.5, getattr(self, 'group_stability', 0) + bonus)
                other.group_stability = min(1.5, getattr(other, 'group_stability', 0) + bonus)

                # Small shared resource trickle when very close
                if dist < 140 and self.internal_biomass > 5 and other.internal_biomass > 5:
                    transfer = 0.15
                    self.internal_biomass -= transfer
                    other.internal_biomass += transfer * 0.8

        # === v757: Richer Alliance Songs (when highly stable with multiple allies) ===
        if len(getattr(self, 'allies', [])) >= 3 and getattr(self, 'group_stability', 0) > 0.85 and random.random() < 0.035:
            try:
                # Longer, more musical group vocalization ("song")
                sound_manager.play_chorus_layer(
                    signal_strength=0.9,
                    density=min(1.0, len(self.allies) / 2.8),
                    avg_timbre=0.52 + (self.specialization_strength * 0.25 if hasattr(self, 'specialization_strength') else 0),
                    avg_mod=0.19
                )
                # Follow-up ethereal layer for depth
                sound_manager.play_ethereal_signal(
                    signal_strength=0.75,
                    density=0.55,
                    avg_voice_freq=850,
                    avg_timbre=0.5,
                    avg_mod=0.17,
                    signal_tendency=0.65,
                    position=self.pos,
                    caller=self
                )
            except:
                pass

        # v755 contextual chorus still active for smaller alliances
        if len(getattr(self, 'allies', [])) >= 2 and random.random() < 0.04:
            try:
                t = get_time_of_day()
                day = is_day(t)
                near_food = (self.pos.distance_to(GREEN_POS) < 200) or (self.pos.distance_to(BLUE_POS) < 180)
                base_strength = 0.7 if near_food else 0.6
                if not day: base_strength *= 0.92

                sound_manager.play_chorus_layer(
                    signal_strength=base_strength,
                    density=min(1.0, len(self.allies) / 3.8),
                    avg_timbre=0.5,
                    avg_mod=0.17
                )
            except:
                pass

        # === v739: Gentle Connection Pulling (First Active Mechanical Use of Links) ===
        # When a macro has 2+ stable fusion_partners (i.e. is part of a connected cluster),
        # it gently tugs nearby lone creatures toward itself. This is the first time
        # the red connection lines produce an observable effect on the world outside the macros.
        # Strength is deliberately low and only active during fusion_prep.
        if len(self.fusion_partners) >= 2 and getattr(self, 'fusion_prep_timer', 0) > 8:
            for c in creatures:
                if getattr(c, 'in_macro', None) is not None:
                    continue
                d = c.pos.distance_to(self.pos)
                if 30 < d < 130:
                    # v743: Active Limb Usage — Coordinated Group Pull
                    # When the macro is part of a stable connected cluster, the pull
                    # becomes stronger and directed toward the group center (not just self).
                    # This makes connected macros act more like a single organism with reach.
                    base_strength = 0.032 * (1.0 - (d / 130.0))

                    # v741 role bias still applies
                    if self.role == "Forager":
                        base_strength *= 1.4
                    elif self.role == "Scout":
                        base_strength *= 0.9
                    elif self.role == "Sensor":
                        base_strength *= 1.2

                    # v743: Coordinated boost when group_stability is decent
                    group_stability = getattr(self, 'group_stability', 0.0)
                    if group_stability > 0.4:
                        base_strength *= (1.0 + group_stability * 0.6)

                    # Pull toward group center when highly connected and stable
                    if len(self.fusion_partners) >= 3 and group_stability > 0.5:
                        avg_partner_pos = pygame.math.Vector2(0, 0)
                        for p in self.fusion_partners:
                            avg_partner_pos += p.pos
                        avg_partner_pos /= len(self.fusion_partners)
                        toward = (avg_partner_pos - c.pos).normalize() * base_strength * 0.7
                    else:
                        toward = (self.pos - c.pos).normalize() * base_strength

                    c.vel = c.vel * 0.87 + toward

        # === v742: Information & Bonus Transfer Through Connections ===
        # When a macro has 2+ stable connected partners, it shares a small bonus
        # with its own members. This is the first time the connection web actively
        # transfers value between macros (proto-information / resource sharing via links).
        if len(self.fusion_partners) >= 2:
            connection_bonus = 0.8 + min(0.6, len(self.fusion_partners) * 0.15)
            for member in self.members:
                # Small reproduction cooldown reduction (information flow benefit)
                if hasattr(member, 'reproduction_cooldown'):
                    member.reproduction_cooldown = max(0, int(member.reproduction_cooldown * 0.92 / connection_bonus * 0.95))
                # Tiny gathering efficiency tick (shared stability)
                if random.random() < 0.15:
                    member.energy = min(member.max_energy(), member.energy + 0.12)

        # === Food Seeking + Threat Avoidance (v569) ===
        t = get_time_of_day()
        day = is_day(t)

        # Strong bias toward active food patch
        target_food = GREEN_POS if day else BLUE_POS
        to_food = target_food - self.pos
        if to_food.length() > 15:
            food_dir = to_food.normalize()

            # v747: Specialization bias on food seeking
            if self.specialization == "forager" and self.specialization_strength > 0.5:
                self.core_drive = self.core_drive * 0.65 + food_dir * 2.6   # Stronger gathering drive
            elif self.specialization == "scout" and self.specialization_strength > 0.5:
                self.core_drive = self.core_drive * 0.72 + food_dir * 1.9   # More mobile/exploratory
            else:
                self.core_drive = self.core_drive * 0.65 + food_dir * 2.2

            # v749: Simple memory-based migration bias
            if self.remembered_locations and random.random() < 0.08:
                best = max(self.remembered_locations, key=lambda x: x[1])
                mem_pos, quality = best
                to_mem = mem_pos - self.pos
                if to_mem.length() > 80:  # Only if far from remembered spot
                    mem_dir = to_mem.normalize()
                    self.core_drive = self.core_drive * 0.7 + mem_dir * (1.8 * quality)

        # Threat avoidance from strong hostile macros
        for other in macro_organisms:
            if other is self or other.role == self.role:
                continue
            d = self.pos.distance_to(other.pos)
            if 10 < d < 160:
                threat = len(other.members) + sum(other.upgrades.values()) * 1.8
                if threat > 5:
                    away = (self.pos - other.pos).normalize()
                    self.core_drive += away * (threat * 0.3)

        # Keep some momentum
        self.core_drive = self.core_drive * 0.85 + self.vel * 0.15

        if self.core_drive.length() > 6.5:
            self.core_drive = self.core_drive.normalize() * 6.5

        # === Connection Tension + Cohesion + Basic Locking (v628) ===
        # Macros now build "locking" when they maintain low stress for a sustained period.
        # This makes stable clusters gradually resist being pulled apart.
        if not hasattr(self, 'cohesion'):
            self.cohesion = 0.0
        if not hasattr(self, 'low_stress_time'):
            self.low_stress_time = 0
        if not hasattr(self, 'group_stability'):
            self.group_stability = 0.0

        self.connection_stress = 0.0

        if getattr(self, 'fusion_prep_timer', 0) > 5:
            # v658 + v659: Ghost Connection Persistence + Weak Forces
            if not hasattr(self, 'ghost_partners'):
                self.ghost_partners = []  # list of (partner_ref, remaining_frames)

            raw_partners = getattr(self, 'fusion_partners', [])
            alive_partners = []

            for p in raw_partners:
                if p in macro_organisms:
                    alive_partners.append(p)
                else:
                    # Turn into ghost (v744: longer persistence)
                    self.ghost_partners.append([p, 420])

            # Update ghosts + apply weak reaching force (v659)
            new_ghosts = []
            for ghost in self.ghost_partners:
                ghost[1] -= 1
                if ghost[1] > 0:
                    new_ghosts.append(ghost)

                    # v744: Stronger reaching force from evolved ghost tendrils
                    partner = ghost[0]
                    if partner in macro_organisms:
                        to_ghost = partner.pos - self.pos
                        if to_ghost.length() > 20:
                            ghost_force = to_ghost.normalize() * 0.018
                            self.core_drive += ghost_force

                    # v757: Richer Ghost Echoes (more varied and emotional)
                    if random.random() < 0.09:
                        try:
                            strength = 0.32 + random.uniform(0, 0.12)
                            timbre = 0.48 + random.uniform(-0.08, 0.12)
                            sound_manager.play_ethereal_signal(
                                signal_strength=strength,
                                density=0.22,
                                avg_voice_freq=760 + random.uniform(-40, 60),
                                avg_timbre=timbre,
                                avg_mod=0.24,
                                signal_tendency=0.38,
                                position=self.pos,
                                caller=self
                            )
                        except:
                            pass

            # v660: Environmental Probing via Ghost Tendrils
            # Ghost connections now weakly sense and pull toward nearby interesting things
            # (other macros or food) within a probing radius. This turns ghosts into primitive sensors.
            if hasattr(self, 'ghost_partners') and len(self.ghost_partners) > 0:
                probe_radius = 180
                for ghost in self.ghost_partners:
                    # Only probe if we still have active ghost connections
                    if ghost[1] > 40:  # v744: Ghosts probe longer (more evolved tendrils)
                        # Look for nearby macros to probe toward
                        for other in macro_organisms:
                            if other is self:
                                continue
                            dist = self.pos.distance_to(other.pos)
                            if dist < probe_radius and dist > 25:
                                # v744: Slightly stronger probing
                                to_other = other.pos - self.pos
                                probe_strength = 0.011 * (1.0 - (dist / probe_radius))
                                self.core_drive += to_other.normalize() * probe_strength
                                break  # Only probe toward one nearby target per frame for performance

            self.ghost_partners = new_ghosts

            partners = alive_partners

            # v661: Basic Polygon Detection (foundation for Phase 3)
            # When a macro has 3+ stable connections, begin detecting if they form a rough polygon.
            # This stores basic "polygon awareness" that later versions will build upon
            # (inside/outside detection, filtration, scooping, etc.).
            if len(partners) >= 3 and self.low_stress_time > 100:
                total_dist = 0
                for p in partners:
                    total_dist += self.pos.distance_to(p.pos)

                avg_connection_dist = total_dist / len(partners)

                if not hasattr(self, 'polygon_awareness'):
                    self.polygon_awareness = 0.0

                # Increase awareness when connections form a reasonably consistent shape
                if 35 < avg_connection_dist < 170:
                    self.polygon_awareness = min(1.0, self.polygon_awareness + 0.006)
                else:
                    self.polygon_awareness = max(0.0, self.polygon_awareness - 0.012)

            # v662: Inside vs Outside Logic (early foundation)
            # When polygon awareness is high enough, the macro begins to understand
            # whether it is currently inside or outside the shape formed by its connections.
            if getattr(self, 'polygon_awareness', 0) > 0.5 and len(partners) >= 3:
                # Simple heuristic: compare distance to average partner position vs average connection length
                avg_partner_pos = pygame.math.Vector2(0, 0)
                for p in partners:
                    avg_partner_pos += p.pos
                avg_partner_pos /= len(partners)

                dist_to_center = self.pos.distance_to(avg_partner_pos)
                avg_conn = 0
                for p in partners:
                    avg_conn += self.pos.distance_to(p.pos)
                avg_conn /= len(partners)

                if not hasattr(self, 'is_inside_web'):
                    self.is_inside_web = False

                # If we're closer to the center than the average connection length, consider us "inside"
                if dist_to_center < avg_conn * 0.7:
                    self.is_inside_web = True
                else:
                    self.is_inside_web = False

            # v663: Basic Filtration (early)
            # When the macro is inside its own web (polygon), it experiences slight movement damping.
            # This is the first step toward webs being able to filter, slow down, or trap things inside them.
            if getattr(self, 'is_inside_web', False) and getattr(self, 'polygon_awareness', 0) > 0.6:
                # Gentle damping when inside the web
                self.core_drive *= 0.96

            # v664: Active Scooping Behavior
            # When inside a well-formed web, the macro weakly pulls nearby vortex particles
            # toward itself (basic scooping / gathering behavior).
            if getattr(self, 'polygon_awareness', 0) > 0.55 and getattr(self, 'is_inside_web', False):
                scoop_radius = 95
                for particle in vortex_particles:
                    dist = self.pos.distance_to(pygame.math.Vector2(particle['x'], particle['y']))
                    if dist < scoop_radius and dist > 8:
                        # Pull particle toward this macro
                        to_macro = self.pos - pygame.math.Vector2(particle['x'], particle['y'])
                        pull = to_macro.normalize() * 0.8
                        particle['x'] += pull.x
                        particle['y'] += pull.y

                        # Slight energy bonus when successfully scooping
                        if dist < 25:
                            self.energy = min(100, self.energy + 0.08)

            # v665: Connection Type Differentiation (early foundation)
            # Same-role connections get small cohesion/energy bonuses.
            # Different roles will later develop more distinct interaction styles.
            if len(partners) >= 2:
                same_role_count = sum(1 for p in partners if getattr(p, 'role', None) == getattr(self, 'role', None))
                if same_role_count >= 2:
                    self.core_drive *= 1.012
                    if hasattr(self, 'energy'):
                        self.energy = min(100, self.energy + 0.025 * same_role_count)

            # v666: Predatory Tendrils
            # When inside a strong web, the macro's connections can aggressively pull in nearby creatures
            # (especially desperate/isolated ones). First predatory behavior from the web structure.
            if getattr(self, 'polygon_awareness', 0) > 0.6 and getattr(self, 'is_inside_web', False):
                predatory_radius = 70
                for other in creatures:
                    if other is self:
                        continue
                    dist = self.pos.distance_to(other.pos)
                    if dist < predatory_radius and dist > 12:
                        # Stronger pull on desperate or low-energy creatures
                        pull_strength = 0.035
                        if getattr(other, 'desperate', False) or getattr(other, 'energy', 50) < 30:
                            pull_strength = 0.065

                        to_self = self.pos - other.pos
                        other.pos += to_self.normalize() * pull_strength

            # v667: Connection Memory
            # Macros remember recent positive connection partners and get small affinity bonuses
            # when near them again. First persistent relationship memory in the web.
            if not hasattr(self, 'connection_memory'):
                self.connection_memory = {}

            # Decay old memories
            for pid in list(self.connection_memory.keys()):
                self.connection_memory[pid] *= 0.995
                if self.connection_memory[pid] < 0.1:
                    del self.connection_memory[pid]

            # Build / strengthen memory from current partners
            for p in partners:
                pid = id(p)
                if pid not in self.connection_memory:
                    self.connection_memory[pid] = 0.4
                else:
                    self.connection_memory[pid] = min(2.5, self.connection_memory[pid] + 0.02)

            # Apply memory bonus (gentle pull toward familiar partners)
            for p in partners:
                pid = id(p)
                affinity = self.connection_memory.get(pid, 0)
                if affinity > 0.9:
                    to_p = p.pos - self.pos
                    if to_p.length() > 25:
                        memory_pull = to_p.normalize() * (affinity * 0.009)
                        self.core_drive += memory_pull

            # v668: Structural Inheritance
            # When macros with strong connection memory maintain long-term stable connections,
            # they can pass on some structural knowledge (polygon awareness) to their partners.
            # This is the first form of web structure being inherited across the network.
            if getattr(self, 'polygon_awareness', 0) > 0.7:
                for p in partners:
                    pid = id(p)
                    affinity = self.connection_memory.get(pid, 0)
                    if affinity > 1.2 and hasattr(p, 'polygon_awareness'):
                        # Pass on some structural knowledge
                        inheritance = min(0.015, (affinity - 1.0) * 0.01)
                        p.polygon_awareness = min(1.0, p.polygon_awareness + inheritance)

            # v669: Persistent Web Identity (emergent group identity)
            # When a cluster maintains very high connection memory + polygon awareness for a long time,
            # they develop a shared "web identity" that gives the whole group bonuses.
            if getattr(self, 'polygon_awareness', 0) > 0.75 and len(partners) >= 3:
                high_memory_count = sum(1 for p in partners if self.connection_memory.get(id(p), 0) > 1.5)

                if high_memory_count >= 2:
                    if not hasattr(self, 'web_identity'):
                        self.web_identity = 0.0

                    self.web_identity = min(1.0, self.web_identity + 0.008)

                    # Group bonus when web identity is high
                    if self.web_identity > 0.5:
                        self.core_drive *= 1.01
                        if hasattr(self, 'energy'):
                            self.energy = min(100, self.energy + 0.04)

            # v670: Macro Cluster Identity (Phase 6 - Macro of Macros foundation)
            # When multiple macros with high web_identity stay connected for a long time,
            # they begin to function more as a single "cluster entity".
            # This is the first step toward true higher-order Macro of Macros behavior.
            if getattr(self, 'web_identity', 0) > 0.6 and len(partners) >= 3:
                cluster_strength = min(1.0, (self.web_identity - 0.5) * 1.5)

                # Shared drive: the macro is influenced by the average drive of its high-identity partners
                avg_partner_drive = pygame.math.Vector2(0, 0)
                high_id_partners = 0
                for p in partners:
                    if getattr(p, 'web_identity', 0) > 0.5:
                        avg_partner_drive += getattr(p, 'core_drive', pygame.math.Vector2(0, 0))
                        high_id_partners += 1

                if high_id_partners >= 2:
                    avg_partner_drive /= high_id_partners
                    # Blend own drive with cluster average
                    self.core_drive = self.core_drive * (1 - cluster_strength * 0.3) + avg_partner_drive * (cluster_strength * 0.3)

            # v671: Web-Net Dynamics
            # High web_identity macros can now weakly influence other high web_identity macros
            # that are nearby but not directly connected — forming the first "web-nets".
            if getattr(self, 'web_identity', 0) > 0.65:
                web_net_radius = 220
                for other in macro_organisms:
                    if other is self:
                        continue
                    if getattr(other, 'web_identity', 0) < 0.5:
                        continue

                    dist = self.pos.distance_to(other.pos)
                    if 40 < dist < web_net_radius:
                        to_other = other.pos - self.pos
                        net_strength = 0.006 * (self.web_identity * other.web_identity)
                        self.core_drive += to_other.normalize() * net_strength

            # v672: Macro of Macros Emergence
            # When a macro is deeply embedded in a high web_identity network,
            # it behaves much more like part of a single larger coherent entity.
            if getattr(self, 'web_identity', 0) > 0.7:
                connected_high_id = 0
                total_web_identity = self.web_identity

                for other in macro_organisms:
                    if other is self:
                        continue
                    if getattr(other, 'web_identity', 0) > 0.6:
                        dist = self.pos.distance_to(other.pos)
                        if dist < 280:
                            connected_high_id += 1
                            total_web_identity += other.web_identity

                if connected_high_id >= 2:
                    collective_strength = min(0.65, (connected_high_id * 0.12) + (total_web_identity * 0.1))

                    avg_net_drive = pygame.math.Vector2(0, 0)
                    count = 0
                    for other in macro_organisms:
                        if other is self:
                            continue
                        if getattr(other, 'web_identity', 0) > 0.6:
                            dist = self.pos.distance_to(other.pos)
                            if dist < 280:
                                avg_net_drive += getattr(other, 'core_drive', pygame.math.Vector2(0, 0))
                                count += 1

                    if count >= 2:
                        avg_net_drive /= count
                        self.core_drive = self.core_drive * (1 - collective_strength) + avg_net_drive * collective_strength

            # v673: Long-term Evolution (Final Version)
            # Web-nets with high collective strength slowly strengthen over time.
            # Stronger web-nets can slightly suppress weaker nearby ones.
            # This gives a sense of long-term evolutionary dynamics between macro clusters.
            if getattr(self, 'web_identity', 0) > 0.75:
                if not hasattr(self, 'evolution_timer'):
                    self.evolution_timer = 0
                self.evolution_timer += 1

                if self.evolution_timer % 180 == 0:
                    self.web_identity = min(1.0, self.web_identity + 0.008)

                # Mild competition: strong webs slightly suppress weaker nearby ones
                for other in macro_organisms:
                    if other is self:
                        continue
                    if getattr(other, 'web_identity', 0) < 0.6:
                        dist = self.pos.distance_to(other.pos)
                        if dist < 200:
                            suppression = 0.0008 * self.web_identity
                            other.web_identity = max(0.0, other.web_identity - suppression)

            low_stress_count = 0

            for partner in partners:
                to_partner = partner.pos - self.pos
                dist = to_partner.length()

                if dist < 5:
                    continue

                base_pref = 68 + min(len(self.members), 12) * 2.0
                preferred = base_pref + getattr(self, 'preferred_spacing_offset', 0)

                deviation = abs(dist - preferred)
                stress = min(1.0, deviation / (preferred * 0.55))
                self.connection_stress = max(self.connection_stress, stress)

                force = 0.042

                if dist > preferred * 1.12:
                    self.core_drive += to_partner.normalize() * ((dist - preferred) * force)
                elif dist < preferred * 0.82:
                    self.core_drive -= to_partner.normalize() * ((preferred * 0.82 - dist) * force * 0.9)

                if stress < 0.25:
                    low_stress_count += 1

            # Accumulate cohesion, locking time, and group stability
            if len(partners) > 0 and low_stress_count / len(partners) > 0.6:
                self.cohesion = min(1.0, self.cohesion + 0.008)
                self.low_stress_time = min(300, self.low_stress_time + 1)

                # Group Stability Score (v633) - builds when network is consistently healthy
                stability_gain = 0.003 + (self.cohesion * 0.004)
                self.group_stability = min(1.0, self.group_stability + stability_gain)
            else:
                self.cohesion = max(0.0, self.cohesion - 0.012)
                self.low_stress_time = max(0, self.low_stress_time - 2)
                self.group_stability = max(0.0, self.group_stability - 0.006)

            # Cohesion gives gentle extra pull toward partners
            if self.cohesion > 0.3:
                for partner in partners:
                    to_partner = partner.pos - self.pos
                    if to_partner.length() > 40:
                        self.core_drive += to_partner.normalize() * (self.cohesion * 0.025)

            # v656: Shape Memory enhancement
            if self.low_stress_time > 60 and len(partners) >= 2:
                avg_pos = pygame.math.Vector2(0, 0)
                for p in partners:
                    avg_pos += p.pos
                avg_pos /= len(partners)

                to_group_center = avg_pos - self.pos
                if to_group_center.length() > 12:
                    shape_memory_strength = min(0.035, (self.low_stress_time - 60) / 400.0)
                    self.core_drive += to_group_center.normalize() * shape_memory_strength

            # v657: Active Flexing (Manual) - Foundational version
            # When the macro has strong directional drive (toward food or away from threat)
            # and good cohesion, it can slightly "flex" (shorten) connections on the pulling side.
            # This is the first step toward deliberate paddling / active control of tendrils.
            if self.cohesion > 0.45 and len(partners) >= 2:
                drive_strength = self.core_drive.length()
                if drive_strength > 1.5:
                    drive_dir = self.core_drive.normalize()

                    for partner in partners:
                        to_partner = partner.pos - self.pos
                        if to_partner.length() < 5:
                            continue

                        # If the partner is roughly in the direction we're driving, gently pull them closer
                        alignment = to_partner.normalize().dot(drive_dir)
                        if alignment > 0.4:  # Partner is in front of our movement direction
                            flex_force = min(0.028, drive_strength * 0.012)
                            self.core_drive += to_partner.normalize() * (to_partner.length() * flex_force)

            # Enhanced locking + Group Identity Seed (v630)
            if self.low_stress_time > 80 and len(partners) >= 2:
                avg_pos = pygame.math.Vector2(0, 0)
                for p in partners:
                    avg_pos += p.pos
                avg_pos /= len(partners)

                to_group = avg_pos - self.pos
                if to_group.length() > 18:
                    lock_strength = min(0.8, (self.low_stress_time - 80) / 220.0)
                    self.core_drive += to_group.normalize() * (lock_strength * 0.045)

                # External force dampening when very stable
                if self.low_stress_time > 160:
                    damp = min(0.65, (self.low_stress_time - 160) / 180.0)
                    self.core_drive *= (1.0 - damp * 0.52)   # v740: slightly stronger damping

                # Stronger Group Cohesion + Coordinated Movement + Stability Benefits (v633)
                if self.low_stress_time > 140 and self.cohesion > 0.35:
                    group_pull = min(0.055, (self.low_stress_time - 140) / 280.0)
                    if to_group.length() > 10:
                        self.core_drive += to_group.normalize() * group_pull

                    # Resistance to disruption (v740: amplified)
                    if self.low_stress_time > 180:
                        resistance = min(0.52, (self.low_stress_time - 180) / 200.0)
                        self.core_drive *= (1.0 - resistance * 0.48)

                    # Coordinated movement
                    if self.low_stress_time > 160 and len(partners) >= 2:
                        avg_vel = pygame.math.Vector2(0, 0)
                        for p in partners:
                            avg_vel += p.vel
                        avg_vel /= len(partners)

                        if avg_vel.length() > 0.3:
                            align_strength = min(0.03, (self.low_stress_time - 160) / 350.0)
                            self.core_drive += avg_vel.normalize() * (avg_vel.length() * align_strength)

                    # Stability Threshold (v635) - clear benefits above certain stability levels
                    if self.group_stability > 0.5:
                        stability_bonus = (self.group_stability - 0.5) * 0.09
                        if to_group.length() > 5:
                            self.core_drive += to_group.normalize() * stability_bonus

                        # Strong resistance when above threshold
                        if self.group_stability > 0.65:
                            damp = (self.group_stability - 0.65) * 0.55
                            self.core_drive *= max(0.6, 1.0 - damp)

                        # Condensed State (v638)
                        # Extremely stable clusters gain condensed-state bonuses
                        if self.group_stability > 0.82 and len(partners) >= 2:
                            condensation_pull = (self.group_stability - 0.82) * 0.065
                            if to_group.length() > 3:
                                self.core_drive += to_group.normalize() * condensation_pull

                            # Very strong dampening
                            if self.group_stability > 0.9:
                                self.core_drive *= 0.75

                            # Strong shared momentum
                            if self.group_stability > 0.93:
                                avg_vel = pygame.math.Vector2(0, 0)
                                for p in partners:
                                    avg_vel += p.vel
                                avg_vel /= len(partners)

                                if avg_vel.length() > 0.25:
                                    self.core_drive += avg_vel * 0.035

                            # Condensed Identity (v640)
                            # Maximum stability macros gain distinct condensed identity bonuses
                            if self.group_stability > 0.95:
                                # Very strong group pull
                                if to_group.length() > 2:
                                    self.core_drive += to_group.normalize() * 0.06

                                # Extreme resistance
                                if self.group_stability > 0.97:
                                    self.core_drive *= 0.58

                                # v745: Macro Group Identity & Shared Goals
                                # Very high stability clusters now strongly share momentum and identity.
                                # This is the first clear "proto super-organism" behavior.
                                if self.group_stability > 0.96 and len(partners) >= 2:
                                    avg_vel = pygame.math.Vector2(0, 0)
                                    for p in partners:
                                        avg_vel += p.vel
                                    avg_vel /= len(partners)

                                    if avg_vel.length() > 0.12:
                                        self.core_drive += avg_vel * 0.09   # Stronger shared momentum

                                # Extreme condensed identity (v745)
                                if self.group_stability > 0.98:
                                    self.core_drive *= 0.48  # Very strong unit resistance
                                    # Small shared identity bonus for members
                                    for member in self.members:
                                        if random.random() < 0.08:
                                            member.energy = min(member.max_energy(), member.energy + 0.25)

                    # Multi-Cluster Fusion Tendency (v648)
                    # When multiple highly condensed macros are close with high persistence, fusion effects become even stronger
                    if self.group_stability > 0.91:
                        condensed_count = 0
                        total_persistence = getattr(self, 'condensation_persistence', 0)

                        for other in macro_organisms:
                            if other is self:
                                continue
                            if getattr(other, 'group_stability', 0) > 0.89:
                                dist = self.pos.distance_to(other.pos)
                                if 5 < dist < 120:
                                    to_other = other.pos - self.pos

                                    base_attraction = (self.group_stability + getattr(other, 'group_stability', 0) - 1.8) * 0.04

                                    persistence = getattr(self, 'condensation_persistence', 0)
                                    fusion_charge = persistence * 0.001

                                    pull = (base_attraction + fusion_charge) * max(0, (120 - dist) / 120)
                                    self.core_drive += to_other.normalize() * pull

                                    condensed_count += 1
                                    total_persistence += getattr(other, 'condensation_persistence', 0)

                                    # Accumulate persistence very fast
                                    if not hasattr(self, 'condensation_persistence'):
                                        self.condensation_persistence = 0
                                    self.condensation_persistence = min(250, self.condensation_persistence + 5)

                        # Cluster Stability (v650)
                        # Condensed clusters with high persistence gain stronger unit-like stability
                        if condensed_count >= 2:
                            multi_bonus = min(0.05, (condensed_count - 1) * 0.022)
                            self.core_drive *= (1.0 - multi_bonus)

                            # Stronger shared momentum in stable clusters
                            if condensed_count >= 3 and total_persistence > 140:
                                avg_vel = pygame.math.Vector2(0, 0)
                                for o in macro_organisms:
                                    if o is not self and getattr(o, 'group_stability', 0) > 0.88:
                                        if self.pos.distance_to(o.pos) < 90:
                                            avg_vel += o.vel
                                if avg_vel.length() > 0.15:
                                    self.core_drive += avg_vel.normalize() * (avg_vel.length() * 0.03)

                            # Extra cluster stability resistance when very persistent
                            if total_persistence > 180:
                                self.core_drive *= 0.92

                            # Cluster Memory Seed (v651)
                            # Long-term stable clusters retain some cohesion even if persistence drops
                            if total_persistence > 200:
                                memory_bonus = min(0.025, (total_persistence - 200) * 0.0001)
                                if to_group.length() > 5:
                                    self.core_drive += to_group.normalize() * memory_bonus

                        # Decay persistence when no condensed neighbors
                        if condensed_count == 0:
                            if hasattr(self, 'condensation_persistence'):
                                self.condensation_persistence = max(0, self.condensation_persistence - 8)

            # === Early Angular Awareness (v621) ===
            # If we have 2+ partners, gently discourage very extreme angles
            if len(partners) >= 2:
                for i in range(len(partners)):
                    for j in range(i + 1, len(partners)):
                        p1 = partners[i]
                        p2 = partners[j]

                        v1 = (p1.pos - self.pos).normalize()
                        v2 = (p2.pos - self.pos).normalize()

                        # Dot product → angle between connections
                        dot = max(-1.0, min(1.0, v1.dot(v2)))
                        angle = math.acos(dot)  # radians (0 to pi)

                        # Discourage very sharp angles (< 35°) or very flat ones (> 145°)
                        if angle < 0.61 or angle > 2.53:  # ~35° and ~145°
                            # Small corrective force perpendicular to the bisector
                            bisector = (v1 + v2).normalize()
                            perp = pygame.math.Vector2(-bisector.y, bisector.x)

                            correction = perp * 0.018
                            self.core_drive += correction

        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update) / 1000.0
        self.last_update = current_time

        # === Macro Tractor Beams (v585) ===
        # Pull in nearby creatures within a radius (multiple targets)
        tractor_radius = 95
        max_targets = 4

        self.tractor_targets = [t for t in self.tractor_targets if t in creatures and t.pos.distance_to(self.pos) < tractor_radius + 20]

        if self.tractor_cooldown <= 0:
            for c in creatures:
                if c.in_macro is not None:
                    continue
                if len(self.tractor_targets) >= max_targets:
                    break
                if c.pos.distance_to(self.pos) < tractor_radius and c not in self.tractor_targets:
                    self.tractor_targets.append(c)

            self.tractor_cooldown = 45  # Fire beams every ~0.75 seconds

        if self.tractor_cooldown > 0:
            self.tractor_cooldown -= 1

        # Apply tractor beam effects (strong, controlling pull)
        for target in self.tractor_targets[:]:
            if target not in creatures:
                self.tractor_targets.remove(target)
                continue

            # Disconnect if target becomes desperate/hostile
            if target.energy <= 25:
                self.tractor_targets.remove(target)
                continue

            to_macro = self.pos - target.pos
            dist = to_macro.length()
            macro_radius = 28 + min(len(self.members), 15) * 2.5

            # Auto-absorb once pulled inside the macro
            if dist < macro_radius + 5:
                # Add to macro
                self.members.append(target)
                target.in_macro = self
                if target in creatures:
                    creatures.remove(target)   # v729: Fix population count
                if not hasattr(target, 'macro_name'):
                    target.macro_name = generate_name() + " [" + self.role + "]"

                # Add modules to outer shell
                angle = random.uniform(0, 2 * 3.14159)
                base_r = 28 + min(len(self.members), 15) * 2.5
                radius = base_r + random.uniform(3, 9)
                for mod in target.modules:
                    tier = getattr(mod, 'tier', 1)
                    self.attached_modules.append((angle, mod.type, radius, tier))
                    if mod.type in self.module_absorption_count:
                        self.module_absorption_count[mod.type] += 1  # v731: track for fusion

                # Release the beam
                self.tractor_targets.remove(target)
                continue

            if dist > 3:
                pull_dir = to_macro.normalize()

                # Hyper-aggressive pull
                target.vel *= 0.02
                target.vel = pull_dir * 14.0

                # Extra damage while being pulled
                if target.energy > 10:
                    target.energy = max(0, target.energy - 0.28)
        
        # === v702: Basic Internal Conflict Loop ===
        # Non-core internals occasionally compete. First visible sign of internal life.
        if len(self.internal_agents) >= 2 and self.internal_conflict_cooldown <= 0:
            if random.random() < 0.35:  # Trigger chance per frame when conditions met
                # Pick two non-core agents
                non_core = [a for a in self.internal_agents if not a.is_core]
                if len(non_core) >= 2:
                    a1, a2 = random.sample(non_core, 2)
                    
                    # Simple siphon
                    if a1.energy > a2.energy:
                        transfer = min(4.5, (a1.energy - a2.energy) * 0.35)
                        a1.energy -= transfer
                        a2.energy += transfer * 0.7
                        winner, loser = a1, a2
                    else:
                        transfer = min(4.5, (a2.energy - a1.energy) * 0.35)
                        a2.energy -= transfer
                        a1.energy += transfer * 0.7
                        winner, loser = a2, a1
                    
                    winner.success_score += 0.8
                    loser.success_score = max(0, loser.success_score - 0.3)
                    
                    # Occasional upset (underdog wins big)
                    if random.random() < 0.12:
                        winner.success_score += 1.5
                        # Small energy swing in upset
                        winner.energy += 6
                        loser.energy = max(5, loser.energy - 8)
                    
                    # Create visual flash effect
                    if self.pos:
                        for _ in range(3):
                            flash_pos = self.pos + pygame.math.Vector2(
                                random.uniform(-18, 18), random.uniform(-18, 18)
                            )
                            self.conflict_flashes.append([flash_pos, 18])  # pos, life
                    
                    self.internal_conflict_cooldown = random.randint(45, 90)
        
        if self.internal_conflict_cooldown > 0:
            self.internal_conflict_cooldown -= 1
        
        # Decay old conflict flashes
        self.conflict_flashes = [[p, life-1] for p, life in self.conflict_flashes if life > 1]

        # === v703: Core Genome Anchor Maintenance ===
        # Guarantee exactly one protected core. This is the lineage anchor.
        cores = [a for a in self.internal_agents if a.is_core]
        
        if len(cores) == 0 and len(self.internal_agents) > 0:
            # No core exists → promote the best one
            best = max(self.internal_agents, key=lambda a: a.success_score)
            best.is_core = True
            # Slight mutation on promotion (foundational for lineage evolution)
            if best.lineage_signature:
                for key in list(best.lineage_signature.keys()):
                    if isinstance(best.lineage_signature[key], (int, float)):
                        best.lineage_signature[key] = max(0.1, min(0.95, 
                            best.lineage_signature[key] + random.uniform(-0.08, 0.08)))
            self.core_genome_id = id(best)
            
        elif len(cores) > 1:
            # Too many cores (shouldn't happen, but safety)
            for c in cores[1:]:
                c.is_core = False

        # If we have a core, store its id
        if cores:
            self.core_genome_id = id(cores[0])

        # === v711: Internal Resource Economy (Basic Consumption) ===
        # Internals consume from the shared nutrient pool
        if self.internal_agents:
            total_consumption = 0.0
            for agent in self.internal_agents:
                consumption = 0.8 + (agent.success_score * 0.05)
                if agent.is_core:
                    consumption *= 0.6  # Core is more efficient

                agent.energy -= consumption
                total_consumption += consumption

            self.internal_nutrient_pool = max(0, self.internal_nutrient_pool - total_consumption * 0.6)

            # Starving internals lose energy faster
            for agent in self.internal_agents:
                if agent.energy < 20:
                    agent.energy -= 1.2

            # Dead internals are removed
            self.internal_agents = [a for a in self.internal_agents if a.energy > 0]

            # (Auto-feeding from macro energy removed in v714 fix —
            #  MacroOrganism does not currently track its own energy.
            #  This can be re-added later when macros have proper resource tracking.)

            # === v712: Internal Reproduction ===
            # High-energy, high-success internals can reproduce
            new_internals = []
            for agent in self.internal_agents:
                if agent.energy > 55 and agent.success_score > 3.5 and random.random() < 0.06:
                    # Cost to reproduce
                    agent.energy -= 18

                    # Create offspring with slight mutation
                    child_signature = agent.lineage_signature.copy() if agent.lineage_signature else {}
                    for key in child_signature:
                        if isinstance(child_signature[key], (int, float)):
                            child_signature[key] = max(0.15, min(0.9, child_signature[key] + random.uniform(-0.07, 0.07)))

                    child = InternalAgent(
                        energy=22,
                        role_bias=agent.role_bias,
                        lineage_signature=child_signature,
                        is_core=False,
                        role=agent.role  # inherit role object
                    )
                    new_internals.append(child)

            self.internal_agents.extend(new_internals)

        # === v721: Call Extracted Internal System Methods ===
        if profiling_enabled:
            update_start = time.perf_counter()

        self.update_internal_economy(dt)
        self.update_internal_reproduction()
        self.check_module_fusion()      # v731
        self.update_internal_stability()

        if profiling_enabled:
            internal_update_time += time.perf_counter() - update_start
            profile_frame_count += 1

        # === v704: Upward Trait Flow ===
        # Successful internals (especially Core) gradually shape the macro's personality
        if len(self.internal_agents) > 0 and random.random() < 0.08:
            # Find strongest influencers
            influencers = sorted(self.internal_agents, key=lambda a: a.success_score, reverse=True)[:3]
            
            for agent in influencers:
                influence = 0.012
                if agent.is_core:
                    influence = 0.035  # Core has much stronger, more permanent effect
                
                # Nudge macro biases toward the agent's lineage_signature
                if agent.lineage_signature:
                    if "voice_timbre" in agent.lineage_signature:
                        target = agent.lineage_signature["voice_timbre"]
                        self.macro_voice_timbre_bias = self.macro_voice_timbre_bias * (1 - influence) + target * influence
                    
                    if "fear_sensitivity" in agent.lineage_signature:
                        target = agent.lineage_signature["fear_sensitivity"]
                        self.macro_fear_sensitivity_bias = self.macro_fear_sensitivity_bias * (1 - influence) + target * influence
                
                # General nudge toward Module_B preference for expressive internals
                if agent.success_score > 4.0:
                    self.macro_module_preference_B_bias = min(0.85, self.macro_module_preference_B_bias + influence * 0.6)
            
            # Occasional visual feedback for strong upward flow (especially from Core)
            if any(a.is_core and a.success_score > 5 for a in influencers) and random.random() < 0.4:
                if self.pos:
                    for _ in range(5):
                        p = self.pos + pygame.math.Vector2(random.uniform(-12,12), random.uniform(-12,12))
                        self.conflict_flashes.append([p, 22])

        # === v713: Internal Role Specialization & Macro Bonuses ===
        if self.internal_agents:
            # Count roles
            role_counts = {"harvester": 0, "defender": 0, "relay": 0}
            for a in self.internal_agents:
                if a.role in role_counts:
                    role_counts[a.role] += 1

            total = len(self.internal_agents)
            if total > 0:
                harvester_ratio = role_counts["harvester"] / total
                defender_ratio  = role_counts["defender"] / total
                relay_ratio     = role_counts["relay"] / total

                # Modest macro bonuses from role composition
                if harvester_ratio > 0.4:
                    # More harvesters → slight gathering efficiency
                    pass  # (can be wired to gathering later)

                if defender_ratio > 0.35:
                    # More defenders → slight damage resistance (future)
                    pass

                if relay_ratio > 0.3:
                    # More relays → slightly stronger voice influence
                    self.macro_voice_timbre_bias = min(0.95, self.macro_voice_timbre_bias + 0.008)

            # Occasional role drift (specialization pressure) - v722
            for agent in self.internal_agents:
                if random.random() < 0.015:
                    current_name = agent.role.name if hasattr(agent.role, 'name') else str(agent.role)
                    if current_name == "harvester" and agent.energy > 40:
                        new_role = ROLE_REGISTRY[random.choice(["defender", "relay"])]
                        self.emit_internal_event('role_changed', {'from': current_name, 'to': new_role.name})
                        agent.role = new_role
                    elif current_name == "defender" and agent.success_score > 2:
                        new_role = ROLE_REGISTRY[random.choice(["harvester", "relay"])]
                        self.emit_internal_event('role_changed', {'from': current_name, 'to': new_role.name})
                        agent.role = new_role
                    elif current_name == "relay":
                        new_role = ROLE_REGISTRY[random.choice(["harvester", "defender"])]
                        self.emit_internal_event('role_changed', {'from': current_name, 'to': new_role.name})
                        agent.role = new_role

        self.age += dt

        # True Absorption: consume creatures after time and inherit their power
        to_remove = []
        for m in self.members:
            mid = id(m)
            if mid not in self.absorption_timers:
                self.absorption_timers[mid] = 0.0

            self.absorption_timers[mid] += dt

            # Aggressive consumption (v568) - much faster for large/strong macros
            base_time = 32
            size_factor = min(20, len(self.members)) * 1.15
            upgrade_factor = sum(self.upgrades.values()) * 2.4
            absorb_time = max(8, base_time - size_factor - upgrade_factor)

            if self.absorption_timers[mid] > absorb_time:
                # Only consume non-core members
                if mid not in self.core_members:
                    to_remove.append(m)

                    # === v701: Foundational InternalAgent conversion chance ===
                    # With a chance, the absorbed creature becomes an internal agent
                    # instead of being fully consumed for upgrades. This is the
                    # first step toward "outside → inside → core" lineage paths.
                    if random.random() < 0.28:  # ~28% chance to become internal
                        # Create lightweight InternalAgent from the absorbed creature
                        new_internal = InternalAgent(
                            energy=random.uniform(35, 65),
                            role_bias=m.get_role() if hasattr(m, 'get_role') else "generalist",
                            lineage_signature={
                                "voice_timbre": getattr(getattr(m, 'brain', None), 'voice_timbre', 0.5),
                                "fear_sensitivity": getattr(getattr(m, 'brain', None), 'fear_sensitivity', 0.65),
                            },
                            is_core=(len(self.internal_agents) == 0)  # First internal becomes core
                        )
                        self.internal_agents.append(new_internal)
                        # Do NOT give full upgrade bonus if converted to internal
                    else:
                        # Normal full consumption path (original behavior)
                        module_value = len(m.modules) * 0.9 + sum(1 for mod in m.modules if not mod.damaged) * 0.5
                        self.upgrades["gathering"] += module_value * 0.018
                        self.upgrades["speed"] += module_value * 0.014
                        self.upgrades["energy_efficiency"] += module_value * 0.012
                        self.upgrades["signaling"] += module_value * 0.01

                        # Add visual module attachments tightly on the perimeter
                        for mod in m.modules:
                            angle = random.uniform(0, 2 * 3.14159)
                            base_r = 28 + min(len(self.members), 15) * 2.5
                            radius = base_r + random.uniform(2, 8)
                            self.attached_modules.append((angle, mod.type, radius))

                            if mod.type not in self.module_composition:
                                self.module_composition[mod.type] = 0
                            self.module_composition[mod.type] += 1

                        # Role evolution based on dominant modules
                        if self.module_composition:
                            dominant = max(self.module_composition, key=self.module_composition.get)
                            if self.module_composition[dominant] >= 8:
                                if dominant == "harvester" and self.role != "Forager":
                                    self.role = "Forager"
                                elif dominant == "mover" and self.role != "Scout":
                                    self.role = "Scout"
                                elif dominant == "storage" and self.role != "Courier":
                                    self.role = "Courier"

        for m in to_remove:
            if m in self.members:
                self.members.remove(m)
            if m in creatures:
                creatures.remove(m)
            m.in_macro = None

        # HARD BOUNDARIES for Macros (v653) - nothing escapes the internal box
        self.pos.x = max(SIM_LEFT, min(SIM_RIGHT, self.pos.x))
        self.pos.y = max(SIM_TOP, min(SIM_BOTTOM, self.pos.y))

        # Strong repulsion when near edges
        edge_force = pygame.math.Vector2(0, 0)
        edge_margin = 55

        if self.pos.x < SIM_LEFT + edge_margin:
            edge_force.x += (SIM_LEFT + edge_margin - self.pos.x) * 0.18
        if self.pos.x > SIM_RIGHT - edge_margin:
            edge_force.x -= (self.pos.x - (SIM_RIGHT - edge_margin)) * 0.18
        if self.pos.y < SIM_TOP + edge_margin:
            edge_force.y += (SIM_TOP + edge_margin - self.pos.y) * 0.18
        if self.pos.y > SIM_BOTTOM - edge_margin:
            edge_force.y -= (self.pos.y - (SIM_BOTTOM - edge_margin)) * 0.18

        if edge_force.length() > 0.05:
            self.vel += edge_force
            self.vel *= 0.88  # damping near walls

        # === Defensive sanitization for macros ===
        if not (math.isfinite(self.pos.x) and math.isfinite(self.pos.y)):
            self.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        if not (math.isfinite(self.vel.x) and math.isfinite(self.vel.y)):
            self.vel = pygame.math.Vector2(0, 0)
        self.pos.x = max(SIM_LEFT - 30, min(SIM_RIGHT + 30, self.pos.x))
        self.pos.y = max(SIM_TOP - 30, min(SIM_BOTTOM + 30, self.pos.y))
        if self.vel.length() > 18:
            self.vel = self.vel.normalize() * 18

    def draw(self, screen):
        if not self.members:
            return

        # v737: Global safe color helper to prevent invalid color crashes
        def _safe_draw_circle(surf, color, pos, radius, width=0):
            try:
                if isinstance(color, (list, tuple)):
                    color = tuple(max(0, min(255, int(c))) for c in color)
                else:
                    color = (180, 180, 200)
                pygame.draw.circle(surf, color, pos, radius, width)
            except Exception:
                pass  # Fail silently to prevent crash
        radius = 28 + min(len(self.members), 15) * 2.5

        # Role-based color (robust lookup)
        role_key = (self.role or "").strip().lower()
        role_color_map = {
            "forager":   (80,  220, 130),
            "scout":     (80,  200, 255),
            "courier":   (220, 100, 255),
            "sensor":    (255, 200,  80),
            "generalist":(230, 230, 230),
            "desperate": (255,  80,  80),
        }
        role_color = role_color_map.get(role_key, (180, 220, 255))

        # Outer ring uses role color (more prominent)
        pygame.draw.circle(screen, role_color, (int(self.pos.x), int(self.pos.y)), radius, 3)
        # Inner ring (slightly darker version of role color)
        inner_color = tuple(max(0, c - 60) for c in role_color)
        pygame.draw.circle(screen, inner_color, (int(self.pos.x), int(self.pos.y)), radius - 5, 2)

        # === v718: Basic Profiling - Internal Drawing Timing ===
        if profiling_enabled:
            draw_start = time.perf_counter()

        # === v717: Drawing Performance Pass ===
        # Optimized internal orb drawing with culling and reduced math
        t = pygame.time.get_ticks() / 1000.0

        if self.internal_agents:
            for i, agent in enumerate(self.internal_agents):
                # Gentle orbiting + slight individual phase offset
                base_angle = (hash(agent.name) % 360) / 57.3
                orbit_speed = 0.15 + (i % 5) * 0.03
                angle = base_angle + t * orbit_speed

                # Slight distance breathing
                dist = radius * 0.52 + math.sin(t * 0.8 + i) * 6 + (hash(agent.name) % 12)

                ix = self.pos.x + math.cos(angle) * dist
                iy = self.pos.y + math.sin(angle) * dist

                if agent.is_core:
                    # Core pulses to stand out (always drawn)
                    pulse = 1.0 + math.sin(t * 2.5) * 0.25
                    core_size = 5.8 * pulse
                    pygame.draw.circle(screen, (100, 255, 255), (int(ix), int(iy)), int(core_size + 2))
                    pygame.draw.circle(screen, (255, 235, 160), (int(ix), int(iy)), int(core_size))
                else:
                    # Role-based colors (v713)
                    breath = 1.0 + math.sin(t * 1.8 + i * 1.3) * 0.18
                    size = (2.6 + min(agent.success_score * 0.12, 1.8)) * breath

                    # v717: Simple size culling - skip very small orbs
                    if size < 1.2:
                        continue

                    alpha = 0.5 + min(agent.energy / 110.0, 0.4)

                    # v722: Use role object's color
                    if hasattr(agent.role, 'color'):
                        base_color = agent.role.color
                        color = tuple(int(c * alpha) for c in base_color)
                    else:
                        color = (int(180 * alpha), int(200 * alpha), int(200 * alpha))

                    _safe_draw_circle(screen, color, (int(ix), int(iy)), int(size))

        if profiling_enabled:
            internal_draw_time += time.perf_counter() - draw_start

        # Conflict flashes + brief energy transfer lines (enhanced for v705)
        for pos, life in self.conflict_flashes:
            alpha = max(0.15, life / 20.0)
            size = 2.5 + (20 - life) * 0.2
            color = (int(160 * alpha), int(255 * alpha), int(210 * alpha))
            _safe_draw_circle(screen, color, (int(pos.x), int(pos.y)), int(size))

        # Attached modules - v735: Extra safe color handling
        def _safe_color(base, brightness=1.0):
            try:
                return tuple(max(0, min(255, int(c * brightness))) for c in base)
            except Exception:
                return (180, 180, 200)

        for mod_data in self.attached_modules:
            if len(mod_data) == 4:
                angle, mod_type, mod_radius, tier = mod_data
            else:
                angle, mod_type, mod_radius = mod_data
                tier = 1

            x = self.pos.x + math.cos(angle) * mod_radius
            y = self.pos.y + math.sin(angle) * mod_radius

            # Ultra-safe base color lookup
            default_color = (180, 180, 200)
            base_color = default_color
            if isinstance(mod_type, str):
                base_color = {
                    "harvester": (100, 220, 150),
                    "mover": (100, 160, 255),
                    "storage": (200, 140, 255),
                    "sensor": (255, 200, 100),
                    "armor": (140, 160, 190),
                }.get(mod_type, default_color)

            brightness = 0.85 + (max(1, tier) - 1) * 0.18
            color = _safe_color(base_color, brightness)
            _safe_draw_circle(screen, color, (int(x), int(y)), 4)

        # Tractor beams
        for target in self.tractor_targets:
            if target in creatures:
                pygame.draw.line(screen, (120, 200, 255), 
                                 (int(self.pos.x), int(self.pos.y)), 
                                 (int(target.pos.x), int(target.pos.y)), 2)

        # Enhanced macro network lines with visual tension feedback (v622)
        if len(getattr(self, 'fusion_partners', [])) >= 1:
            for partner in getattr(self, 'fusion_partners', []):
                if partner in macro_organisms and self.pos.distance_to(partner.pos) < 195:
                    dist = self.pos.distance_to(partner.pos)
                    pulse = (pygame.time.get_ticks() // 140) % 5
                    base_thickness = 2 + (pulse // 2)

                    stress = getattr(self, 'connection_stress', 0.0)
                    cohesion = getattr(self, 'cohesion', 0.0)
                    group_stability = getattr(self, 'group_stability', 0.0)

                    # v740: Stronger visual stress + cohesion feedback
                    thickness = base_thickness + int(stress * 3.5) + int(cohesion * 2.5)
                    color_intensity = int(140 + stress * 100 + cohesion * 60)
                    # High group_stability → brighter, slightly warmer lines (cluster "glow")
                    if group_stability > 0.6:
                        color_intensity = min(255, color_intensity + int((group_stability - 0.6) * 80))

                    # v741: Role-based connection tint (Connection Type Differentiation)
                    role_tint = (0, 0, 0)
                    if self.role == "Forager":
                        role_tint = (40, 80, 20)      # Greenish bias
                    elif self.role == "Scout":
                        role_tint = (20, 60, 120)     # Bluish bias
                    elif self.role == "Courier":
                        role_tint = (120, 80, 20)     # Amber bias
                    elif self.role == "Sensor":
                        role_tint = (80, 30, 110)     # Purple bias

                    r = min(255, color_intensity + role_tint[0])
                    g = max(20, min(200, 115 - int(stress * 55) + role_tint[1]))
                    b = min(120, 30 + role_tint[2])
                    line_color = (r, g, b)

                    pygame.draw.line(screen, line_color, 
                                     (int(self.pos.x), int(self.pos.y)), 
                                     (int(partner.pos.x), int(partner.pos.y)), thickness)

        # v753: Draw alliance connections (thicker, glowing cyan-purple lines)
        if hasattr(self, 'allies') and self.allies:
            for other in macro_organisms:
                if id(other) in self.allies and self.pos.distance_to(other.pos) < 250:
                    pulse = (pygame.time.get_ticks() // 180) % 4
                    thickness = 3 + (pulse // 2)
                    # Cyan-purple glowing alliance line
                    alliance_color = (100 + pulse*20, 80, 200 + pulse*15)
                    pygame.draw.line(screen, alliance_color,
                                     (int(self.pos.x), int(self.pos.y)),
                                     (int(other.pos.x), int(other.pos.y)), thickness)

        # v658: Draw Ghost Connections (faded orange)
        if hasattr(self, 'ghost_partners') and len(self.ghost_partners) > 0:
            for ghost in self.ghost_partners:
                partner = ghost[0]
                remaining = ghost[1]
                # Only draw if the ghost reference still exists in the list of macros
                if partner in macro_organisms:
                    alpha = max(40, int(180 * (remaining / 240.0)))  # fade out over time
                    ghost_color = (255, 140, 40)  # Faded orange
                    pygame.draw.line(screen, ghost_color,
                                     (int(self.pos.x), int(self.pos.y)),
                                     (int(partner.pos.x), int(partner.pos.y)), 1)


class Module:
    def __init__(self, mtype, rank=1, tier=1):
        self.type = mtype
        self.rank = rank
        self.tier = tier          # Tier I–V
        self.damaged = False

    def get_color(self):
        if self.damaged:
            return (120, 120, 120)
        base = {
            "harvester": (100, 220, 150),
            "mover": (100, 160, 255),
            "storage": (200, 140, 255),
            "armor": (235, 165, 85),
            "sensor": (150, 200, 255),
            "efficient": (255, 220, 100)
        }.get(self.type, (180, 180, 180))

        # Higher tiers = brighter
        factor = 1.0 + (self.tier - 1) * 0.1
        return tuple(min(255, int(c * factor)) for c in base)

    def get_size(self):
        base = {"harvester": 5.5, "mover": 4.5, "storage": 5.2,
                "sensor": 4.8, "efficient": 4.7, "armor": 5.0}.get(self.type, 5.0)
        return base * (1.0 + (self.rank - 1) * 0.15)  # Slightly larger for higher rank

# -----------------------------------------------------------------------------
# Creature Class
# The main agent in the simulation. Contains:
# - Modules (body parts that provide abilities and can be damaged)
# - Neural network brain
# - Needs, drives, memory, and behavior logic
# -----------------------------------------------------------------------------
class Creature:
    def __init__(self, x, y, modules=None, brain=None, name=None, memory_food=None, memory_threat=None):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.energy = random.uniform(95, 125)
        self.modules = modules if modules else []
        self.carried_biomass = 0.0
        self.brain = brain if brain else NeuralNet()
        self.last_nn_outputs = np.zeros(5)
        self.last_inputs = np.zeros(27)
        self.using_energy_tail = False
        self.deposit_cooldown = 0
        self.is_attacking = False
        self.regenerating = False
        self.current_prey = None
        self.attack_timer = 0
        self.offspring_count = 0
        self.offspring_names = []
        self.reproduction_cooldown = 0
        self.name = name if name else generate_name()
        self.last_attacked_by = None
        self.preparing_to_reproduce = False
        self.memory_food = memory_food if memory_food else pygame.math.Vector2(0, 0)
        self.memory_threat = memory_threat if memory_threat else pygame.math.Vector2(0, 0)
        self.struggle_cooldown = 0
        self.last_slowdown_tone_time = 0  # For differentiated day/night slowdown tones
        self.stun_timer = 0
        self.post_kill_repro_lock = 0
        self.forced_eat_timer = 0          # Temporary override to seek food after hitting wall
        self.launch_momentum = 0           # Frames of strong launch momentum from inner zone
        self.launch_velocity = pygame.math.Vector2(0, 0)

        # Stability improvements (Stage 5.1)
        self.energy_drain_modifier = 1.0
        self.reproduction_success_bonus = 0.0

        # Energy Tail system timers
        self.energy_tail_cooldown = 0

        # Behavioral needs (Stage 5.1)
        self.hunger = 0.0
        self.desperation = 0.0
        self.exploration_need = 0.0
        self.social_need = 0.0

        # Kill tracking
        self.kills = 0

        # Module combination cooldown
        self.module_combine_cooldown = 0

        # Signaling tendency (Stage 5.3)
        self.signal_tendency = 0.3

        # Social Affiliation Memory (v537)
        self.affiliations = {}          # creature_id -> affiliation_score (-100 to +100)
        self.max_affiliations = 10      # Limit tracked relationships for performance
        self.in_macro = None            # Reference to MacroOrganism if member (Phase 1+)
        self.energy_tail_active_timer = 0
        self.post_tail_hunger_timer = 0
        self.post_kill_exploration_timer = 0

        # === Phase 1: Recurrent + Internal State ===
        self.recurrent_state = np.zeros(10)
        self.internal_state = np.zeros(6)
        self.last_recurrent_state = np.zeros(10)

        # === Phase A: Lineage Tracking (Parent & Children) ===
        self.parent_name = None
        self.children_names = []

        # Phase 1: Evolutionary Pressure on Rhythm
        self.recent_rhythmic_call = 0   # Timer for recent multi-segment rhythmic signaling

        # Phase 4: Lineage rhythmic signature (for kin recognition)
        self.lineage_rhythm_signature = 0.5

        # === Emotional State System (v402) ===
        self.fear = 0.0
        self.loneliness = 0.0
        self.contentment = 0.0
        self.curiosity = 0.0
        self.aggression = 0.0
        self.dominant_emotion = "Drifting"

    def external_storage_capacity(self):
        return self.carry_capacity() * 2.0

    def get_role(self):
        if not self.modules:
            return "generalist"
        counts = {}
        for m in self.modules:
            if m.damaged: continue
            counts[m.type] = counts.get(m.type, 0) + 1
        if not counts:
            return "generalist"
        dominant = max(counts, key=counts.get)
        if dominant == "harvester" and counts.get("harvester", 0) >= 2: return "forager"
        if dominant == "mover" and counts.get("mover", 0) >= 2: return "scout"
        if dominant == "storage" and counts.get("storage", 0) >= 2: return "courier"
        if dominant == "sensor": return "sensor"
        return "generalist"

    def get_thought(self):
        """Returns a short phrase describing the creature's current goal or state."""
        if self.regenerating:
            return "Regenerating"

        if self.desperation > 0.65:
            return "Avoiding danger"

        role = self.get_role()
        same_role_nearby = sum(1 for c in creatures if c is not self and c.get_role() == role and self.pos.distance_to(c.pos) < 70)
        total_nearby = sum(1 for c in creatures if c is not self and self.pos.distance_to(c.pos) < 70)

        if same_role_nearby >= 5:
            return "Moving with group"
        if total_nearby >= 5:
            return "Coordinating"

        if self.exploration_need > 0.75:
            return "Exploring"

        if self.social_need > 0.7 and same_role_nearby >= 2:
            return "Seeking others"

        # Default
        return "Drifting"

    def update_emotions(self, nearby, is_desperate):
        """Calculate emotional drives based on environment and recent events.
        Now modulated by heritable emotional sensitivities.
        """
        brain = self.brain
        # Count threats and social context
        nearby_desperate = sum(1 for c in nearby if c.is_desperate())
        same_role_nearby = sum(1 for c in nearby if c.get_role() == self.get_role())
        total_nearby = len(nearby)

        # Fear (modulated by sensitivity)
        threat_level = min(1.0, nearby_desperate / 6.0)
        base_fear = threat_level * 0.7 + (1.0 - self.energy / self.max_energy()) * 0.3
        self.fear = max(0.0, min(1.0, base_fear * brain.fear_sensitivity))

        # Loneliness
        base_loneliness = 1.0 - (total_nearby / 12.0)
        if same_role_nearby < 2:
            base_loneliness += 0.25
        self.loneliness = max(0.0, min(1.0, base_loneliness * brain.loneliness_sensitivity))

        # Contentment
        in_correct_patch = False
        t = get_time_of_day()
        if (is_day(t) and self.pos.distance_to(GREEN_POS) < 160) or \
           (not is_day(t) and self.pos.distance_to(BLUE_POS) < 160):
            in_correct_patch = True

        base_content = 0.0
        if self.energy > 70 and not is_desperate:
            base_content += 0.4
        if in_correct_patch:
            base_content += 0.35
        if total_nearby >= 4:
            base_content += 0.25
        self.contentment = min(1.0, base_content * brain.contentment_sensitivity)

        # Curiosity
        if 35 < self.energy < 85 and total_nearby < 5:
            base_curiosity = 0.6 + (self.sensor_count() * 0.08)
        else:
            base_curiosity = self.curiosity * 0.7
        self.curiosity = max(0.0, min(1.0, base_curiosity * brain.curiosity_sensitivity))

        # Aggression
        if any(m.damaged for m in self.modules) and len(self.modules) >= 4:
            base_aggression = self.aggression + 0.15
        else:
            base_aggression = self.aggression * 0.85
        self.aggression = max(0.0, min(1.0, base_aggression * brain.aggression_sensitivity))

        # When desperate, strongly push toward Aggression
        if self.is_desperate():
            self.aggression = min(1.0, self.aggression + 0.45)

        # Determine dominant emotion
        emotions = {
            "Scared": self.fear,
            "Lonely": self.loneliness,
            "Content": self.contentment,
            "Curious": self.curiosity,
            "Aggression": self.aggression
        }
        self.dominant_emotion = max(emotions, key=emotions.get)

        # Light influence on existing needs
        if self.fear > 0.6:
            self.exploration_need = max(0.0, self.exploration_need - 0.08)
        if self.loneliness > 0.65:
            self.social_need = min(1.0, self.social_need + 0.06)
        if self.contentment > 0.7:
            self.exploration_need = max(0.0, self.exploration_need - 0.05)

    def effective_module_count(self):
        """Returns number of non-damaged modules (used for combat calculations)."""
        return sum(1 for m in self.modules if not m.damaged)

    def get_time_modifiers(self):
        """Returns moderate day/night bonuses/penalties for this creature."""
        t = get_time_of_day()
        day = is_day(t)
        mods = {"mover": 0.0, "harvester": 0.0, "storage": 0.0}

        if day:
            mods["mover"] = 0.12
            mods["harvester"] = 0.15
        else:
            mods["storage"] = 0.12

        return mods

    def get_active_synergies(self):
        types = set(m.type for m in self.modules if not m.damaged)
        active = []
        for pair, data in {
            frozenset(["harvester", "sensor"]): {"name": "Efficient Foraging"},
            frozenset(["mover", "storage"]): {"name": "Endurance Runner"},
            frozenset(["harvester", "mover"]): {"name": "Mobile Harvester"},
            frozenset(["sensor", "storage"]): {"name": "Resource Hoarder"},
        }.items():
            if pair.issubset(types):
                active.append(data)
        return active

    def sensor_count(self):
        return sum(1 for m in self.modules if m.type == "sensor" and not m.damaged)

    def count_nearby(self, creatures_list=None, radius=110):
        """Use precomputed cache when available"""
        if radius == 90 and hasattr(self, 'nearby_count_90'):
            return self.nearby_count_90
        if radius == 110 and hasattr(self, 'nearby_count_110'):
            return self.nearby_count_110
        if radius == 180 and hasattr(self, 'nearby_count_180'):
            return self.nearby_count_180
        # Fallback
        if creatures_list is None:
            return 0
        return sum(1 for c in creatures_list if c is not self and self.pos.distance_to(c.pos) < radius)

    def count_nearby_role(self, role, radius=110, creatures_list=None):
        """Count nearby creatures of a specific role"""
        if creatures_list is None:
            return 0
        return sum(1 for c in creatures_list 
                   if c is not self 
                   and c.get_role() == role 
                   and self.pos.distance_to(c.pos) < radius)

    def is_desperate(self):
        return self.energy < 28

    def is_injured(self):
        return any(m.damaged for m in self.modules)

    def max_energy(self):
        bonus = sum(0.015 for s in self.get_active_synergies())
        return 155 + sum(28 for m in self.modules if m.type == "storage" and not m.damaged) + bonus * 50

    def carry_capacity(self):
        storage_count = sum(1 for m in self.modules if m.type == "storage" and not m.damaged)
        base = 0.9 + (storage_count * 4.0)
        if self.get_role() == "courier":
            base *= 1.25  # Worker caste (Courier) bonus to carrying capacity
        return base

    def speed(self):
        base = 0.78
        time_mods = self.get_time_modifiers()
        mover_bonus = sum(0.52 for m in self.modules if m.type == "mover" and not m.damaged)
        base += mover_bonus * (1.0 + time_mods.get("mover", 0.0))

        # Worker caste trade-offs
        role = self.get_role()
        if role == "forager":
            base *= 0.88  # Foragers are slower (optimized for gathering, not travel)
        if role == "courier" and self.carried_biomass > self.external_storage_capacity() * 0.6:
            base *= 0.85  # Couriers slow down when heavily loaded

        # Time of day + wrong patch energy drain (now much stronger)
        t = get_time_of_day()
        day = is_day(t)
        g_dist = self.pos.distance_to(GREEN_POS)
        b_dist = self.pos.distance_to(BLUE_POS)
        green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
        blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))

        if day:
            if g_dist < green_r:
                base += 0.10
            if b_dist < blue_r and not self.is_desperate():
                # EXTREME drain when inside Blue patch during day
                # Stop applying once the creature becomes desperate (so predators can finish them)
                depth = 1.0 - (b_dist / blue_r)
                drain = 2.4 + (depth * 2.8)
                drain *= EFFECTIVE_WRONG_PATCH_MULT
                # Armor greatly reduces wrong-patch damage
                armor_count = sum(1 for m in self.modules if m.type == "armor" and not m.damaged)
                if armor_count > 0:
                    drain *= max(0.15, 1.0 - (armor_count * 0.35))
                self.energy = max(0, self.energy - drain)
                self.signal_tendency = min(1.0, self.signal_tendency + 0.06)
        else:
            if b_dist < blue_r:
                base += 0.10
            if g_dist < green_r and not self.is_desperate():
                # EXTREME drain when inside Green patch during night
                # Stop applying once the creature becomes desperate
                depth = 1.0 - (g_dist / green_r)
                drain = 2.4 + (depth * 2.8)
                drain *= EFFECTIVE_WRONG_PATCH_MULT
                armor_count = sum(1 for m in self.modules if m.type == "armor" and not m.damaged)
                if armor_count > 0:
                    drain *= max(0.15, 1.0 - (armor_count * 0.35))
                self.energy = max(0, self.energy - drain)
                self.signal_tendency = min(1.0, self.signal_tendency + 0.06)

        if self.is_desperate():
            base += 7.5
            if self.current_prey:
                base += 5.0
        if self.using_energy_tail:
            base += 9.5
        carry_penalty = self.carried_biomass * 0.02
        return base - carry_penalty

    def effective_speed(self):
        """Speed after possible predator slowdown"""
        spd = self.speed()
        # If being targeted by a desperate predator, slow down (unless armored)
        if self.current_prey is None:  # This creature is prey
            for other in creatures:
                if other.current_prey is self and other.is_desperate():
                    armor_count = sum(1 for m in self.modules if m.type == "armor" and not m.damaged)

                    if armor_count == 0:
                        # No armor → prey stops and slowly drifts toward predator
                        spd = 0.06
                        to_pred = (other.pos - self.pos)
                        if to_pred.length() > 0.3:
                            self.vel = to_pred.normalize() * 0.55
                    else:
                        slowdown = 0.5 if armor_count == 1 else 0.75
                        spd *= slowdown
                        to_pred = (other.pos - self.pos)
                        if to_pred.length() > 0.5:
                            self.vel += to_pred.normalize() * (0.3 if armor_count == 1 else 0.1)
                    break
        return spd

    def gather_rate(self):
        base = 2.8
        if self.get_role() == "forager": base += 0.6
        for s in self.get_active_synergies():
            if "Efficient Foraging" in s["name"] or "Mobile Harvester" in s["name"]:
                base += 0.35
        return base + sum(1.1 for m in self.modules if m.type == "harvester" and not m.damaged)

    def energy_drain(self):
        if self.is_attacking:
            return 0.0

        base = 0.055          # Slightly reduced baseline hunger drain
        if self.is_desperate():
            base -= 0.008
        if self.get_role() == "courier":
            carry_ratio = self.carried_biomass / max(self.external_storage_capacity(), 1)
            base -= 0.014 + (carry_ratio * 0.012)
        for s in self.get_active_synergies():
            if "Resource Hoarder" in s["name"] or "Endurance Runner" in s["name"]:
                base -= 0.008
        if not self.is_gathering():
            base += 0.022
        carry_cost = self.carried_biomass * 0.0045
        base += carry_cost
        if self.using_energy_tail:
            base += 0.22
        g_dist = self.pos.distance_to(GREEN_POS)
        b_dist = self.pos.distance_to(BLUE_POS)
        green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
        blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))
        dist_to_food = min(g_dist - green_r, b_dist - blue_r)
        if dist_to_food > 70:
            base += 0.009 * min(2.5, dist_to_food / 110)
        if self.energy < 38:
            starvation = (38 - self.energy) / 38
            base += 0.032 * starvation

        pop = len(creatures)
        if pop > 450:
            over = pop - 450
            pressure = min(12.0, over / 75)
            base += 0.052 * pressure

        return base - sum(0.014 for m in self.modules if m.type == "armor" and not m.damaged) - sum(0.004 for m in self.modules if m.type == "efficient" and not m.damaged)

    def is_gathering(self):
        g_dist = self.pos.distance_to(GREEN_POS)
        b_dist = self.pos.distance_to(BLUE_POS)
        green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
        blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))
        return g_dist < green_r or b_dist < blue_r

    def get_nearest_attractive_patch(self):
        search_radius = 300
        candidates = patch_grid.query(self.pos.x, self.pos.y, search_radius)
        attractive = [p for p in candidates if p.is_attractive()]
        if not attractive:
            return None, 9999
        nearest = min(attractive, key=lambda p: self.pos.distance_to(p.pos))
        return nearest, self.pos.distance_to(nearest.pos)

    def lifetime_learn(self, reward):
        if reward <= 0 or self.last_inputs is None:
            return
        try:
            h3 = np.tanh(np.dot(self.last_inputs, self.brain.w3) + self.brain.b3)
            delta = np.outer(h3, self.last_nn_outputs) * reward * 0.0008
            self.brain.w4 += delta
        except:
            pass

# =============================================================================
# SECTION 4: UPDATE LOGIC
# =============================================================================
# This section handles all game state changes per frame:
# - Creature needs, neural processing, movement, combat, healing, etc.
# =============================================================================

    def update(self, creatures):
        global GREEN_FOOD, BLUE_FOOD, selected_creature

        if self.energy <= 0:
            return

        # Optimization + Strong Macro Following (Overhauled)
        if self.in_macro is not None:
            macro = self.in_macro
            if macro and macro.members:
                # Direct control from macro
                drive = macro.core_drive if macro.core_drive.length() > 0.1 else macro.vel
                if drive.length() > 0.01:
                    speed_mult = 1.0 + macro.upgrades.get("speed", 0)

                    # Module specialization (Mover modules)
                    mover_count = macro.module_composition.get("mover", 0)
                    speed_mult += mover_count * 0.035

                    # Role-specific speed bonuses
                    if macro.role == "Scout":
                        speed_mult *= 1.35
                    elif macro.role == "Desperate":
                        speed_mult *= 1.2
                    elif macro.role == "Courier":
                        speed_mult *= 1.1

                    jitter = pygame.math.Vector2(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4))
                    self.vel = drive.normalize() * (drive.length() * speed_mult * 0.95) + jitter

            # Basic physics update (this was being skipped before!)
            self.pos += self.vel
            self.energy = max(0, self.energy - 0.003)
            return

        # === Hot path caching (safe optimization) ===
        t = get_time_of_day()
        day = is_day(t)
        g_dist = self.pos.distance_to(GREEN_POS)
        b_dist = self.pos.distance_to(BLUE_POS)
        green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
        blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))
        in_correct_patch = (day and g_dist < green_r) or (not day and b_dist < blue_r)

        if self.deposit_cooldown > 0:
            self.deposit_cooldown -= 1
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

            # Dramatic reproduction boost when on correct patch at correct time of day
            if in_correct_patch:
                self.reproduction_cooldown = max(0, self.reproduction_cooldown - 15)
        if self.struggle_cooldown > 0:
            self.struggle_cooldown -= 1
        if self.stun_timer > 0:
            self.stun_timer -= 1
        if self.forced_eat_timer > 0:
            self.forced_eat_timer -= 1

        role = self.get_role()
        desperate = self.is_desperate()
        g_dist = self.pos.distance_to(GREEN_POS)
        b_dist = self.pos.distance_to(BLUE_POS)

        t = get_time_of_day()
        day = is_day(t)

        # Enhanced visual growth
        green_size_mult = 1.65 if day else 0.8
        blue_size_mult = 0.8 if day else 1.65

        green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX) * green_size_mult)
        blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX) * blue_size_mult)

        inside_green = g_dist < green_r
        inside_blue = b_dist < blue_r

        self.preparing_to_reproduce = self.can_reproduce() and not desperate

        nearest_patch, patch_dist = self.get_nearest_attractive_patch()

        base_radius = 165 if not desperate else PREDATOR_VISION_RADIUS
        query_radius = base_radius + (self.sensor_count() * 22)
        if desperate:
            query_radius *= 1.7   # Predators search a wider area for prey
        nearby = creature_grid.query(self.pos.x, self.pos.y, query_radius)

        # === Role Group System (v519) ===
        # Same-role creatures get scaling bonuses. Different-role creatures exert pressure.
        my_role = self.get_role()
        same_role_nearby = 0
        different_role_nearby = 0

        for other in nearby:
            if other is self:
                continue
            other_role = other.get_role()
            dist = self.pos.distance_to(other.pos)
            if dist < ROLE_GROUP_RADIUS:
                if other_role == my_role:
                    same_role_nearby += 1
                else:
                    different_role_nearby += 1

                # === Social Affiliation Update (v537) ===
                # Same role = faster positive drift. Different role = slower / mild negative.
                # Groups of 7+ different-role creatures are treated as hostile to outsiders.
                other_id = id(other)
                dist = self.pos.distance_to(other.pos)
                if dist < 110:
                    if other_id not in self.affiliations:
                        self.affiliations[other_id] = 0.0

                    # Same role bonus (increased for more macro formation)
                    if other_role == my_role:
                        drift = 1.6
                    else:
                        drift = -0.25

                    # Hostile group detection (7+ different role nearby)
                    if different_role_nearby >= 7 and other_role != my_role:
                        drift = -1.2

                    self.affiliations[other_id] += drift
                    self.affiliations[other_id] = max(-100, min(100, self.affiliations[other_id]))

                    # Prune weakest relationships if over limit
                    if len(self.affiliations) > self.max_affiliations:
                        weakest = min(self.affiliations, key=self.affiliations.get)
                        del self.affiliations[weakest]

        # --- Same-Role Group Bonuses (scale with group size) ---
        pack_speed_mult = 1.0
        energy_efficiency_bonus = 0.0
        reproduction_bonus = 0

        if same_role_nearby >= 3:
            pack_speed_mult = 1.0 + min(0.42, (same_role_nearby - 2) * 0.085)
            energy_efficiency_bonus = 0.012
        if same_role_nearby >= 5:
            pack_speed_mult = 1.0 + min(0.55, (same_role_nearby - 2) * 0.095)
            energy_efficiency_bonus = 0.022
        if same_role_nearby >= 7:
            reproduction_bonus = 3  # small cooldown reduction

        # Apply energy efficiency
        if energy_efficiency_bonus > 0:
            self.energy = min(self.max_energy(), self.energy + energy_efficiency_bonus)

        if reproduction_bonus > 0 and self.reproduction_cooldown > 0:
            self.reproduction_cooldown = max(0, self.reproduction_cooldown - reproduction_bonus)

        # === General Proximity Energy Bonus (v526) ===
        # Any creatures near each other gain a small energy benefit (encourages grouping)
        nearby_count_for_proximity = 0
        for o in nearby:
            if o is self: continue
            if self.pos.distance_to(o.pos) < 95:
                nearby_count_for_proximity += 1

        if nearby_count_for_proximity >= 2:
            proximity_bonus = 0.028 * min(nearby_count_for_proximity / 3.0, 2.0)
            self.energy = min(self.max_energy(), self.energy + proximity_bonus)
            if self.reproduction_cooldown > 0:
                self.reproduction_cooldown = max(0, self.reproduction_cooldown - 2)  # Proximity energy helps reproduction (one more pass)

        nearby_count = 0
        nearby_carried_sum = 0
        nearby_desperate = 0
        for o in nearby:
            if o is self: continue
            d = self.pos.distance_to(o.pos)
            if d < query_radius:
                nearby_count += 1
                nearby_carried_sum += o.carried_biomass
                if o.is_desperate():
                    nearby_desperate += 1

        local_density = min(nearby_count / 14.0, 1.0) if nearby_count > 0 else 0.0
        avg_nearby_biomass = (nearby_carried_sum / nearby_count) if nearby_count > 0 else 0.0

        # Ally count for neural input (from Phase B)
        ally_count = sum(1 for o in nearby if not o.is_desperate() and self.pos.distance_to(o.pos) < 180)

        dist_to_green = self.pos.distance_to(GREEN_POS)
        dist_to_blue = self.pos.distance_to(BLUE_POS)

        # Depth-scaled outward push + special Inner Launch Zone (dark green core)
        # Creatures that enter the inner dark circle get a powerful launch across the map.
        green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
        blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))
        green_inner_r = green_r * GREEN_INNER_RADIUS_RATIO
        blue_inner_r = blue_r * BLUE_INNER_RADIUS_RATIO

        # Inner launch zone (dark core) - very strong ejection with momentum carry
        # Works for both green and blue patches
        if dist_to_green < green_inner_r:
            outward = (self.pos - GREEN_POS)
            if outward.length() > 2:
                launch = MAIN_PATCH_PUSH_STRENGTH * INNER_LAUNCH_STRENGTH * (0.85 + random.random() * 0.3)
                self.launch_velocity = outward.normalize() * launch
                self.launch_momentum = 38
                self.pos += self.launch_velocity
                try:
                    sound_manager.play_inner_launch((self.pos.x, self.pos.y), is_green=True)
                except: pass
        elif dist_to_blue < blue_inner_r:
            outward = (self.pos - BLUE_POS)
            if outward.length() > 2:
                launch = MAIN_PATCH_PUSH_STRENGTH * INNER_LAUNCH_STRENGTH * (0.85 + random.random() * 0.3)
                self.launch_velocity = outward.normalize() * launch
                self.launch_momentum = 38
                self.pos += self.launch_velocity
                try:
                    sound_manager.play_inner_launch((self.pos.x, self.pos.y), is_green=False)
                except: pass
        # Normal depth-scaled push in the outer ring of either patch
        # Green pushes hard at night, Blue pushes hard during day. No push at correct time.
        t = get_time_of_day()
        day = is_day(t)

        effective_green_push = MAIN_PATCH_PUSH_STRENGTH if not day else 0.0
        effective_blue_push  = MAIN_PATCH_PUSH_STRENGTH if day else 0.0

        if dist_to_green < green_r:
            outward = (self.pos - GREEN_POS)
            if outward.length() > 3:
                depth = max(0.0, (green_r - dist_to_green) / green_r)
                scaled = effective_green_push * (0.4 + 0.6 * depth)
                push = outward.normalize() * scaled
                self.pos += push
        if dist_to_blue < blue_r:
            outward = (self.pos - BLUE_POS)
            if outward.length() > 3:
                depth = max(0.0, (blue_r - dist_to_blue) / blue_r)
                scaled = effective_blue_push * (0.4 + 0.6 * depth)
                push = outward.normalize() * scaled
                self.pos += push

        # === Vortex / Central Current (v505) - Improved response ===
        # Clockwise, gentle but noticeable, distance-based falloff
        dist_to_green = self.pos.distance_to(GREEN_POS)
        dist_to_blue = self.pos.distance_to(BLUE_POS)
        green_exempt = dist_to_green < (green_r + VORTEX_EXEMPT_RADIUS)
        blue_exempt = dist_to_blue < (blue_r + VORTEX_EXEMPT_RADIUS)

        if not (green_exempt or blue_exempt) and VORTEX_INTENSITY > 0.02:
            to_center = VORTEX_CENTER - self.pos
            dist = to_center.length()

            if dist > 15 and dist < VORTEX_RADIUS:
                norm_dist = min(1.0, dist / VORTEX_RADIUS)
                # Gentler falloff curve (still stronger near center)
                strength = abs(VORTEX_INTENSITY) * (1.0 - norm_dist**0.85)

                # Direction based on sign of VORTEX_INTENSITY
                # Positive = Clockwise, Negative = Counterclockwise
                if VORTEX_INTENSITY >= 0:
                    tangent = pygame.math.Vector2(-to_center.y, to_center.x).normalize()
                else:
                    tangent = pygame.math.Vector2(to_center.y, -to_center.x).normalize()

                vortex_force = tangent * strength * 1.1

                # Apply to velocity for smoother integration with other movement systems
                self.vel += vortex_force * 0.6

        # === Inter-Role Pressure (v519) ===
        # Creatures near more members of other roles get pushed away and take damage
        if different_role_nearby > same_role_nearby and different_role_nearby >= 2:
            # Calculate center of nearby different-role creatures
            diff_center = pygame.math.Vector2(0, 0)
            count = 0
            for other in nearby:
                if other is not self and other.get_role() != my_role:
                    d = self.pos.distance_to(other.pos)
                    if d < ROLE_GROUP_RADIUS:
                        diff_center += other.pos
                        count += 1
            if count > 0:
                diff_center /= count
                away_dir = (self.pos - diff_center)
                if away_dir.length() > 1:
                    repulsion = away_dir.normalize() * REPULSION_STRENGTH * min(1.6, (different_role_nearby - same_role_nearby) * 0.25)
                    self.vel += repulsion

            # Meaningful energy damage while in hostile territory
            damage = INTER_ROLE_DAMAGE * (1.0 + (different_role_nearby - same_role_nearby) * 0.08)
            self.energy = max(0, self.energy - damage)

        # === Affiliation-based Relative Pull / Repulsion (v537) ===
        # Creatures are pulled toward high positive bonds and pushed from negative ones.
        # Strength scales with bond level.
        if self.affiliations:
            pull = pygame.math.Vector2(0, 0)
            for other_id, score in list(self.affiliations.items()):
                # Find the actual creature object (simple linear search for now)
                for other in nearby:
                    if id(other) == other_id:
                        if score > 5:
                            direction = (other.pos - self.pos)
                            if direction.length() > 1:
                                strength = min(1.8, (score / 60.0))
                                pull += direction.normalize() * strength * 0.6
                        elif score < -8:
                            direction = (self.pos - other.pos)
                            if direction.length() > 1:
                                strength = min(1.5, (abs(score) / 70.0))
                                pull += direction.normalize() * strength * 0.55
                        break
            if pull.length() > 0.1:
                self.vel += pull

        # === Phase 2: Follow Macro Drive + Upgrades ===
        if self.in_macro is not None:
            macro = self.in_macro
            if macro.members:
                target_vel = macro.vel + macro.drive
                if target_vel.length() > 0.1:
                    blend = 0.75
                    speed_mult = 1.0 + macro.upgrades.get("speed", 0)
                    self.vel = self.vel * (1.0 - blend) + target_vel.normalize() * min(target_vel.length() * speed_mult, 5.5) * blend

                # Energy efficiency upgrade
                eff = 1.0 + macro.upgrades.get("energy_efficiency", 0)
                if eff > 1.0:
                    self.energy = min(self.max_energy(), self.energy + 0.012 * (eff - 1.0))

        # === Auditory Bonding / Threat Signals (v537) ===
        # When in strong positive same-role bonds, emit "safe bonding" signal.
        # When near hostile groups, emit warning signal.
        # These can be heard at longer range.
        positive_bond_count = sum(1 for score in self.affiliations.values() if score > 25)
        if positive_bond_count >= 2 and same_role_nearby >= 3:
            # Strong positive social cluster → safe bonding signal
            intensity = 0.75 if self.in_macro is not None else 0.6
            if self.in_macro is not None:
                intensity += self.in_macro.upgrades.get("signaling", 0) * 0.4
            try:
                sound_manager.play_ethereal_signal(
                    (self.pos.x, self.pos.y),
                    emotion="content",
                    intensity=min(2.0, intensity),
                    role_hint=my_role
                )
            except:
                pass
        elif different_role_nearby >= 7:
            # Near hostile group → warning signal
            try:
                sound_manager.play_ethereal_signal(
                    (self.pos.x, self.pos.y),
                    emotion="fear",
                    intensity=0.7
                )
            except:
                pass

        ext_cap = self.external_storage_capacity()

        being_attacked = any(o.current_prey is self and o.is_attacking for o in nearby)

        inputs = [
            (GREEN_POS.x - self.pos.x) / WIDTH,
            (GREEN_POS.y - self.pos.y) / HEIGHT,
            (BLUE_POS.x - self.pos.x) / WIDTH,
            (BLUE_POS.y - self.pos.y) / HEIGHT,
            (nearest_patch.pos.x - self.pos.x) / WIDTH if nearest_patch else 0.0,
            (nearest_patch.pos.y - self.pos.y) / HEIGHT if nearest_patch else 0.0,
            (nearest_patch.amount / 50.0) if nearest_patch else 0.0,
            1.0 if (nearest_patch and nearest_patch.is_strategic) else 0.0,
            self.energy / self.max_energy(),
            self.carried_biomass / max(ext_cap, 1),
            local_density,
            min(avg_nearby_biomass / 12.0, 1.0),
            min(nearby_desperate / 8.0, 1.0),
            1.0 if being_attacked else 0.0,
            1.0 if self.is_gathering() else 0.0,
            1.0 if desperate else 0.0,
            min(dist_to_green / 900, 1.0),
            min(dist_to_blue / 900, 1.0),
            patch_dist / 650 if patch_dist < 650 else 1.0,
            self.memory_food.length(),
            self.memory_threat.length(),
            min(max((self.energy - 60) / 80, -1.0), 1.0),
            self.sensor_count() / 6.0,
            len(self.modules) / 12.0,
            self.carry_capacity() / 20.0,
            1.0 if role == "courier" else 0.0,
            1.0 if self.struggle_cooldown <= 0 and self.energy > 35 else 0.0,
            # Phase B inputs: Threat & Social Awareness
            min(nearby_desperate / 6.0, 1.0),     # Nearby predator density
            min(ally_count / 8.0, 1.0)            # Ally density
        ]
        self.last_inputs = np.array(inputs)

        # === Phase 1: Update Recurrent State ===
        self.recurrent_state = self.brain.update_recurrent_state(
            np.array(inputs), self.recurrent_state
        )
        self.last_recurrent_state = self.recurrent_state.copy()

        # Phase 1: Light decay + clipping on internal state for stability
        self.internal_state *= 0.995
        self.internal_state = np.clip(self.internal_state, -4.0, 4.0)
        if np.any(np.isnan(self.internal_state)) or np.any(np.isinf(self.internal_state)):
            self.internal_state = np.zeros_like(self.internal_state)

        # Append recurrent and internal state for main network
        full_inputs = inputs + self.recurrent_state.tolist() + self.internal_state.tolist()

        # Performance optimization: Skip full neural update for non-critical creatures when crowded
        if do_full_neural_update or desperate:
            nn_out = self.brain.forward_with_memory(
                np.array(inputs), self.recurrent_state, self.internal_state, role=self.get_role()
            )
            self.last_nn_outputs = nn_out.copy()
        else:
            # Use previous outputs (cheap approximation)
            if self.last_nn_outputs is not None and len(self.last_nn_outputs) >= 6:
                nn_out = self.last_nn_outputs
            else:
                nn_out = np.zeros(6)

        desired_dir = pygame.math.Vector2(nn_out[0], nn_out[1])

        # === Role-Specific Movement Styles ===
        role = self.get_role()
        if role == "forager":
            # Foragers move more deliberately (slightly slower, smoother turns)
            desired_dir *= 0.92
        elif role == "scout":
            # Scouts are faster and more responsive
            desired_dir *= 1.12
        elif role == "courier":
            # Couriers have inertia when heavily loaded
            load_ratio = self.carried_biomass / max(self.external_storage_capacity(), 1)
            if load_ratio > 0.5:
                desired_dir *= (1.0 - (load_ratio - 0.5) * 0.35)
        elif self.is_desperate():
            # Desperate creatures move jittery and inefficiently
            desired_dir *= 1.08
            if random.random() < 0.15:
                desired_dir = desired_dir.rotate(random.uniform(-35, 35))

        deposit_intensity = nn_out[2]
        social_drive = nn_out[3]
        exploration_drive = nn_out[4]
        if self.post_kill_exploration_timer > 0:
            exploration_drive = max(exploration_drive, 0.85)

        # Injured creatures have slightly higher drive to seek food/social healing
        if self.is_injured():
            exploration_drive = min(1.0, exploration_drive + 0.08)
            social_drive = min(1.0, social_drive + 0.06)

        # Tiny exploration push from correct food at correct time
        t = get_time_of_day()
        day = is_day(t)
        g_dist = self.pos.distance_to(GREEN_POS)
        b_dist = self.pos.distance_to(BLUE_POS)

        if day and g_dist < 160:
            exploration_drive = min(1.0, exploration_drive + 0.06)
        elif not day and b_dist < 160:
            exploration_drive = min(1.0, exploration_drive + 0.06)

        hunting_persistence = nn_out[5]

        desperate = self.is_desperate()

        # =====================================================================
        # HUNT MODE (Improved)
        # =====================================================================
        if desperate and self.current_prey and self.current_prey in creatures:
            to_prey = (self.current_prey.pos - self.pos)
            dist_to_prey = to_prey.length()

            if dist_to_prey > 0.5:
                desired_dir = to_prey.normalize() * 45.0
                self.vel = to_prey.normalize() * max(7.5, self.speed() * 3.0)
                exploration_drive = 0.0
                social_drive = 0.0
                deposit_intensity = 0.0

            # Contact-based damage (module-scaled)
            if dist_to_prey < 25:
                prey = self.current_prey
                predator_power = max(1, self.effective_module_count())
                prey_undamaged = sum(1 for m in prey.modules if not m.damaged)

                # === Special Rule: Predator vs Predator = Insta-Kill ===
                if desperate and prey.is_desperate():
                    # Insta-kill the other predator
                    try:
                        creatures.remove(prey)
                    except ValueError:
                        pass
                    if selected_creature is prey:
                        selected_creature = None

                    self.energy = min(self.max_energy(), self.energy + (self.max_energy() * 0.5))
                    if prey.modules:
                        new_type = random.choice([m.type for m in prey.modules])
                        self.modules.append(Module(new_type))

                    self.brain.update_importance()
                    for imp in [self.brain.importance_w1, self.brain.importance_w2, self.brain.importance_w3]:
                        imp *= 1.08

                    self.post_kill_repro_lock = 3600
                    self.reproduction_cooldown = 600
                    self.kills += 1
                    sound_manager.play_death_pop()
                    self.current_prey = None
                    # Skip normal damage since it's an insta-kill
                else:
                    # Normal prey damage (non-predator or non-desperate attacker)
                    # Module damage system
                    if prey.modules and random.random() < 0.65:
                        undamaged_modules = [m for m in prey.modules if not m.damaged]
                        if undamaged_modules:
                            target_module = random.choice(undamaged_modules)
                            target_module.damaged = True

                    # Core damage (energy)
                    core_damage = max(8, predator_power * 3.5)
                    if prey_undamaged == 0:
                        core_damage *= 2.2

                    prey.energy -= core_damage

                    if prey.energy <= 0 or prey_undamaged == 0:
                        # Successful kill
                        try:
                            creatures.remove(prey)
                        except ValueError:
                            pass
                        if selected_creature is prey:
                            selected_creature = None

                        self.energy = min(self.max_energy(), self.energy + (self.max_energy() * 0.5))
                        if prey.modules:
                            new_type = random.choice([m.type for m in prey.modules])
                            self.modules.append(Module(new_type))

                        self.brain.update_importance()
                        for imp in [self.brain.importance_w1, self.brain.importance_w2, self.brain.importance_w3]:
                            imp *= 1.05

                        self.post_kill_repro_lock = 3600
                        self.reproduction_cooldown = 600
                        self.kills += 1
                        sound_manager.play_death_pop()
                        self.current_prey = None

        else:
            best_target = None
            best_score = -99999

            # Only desperate creatures act as predators.
            # Non-desperate creatures should not aggressively acquire targets.
            if desperate:
                for o in nearby:
                    if o is self: continue
                    d = self.pos.distance_to(o.pos)
                    if d > query_radius: continue

                    # Predator targeting logic (fixed):
                    # Only give high priority to other predators if they are currently attacking a NON-predator.
                    if desperate:
                        distance_penalty = d ** 1.6 * 9.0
                        module_penalty = len(o.modules) * 28
                        score = 1300 - distance_penalty - module_penalty

                        # Only prioritize predators that are actively hunting normal prey
                        if o.is_desperate() and o.is_attacking and o.current_prey is not None:
                            if not o.current_prey.is_desperate():  # Only if target is attacking a normal creature
                                score += 750
                            else:
                                score -= 200  # Avoid chaining predator-predator locks
                        elif o.is_desperate():
                            score -= 450  # Strongly deprioritize idle predators

                        if len(o.modules) <= 3:
                            score += 160
                    else:
                        if o.is_desperate():
                            score = 600 - (d * 3.5)
                            score -= len(o.modules) * 20
                        else:
                            score = 200 - (d * 4.0)

                    if o.is_attacking and o.current_prey is not None:
                        score += 300

                    nearby_count = self.count_nearby(radius=90)
                    if nearby_count >= 5:
                        score -= 220

                    if desperate:
                        if nearby_count == 0:
                            score += 650
                        elif nearby_count == 1:
                            score += 420
                        elif nearby_count <= 3:
                            score += 180

                    if score > best_score:
                        best_score = score
                        best_target = o

            if best_target:
                if desperate:
                    self.current_prey = best_target
                    self.attack_timer = max(0, self.attack_timer - 8)
                else:
                    if self.current_prey and self.current_prey in creatures:
                        current_d = self.pos.distance_to(self.current_prey.pos)
                        new_d = self.pos.distance_to(best_target.pos)
                        if best_score > 120 and new_d < current_d * 0.7:
                            self.current_prey = best_target
                            self.attack_timer = 0
                    else:
                        self.current_prey = best_target
                        self.attack_timer = 0

            # Clean up invalid predator targets (only keep if still attacking a non-predator)
            if self.current_prey and self.current_prey in creatures:
                if self.current_prey.is_desperate():
                    target_is_valid = (
                        self.current_prey.is_attacking and 
                        self.current_prey.current_prey is not None and 
                        not self.current_prey.current_prey.is_desperate()
                    )
                    if not target_is_valid:
                        self.current_prey = None

        has_damaged_modules = any(m.damaged for m in self.modules)
        if has_damaged_modules:
            self.regenerating = True

            # Base pull toward food when injured
            dist_to_food = min(g_dist, b_dist)
            pull_strength = 0.65 if dist_to_food > 140 else 1.15
            if g_dist < b_dist:
                desired_dir = desired_dir * 0.28 + (GREEN_POS - self.pos).normalize() * pull_strength
            else:
                desired_dir = desired_dir * 0.28 + (BLUE_POS - self.pos).normalize() * pull_strength

            # Bonus healing when injured (contextual)
            heal_chance = 0.095 if self.is_gathering() else 0.014

            # Stronger healing inside main patches
            if g_dist < green_r or b_dist < blue_r:
                heal_chance *= 2.2

            # Bonus healing near same-role creatures (social healing)
            role = self.get_role()
            same_role_nearby = sum(1 for c in creatures if c is not self and c.get_role() == role and self.pos.distance_to(c.pos) < 70)
            if same_role_nearby >= 2:
                heal_chance *= 1.8

            if random.random() < heal_chance:
                for m in self.modules:
                    if m.damaged:
                        m.damaged = False
                        break
        else:
            self.regenerating = False

        legend_top = HEIGHT - BOTTOM_PANEL_HEIGHT - 25
        edge_force = pygame.math.Vector2(0, 0)
        margin = 52

        if self.pos.x < margin:
            dist = margin - self.pos.x
            strength = 2.9 + (dist / margin) * 4.0
            edge_force.x += dist * strength * 0.055
        if self.pos.x > WIDTH - margin:
            dist = self.pos.x - (WIDTH - margin)
            strength = 2.9 + (dist / margin) * 4.0
            edge_force.x -= dist * strength * 0.055
        if self.pos.y < margin:
            dist = margin - self.pos.y
            strength = 2.9 + (dist / margin) * 4.0
            edge_force.y += dist * strength * 0.055
        if self.pos.y > legend_top - 32:
            dist = self.pos.y - (legend_top - 32)
            strength = 3.6 + (dist / 36) * 5.0
            edge_force.y -= dist * strength * 0.065

        # When touching the outer perimeter: strong push-back + hunger nudge
        touching_wall = False
        wall_margin = 18
        if self.pos.x < wall_margin or self.pos.x > WIDTH - wall_margin or \
           self.pos.y < wall_margin or self.pos.y > legend_top - wall_margin:
            touching_wall = True

        if touching_wall:
            # Strong immediate repulsion
            to_center = pygame.math.Vector2(WIDTH/2, HEIGHT/2) - self.pos
            if to_center.length() > 0:
                self.vel += to_center.normalize() * 2.8

            # Set temporary forced eat urge (helps unstuck creatures at the boundary)
            self.forced_eat_timer = max(self.forced_eat_timer, 180)  # ~3 seconds override

            # Hunger nudge
            self.energy = max(0, self.energy - 0.8)

        if self.pos.x < 20 or self.pos.x > WIDTH - 20 or self.pos.y < 20 or self.pos.y > legend_top - 20:
            self.vel *= 0.82

        # Strengthened edge avoidance + memory return for non-desperate creatures
        if edge_force.length() > 0.1:
            edge_weight = 0.60 if desperate else 0.48
            desired_dir = desired_dir * edge_weight + edge_force.normalize() * min(1.8, edge_force.length() * 0.032)

        # Non-desperate creatures should actively return to known food locations
        if not desperate and self.memory_food.length() > 0.08:
            mem_weight = 0.58
            desired_dir = desired_dir * (1.0 - mem_weight) + self.memory_food.normalize() * mem_weight

        # === Phase 2: Social Approach Bonus toward Rhythmic Signalers ===
        # Creatures are slightly attracted to nearby creatures who recently did rhythmic calls
        if not desperate:
            rhythmic_attraction = pygame.math.Vector2(0, 0)
            for other in nearby:
                if other is self: continue
                if other.recent_rhythmic_call > 0:
                    dist = self.pos.distance_to(other.pos)
                    if dist < 160 and dist > 5:
                        weight = 0.35 * (1.0 - (dist / 160))
                        rhythmic_attraction += (other.pos - self.pos).normalize() * weight

            if rhythmic_attraction.length() > 0.1:
                desired_dir = desired_dir * 0.85 + rhythmic_attraction.normalize() * 0.15

            # Phase 4: Light kin recognition — slight attraction to similar rhythmic lineages
            kin_attraction = pygame.math.Vector2(0, 0)
            for other in nearby:
                if other is self: continue
                if hasattr(other, 'lineage_rhythm_signature'):
                    similarity = 1.0 - abs(self.lineage_rhythm_signature - other.lineage_rhythm_signature)
                    if similarity > 0.6:
                        dist = self.pos.distance_to(other.pos)
                        if dist < 140 and dist > 0.5:  # Prevent zero vector
                            weight = 0.2 * similarity * (1.0 - dist / 140)
                            direction = (other.pos - self.pos)
                            if direction.length() > 0:
                                kin_attraction += direction.normalize() * weight

            if kin_attraction.length() > 0.1:
                desired_dir = desired_dir * 0.9 + kin_attraction.normalize() * 0.1

            # === Phase 5: Group Rhythmic Coordination Bonus ===
            # When multiple rhythmic signalers are close, they get a small shared benefit
            rhythmic_nearby = sum(1 for o in nearby if o is not self and o.recent_rhythmic_call > 0)
            if rhythmic_nearby >= 2:
                # Small coordination / comfort bonus
                self.social_need = max(0.0, self.social_need - 0.008)
                if random.random() < 0.15:
                    self.energy = min(self.max_energy(), self.energy + 0.3)

            # === Update Emotional State ===
            self.update_emotions(nearby, desperate)

        if desired_dir.length() < 0.11:
            desired_dir = pygame.math.Vector2(random.uniform(-0.55, 0.55), random.uniform(-0.55, 0.55))

        # Forced eat override after hitting wall (temporary strong food-seeking)
        if self.forced_eat_timer > 0:
            if self.memory_food.length() > 0.05:
                desired_dir = desired_dir * 0.25 + self.memory_food.normalize() * 0.75
            else:
                # Fallback: strong pull toward nearest main food
                target = GREEN_POS if g_dist < b_dist else BLUE_POS
                desired_dir = desired_dir * 0.3 + (target - self.pos).normalize() * 0.7

        # === Launch Momentum from Inner Green Zone ===
        if self.launch_momentum > 0:
            self.launch_momentum -= 1
            # Maintain strong velocity with gradual decay
            self.vel = self.launch_velocity * (0.96 + (self.launch_momentum / 45.0) * 0.04)
            self.launch_velocity = self.vel * 0.97

            # Wall bounce during launch momentum (same style as micro-patches)
            bounced = False
            if self.pos.x < 30:
                self.pos.x = 30
                self.vel.x *= -0.82
                self.launch_velocity.x *= -0.82
                bounced = True
            if self.pos.x > WIDTH - 30:
                self.pos.x = WIDTH - 30
                self.vel.x *= -0.82
                self.launch_velocity.x *= -0.82
                bounced = True
            if self.pos.y < 30:
                self.pos.y = 30
                self.vel.y *= -0.82
                self.launch_velocity.y *= -0.82
                bounced = True
            if self.pos.y > legend_top - 30:
                self.pos.y = legend_top - 30
                self.vel.y *= -0.82
                self.launch_velocity.y *= -0.82
                bounced = True

            if bounced:
                self.launch_momentum = max(8, self.launch_momentum - 6)
                try:
                    sound_manager.play_wall_bounce((self.pos.x, self.pos.y))
                except: pass
        else:
            # Normal movement when not in launch momentum
            if desired_dir.length() > 0.1:
                effective_speed = self.speed() * pack_speed_mult
                target_vel = desired_dir.normalize() * effective_speed
                self.vel = self.vel.lerp(target_vel, 0.28)
            else:
                self.vel *= 0.86

        self.pos += self.vel
        self.energy = min(self.max_energy(), self.energy - self.energy_drain())

        # HARD BOUNDARIES for all Creatures (v653)
        self.pos.x = max(SIM_LEFT, min(SIM_RIGHT, self.pos.x))
        self.pos.y = max(SIM_TOP, min(SIM_BOTTOM, self.pos.y))

        # Strong edge repulsion
        edge_force = pygame.math.Vector2(0, 0)
        edge_margin = 50
        if self.pos.x < SIM_LEFT + edge_margin:
            edge_force.x += (SIM_LEFT + edge_margin - self.pos.x) * 0.16
        if self.pos.x > SIM_RIGHT - edge_margin:
            edge_force.x -= (self.pos.x - (SIM_RIGHT - edge_margin)) * 0.16
        if self.pos.y < SIM_TOP + edge_margin:
            edge_force.y += (SIM_TOP + edge_margin - self.pos.y) * 0.16
        if self.pos.y > SIM_BOTTOM - edge_margin:
            edge_force.y -= (self.pos.y - (SIM_BOTTOM - edge_margin)) * 0.16

        if edge_force.length() > 0.05:
            self.vel += edge_force
            self.vel *= 0.90

        # === Module Tiering: 3 same type/tier → 1 higher tier ===
        if self.module_combine_cooldown <= 0 and len(self.modules) >= 3:
            from collections import defaultdict
            groups = defaultdict(list)
            for mod in self.modules:
                if not mod.damaged:
                    groups[(mod.type, mod.tier)].append(mod)

            for (mtype, tier), mods_list in list(groups.items()):
                if len(mods_list) >= 3 and tier < 5:
                    for _ in range(3):
                        if mods_list and mods_list[0] in self.modules:
                            self.modules.remove(mods_list[0])
                        if mods_list:
                            mods_list.pop(0)
                    new_mod = Module(mtype, tier=tier + 1)
                    self.modules.append(new_mod)
                    self.module_combine_cooldown = 300
                    break

        if self.module_combine_cooldown > 0:
            self.module_combine_cooldown -= 1

        if random.random() < 0.35:
            for other in nearby:
                if other is self: continue
                dist = self.pos.distance_to(other.pos)
                if dist < 95:
                    trust = 0.012
                    trust += other.sensor_count() * 0.004
                    if other.energy > 60:
                        trust += 0.008
                    if other.is_desperate():
                        trust *= 0.5
                    if other.memory_food.length() > 0.1:
                        self.memory_food = self.memory_food * (1.0 - trust) + other.memory_food * trust
                    if other.memory_threat.length() > 0.1:
                        self.memory_threat = self.memory_threat * (1.0 - trust * 0.6) + other.memory_threat * (trust * 0.6)

        # === Energy Tail System ===
        # Activation: ≥50% energy | Duration: ~2s burst | Cutoff: ≤20% | High drain + cooldown
        ext_cap = self.external_storage_capacity()

        if self.energy_tail_cooldown > 0:
            self.energy_tail_cooldown -= 1
            self.using_energy_tail = False
            self.energy_tail_active_timer = 0
        else:
            is_fleeing_predator = not self.is_desperate() and nearby_desperate > 0
            trigger_condition = not self.is_desperate() and (self.carried_biomass > (ext_cap * 0.25) or is_fleeing_predator)

            # Can only start if we have at least 50% energy
            can_start = self.energy >= self.max_energy() * 0.50

            if trigger_condition and self.energy_tail_active_timer <= 0 and can_start:
                self.energy_tail_active_timer = 120   # ~2 second burst
                self.using_energy_tail = True

            if self.energy_tail_active_timer > 0:
                self.energy_tail_active_timer -= 1
                self.using_energy_tail = True
                self.energy = max(0, self.energy - 1.25)   # Reduced sprint drain

                # Cut off if energy drops to 20% or below
                if self.energy <= self.max_energy() * 0.20:
                    self.using_energy_tail = False
                    self.energy_tail_active_timer = 0
                    self.energy_tail_cooldown = 160
                    self.post_tail_hunger_timer = 180   # Strong urge to eat

                if self.energy_tail_active_timer <= 0 and self.using_energy_tail:
                    # Normal burst end
                    self.using_energy_tail = False
                    self.energy_tail_cooldown = 200
                    self.post_tail_hunger_timer = 120
            else:
                self.using_energy_tail = False

        # Apply post-burst hunger urge (stronger attraction to food)
        if self.post_tail_hunger_timer > 0:
            self.post_tail_hunger_timer -= 1

        ext_cap = self.external_storage_capacity()
        gather_mult = 1.55 if desperate else (1.25 if self.energy < 55 else 1.0)
        if inside_green or inside_blue:
            gather_mult *= 1.15

        # Strong urge to eat after Energy Tail use
        if self.post_tail_hunger_timer > 0:
            gather_mult *= 1.6

        # Post-kill exploration + slight gathering boost
        if self.post_kill_exploration_timer > 0:
            self.post_kill_exploration_timer -= 1
        if self.recent_rhythmic_call > 0:
            self.recent_rhythmic_call -= 1
            gather_mult *= 1.25

        if GREEN_FOOD < 30 or BLUE_FOOD < 20:
            gather_mult *= 0.6

        if not desperate and self.carried_biomass < ext_cap * 0.92:
            role = self.get_role()
            forager_mult = 1.35 if role == "forager" else 1.0   # Worker caste bonus

            # Competition for shared resources inside main patches
            nearby_gatherers = 0
            for other in nearby:
                if other is not self:
                    other_g = other.pos.distance_to(GREEN_POS) < green_r
                    other_b = other.pos.distance_to(BLUE_POS) < blue_r
                    if other_g or other_b:
                        nearby_gatherers += 1

            competition_mult = 1.0 / (1.0 + 0.45 * nearby_gatherers)   # Diminishing returns

            if inside_green and GREEN_FOOD > 1.5:
                take = min(5.2 * gather_mult * forager_mult * competition_mult, GREEN_FOOD * 0.68, ext_cap - self.carried_biomass)
                self.carried_biomass += take
                GREEN_FOOD -= take
                self.lifetime_learn(0.6)
                self.brain.update_importance()
            elif inside_blue and BLUE_FOOD > 1.5:
                take = min(5.2 * gather_mult * forager_mult * competition_mult, BLUE_FOOD * 0.68, ext_cap - self.carried_biomass)
                self.carried_biomass += take
                BLUE_FOOD -= take
                self.lifetime_learn(0.6)
                self.brain.update_importance()

        if self.carried_biomass > 0.07:
            self.carried_biomass *= 0.9985

        if desperate and self.carried_biomass > 0.09:
            eat = min(self.carried_biomass, 1.65)
            self.carried_biomass -= eat
            self.energy = min(self.max_energy(), self.energy + eat * 0.73)

        memory_write_strength = 0.0
        if inside_green:
            closeness = max(0.3, 1.0 - (g_dist / green_r))
            memory_write_strength = 0.65 * closeness
        elif inside_blue:
            closeness = max(0.3, 1.0 - (b_dist / blue_r))
            memory_write_strength = 0.65 * closeness

        if self.is_gathering() and self.carried_biomass > 0.8:
            memory_write_strength = max(memory_write_strength, 0.85)

        if memory_write_strength > 0.1:
            target_pos = GREEN_POS if g_dist < b_dist else BLUE_POS
            direction = target_pos - self.pos
            if direction.length() > 0:
                new_mem = direction.normalize() * memory_write_strength
                self.memory_food = self.memory_food * 0.6 + new_mem * 0.4

        if self.last_attacked_by is not None:
            for o in nearby:
                if o.name == self.last_attacked_by:
                    threat_dir = o.pos - self.pos
                    if threat_dir.length() > 0:
                        self.memory_threat = threat_dir.normalize() * 0.78
                    break
            self.last_attacked_by = None

        ext_cap = self.external_storage_capacity()
        deposit_chance = 0.0042
        if deposit_intensity > 0.22 and self.carried_biomass > (ext_cap * 0.26):
            deposit_chance = 0.016 + (deposit_intensity * 0.035)
            if desperate:
                deposit_chance *= 0.1

        dist_from_food = min(dist_to_green, dist_to_blue)

        if self.deposit_cooldown <= 0 and self.carried_biomass > (ext_cap * 0.24) and random.random() < deposit_chance:
            # Staggered depositing: avoid dropping micro-patches too close to existing ones near main patches
            # This creates natural "take turns" behavior around the perimeter
            too_close = False
            if dist_from_food < 220:  # Only apply near main patches
                for p in micro_patches:
                    if self.pos.distance_to(p.pos) < 38:
                        too_close = True
                        break

            if too_close:
                # Greatly reduce chance if another micro-patch is already nearby (take turns)
                if random.random() < 0.25:
                    too_close = False  # Occasionally allow it anyway

            if not too_close:
                deposit = min(self.carried_biomass, 2.1)
                self.carried_biomass -= deposit
                far_bonus = 1.0
                is_strategic = False
                if dist_from_food > 280:
                    far_bonus = 2.0
                    is_strategic = True
                elif dist_from_food > 180:
                    far_bonus = 1.35

                created = MicroPatch(self.pos.x + random.uniform(-4, 4), self.pos.y + random.uniform(-4, 4), deposit * 4.9 * far_bonus, is_strategic=is_strategic)
                micro_patches.append(created)
                patch_grid.insert(created, created.pos.x, created.pos.y)

                energy_gain = 1.25 * far_bonus
                if is_strategic:
                    energy_gain *= 1.04
                self.energy = min(self.max_energy(), self.energy + energy_gain - 2.8)
                self.deposit_cooldown = 52 + int(deposit * 4.8)
                self.lifetime_learn(1.0)

        # CarryTrail creation removed for performance

        # === Defensive sanitization (prevents invalid blit / NaN positions) ===
        if not (math.isfinite(self.pos.x) and math.isfinite(self.pos.y)):
            self.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        if not (math.isfinite(self.vel.x) and math.isfinite(self.vel.y)):
            self.vel = pygame.math.Vector2(0, 0)

        # Soft clamp to simulation bounds (with margin)
        self.pos.x = max(SIM_LEFT - 50, min(SIM_RIGHT + 50, self.pos.x))
        self.pos.y = max(SIM_TOP - 50, min(SIM_BOTTOM + 50, self.pos.y))

        # Velocity clamp (prevents runaway acceleration)
        if self.vel.length() > 28:
            self.vel = self.vel.normalize() * 28

    def draw(self, s, is_selected=False):
        role = self.get_role()
        desperate = self.is_desperate()

        if role == "forager": core_size = 7.5
        elif role == "scout": core_size = 7.0
        elif role == "courier": core_size = 8.0
        elif role == "sensor": core_size = 6.5
        else: core_size = 6.5

        # Blit pre-rendered surface (major performance win)
        surf = get_creature_surface(role, desperate, core_size)
        off = surf.get_width() // 2

        # Defensive blit (prevents crash on invalid positions)
        try:
            bx = int(self.pos.x) - off
            by = int(self.pos.y) - off
            if  -200 < bx < WIDTH + 200 and -200 < by < HEIGHT + 200:
                s.blit(surf, (bx, by))
        except (ValueError, OverflowError):
            pass  # Skip drawing this frame if position is still bad

        # Only draw cyan tractor beam for desperate predators.
        # No white or light lines between creatures under any circumstances.
        if desperate and self.current_prey and self.current_prey in creatures:
            prey = self.current_prey
            pygame.draw.line(s, (0, 255, 200), (int(self.pos.x), int(self.pos.y)), (int(prey.pos.x), int(prey.pos.y)), 1)

        # Communication visuals removed per request

        # Only show highlight on selected creature (no cyan circle on normal creatures)
        if is_selected:
            pulse = 5 + math.sin(pygame.time.get_ticks() / 200.0) * 2
            pygame.draw.circle(s, SELECT_HIGHLIGHT, (int(self.pos.x), int(self.pos.y)), int(core_size + 10 + pulse), 2)

        if self.regenerating:
            glow = 7 + math.sin(pygame.time.get_ticks() / 100.0) * 3
            pygame.draw.circle(s, REGEN_COLOR, (int(self.pos.x), int(self.pos.y)), int(core_size + glow), 2)

        if self.using_energy_tail:
            # Basic line with jetpack-style short bursts (pulsing on/off)
            if self.vel.length() > 0.1:
                back_dir = -self.vel.normalize()
            else:
                back_dir = pygame.math.Vector2(0, 0.9)

            # Pulsing: visible for short bursts, then off (feels like controlled jets)
            cycle = (pygame.time.get_ticks() // 400) % 2
            if cycle == 0:
                start = self.pos + back_dir * 6.5
                length = 15
                end = start + back_dir * length
                pygame.draw.line(s, (100, 255, 255), (int(start.x), int(start.y)), (int(end.x), int(end.y)), 2)

        for i, m in enumerate(self.modules):
            ang = (i / max(len(self.modules), 1)) * 6.28
            off = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * 9
            size = m.get_size()
            pygame.draw.circle(s, m.get_color(), (int(self.pos.x) + int(off.x), int(self.pos.y) + int(off.y)), size)

        ext_cap = self.external_storage_capacity()
        if self.carried_biomass > 0.07:
            carry_ratio = min(self.carried_biomass / ext_cap, 1.0)
            carry_size = 3.5 + (carry_ratio * 5.2)
            glow_size = carry_size + 4.0 + math.sin(pygame.time.get_ticks() / 180.0) * 0.9
            pygame.draw.circle(s, CARRY_GLOW_COLOR, (int(self.pos.x), int(self.pos.y - 8)), int(glow_size), 2)
            pygame.draw.circle(s, CARRY_COLOR, (int(self.pos.x), int(self.pos.y - 8)), int(carry_size))

    def can_reproduce(self):
        if self.reproduction_cooldown > 0:
            return False
        if self.post_kill_repro_lock > 0:
            return False

        # Reproduction bonus when in correct patch at correct time
        t = get_time_of_day()
        day = is_day(t)
        g_dist = self.pos.distance_to(GREEN_POS)
        b_dist = self.pos.distance_to(BLUE_POS)
        green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
        blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))

        if (day and g_dist < green_r) or (not day and b_dist < blue_r):
            # On correct patch at correct time → much higher chance to reproduce
            if random.random() < 0.65:   # Strong boost
                return True

        # New condition: must be near other creatures or food to reproduce
        near_others = False
        near_food = False

        # Check proximity to other non-desperate creatures using spatial grid
        nearby_others = creature_grid.query(self.pos.x, self.pos.y, 140)
        same_role_count = 0
        for other in nearby_others:
            if other is not self and not other.is_desperate():
                near_others = True
                if other.get_role() == self.get_role():
                    same_role_count += 1

        # Check proximity to food nodes or active MicroPatches
        g_dist = self.pos.distance_to(GREEN_POS)
        b_dist = self.pos.distance_to(BLUE_POS)
        if g_dist < 160 or b_dist < 160:
            near_food = True
        else:
            for p in micro_patches:
                if self.pos.distance_to(p.pos) < p.radius + 30:
                    near_food = True
                    break

        if not (near_others or near_food):
            return False

        # Proximity-based reproduction boost for non-Forager roles
        # (encourages same-role clustering for reproduction)
        role = self.get_role()
        if role != "forager" and same_role_count >= 2:
            chance = min(0.32, 0.06 + (same_role_count * 0.065))
            if random.random() < chance:
                return True

        bonus = 0.0
        ext_cap = self.external_storage_capacity()
        if ext_cap > 0:
            carry_ratio = self.carried_biomass / ext_cap
            if carry_ratio > 0.6:
                bonus = 0.08
        return self.energy > self.max_energy() * (0.75 - bonus)

    def reproduce(self):
        global generation
        pop = len(creatures)
        # Stronger energy cost when population is high (helps keep it around 450-550)
        if pop > 550:
            self.energy *= max(0.25, 0.45 - population_pressure * 0.15)
        elif pop > 480:
            self.energy *= 0.48
        elif pop > 380:
            self.energy *= 0.55
        else:
            self.energy *= 0.60

        self.offspring_count += 1
        self.reproduction_cooldown = REPRODUCTION_COOLDOWN
        self.preparing_to_reproduce = False

        # === Phase 1: Reproduction Bias on Rhythm ===
        # Creatures that recently produced rhythmic calls near others get a small advantage
        if self.recent_rhythmic_call > 0:
            nearby_count = self.count_nearby(radius=140)
            if nearby_count >= 2:
                # Small but meaningful bonus: reduced cooldown + slight energy benefit
                self.reproduction_cooldown = max(60, int(self.reproduction_cooldown * 0.65))
                self.energy = min(self.max_energy(), self.energy + 8)
                self.lifetime_learn(0.6)

        # Phase 2: Update importance + stronger boost for successful reproduction
        self.brain.update_importance()
        # Stronger importance boost to help successful lineages protect useful structure
        for imp in [self.brain.importance_w1, self.brain.importance_w2, self.brain.importance_w3]:
            imp *= 1.04

        # Success History Modulation (v54)
        # Stronger and longer-lasting boost after successful reproduction
        self.brain.struct_add_chance = min(0.35, self.brain.struct_add_chance * 1.08)
        self.brain.recent_success_boost = min(0.10, self.brain.recent_success_boost + 0.04)

        # Light natural decay
        self.brain.struct_add_chance = max(0.04, self.brain.struct_add_chance * 0.985)
        self.brain.struct_prune_chance = max(0.04, self.brain.struct_prune_chance * 0.985)

        # Hard rule: only one offspring per reproduction
        new_creatures = []

        new_modules = [Module(m.type) for m in self.modules]

        mutation_roll = random.random()

        if mutation_roll < 0.08:
            choices = ["harvester", "sensor", "mover", "storage", "efficient", "armor"]
            weights = [1, 1, 1, 1.6, 1, 1]

            # Light heritable caste bias for worker lineages
            parent_role = self.get_role()
            if parent_role == "forager":
                weights[0] += 0.8  # Bias toward harvester
            elif parent_role == "courier":
                weights[3] += 0.8  # Bias toward storage

            new_modules.append(Module(random.choices(choices, weights=weights, k=1)[0]))
        elif mutation_roll < 0.10:
            if len(new_modules) > 0:
                new_modules.pop(random.randint(0, len(new_modules) - 1))
        elif mutation_roll < 0.27:
            choices = ["harvester", "sensor", "mover", "storage", "efficient", "armor"]
            weights = [1, 1, 1, 1.5, 1, 1]

            parent_role = self.get_role()
            if parent_role == "forager":
                weights[0] += 0.8
            elif parent_role == "courier":
                weights[3] += 0.8

            new_modules.append(Module(random.choices(choices, weights=weights, k=1)[0]))

        new_brain = self.brain.copy()
        new_brain.mutate()

        # Ancestral Signature + Fading (v135 - Final step of Option A)
        ancestral_influence = (getattr(self, 'ancestral_timbre', 0.5) - 0.5) * 0.55
        new_brain.voice_timbre = np.clip(new_brain.voice_timbre + ancestral_influence, 0.1, 0.9)

        # Accumulate lineage memory strength
        if getattr(self, 'recent_success_boost', 0.0) > 0.0:
            self.lineage_memory_strength = min(0.28, getattr(self, 'lineage_memory_strength', 0.0) + 0.018)

        # Lineage Memory + Fitness Link + Light Integration (v162 return to main track)
        lineage_fitness = getattr(self, 'lineage_memory_strength', 0.0) * 0.8
        if lineage_fitness > 0.05:
            self.add_chance = min(0.6, self.add_chance + lineage_fitness * 0.04)

        # Lineage Integration (Stage 5.1)
        lineage_strength = getattr(self, 'lineage_memory_strength', 0.0)

        if lineage_strength > 0.10:
            # Strong lineages are slightly less desperate and more stable
            self.desperation = max(0.0, self.desperation - 0.02)
            self.exploration_need = max(0.0, self.exploration_need - 0.012)

        if lineage_strength > 0.18:
            # Very successful lineages gain a small social/cooperative bias
            self.social_need = max(0.0, self.social_need - 0.015)
            self.add_chance = min(0.65, self.add_chance + 0.01)

        # Role Behavioral Differentiation (Stage 5.1)
        role = self.get_role()

        if role == "scout":
            self.exploration_need = max(0.0, self.exploration_need - 0.01)
        elif role == "forager":
            self.hunger = max(0.0, self.hunger - 0.008)
        elif role == "sensor":
            self.social_need = max(0.0, self.social_need - 0.01)

        # Module Behavioral Influence (Stage 5.1)
        has_efficient = any(m.type == "efficient" for m in self.modules)
        has_armor = any(m.type == "armor" for m in self.modules)
        has_storage = any(m.type == "storage" for m in self.modules)

        if has_efficient:
            self.hunger = max(0.0, self.hunger - 0.006)
        if has_armor:
            self.desperation = max(0.0, self.desperation - 0.01)
        if has_storage:
            self.exploration_need = max(0.0, self.exploration_need - 0.008)

        # Needs System Stabilization (Stage 5.1)
        self.hunger = max(0.0, self.hunger * 0.995)
        self.desperation = max(0.0, self.desperation * 0.992)
        self.exploration_need = max(0.0, self.exploration_need * 0.993)
        self.social_need = max(0.0, self.social_need * 0.994)

        # Energy & Reproduction Stability (Stage 5.1)
        if self.energy < 40:
            self.energy_drain_modifier = 0.92
        else:
            self.energy_drain_modifier = 1.0

        if self.offspring_count > 3:
            self.reproduction_success_bonus = min(0.08, self.offspring_count * 0.015)

        # Low Energy Behavior (Stage 5.1)
        if self.energy < 25:
            self.desperation = min(1.0, self.desperation + 0.015)
            self.exploration_need = max(0.0, self.exploration_need - 0.01)

        # Local Awareness Begin (Stage 5.2)
        nearby_count = self.count_nearby(radius=120)
        if nearby_count >= 4:
            # Slight social pull when in groups
            self.social_need = max(0.0, self.social_need - 0.008)
        if nearby_count <= 1 and self.energy > 50:
            # Slightly more exploratory when alone
            self.exploration_need = min(1.0, self.exploration_need + 0.006)

        # Nearby Role Awareness (Stage 5.2)
        same_role_nearby = self.count_nearby_role(self.get_role(), radius=110, creatures_list=creatures)
        if same_role_nearby >= 2:
            # Slight comfort/presence boost when near same role
            self.desperation = max(0.0, self.desperation - 0.005)

        # Density Awareness (Stage 5.2)
        if nearby_count >= 6:
            # In dense areas, slightly reduce exploration (more social)
            self.exploration_need = max(0.0, self.exploration_need - 0.01)
        elif nearby_count <= 2:
            # In sparse areas, slightly increase exploration
            self.exploration_need = min(1.0, self.exploration_need + 0.008)

        # Desperate Creature Awareness (Stage 5.2)
        desperate_nearby = sum(1 for c in creatures if c is not self and c.is_desperate() and self.pos.distance_to(c.pos) < 100)
        if desperate_nearby >= 1:
            # Slight avoidance / caution when near desperate creatures
            self.exploration_need = min(1.0, self.exploration_need + 0.01)

        # Local Module Awareness (Stage 5.2)
        high_module_nearby = sum(1 for c in creatures if c is not self and len(c.modules) >= 15 and self.pos.distance_to(c.pos) < 90)
        if high_module_nearby >= 1:
            # Slight social interest near high-module creatures
            self.social_need = max(0.0, self.social_need - 0.006)

        # Memory & Social Pull (Stage 5.2)
        # Slight pull toward remembered food locations when not desperate
        if not self.is_desperate() and self.memory_food.length() > 5:
            dist_to_memory = self.pos.distance_to(self.memory_food)
            if dist_to_memory > 80:
                self.exploration_need = max(0.0, self.exploration_need - 0.005)

        # Similar Module Awareness (Stage 5.2)
        similar_module_nearby = sum(1 for c in creatures 
                                    if c is not self 
                                    and abs(len(c.modules) - len(self.modules)) <= 3 
                                    and self.pos.distance_to(c.pos) < 85)
        if similar_module_nearby >= 2:
            # Slight comfort when near creatures with similar complexity
            self.social_need = max(0.0, self.social_need - 0.005)

        # Threat Awareness (Stage 5.2)
        predators_nearby = sum(1 for c in creatures if c is not self and c.is_desperate() and self.pos.distance_to(c.pos) < 95)
        if predators_nearby >= 1:
            # Increase caution/exploration when near potential predators
            self.exploration_need = min(1.0, self.exploration_need + 0.012)
            self.desperation = max(0.0, self.desperation - 0.004)  # Slight urgency

        # Group Comfort (Stage 5.2)
        if nearby_count >= 5:
            # Being in a decent-sized group provides slight comfort
            self.desperation = max(0.0, self.desperation - 0.008)

        # Stage 5.2 awareness summary effect
        if nearby_count >= 3:
            # General presence comfort in small groups
            self.social_need = max(0.0, self.social_need - 0.003)

        # Contextual Signaling (Stage 5.3)
        signal_boost = 0.0

        # More signaling near food
        if self.memory_food.length() > 10 and self.pos.distance_to(self.memory_food) < 120:
            signal_boost += 0.18

        # More signaling when desperate or low energy
        if self.desperation > 0.55 or self.energy < 35:
            signal_boost += 0.22

        # Slight reduction in signaling when very comfortable in groups
        if self.social_need < 0.3 and nearby_count >= 5:
            signal_boost -= 0.08

        self.signal_tendency = max(0.2, min(1.0, 0.35 + signal_boost))

        # Signal Strength (Stage 5.3)
        # Stronger behavioral impact from signal_tendency
        if self.signal_tendency > 0.55:
            self.exploration_need = min(1.0, self.exploration_need + 0.012)
            self.social_need = min(1.0, self.social_need + 0.01)

        if self.signal_tendency > 0.75:
            # Very high signaling creatures are more active overall
            self.desperation = max(0.0, self.desperation - 0.005)

        # Role-based social boost (safe version)
        role = self.get_role()
        similar_nearby = sum(1 for c in creatures if c is not self and c.get_role() == role and self.pos.distance_to(c.pos) < 80)
        if similar_nearby >= 3:
            self.social_need = min(1.0, self.social_need + 0.01)

        if self.signal_tendency > 0.6:
            self.exploration_need = min(1.0, self.exploration_need + 0.01)
            self.social_need = min(1.0, self.social_need + 0.008)

        # Eerie Presence (Stage 12.2)
        # Deep system overlap creates moments of surprising, alien coherence
        role = self.get_role()
        same_role_nearby = sum(1 for c in creatures if c is not self and c.get_role() == role and self.pos.distance_to(c.pos) < 70)
        nearby_signalers = sum(1 for c in creatures if c is not self and getattr(c, 'signal_tendency', 0) > 0.5 and self.pos.distance_to(c.pos) < 80)

        if same_role_nearby >= 5 and nearby_signalers >= 3:
            # Strong eerie presence / alien coherence
            self.social_need = min(1.0, self.social_need + 0.038)
            self.exploration_need = min(1.0, self.exploration_need + 0.012)

            # "It feels more than the sum of its parts"
            if self.desperation > 0.08:
                self.desperation = max(0.0, self.desperation - 0.004)

        # Signal Refinement (Stage 5.3)
        # More nuanced signaling behavior
        role = self.get_role()

        if role == "scout" and self.exploration_need > 0.55:
            self.signal_tendency = min(1.0, self.signal_tendency + 0.012)

        if role == "forager" and self.memory_food.length() > 6:
            if self.pos.distance_to(self.memory_food) < 90:
                self.signal_tendency = min(1.0, self.signal_tendency + 0.01)

        if role == "sensor" and nearby_count >= 3:
            self.signal_tendency = min(1.0, self.signal_tendency + 0.008)

        # Signal Persistence (carried from previous)
        if self.kills > 4:
            self.signal_tendency = min(1.0, self.signal_tendency + 0.0025)
        if self.offspring_count > 3:
            self.signal_tendency = min(1.0, self.signal_tendency + 0.002)

        # === Stage 5.1 Complete ===
        # Core stabilization finished:
        # - Lineage memory integration
        # - Role behavioral differentiation
        # - Module behavioral influence
        # - Needs system stabilization
        # - Energy & reproduction stability
        # - Low energy behavior
        # Ready to move to Stage 5.2 (Collective Awareness)

        generation += 1
        # Fixed: Much higher chance of generating a new name to prevent excessive name duplication
        if random.random() < 0.82:
            new_name = generate_name()
        else:
            new_name = self.name

        new_memory_food = self.memory_food * 0.82
        new_memory_threat = self.memory_threat * 0.82

        if new_memory_food.length() > 0.1:
            new_memory_food = new_memory_food.rotate(random.uniform(-0.4, 0.4)) * random.uniform(0.92, 1.08)
        if new_memory_threat.length() > 0.1:
            new_memory_threat = new_memory_threat.rotate(random.uniform(-0.4, 0.4)) * random.uniform(0.92, 1.08)

        # Spawn offspring well inside the hard box (v654)
        spawn_x = max(SIM_LEFT + 40, min(SIM_RIGHT - 40, self.pos.x + random.randint(-12, 12)))
        spawn_y = max(SIM_TOP + 40, min(SIM_BOTTOM - 40, self.pos.y + random.randint(-12, 12)))

        new_creature = Creature(
            spawn_x,
            spawn_y,
            new_modules,
            new_brain,
            name=new_name,
            memory_food=new_memory_food,
            memory_threat=new_memory_threat
        )

        # Only Foragers start ready to reproduce immediately
        if new_creature.get_role() == "forager":
            new_creature.reproduction_cooldown = 0
        else:
            new_creature.reproduction_cooldown = 720  # Other roles get cooldown

        # === Phase 4: Stronger Lineage Memory for Rhythm ===
        # Offspring inherit a clearer bias toward the parent's rhythmic style
        lineage_rhythm_bias = 0.22
        new_creature.signal_tendency = np.clip(
            self.signal_tendency * (1 - lineage_rhythm_bias) + 
            self.signal_tendency * lineage_rhythm_bias + np.random.normal(0, 0.035),
            0.2, 1.0
        )

        # Small kin recognition effect: slight preference for similar rhythmic lineages
        new_creature.lineage_rhythm_signature = self.signal_tendency  # Store parent's rhythmic tendency

        # Pass fading ancestral signature
        parent_ancestral = getattr(self, 'ancestral_timbre', 0.5)
        new_creature.ancestral_timbre = max(0.15, min(0.85, parent_ancestral * 0.91 + (self.brain.voice_timbre * 0.09)))

        # === Phase A: Lineage Tracking ===
        new_creature.parent_name = self.name
        self.children_names.append(new_name)

        # === Phase 1: Initialize recurrent and internal state ===
        new_creature.recurrent_state = new_brain.init_recurrent_state()
        new_creature.internal_state = new_brain.init_internal_state() * 0.65 + np.random.uniform(-0.2, 0.2, 6)

        self.offspring_names.append(new_name)
        if len(self.offspring_names) > 4:
            self.offspring_names.pop(0)

        self.lifetime_learn(0.8)

        return new_creature

def reset_simulation():
    global creatures, GREEN_FOOD, BLUE_FOOD, WASTE, waste_particles, energy_tails, micro_patches, GREEN_GLOW, BLUE_GLOW, generation, deposit_flashes, selected_creature, start_time
    creatures = [Creature(random.randint(SIM_LEFT + 60, SIM_RIGHT - 60), random.randint(SIM_TOP + 60, SIM_BOTTOM - 60)) for _ in range(48)]
    GREEN_FOOD = 480.0
    BLUE_FOOD = 240.0
    WASTE = 0.0
    waste_particles = []
    carry_trails = []
    energy_tails = []
    micro_patches = []
    deposit_flashes = []
    GREEN_GLOW = 0
    BLUE_GLOW = 0
    generation = 0
    selected_creature = None
    start_time = time.time()
    creature_grid.clear()
    patch_grid.clear()

running = True
dragging_volume = False
dragging_wrong_patch = False
dragging_patch_push = False
dragging_pop_scaled = False   # For the population-scaled wrong patch toggle button
dragging_vortex = False       # Vortex intensity slider
selected_creature = None
child_name_rects = []   # UI Mini Phase 3
top_creature_rects = []   # UI Mini Phase 5: Clickable Top 8 regions
top_macro_rects = []        # For Top Macros list
top_predator_rects = []   # Top 8 Predators by Kills (clickable)

# Initialize the simulation on first run
reset_simulation()

while running:
# =============================================================================
# SECTION 5: MAIN GAME LOOP
# =============================================================================
# Event handling, update, and rendering happen here every frame.
# =============================================================================

    clock.tick(FPS)
    screen.fill(BLACK)

    # Compute effective wrong-patch damage multiplier for this frame
    # Even stronger ramp (manual now goes to 20x, so auto should be able to go higher too)
    pop = len(creatures)
    if POPULATION_SCALED_WRONG_PATCH:
        if pop <= 40:
            EFFECTIVE_WRONG_PATCH_MULT = 0.35
        elif pop <= 130:
            t = (pop - 40) / (130 - 40)
            EFFECTIVE_WRONG_PATCH_MULT = 0.35 + t * (6.0 - 0.35)
        elif pop <= 190:
            t = (pop - 130) / (190 - 130)
            EFFECTIVE_WRONG_PATCH_MULT = 6.0 + t * (14.0 - 6.0)
        else:
            t = min(1.0, (pop - 190) / 100.0)
            EFFECTIVE_WRONG_PATCH_MULT = 14.0 + t * (25.0 - 14.0)
    else:
        EFFECTIVE_WRONG_PATCH_MULT = WRONG_PATCH_DAMAGE_MULT

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            if e.key == pygame.K_r:
                reset_simulation()
            if e.key == pygame.K_SPACE:
                # Simple pause toggle (can be expanded)
                pass
            if e.key == pygame.K_i:
                # v705: Toggle internal ecosystem inspector
                show_internal_inspector = not show_internal_inspector
        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            legend_y = HEIGHT - BOTTOM_PANEL_HEIGHT
            if WIDTH - 190 <= mx <= WIDTH - 30 and legend_y + 78 <= my <= legend_y + 92:
                dragging_volume = True
                new_vol = (mx - (WIDTH - 190)) / 160
                sound_manager.set_master_volume(new_vol)
                continue
            # Ethereal slider click
            if WIDTH - 190 <= mx <= WIDTH - 30 and legend_y + 112 <= my <= legend_y + 122:
                sound_manager.ethereal_base = max(0.0, min(1.0, (mx - (WIDTH - 190)) / 160))
                continue
            # Chorus slider click
            if WIDTH - 190 <= mx <= WIDTH - 30 and legend_y + 138 <= my <= legend_y + 148:
                sound_manager.chorus_base = max(0.0, min(1.0, (mx - (WIDTH - 190)) / 160))
                continue
            # Birth/Death slider click
            if WIDTH - 190 <= mx <= WIDTH - 30 and legend_y + 164 <= my <= legend_y + 174:
                sound_manager.life_event_base = max(0.0, min(1.0, (mx - (WIDTH - 190)) / 160))
                continue
            # Vortex Intensity slider DISABLED (now automatic day/night cycle)
            # if 945 <= mx <= 1075 and legend_y + 55 <= my <= legend_y + 65:
            #     dragging_vortex = True
            #     raw = (mx - 945) / 130
            #     VORTEX_INTENSITY = max(-20.0, min(20.0, (raw * 40.0) - 20.0))
            #     continue
            # Wrong Patch Damage slider click (shifted down)
            if 945 <= mx <= 1075 and legend_y + 85 <= my <= legend_y + 95:
                dragging_wrong_patch = True
                raw = (mx - 945) / 130
                WRONG_PATCH_DAMAGE_MULT = max(0.35, min(20.0, raw * 20.0))
                continue
            # Main Patch Push Strength slider (controls active patch only)
            if 945 <= mx <= 1075 and legend_y + 115 <= my <= legend_y + 125:
                dragging_patch_push = True
                raw = (mx - 945) / 130
                MAIN_PATCH_PUSH_STRENGTH = max(0.0, min(11.72, raw * 11.72))
                continue
            # Population-scaled Wrong Patch toggle (shifted down)
            if 945 <= mx <= 1075 and legend_y + 143 <= my <= legend_y + 158:
                POPULATION_SCALED_WRONG_PATCH = not POPULATION_SCALED_WRONG_PATCH
                continue
            if WIDTH - 140 <= mx <= WIDTH - 30 and legend_y + 12 <= my <= legend_y + 38:
                reset_simulation()
                continue
            if WIDTH - 140 <= mx <= WIDTH - 30 and legend_y + 45 <= my <= legend_y + 71:
                sound_manager.toggle_mute()
                continue
            clicked = False

            # If popup is open, check if click landed inside it (prevent accidental deselection)
            popup_rect = None
            if selected_creature:
                popup_rect = pygame.Rect(20, 20, 520, 340)

            if popup_rect and popup_rect.collidepoint(mx, my):
                clicked = True   # Consume the click so we don't deselect

                # UI Mini Phase 3: Check for clicks on child names
                for child_name, rect in child_name_rects:
                    if rect.collidepoint(mx, my):
                        # Prefer actual children of current creature if duplicates exist
                        found = None
                        for c in creatures:
                            if c.name == child_name:
                                if c.parent_name == sel.name:
                                    found = c
                                    break
                                if found is None:
                                    found = c
                        if found:
                            selected_creature = found
                        break

                # UI Mini Phase 5: Check clicks on Top 8 list
            if not clicked:
                # UI Mini Phase 5: Click handling for Top 8 list (in legend)
                for creature_obj, rect in top_creature_rects:
                    if rect.collidepoint(mx, my):
                        selected_creature = creature_obj
                        clicked = True
                        break

                # Handle clicks on Top 8 Predators list
                for predator_obj, rect in top_predator_rects:
                    if rect.collidepoint(mx, my):
                        selected_creature = predator_obj
                        clicked = True
                        break

            if not clicked:
                for c in creatures:
                    if c.pos.distance_to(pygame.math.Vector2(mx, my)) < 22:
                        selected_creature = c
                        clicked = True
                        break

            if not clicked:
                selected_creature = None
        if e.type == pygame.MOUSEBUTTONUP:
            dragging_volume = False
            dragging_wrong_patch = False
            dragging_patch_push = False
            dragging_pop_scaled = False
            dragging_vortex = False
        if e.type == pygame.MOUSEMOTION and dragging_volume:
            mx, _ = pygame.mouse.get_pos()
            new_vol = max(0.0, min(1.0, (mx - (WIDTH - 190)) / 160))
            sound_manager.set_master_volume(new_vol)
        if e.type == pygame.MOUSEMOTION and dragging_wrong_patch:
            mx, _ = pygame.mouse.get_pos()
            raw = (mx - 945) / 130
            WRONG_PATCH_DAMAGE_MULT = max(0.35, min(20.0, raw * 20.0))
        if e.type == pygame.MOUSEMOTION and dragging_patch_push:
            mx, _ = pygame.mouse.get_pos()
            raw = (mx - 945) / 130
            MAIN_PATCH_PUSH_STRENGTH = max(0.0, min(11.72, raw * 11.72))
        # Vortex slider motion DISABLED (automatic)
        # if e.type == pygame.MOUSEMOTION and dragging_vortex:
        #     mx, _ = pygame.mouse.get_pos()
        #     raw = (mx - 945) / 130
        #     VORTEX_INTENSITY = max(-20.0, min(20.0, (raw * 40.0) - 20.0))

    creature_grid.clear()
    for c in creatures:
        creature_grid.insert(c, c.pos.x, c.pos.y)
    patch_grid.clear()
    for p in micro_patches:
        patch_grid.insert(p, p.pos.x, p.pos.y)

    pop = len(creatures)

    # Aggressive performance settings
    target_pop_min = 450
    target_pop_max = 550

    # Very aggressive throttling when population is high
    do_expensive_targeting = (pop < 250) or (random.random() < 0.25)
    do_full_neural_update = (pop < 300) or (random.random() < 0.40)

    # Soft population control
    population_pressure = max(0.0, (pop - target_pop_max) / 150.0)

    # Drawing optimization flag
    high_pop_mode = pop > 450

    # Update position arrays (module level)
    if len(creatures) > 0:
        positions_x = np.array([c.pos.x for c in creatures], dtype=np.float32)
        positions_y = np.array([c.pos.y for c in creatures], dtype=np.float32)
    else:
        positions_x = np.array([], dtype=np.float32)
        positions_y = np.array([], dtype=np.float32)

    # Use Numba-accelerated counting when available
    if NUMBA_AVAILABLE and len(positions_x) > 0:
        for i, c in enumerate(creatures):
            c.nearby_count_90 = fast_count_nearby(positions_x, positions_y, c.pos.x, c.pos.y, 90)
            c.nearby_count_110 = fast_count_nearby(positions_x, positions_y, c.pos.x, c.pos.y, 110)
            c.nearby_count_180 = fast_count_nearby(positions_x, positions_y, c.pos.x, c.pos.y, 180)
    else:
        for c in creatures:
            c.nearby_count_90 = creature_grid.count_nearby(c.pos.x, c.pos.y, 90)
            c.nearby_count_110 = creature_grid.count_nearby(c.pos.x, c.pos.y, 110)
            c.nearby_count_180 = creature_grid.count_nearby(c.pos.x, c.pos.y, 180)

    pass  # carry_trails fully removed
    for t in energy_tails[:]:
        t.update()
        if t.life <= 0: energy_tails.remove(t)
    # Precompute patch radii once per frame (more efficient)
    green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
    blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))

    for p in micro_patches[:]:
        p.update()
        if p.is_expired():
            micro_patches.remove(p)
            continue

        # Skip brown ejection patches (strict protection)
        if getattr(p, 'persistent', False) and getattr(p, 'outbound', False):
            continue
        if getattr(p, 'not_harvestable', False):
            continue  # Extra safety layer

        g_dist = p.pos.distance_to(GREEN_POS)
        b_dist = p.pos.distance_to(BLUE_POS)

        if g_dist < green_r * 0.9:
            GREEN_FOOD = min(GREEN_MAX, GREEN_FOOD + p.amount * 0.9)
            micro_patches.remove(p)
            continue
        if b_dist < blue_r * 0.9:
            BLUE_FOOD = min(BLUE_MAX, BLUE_FOOD + p.amount * 0.9)
            micro_patches.remove(p)
            continue

    for f in deposit_flashes[:]:
        f[2] -= 1.6
        if f[2] <= 0: deposit_flashes.remove(f)

    # === Vortex Visualization Particles ===
    # Spawn from outer edges, flow toward center, removed at center
    if random.random() < 0.65:  # Spawn rate
        side = random.randint(0, 3)
        # Spawn from the edges of the INTERNAL hard simulation box (v653)
        if side == 0:   # Left inner edge
            x = SIM_LEFT - 18
            y = random.randint(SIM_TOP + 15, SIM_BOTTOM - 15)
        elif side == 1: # Right inner edge
            x = SIM_RIGHT + 18
            y = random.randint(SIM_TOP + 15, SIM_BOTTOM - 15)
        elif side == 2: # Top inner edge
            x = random.randint(SIM_LEFT + 15, SIM_RIGHT - 15)
            y = SIM_TOP - 18
        else:           # Bottom inner edge
            x = random.randint(SIM_LEFT + 15, SIM_RIGHT - 15)
            y = SIM_BOTTOM + 18

        p = VortexParticle(x, y)
        # Initial velocity toward center with slight randomness
        to_center = VORTEX_CENTER - p.pos
        if to_center.length() > 0:
            p.vel = to_center.normalize() * random.uniform(1.8, 3.2)
        vortex_particles.append(p)

    # Update vortex particles - better drain behavior
    # Goal: spiral inward toward center instead of being flung outward
    green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
    blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))

    for p in vortex_particles[:]:
        to_center = VORTEX_CENTER - p.pos
        dist = to_center.length()

        if dist < 8:
            vortex_particles.remove(p)
            # v729: Vortex Rebirth - particles have a chance to become new creatures
            if random.random() < 0.35:  # 35% chance to rebirth
                spawn_x = max(SIM_LEFT + 60, min(SIM_RIGHT - 60, VORTEX_CENTER.x + random.randint(-80, 80)))
                spawn_y = max(SIM_TOP + 60, min(SIM_BOTTOM - 60, VORTEX_CENTER.y + random.randint(-80, 80)))
                new_creature = Creature(spawn_x, spawn_y)
                creatures.append(new_creature)
            continue

        # Base strong inward pull (the "drain")
        if dist > 0:
            inward_dir = to_center.normalize()
            # Stronger pull when closer to center
            inward_strength = 2.8 + (1.0 - min(1.0, dist / VORTEX_RADIUS)) * 3.5
            p.vel = p.vel * 0.92 + inward_dir * inward_strength * 0.18

        # Apply vortex swirl (tangential) only outside exempt zones
        dist_to_green = p.pos.distance_to(GREEN_POS)
        dist_to_blue = p.pos.distance_to(BLUE_POS)
        green_exempt = dist_to_green < (green_r + VORTEX_EXEMPT_RADIUS)
        blue_exempt = dist_to_blue < (blue_r + VORTEX_EXEMPT_RADIUS)

        if not (green_exempt or blue_exempt) and abs(VORTEX_INTENSITY) > 0.02 and dist > 25:
            norm_dist = min(1.0, dist / VORTEX_RADIUS)
            # Gentler tangential strength so they spiral instead of fling
            strength = abs(VORTEX_INTENSITY) * (0.9 - norm_dist * 0.6)

            # Direction based on sign
            if VORTEX_INTENSITY >= 0:
                tangent = pygame.math.Vector2(-to_center.y, to_center.x).normalize()
            else:
                tangent = pygame.math.Vector2(to_center.y, -to_center.x).normalize()

            # Add swirl but keep it balanced with inward pull
            p.vel += tangent * strength * 0.55

        # Move
        p.pos += p.vel

        # Soft speed limit so nothing flies off the map
        if p.vel.length() > 7.5:
            p.vel = p.vel.normalize() * 7.5

        # === Particle gives energy to creature on contact ===
        for c in creatures:
            if c.energy > 0 and p.pos.distance_to(c.pos) < 11:
                c.energy = min(c.max_energy(), c.energy + c.max_energy() * 0.25)
                c.reproduction_cooldown = max(0, c.reproduction_cooldown - 11)  # Picking up particles resets cooldown (final pass)
                if p in vortex_particles:
                    vortex_particles.remove(p)
                break  # Only one creature per particle per frame

    green_radius = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
    blue_radius = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))

    green_regen = 7.8
    blue_regen = 4.5

    if GREEN_FOOD < 80:
        green_regen += 10.0
    if BLUE_FOOD < 50:
        blue_regen += 6.0

    nearby_green = sum(1 for c in creatures if c.pos.distance_to(GREEN_POS) < green_radius)
    nearby_blue = sum(1 for c in creatures if c.pos.distance_to(BLUE_POS) < blue_radius)

    green_pressure = max(0.58, 1.0 - (nearby_green * 0.026))
    blue_pressure = max(0.52, 1.0 - (nearby_blue * 0.032))

    t = get_time_of_day()
    day = is_day(t)

    # === Automatic Day/Night Vortex (v541) ===
    # Max CW (+20) at middle of day (t=0.25), Max CCW (-20) at middle of night (t=0.75)
    import math
    VORTEX_INTENSITY = 20 * math.cos( (t - 0.25) * 2 * math.pi )

    # Completely stop regeneration in the wrong patch
    green_mult = 1.6 if day else 0.0      # No regen for Green at night
    blue_mult = 0.0 if day else 1.6       # No regen for Blue during day

    GREEN_FOOD = min(GREEN_MAX, GREEN_FOOD + green_regen * green_pressure * green_mult)
    BLUE_FOOD = min(BLUE_MAX, BLUE_FOOD + blue_regen * blue_pressure * blue_mult)

    if GREEN_FOOD > 430:
        GREEN_FOOD -= 0.32
    if BLUE_FOOD > 230:
        BLUE_FOOD -= 0.22

    # Day/Night Micro-Patch Jets + Dawn/Dusk Food Bursts
    t = get_time_of_day()

    # Detect Dawn and Dusk transitions
    if 'prev_time_of_day' not in globals():
        prev_time_of_day = t

    # Dawn: Night → Day (crossing from high t to low t, or just became day)
    if not is_day(prev_time_of_day) and is_day(t):
        GREEN_FOOD = min(GREEN_MAX, GREEN_FOOD + 300)
        print(f"[DAWN] Green patch received +300 food burst! (Current: {GREEN_FOOD:.1f})")

    # Dusk: Day → Night
    if is_day(prev_time_of_day) and not is_day(t):
        BLUE_FOOD = min(BLUE_MAX, BLUE_FOOD + 300)
        print(f"[DUSK] Blue patch received +300 food burst! (Current: {BLUE_FOOD:.1f})")

    prev_time_of_day = t

    if is_day(t):
        # Green spot creates micro-patches during day
        if random.random() < 0.03:
            # Spawn slightly offset outward + strong radial push
            angle = random.uniform(0, 2 * 3.14159)
            offset = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 45
            patch = MicroPatch(GREEN_POS.x + offset.x, GREEN_POS.y + offset.y, amount=random.uniform(4, 9), persistent=True, outbound=True)
            radial_dir = offset.normalize() if offset.length() > 0.1 else pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
            patch.vel = radial_dir * random.uniform(9.0, 13.0)
            patch.jet_speed = True
            micro_patches.append(patch)
    else:
        # Blue spot creates micro-patches during night
        if random.random() < 0.03:
            angle = random.uniform(0, 2 * 3.14159)
            offset = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 45
            patch = MicroPatch(BLUE_POS.x + offset.x, BLUE_POS.y + offset.y, amount=random.uniform(4, 9), persistent=True, outbound=True)
            radial_dir = offset.normalize() if offset.length() > 0.1 else pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
            patch.vel = radial_dir * random.uniform(9.0, 13.0)
            patch.jet_speed = True
            micro_patches.append(patch)

    for p in waste_particles[:]:
        g_dist = p.distance_to(GREEN_POS)
        b_dist = p.distance_to(BLUE_POS)
        target = GREEN_POS if g_dist < b_dist else BLUE_POS
        direction = (target - p).normalize() if (target - p).length() > 5 else pygame.math.Vector2()
        p += direction * 1.05

        if g_dist < green_radius + 12 or b_dist < blue_radius + 12:
            GREEN_FOOD = min(GREEN_MAX, GREEN_FOOD + 1.8)
            BLUE_FOOD = min(BLUE_MAX, BLUE_FOOD + 1.1)
            GREEN_GLOW = max(GREEN_GLOW, 10)
            BLUE_GLOW = max(BLUE_GLOW, 10)

            if random.random() < 0.22:
                is_strat = (g_dist > 220 or b_dist > 220)
                created = MicroPatch(p.x, p.y, random.uniform(18, 32), is_strategic=is_strat)
                micro_patches.append(created)
                patch_grid.insert(created, created.pos.x, created.pos.y)

            waste_particles.remove(p)
            WASTE = max(0, WASTE - 0.6)

    if GREEN_GLOW > 0: GREEN_GLOW -= 1
    if BLUE_GLOW > 0: BLUE_GLOW -= 1

    new_creatures = []
    to_remove = []

    # === Phase 1: Macro-Organism Cleanup (runs every frame) ===
    for macro in macro_organisms[:]:
        macro.update()

        # Aggressive cleanup + Dissolution (Phase 4)
        macro.members = [m for m in macro.members 
                         if m in creatures and m.energy > 0 and m.pos.distance_to(macro.pos) < 140]

        # Calculate average affiliation inside the macro
        if len(macro.members) >= 2:
            total_aff = 0
            count = 0
            for m in macro.members:
                for other in macro.members:
                    if m is not other and id(other) in m.affiliations:
                        total_aff += m.affiliations[id(other)]
                        count += 1
            avg_aff = total_aff / count if count > 0 else 0

            # Dissolution: slowly eject members if cohesion is low or macro is very large
            if avg_aff < 15 or len(macro.members) > 10:
                if random.random() < 0.15:  # Chance to lose a member
                    # Eject the member with lowest affiliation to the group
                    worst = min(macro.members, key=lambda m: sum(m.affiliations.get(id(o), 0) for o in macro.members if o is not m) / max(len(macro.members)-1, 1))
                    macro.members.remove(worst)
                    worst.in_macro = None

        # Do not auto-remove macros even if they have few members (prevents disappearing)
        # Empty or small macros can still exist and potentially regrow.

    # Formation: stricter and less frequent
    if random.random() < 0.04:
        for c in creatures:
            if c.in_macro is not None or len(c.affiliations) < 2:
                continue
            same_role_close = []
            for other_id, score in c.affiliations.items():
                if score > 40:  # Slightly higher threshold
                    for other in creatures:
                        if id(other) == other_id and other.get_role() == c.get_role() and other.in_macro is None:
                            if c.pos.distance_to(other.pos) < 45:
                                same_role_close.append(other)
                            break
            if len(same_role_close) >= 2:
                members = [c] + same_role_close[:5]
                macro = MacroOrganism(members)
                macro_organisms.append(macro)
                for m in members:
                    m.in_macro = macro
                    # Give absorbed creatures a new name
                    if not hasattr(m, 'macro_name'):
                        m.macro_name = generate_name() + " [" + macro.role + "]"
                break

    # === Easier Macro Formation in Dense Areas (v595) ===
    # Allow new macros to form more easily when many same-role creatures are clustered (e.g. from tractor beams)
    dense_clusters = {}
    for c in creatures:
        if c.in_macro is not None:
            continue
        role = c.get_role()
        if role not in dense_clusters:
            dense_clusters[role] = []
        dense_clusters[role].append(c)

    for role, group in dense_clusters.items():
        if len(group) >= 6:  # Lower threshold in dense areas
            # Pick a central creature
            center = group[0]
            close_ones = [c for c in group if c.pos.distance_to(center.pos) < 70]
            if len(close_ones) >= 5:
                # Form new macro from dense cluster
                new_macro = MacroOrganism(close_ones[:8])
                macro_organisms.append(new_macro)
                for c in close_ones[:8]:
                    c.in_macro = new_macro
                    if not hasattr(c, 'macro_name'):
                        c.macro_name = generate_name() + " [" + role + "]"

    # === Macro Interaction (v579) ===
    # Macros no longer damage/kill each other.
    # They only push each other apart (handled in separation code).
    # They are now primarily dangerous to individual creatures.

    # === Dangerous Macro Overlap (v576) ===
    # Creatures overlapping macros take damage and can be absorbed
    for macro in macro_organisms:
        macro_radius = 28 + min(len(macro.members), 15) * 2.5

        for c in creatures:
            if c.in_macro is not None:
                continue

            dist = c.pos.distance_to(macro.pos)
            if dist < macro_radius + 8:
                # Very strong repulsion (safe normalization)
                if dist > 0.5:
                    away = (c.pos - macro.pos).normalize()
                else:
                    away = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                c.vel += away * 4.5

                # Stop damaging once desperate
                if c.energy > 25:
                    c.energy = max(0, c.energy - 0.55)  # Much faster lethal damage

                # Overlap timer
                if not hasattr(c, 'macro_overlap_time'):
                    c.macro_overlap_time = 0.0
                c.macro_overlap_time += 1.6

                # Very fast turn hostile
                if c.macro_overlap_time > 3.0:
                    if c.get_role() == macro.role and random.random() < 0.35:
                        # Absorb into macro
                        macro.members.append(c)
                        c.in_macro = macro
                        if not hasattr(c, 'macro_name'):
                            c.macro_name = generate_name() + " [" + macro.role + "]"

                        angle = random.uniform(0, 2 * 3.14159)
                        base_r = 28 + min(len(macro.members), 15) * 2.5
                        radius = base_r + random.uniform(3, 9)
                        for mod in c.modules:
                            macro.attached_modules.append((angle, mod.type, radius))
                    else:
                        # Turn hostile quickly
                        c.energy = max(0, c.energy - 35)

                    c.macro_overlap_time = 0
            else:
                if hasattr(c, 'macro_overlap_time'):
                    c.macro_overlap_time = max(0, c.macro_overlap_time - 0.8)

    # === Smarter Macro Splitting (v588) ===
    for macro in macro_organisms[:]:
        total_power = len(macro.members) + sum(macro.upgrades.values()) * 3

        # Split when large AND has enough modules to support a new specialization
        dominant_module = None
        if macro.module_composition:
            dominant_module = max(macro.module_composition, key=macro.module_composition.get)

        split_threshold = 18
        if dominant_module:
            split_threshold = max(14, 18 - macro.module_composition.get(dominant_module, 0) // 2)

        # v752: Basic Macro Reproduction / Budding
        # Only large, stable, resource-rich macros can bud off a new daughter macro.
        can_bud = (
            len(macro.members) >= split_threshold and
            total_power >= 32 and
            getattr(macro, 'internal_stability', 1.0) > 1.1 and
            getattr(macro, 'internal_biomass', 0) > 12 and
            len(getattr(macro, 'fusion_partners', [])) >= 2
        )

        if can_bud:
            if random.random() < 0.09:  # Slightly rarer but more meaningful
                split_point = len(macro.members) // 2
                new_members = macro.members[split_point:]
                macro.members = macro.members[:split_point]

                if new_members:
                    new_macro = MacroOrganism(new_members)

                    # v752: Enhanced budding inheritance (stronger than regular split)
                    for key in macro.upgrades:
                        inherited = macro.upgrades[key] * random.uniform(0.55, 0.75)
                        new_macro.upgrades[key] = inherited
                        macro.upgrades[key] *= random.uniform(0.70, 0.90)

                    if hasattr(macro, 'specialization'):
                        new_macro.specialization = macro.specialization
                        new_macro.specialization_strength = max(0.4, macro.specialization_strength * random.uniform(0.75, 1.05))

                    # Child gets a small starting biomass from parent
                    if hasattr(macro, 'internal_biomass') and macro.internal_biomass > 15:
                        new_macro.internal_biomass = macro.internal_biomass * 0.25
                        macro.internal_biomass *= 0.85

                    # Child macro born with role bias from dominant module
                    if dominant_module == "harvester":
                        new_macro.role = "Forager"
                    elif dominant_module == "mover":
                        new_macro.role = "Scout"
                    elif dominant_module == "storage":
                        new_macro.role = "Courier"
                    # else keep parent's role

                    macro_organisms.append(new_macro)
                    new_macro.core_members = set(id(m) for m in new_members[:2])
                    if new_members:
                        core = new_members[0]
                        new_macro.core_name = getattr(core, 'name', generate_name()) + " Core"

    # === Macro Affiliation + Fusion Prep (v588) ===
    for i, macro1 in enumerate(macro_organisms):
        nearby_same = []
        for macro2 in macro_organisms:
            if macro1 is macro2:
                continue
            if macro1.role != macro2.role:
                continue
            if macro1.pos.distance_to(macro2.pos) < 160:
                nearby_same.append(macro2)

        if len(nearby_same) >= 2:  # 3 total including self
            # Enter fusion preparation
            for m in [macro1] + nearby_same:
                m.fusion_prep_timer = getattr(m, 'fusion_prep_timer', 0) + 1

                # Temporary boosts during prep
                m.core_drive *= 1.15  # Move faster
                # Increase consumption rate temporarily (handled via age/module bonuses already being strong)

            # Draw orange lines between them (done in draw method)
            macro1.fusion_partners = nearby_same
        else:
            if hasattr(macro1, 'fusion_prep_timer'):
                macro1.fusion_prep_timer = max(0, macro1.fusion_prep_timer - 2)

    # === Fusion Prep State (visuals + boosts only, no actual merging) ===
    # Macros get orange lines, move faster, and consume more when near same-role macros.
    # No macros are ever merged or destroyed from this.

    # === Prevent Macro Overlap (stronger when overlapping more) ===
    for i, macro1 in enumerate(macro_organisms):
        for macro2 in macro_organisms[i+1:]:
            dist = macro1.pos.distance_to(macro2.pos)
            r1 = 28 + min(len(macro1.members), 15) * 2.5
            r2 = 28 + min(len(macro2.members), 15) * 2.5
            min_dist = r1 + r2 + 8

            if dist < min_dist and dist > 0.1:
                push_dir = (macro1.pos - macro2.pos).normalize()
                overlap = min_dist - dist

                # Stronger repulsion the more they overlap
                push_strength = overlap * (1.0 + overlap * 0.15)

                macro1.pos += push_dir * (push_strength * 0.5)
                macro2.pos -= push_dir * (push_strength * 0.5)

                # Push their drives harder when deeply overlapping
                macro1.core_drive += push_dir * (push_strength * 0.4)
                macro2.core_drive -= push_dir * (push_strength * 0.4)

    for c in creatures[:]:
        c.update(creatures)
        g_dist = c.pos.distance_to(GREEN_POS)
        b_dist = c.pos.distance_to(BLUE_POS)
        if g_dist < green_radius and GREEN_FOOD > 2:
            take = min(c.gather_rate() * 0.42, GREEN_FOOD)
            if c.energy > 0:
                c.energy = min(c.max_energy(), c.energy + take)
            GREEN_FOOD -= take
            WASTE += take * 0.22
            c.reproduction_cooldown = max(0, c.reproduction_cooldown - 18)  # Eating resets cooldown (final pass)

            # Macro gathering bonus (uses upgrades + role + module specialization)
            if c.in_macro is not None:
                macro = c.in_macro
                bonus = 1.0 + macro.upgrades.get("gathering", 0)

                # Module specialization bonus
                harvester_count = macro.module_composition.get("harvester", 0)
                bonus += harvester_count * 0.04

                # Age bonus
                age_bonus = 1.0 + min(macro.age / 120.0, 2.0)
                bonus *= age_bonus

                # Role-specific bonus
                if macro.role == "Forager":
                    bonus *= 1.5
                elif macro.role == "Courier":
                    bonus *= 1.2

                c.energy = min(c.max_energy(), c.energy + take * bonus)
            if random.random() < 0.42:
                waste_particles.append(c.pos + pygame.math.Vector2(random.uniform(-4, 4), random.uniform(-4, 4)))
        if b_dist < blue_radius and BLUE_FOOD > 2:
            take = min(c.gather_rate() * 0.42, BLUE_FOOD)
            if c.energy > 0:
                c.energy = min(c.max_energy(), c.energy + take)
            BLUE_FOOD -= take
            WASTE += take * 0.22
            c.reproduction_cooldown = max(0, c.reproduction_cooldown - 18)  # Eating resets cooldown (final pass)

            # Macro gathering bonus (uses upgrades + role + module specialization)
            if c.in_macro is not None:
                macro = c.in_macro
                bonus = 1.0 + macro.upgrades.get("gathering", 0)

                # Module specialization bonus
                harvester_count = macro.module_composition.get("harvester", 0)
                bonus += harvester_count * 0.04

                # Age bonus
                age_bonus = 1.0 + min(macro.age / 120.0, 2.0)
                bonus *= age_bonus

                # Role-specific bonus
                if macro.role == "Forager":
                    bonus *= 1.5
                elif macro.role == "Courier":
                    bonus *= 1.2

                c.energy = min(c.max_energy(), c.energy + take * bonus)
            if random.random() < 0.42:
                waste_particles.append(c.pos + pygame.math.Vector2(random.uniform(-4, 4), random.uniform(-4, 4)))
        for p in micro_patches[:]:
            dist = c.pos.distance_to(p.pos)
            if dist < p.radius + 11 and p.amount > 1.1:
                if c.energy <= 0:
                    continue   # Dead creatures can't recover

                # Micro-patch competition
                nearby_competitors = 0
                for other in creatures:
                    if other is not c and other.pos.distance_to(p.pos) < p.radius + 25:
                        nearby_competitors += 1
                comp_mult = 1.0 / (1.0 + 0.5 * nearby_competitors)

                pop = len(creatures)
                cache_mult = 1.15 if pop < 380 else 0.68
                take = min(3.6 * comp_mult, p.amount * 0.78)
                if c.energy > 0:
                    c.energy = min(c.max_energy(), c.energy + take * cache_mult)
                c.carried_biomass = min(c.external_storage_capacity(), c.carried_biomass + take * 0.48)
                p.amount -= take * 0.82
                c.reproduction_cooldown = max(0, c.reproduction_cooldown - 15)  # Eating resets cooldown (final pass)
                if p.amount < 1.2:
                    micro_patches.remove(p)
                c.lifetime_learn(0.7)
                break

        # Micro-Patch recycling / ejection system
        # When micro-patches drift close to Green or Blue, they get converted into
        # small outward-ejected mini-patches (like the main patches are "shooting" them back out)
        for p in micro_patches[:]:
            g_dist = p.pos.distance_to(GREEN_POS)
            b_dist = p.pos.distance_to(BLUE_POS)
            green_r = max(MIN_RADIUS, GREEN_BASE_RADIUS * (GREEN_FOOD / GREEN_MAX))
            blue_r = max(MIN_RADIUS, BLUE_BASE_RADIUS * (BLUE_FOOD / BLUE_MAX))

            if (g_dist < green_r + 25) or (b_dist < blue_r + 25):
                if p.amount > 12 and random.random() < 0.08:  # Occasional ejection
                    # Determine direction: push away from the main patch
                    target = GREEN_POS if g_dist < b_dist else BLUE_POS
                    outward = (p.pos - target)
                    if outward.length() < 1:
                        outward = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1))

                    # Create a small fast-moving ejected mini-patch
                    ejected = MicroPatch(p.pos.x, p.pos.y, p.amount * 0.45, is_strategic=False)
                    ejected.pos += outward.normalize() * 8
                    # Give it some outward velocity so it flies out
                    # (we'll abuse the fact that MicroPatch doesn't have vel, so we move it manually later if needed)
                    micro_patches.append(ejected)

                    # Reduce original
                    p.amount *= 0.55
                    if p.amount < 4:
                        micro_patches.remove(p)
        if c.can_reproduce():
            new_creatures.append(c.reproduce())
            sound_manager.play_reproduce_sound()
        if c.energy <= 0:
            to_remove.append(c)

    for c in to_remove:
        if c in creatures:
            sound_manager.play_death_pop()
            if selected_creature is c:
                selected_creature = None
            creatures.remove(c)

    creatures.extend(new_creatures)
    sound_manager.update_background_tone(len(creatures))

    # === Frequent Beautiful Tones (v104) ===
    for c in creatures:
        if (c.pos - GREEN_POS).length() < 140:
            c.signal_value = max(getattr(c, 'signal_value', 0), 0.52)

    signaling_creatures = [c for c in creatures if getattr(c, 'signal_value', 0) > 0.20]

    if len(signaling_creatures) > 0 and random.random() < 0.06:
        pass  # print(f"[SIGNAL] active={len(signaling_creatures)}")  # Disabled for dawn/dusk debugging

    # Natural ethereal tone triggering
    if len(signaling_creatures) >= 1:
        if random.random() < 0.92:
            avg_sig = sum(c.signal_value for c in signaling_creatures) / len(signaling_creatures)
            local_density = min(1.0, len(signaling_creatures) / 8.0)

            avg_voice = sum(getattr(c.brain, 'voice_base_freq', 880.0) for c in signaling_creatures) / len(signaling_creatures)
            avg_timbre = sum(getattr(c.brain, 'voice_timbre', 0.5) for c in signaling_creatures) / len(signaling_creatures)
            avg_mod = sum(getattr(c.brain, 'voice_mod_depth', 0.15) for c in signaling_creatures) / len(signaling_creatures)

            # Pass position + velocity for spatial + Doppler audio
            creature = signaling_creatures[0] if signaling_creatures else None
            pos = creature.pos if creature else None
            vel = getattr(creature, 'vel', None) if creature else None

            sound_manager.play_ethereal_signal(
                signal_strength=avg_sig,
                density=local_density,
                avg_voice_freq=avg_voice,
                avg_timbre=avg_timbre,
                avg_mod=avg_mod,
                signal_tendency=avg_sig,
                position=pos,
                velocity=vel,
                caller=creature
            )

            # Phase 3: Energy efficiency for rhythmic signaling
            if creature and creature.recent_rhythmic_call > 0 and creature.signal_tendency > 0.6:
                creature.energy = min(creature.max_energy(), creature.energy + 0.6)

            # Phase 3: Module Synergy - Sensor + Social modules boost rhythmic signaling
            if creature:
                sensor_count = creature.sensor_count()
                social_modules = sum(1 for m in creature.modules if m.type == "sensor" and not m.damaged)
                if creature.recent_rhythmic_call > 0:
                    boost = 0.025 * (sensor_count + social_modules)
                    creature.signal_tendency = min(1.0, creature.signal_tendency + boost)

            # Phase 3: Light role-based rhythmic flavor
            if creature and creature.recent_rhythmic_call > 0:
                role = creature.get_role()
                if role == "scout":
                    creature.signal_tendency = min(1.0, creature.signal_tendency + 0.02)
                elif role == "forager":
                    creature.signal_tendency = min(1.0, creature.signal_tendency + 0.015)
        # Chorus - user likes it, so keep it decent
        if len(signaling_creatures) >= 4 and random.random() < 0.25:
            avg_sig = sum(c.signal_value for c in signaling_creatures) / len(signaling_creatures)
            if avg_sig > 0.45 and not DISABLE_CHORUS:
                # print("[CHORUS] Chorus triggered")  # Disabled for dawn/dusk debugging
                local_density = min(1.0, len(signaling_creatures) / 9.0)

                avg_timbre = sum(getattr(c.brain, 'voice_timbre', 0.5) for c in signaling_creatures) / len(signaling_creatures)
                avg_mod = sum(getattr(c.brain, 'voice_mod_depth', 0.15) for c in signaling_creatures) / len(signaling_creatures)

                sound_manager.play_chorus_layer(
                    signal_strength=avg_sig,
                    density=local_density,
                    avg_timbre=avg_timbre,
                    avg_mod=avg_mod
                )

    # Drawing
    g_ratio = max(0, GREEN_FOOD / GREEN_MAX)
    if GREEN_GLOW > 0:
        pygame.draw.circle(screen, (255, 255, 220), (int(GREEN_POS.x), int(GREEN_POS.y)), int(green_radius + 6), 3)
    green_color = (int(85 + 80 * g_ratio), int(145 + 65 * g_ratio), int(90 + 60 * g_ratio))
    pygame.draw.circle(screen, green_color, (int(GREEN_POS.x), int(GREEN_POS.y)), int(green_radius))
    # Inner launch zone (darker green core)
    inner_r = int(green_radius * GREEN_INNER_RADIUS_RATIO)
    pygame.draw.circle(screen, (45, 95, 55), (int(GREEN_POS.x), int(GREEN_POS.y)), inner_r)
    pygame.draw.circle(screen, (130, 255, 140), (int(GREEN_POS.x), int(GREEN_POS.y)), int(green_radius), 4)

    b_ratio = max(0, BLUE_FOOD / BLUE_MAX)
    if BLUE_GLOW > 0:
        pygame.draw.circle(screen, (255, 255, 220), (int(BLUE_POS.x), int(BLUE_POS.y)), int(blue_radius + 6), 3)
    blue_color = (int(90 + 75 * b_ratio), int(110 + 70 * b_ratio), int(160 + 65 * b_ratio))
    pygame.draw.circle(screen, blue_color, (int(BLUE_POS.x), int(BLUE_POS.y)), int(blue_radius))
    # Inner launch zone (darker blue core)
    blue_inner_r_draw = int(blue_radius * BLUE_INNER_RADIUS_RATIO)
    pygame.draw.circle(screen, (55, 70, 115), (int(BLUE_POS.x), int(BLUE_POS.y)), blue_inner_r_draw)
    pygame.draw.circle(screen, (150, 180, 255), (int(BLUE_POS.x), int(BLUE_POS.y)), int(blue_radius), 4)

    # === Vortex Center Placeholder (black circle) + Flow Particles ===
    # Draw black circle at center (placeholder for future "drain" mechanic)
    pygame.draw.circle(screen, (0, 0, 0), (int(VORTEX_CENTER.x), int(VORTEX_CENTER.y)), 28)
    pygame.draw.circle(screen, (40, 40, 50), (int(VORTEX_CENTER.x), int(VORTEX_CENTER.y)), 28, 2)

    # Draw vortex flow particles (white pixels)
    for p in vortex_particles:
        pygame.draw.circle(screen, (255, 255, 255), (int(p.pos.x), int(p.pos.y)), 1)

    for p in waste_particles:
        pygame.draw.circle(screen, WASTE_COLOR, (int(p.x), int(p.y)), 3)
    # Drawing optimization: skip some visual effects in high population mode for speed
    for t in energy_tails:
        t.draw(screen)
    for p in micro_patches:
        p.draw(screen)

    for f in deposit_flashes:
        alpha = max(0, f[2] / 14)
        size = 3.1 + (14 - f[2]) * 0.24
        pygame.draw.circle(screen, (255, 220, 100), (int(f[0]), int(f[1])), int(size), 2)

    for c in creatures:
        is_selected = (selected_creature is c)
        c.draw(screen, is_selected=is_selected)

    # Update macros first (important for movement)
    for macro in macro_organisms:
        macro.update()

    # Draw macro-organisms
    for macro in macro_organisms:
        macro.draw(screen)

    # Bottom UI
    legend_y = HEIGHT - BOTTOM_PANEL_HEIGHT
    pygame.draw.rect(screen, LEGEND_BG, (0, legend_y, WIDTH, BOTTOM_PANEL_HEIGHT))

    screen.blit(title_font.render("Modular Life Sim v729 - Legend Fixes + Vortex Rebirth", True, WHITE), (20, legend_y + 8))

    # v727: Enhanced Internal Inspector (press I)
    if show_internal_inspector:
        inspector_y = legend_y + 8
        screen.blit(small_font.render("[I] Internal Ecosystem Inspector ACTIVE", True, (120, 255, 200)), (420, inspector_y))

        # Find first macro with internals for detailed view
        target_macro = None
        for m in macro_organisms:
            if m.internal_agents:
                target_macro = m
                break

        if target_macro:
            internals = target_macro.internal_agents
            core_count = sum(1 for a in internals if a.is_core)

            # Role breakdown
            role_stats = {}
            for agent in internals:
                rname = agent.role.name if hasattr(agent.role, 'name') else str(agent.role)
                if rname not in role_stats:
                    role_stats[rname] = {'count': 0, 'total_energy': 0}
                role_stats[rname]['count'] += 1
                role_stats[rname]['total_energy'] += agent.energy

            # Display header
            header_y = inspector_y + 20
            screen.blit(tiny_font.render(f"Macro Internals: {len(internals)}  |  Core: {core_count}", True, (200, 255, 200)), (420, header_y))

            # Role breakdown lines
            ry = header_y + 16
            for rname, stats in sorted(role_stats.items()):
                avg_e = stats['total_energy'] / stats['count'] if stats['count'] > 0 else 0
                txt = f"{rname}: {stats['count']}  avg {avg_e:.1f} energy"
                screen.blit(tiny_font.render(txt, True, (180, 220, 255)), (420, ry))
                ry += 13

            # Simple health bar
            if internals:
                avg_energy = sum(a.energy for a in internals) / len(internals)
                bar_width = min(120, int(avg_energy * 1.2))
                pygame.draw.rect(screen, (60, 60, 70), (420, ry + 4, 120, 8))
                pygame.draw.rect(screen, (100, 255, 150), (420, ry + 4, bar_width, 8))
                screen.blit(tiny_font.render(f"Avg Energy: {avg_energy:.1f}", True, (180, 255, 200)), (550, ry))

    y = legend_y + 36
    screen.blit(font.render(f"Population: {len(creatures)}", True, WHITE), (20, y)); y += 17
    avg = sum(len(c.modules) for c in creatures) / max(len(creatures), 1)
    screen.blit(font.render(f"Avg Modules: {avg:.2f}", True, WHITE), (20, y)); y += 15
    # Removed "Most Modules" / top creatures line as requested
    screen.blit(font.render(f"Generation: {generation}", True, (180, 220, 255)), (20, y)); y += 16
    screen.blit(font.render(f"Green Food: {int(max(0, GREEN_FOOD))}", True, (140, 255, 160)), (20, y)); y += 14
    screen.blit(font.render(f"Blue Food:  {int(max(0, BLUE_FOOD))}", True, (140, 200, 255)), (20, y))

    y = legend_y + 36
    screen.blit(font.render("Specialists", True, WHITE), (280, y)); y += 16
    role_counts = defaultdict(int)
    desperate_count = 0
    for c in creatures:
        if c.is_desperate(): desperate_count += 1
        else: role_counts[c.get_role()] += 1

    screen.blit(small_font.render(f"Forager:   {role_counts['forager']}", True, FORAGER_COLOR), (280, y)); y += 13
    screen.blit(small_font.render(f"Scout:     {role_counts['scout']}", True, SCOUT_COLOR), (280, y)); y += 13
    screen.blit(small_font.render(f"Courier:   {role_counts['courier']}", True, COURIER_COLOR), (280, y)); y += 13
    screen.blit(small_font.render(f"Sensor:    {role_counts['sensor']}", True, SENSOR_COLOR), (280, y)); y += 13
    screen.blit(small_font.render(f"Generalist:{role_counts['generalist']}", True, GENERALIST_COLOR), (280, y)); y += 13
    screen.blit(small_font.render(f"Desperate: {desperate_count}", True, DESPERATE_COLOR), (280, y))

    y2 = legend_y + 155
    active_patches = len(micro_patches)
    total_cached = sum(p.amount for p in micro_patches)
    screen.blit(small_font.render(f"Micro-Patches: {active_patches}  |  Cached: {total_cached:.1f}", True, (120, 255, 200)), (20, y2))

    # UI Mini Phase 4: Run Time moved to lower left
    elapsed = int(time.time() - start_time)
    mins, secs = divmod(elapsed, 60)
    screen.blit(font.render(f"Run Time: {mins}m {secs}s", True, (255, 255, 255)), (20, y2 + 18))

    # === Day/Night Clock (Further right + down, larger) ===
    clock_x = 890
    clock_y = legend_y + 65
    clock_radius = 27

    t = get_time_of_day()

    # Base circle
    pygame.draw.circle(screen, (50, 50, 60), (clock_x, clock_y), clock_radius)
    pygame.draw.circle(screen, (200, 200, 210), (clock_x, clock_y), clock_radius, 2)

    # Right half = Day (yellow)
    pygame.draw.arc(screen, (255, 200, 80),
                    (clock_x - clock_radius, clock_y - clock_radius, clock_radius*2, clock_radius*2),
                    -math.pi/2, math.pi/2, clock_radius)

    # Left half = Night (blue)
    pygame.draw.arc(screen, (70, 100, 200),
                    (clock_x - clock_radius, clock_y - clock_radius, clock_radius*2, clock_radius*2),
                    math.pi/2, math.pi * 1.5, clock_radius)

    # Moving hand - synced with day/night
    angle = (t * 2 * math.pi) - (math.pi / 2)
    hand_x = clock_x + math.cos(angle) * (clock_radius - 5)
    hand_y = clock_y + math.sin(angle) * (clock_radius - 5)
    pygame.draw.line(screen, (255, 255, 255), (clock_x, clock_y), (hand_x, hand_y), 2)
    pygame.draw.circle(screen, (255, 255, 255), (clock_x, clock_y), 3)

    screen.blit(small_font.render("Time", True, (200, 200, 210)), (clock_x - 16, clock_y + clock_radius + 5))

    # === Top Macros (replaces Top 8 Creatures) ===
    top_macro_rects.clear()
    # Sort macros by total power (members + upgrades)
    sorted_macros = sorted(macro_organisms, key=lambda m: len(m.members) + sum(m.upgrades.values()) * 3, reverse=True)[:8]
    ty = legend_y + 36

    screen.blit(small_font.render("Top Macros", True, (180, 220, 255)), (500, ty)); ty += 16

    for i, macro in enumerate(sorted_macros):
        # Core name + role
        name_text = f"{i+1}. {macro.core_name}"
        name_surface = small_font.render(name_text, True, (180, 230, 255))
        screen.blit(name_surface, (500, ty))

        # Stats: Members + Upgrades + Energy
        total_upgrades = sum(macro.upgrades.values())
        stats_text = f" - {macro.role} | Members: {len(macro.members)} | Upgrades: {total_upgrades:.1f}"
        stats_surface = small_font.render(stats_text, True, (200, 220, 200))
        screen.blit(stats_surface, (500 + name_surface.get_width(), ty))

        ty += 16

    # === Top 8 Predators by Kills (to the right of Top Creatures) ===
    top_predator_rects.clear()
    top_predators = sorted(creatures, key=lambda c: c.kills, reverse=True)[:8]
    pty = legend_y + 36
    px = 720  # Position to the right of Top 8 Creatures

    screen.blit(small_font.render("Top 8 Predators", True, (255, 200, 200)), (px, pty)); pty += 16

    for i, c in enumerate(top_predators):
        name_text = f"{i+1}. {c.name}"
        name_surface = small_font.render(name_text, True, (255, 180, 180))
        screen.blit(name_surface, (px, pty))

        stats_text = f" - Kills: {c.kills}"
        stats_surface = small_font.render(stats_text, True, (230, 230, 230))
        screen.blit(stats_surface, (px + name_surface.get_width(), pty))

        full_rect = pygame.Rect(px, pty, name_surface.get_width() + stats_surface.get_width(), 16)
        top_predator_rects.append((c, full_rect))

        pty += 16

    # Bottom selected creature inspector removed (Phase 1 clean version)
    pass

    pygame.draw.rect(screen, (70, 70, 80), (WIDTH - 140, legend_y + 12, 110, 26), border_radius=5)
    screen.blit(small_font.render("Reset (R)", True, WHITE), (WIDTH - 125, legend_y + 17))

    mute_text = "Unmute" if sound_manager.muted else "Mute"
    pygame.draw.rect(screen, (70, 70, 80), (WIDTH - 140, legend_y + 45, 110, 26), border_radius=5)
    screen.blit(small_font.render(mute_text, True, WHITE), (WIDTH - 125, legend_y + 50))

    pygame.draw.rect(screen, (60, 60, 65), (WIDTH - 190, legend_y + 78, 160, 14), border_radius=4)
    fill_width = int(160 * sound_manager.master_volume)
    pygame.draw.rect(screen, (140, 200, 255), (WIDTH - 190, legend_y + 78, fill_width, 14), border_radius=4)
    screen.blit(small_font.render("Master", True, WHITE), (WIDTH - 190, legend_y + 94))

    # Ethereal Tones slider
    pygame.draw.rect(screen, (60, 60, 65), (WIDTH - 190, legend_y + 112, 160, 10), border_radius=3)
    fill = int(160 * sound_manager.ethereal_base)
    pygame.draw.rect(screen, (180, 255, 180), (WIDTH - 190, legend_y + 112, fill, 10), border_radius=3)
    screen.blit(tiny_font.render(f"Ethereal {sound_manager.ethereal_base:.2f}", True, WHITE), (WIDTH - 190, legend_y + 124))

    # Chorus slider
    pygame.draw.rect(screen, (60, 60, 65), (WIDTH - 190, legend_y + 138, 160, 10), border_radius=3)
    fill = int(160 * sound_manager.chorus_base)
    pygame.draw.rect(screen, (255, 200, 150), (WIDTH - 190, legend_y + 138, fill, 10), border_radius=3)
    screen.blit(tiny_font.render(f"Chorus {sound_manager.chorus_base:.2f}", True, WHITE), (WIDTH - 190, legend_y + 150))

    # Birth/Death slider
    pygame.draw.rect(screen, (60, 60, 65), (WIDTH - 190, legend_y + 164, 160, 10), border_radius=3)
    fill = int(160 * sound_manager.life_event_base)
    pygame.draw.rect(screen, (255, 180, 200), (WIDTH - 190, legend_y + 164, fill, 10), border_radius=3)
    screen.blit(tiny_font.render(f"Birth/Death {sound_manager.life_event_base:.2f}", True, WHITE), (WIDTH - 190, legend_y + 176))

    # === Right-side Sliders (v504 layout) ===
    slider_x = 945
    is_pop_scaled = POPULATION_SCALED_WRONG_PATCH

    # Vortex is now AUTOMATIC (day/night cycle) - Slider disabled
    pygame.draw.rect(screen, (50, 50, 55), (slider_x, legend_y + 55, 130, 10), border_radius=3)
    abs_val = abs(VORTEX_INTENSITY)
    fill = int(130 * min(abs_val / 20.0, 1.0))
    bar_color = (100, 200, 255) if VORTEX_INTENSITY >= 0 else (255, 150, 100)
    pygame.draw.rect(screen, bar_color, (slider_x, legend_y + 55, fill, 10), border_radius=3)
    direction = "CW" if VORTEX_INTENSITY >= 0 else "CCW"
    screen.blit(tiny_font.render(f"Vortex {VORTEX_INTENSITY:.1f} ({direction}) [AUTO]", True, (180, 200, 220)), (slider_x, legend_y + 67))

    # Wrong Patch Damage slider (shifted down)
    pygame.draw.rect(screen, (60, 60, 65), (slider_x, legend_y + 85, 130, 10), border_radius=3)

    if is_pop_scaled:
        fill = int(130 * min(EFFECTIVE_WRONG_PATCH_MULT / 25.0, 1.0))
        pygame.draw.rect(screen, (90, 90, 95), (slider_x, legend_y + 85, fill, 10), border_radius=3)
        screen.blit(tiny_font.render(f"Wrong Patch {EFFECTIVE_WRONG_PATCH_MULT:.2f}x", True, (160, 160, 165)), (slider_x, legend_y + 97))
    else:
        fill = int(130 * min(WRONG_PATCH_DAMAGE_MULT / 20.0, 1.0))
        pygame.draw.rect(screen, (255, 120, 120), (slider_x, legend_y + 85, fill, 10), border_radius=3)
        screen.blit(tiny_font.render(f"Wrong Patch {WRONG_PATCH_DAMAGE_MULT:.2f}x", True, WHITE), (slider_x, legend_y + 97))

    # Patch Push Slider (controls the currently active patch only)
    t = get_time_of_day()
    day = is_day(t)
    green_push = MAIN_PATCH_PUSH_STRENGTH if not day else 0.0
    blue_push  = MAIN_PATCH_PUSH_STRENGTH if day else 0.0

    active_label = "Green (Night)" if not day else "Blue (Day)"
    pygame.draw.rect(screen, (60, 60, 65), (slider_x, legend_y + 115, 130, 10), border_radius=3)
    fill = int(130 * min(MAIN_PATCH_PUSH_STRENGTH / 11.72, 1.0))
    pygame.draw.rect(screen, (180, 210, 255), (slider_x, legend_y + 115, fill, 10), border_radius=3)
    screen.blit(tiny_font.render(f"Push {MAIN_PATCH_PUSH_STRENGTH:.2f} ({active_label})", True, WHITE), (slider_x, legend_y + 127))

    # Population-Scaled Wrong Patch toggle (shifted down)
    toggle_y = legend_y + 143
    toggle_color = (80, 180, 120) if is_pop_scaled else (100, 100, 105)
    pygame.draw.rect(screen, toggle_color, (slider_x, toggle_y, 130, 15), border_radius=3)
    label = "Pop-Scaled ON" if is_pop_scaled else "Manual Slider"
    screen.blit(tiny_font.render(label, True, WHITE), (slider_x + 8, toggle_y + 1))

    # Clear indicator of current effective damage when pop-scaling is active
    if is_pop_scaled:
        screen.blit(tiny_font.render(f"Effective: {EFFECTIVE_WRONG_PATCH_MULT:.2f}x (pop {len(creatures)})", True, (200, 255, 200)), (slider_x, toggle_y + 18))

    # UI Mini Phase 4: Removed overlapping phase description text

    # Bottom legend key text removed (UI Mini Phase 5)

    # ============================================================
    # ZOOM POPUP — Consolidated inspector information
    # ============================================================
    if selected_creature:
        popup_x, popup_y = 20, 20
        popup_w, popup_h = 620, 420
        zoom_size = 260

        # UI Mini Phase 3: Clear clickable regions every time we draw a new popup
        # This prevents stale rectangles from previous creatures
        child_name_rects.clear()

        if 'zoom_level' not in globals():
            global zoom_level
            zoom_level = 4.2

        sel = selected_creature
        center_x, center_y = zoom_size // 2, zoom_size // 2

        popup_surf = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
        popup_surf.fill((20, 20, 26, 245))
        pygame.draw.rect(popup_surf, (65, 65, 85), (0, 0, popup_w, popup_h), 2)

        # Zoom View
        zoom_surf = pygame.Surface((zoom_size, zoom_size))
        zoom_surf.fill((10, 10, 14))

        grid_color = (35, 35, 45)
        grid_spacing = max(10, int(13 * zoom_level))
        offset_x = int((sel.pos.x * 0.3) % grid_spacing)
        offset_y = int((sel.pos.y * 0.3) % grid_spacing)
        line_width = 1 if zoom_level < 6.0 else 2
        for gx in range(-grid_spacing * 2, zoom_size + grid_spacing * 2, grid_spacing):
            pygame.draw.line(zoom_surf, grid_color, (gx - offset_x, 0), (gx - offset_x, zoom_size), line_width)
        for gy in range(-grid_spacing * 2, zoom_size + grid_spacing * 2, grid_spacing):
            pygame.draw.line(zoom_surf, grid_color, (0, gy - offset_y), (zoom_size, gy - offset_y), line_width)

        # Nearby entities
        for p in micro_patches:
            if p.pos.distance_to(sel.pos) > 150: continue
            dx = (p.pos.x - sel.pos.x) * zoom_level
            dy = (p.pos.y - sel.pos.y) * zoom_level
            if abs(dx) < zoom_size//2 and abs(dy) < zoom_size//2:
                size = max(2, int(p.radius * 0.18 * zoom_level))
                pygame.draw.circle(zoom_surf, (160, 255, 170), (int(center_x + dx), int(center_y + dy)), size)

        nearby_for_zoom = creature_grid.query(sel.pos.x, sel.pos.y, 150)
        for other in nearby_for_zoom:
            if other is sel: continue
            dx = (other.pos.x - sel.pos.x) * zoom_level
            dy = (other.pos.y - sel.pos.y) * zoom_level
            if abs(dx) < zoom_size//2 and abs(dy) < zoom_size//2:
                color = (255, 100, 100) if other.is_desperate() else (160, 180, 255)
                r = max(3, int(5 * zoom_level * 0.32))
                pygame.draw.circle(zoom_surf, color, (int(center_x + dx), int(center_y + dy)), r)

        if sel.is_desperate() and sel.current_prey and sel.current_prey in creatures:
            prey = sel.current_prey
            dx = (prey.pos.x - sel.pos.x) * zoom_level
            dy = (prey.pos.y - sel.pos.y) * zoom_level
            pygame.draw.line(zoom_surf, (0, 255, 210), (center_x, center_y),
                             (int(center_x + dx), int(center_y + dy)), 2)

        # Main creature
        core_size = max(10, int(11 * zoom_level * 0.55))
        pygame.draw.circle(zoom_surf, (255, 255, 215), (center_x, center_y), core_size)
        pygame.draw.circle(zoom_surf, (255, 235, 130), (center_x, center_y), core_size + max(3, int(4 * zoom_level * 0.4)), 2)

        if sel.using_energy_tail and sel.vel.length() > 0.1:
            back_dir = -sel.vel.normalize()
            start = pygame.math.Vector2(center_x, center_y) + back_dir * (core_size + 4)
            end = start + back_dir * (core_size * 1.35)
            pygame.draw.line(zoom_surf, (90, 255, 255), (int(start.x), int(start.y)), (int(end.x), int(end.y)), 3)

        for i, m in enumerate(sel.modules):
            angle = (i / max(len(sel.modules), 1)) * 6.28
            ox = int(math.cos(angle) * (core_size + max(6, int(7 * zoom_level * 0.4))))
            oy = int(math.sin(angle) * (core_size + max(6, int(7 * zoom_level * 0.4))))
            size = max(3, int(m.get_size() * 0.65 * zoom_level * 0.35))
            pygame.draw.circle(zoom_surf, m.get_color(), (center_x + ox, center_y + oy), size)

        popup_surf.blit(zoom_surf, (20, 45))

        # Energy bar below the zoom grid (closer to original style)
        bar_x = 20
        bar_y = 312
        bar_w = 260
        bar_h = 13

        pygame.draw.rect(popup_surf, (50, 50, 58), (bar_x, bar_y, bar_w, bar_h), border_radius=2)

        energy_ratio = max(0, min(1.0, sel.energy / sel.max_energy()))
        fill_w = int(bar_w * energy_ratio)

        if fill_w > 0:
            if energy_ratio > 0.5:
                fill_col = (85, 215, 115)
            elif energy_ratio > 0.28:
                fill_col = (255, 195, 70)
            else:
                fill_col = (255, 85, 85)
            pygame.draw.rect(popup_surf, fill_col, (bar_x, bar_y, fill_w, bar_h), border_radius=2)

        # Only predatory (red) marker remains
        pygame.draw.line(popup_surf, (255, 70, 70), (bar_x + int(bar_w * 0.15), bar_y), (bar_x + int(bar_w * 0.15), bar_y + bar_h), 2)

        # Text above the bar
        popup_surf.blit(tiny_font.render(f"{sel.energy:.1f} / {sel.max_energy():.1f}", True, (255, 225, 160)), (bar_x, bar_y - 14))

        # Predatory label with kill count
        kill_text = f"PREDATORY  //  KILLS: {sel.kills}"
        popup_surf.blit(tiny_font.render(kill_text, True, (255, 100, 100)), (bar_x, bar_y + bar_h + 2))

        # Carried Biomass (moved lower)
        popup_surf.blit(tiny_font.render(f"Carried Biomass: {sel.carried_biomass:.2f}", True, CARRY_COLOR), (bar_x, bar_y + 32))

        # Zoom buttons
        btn_y = 48
        pygame.draw.rect(popup_surf, (55, 55, 70), (zoom_size + 30, btn_y, 20, 17), border_radius=3)
        popup_surf.blit(small_font.render("-", True, (255, 255, 255)), (zoom_size + 36, btn_y))
        pygame.draw.rect(popup_surf, (55, 55, 70), (zoom_size + 55, btn_y, 20, 17), border_radius=3)
        popup_surf.blit(small_font.render("+", True, (255, 255, 255)), (zoom_size + 61, btn_y))
        popup_surf.blit(tiny_font.render(f"{zoom_level:.1f}x", True, (200, 210, 255)), (zoom_size + 80, btn_y + 1))

        popup_surf.blit(small_font.render(f"ZOOM — {sel.name}", True, (255, 235, 160)), (12, 12))

        # Right info panel (brought left a bit to close the gap)
        info_x = 285
        info_y = 68   # Moved lower to avoid overlapping zoom controls
        line_h = 15

        popup_surf.blit(tiny_font.render("STATUS", True, (170, 200, 255)), (info_x, info_y)); info_y += 16
        popup_surf.blit(tiny_font.render(f"Desperate: {'Yes' if sel.is_desperate() else 'No'}", True,
                                         DESPERATE_COLOR if sel.is_desperate() else (180, 255, 180)), (info_x, info_y)); info_y += line_h
        ready_text = "Yes" if sel.reproduction_cooldown <= 0 else f"No ({sel.reproduction_cooldown})"
        popup_surf.blit(tiny_font.render(f"Can Reproduce: {ready_text}", True,
                                         (100, 255, 150) if sel.reproduction_cooldown <= 0 else (255, 180, 100)), (info_x, info_y)); info_y += line_h
        popup_surf.blit(tiny_font.render(f"Attacking: {'Yes' if sel.is_attacking else 'No'}", True, ATTACK_GLOW if sel.is_attacking else WHITE), (info_x, info_y)); info_y += line_h
        popup_surf.blit(tiny_font.render(f"Regenerating: {'Yes' if sel.regenerating else 'No'}", True, REGEN_COLOR if sel.regenerating else WHITE), (info_x, info_y)); info_y += line_h + 8

        # === UI Mini Phase 2: Lineage Info ===
        popup_surf.blit(tiny_font.render("LINEAGE", True, (170, 200, 255)), (info_x, info_y)); info_y += 16
        # Parent name (clickable)
        parent_text = sel.parent_name if sel.parent_name else "None (First Generation)"
        parent_surface = tiny_font.render(f"Parent: {parent_text}", True, (255, 220, 180))
        parent_rect = parent_surface.get_rect(topleft=(popup_x + info_x, popup_y + info_y))
        popup_surf.blit(parent_surface, (info_x, info_y))
        if sel.parent_name:
            child_name_rects.append((sel.parent_name, parent_rect))
        info_y += line_h

        child_count = len(sel.children_names)
        popup_surf.blit(tiny_font.render(f"Children: {child_count}", True, (255, 200, 150)), (info_x, info_y)); info_y += line_h

        if sel.children_names:
            display_limit = 5
            display_children = sel.children_names[:display_limit]
            for child_name in display_children:
                text_surface = tiny_font.render(f"• {child_name}", True, (180, 230, 255))
                # Store absolute screen coordinates for click detection
                text_rect = text_surface.get_rect(topleft=(popup_x + info_x, popup_y + info_y))
                popup_surf.blit(text_surface, (info_x, info_y))
                child_name_rects.append((child_name, text_rect))
                info_y += line_h

            if child_count > display_limit:
                popup_surf.blit(tiny_font.render(f"+{child_count - display_limit} more...", True, (160, 180, 200)), (info_x, info_y)); info_y += line_h

        if sel.last_nn_outputs is not None and len(sel.last_nn_outputs) >= 6:
            nn = sel.last_nn_outputs
        # MEMORY moved below Neural Activation visualizer

        # Modules section (far right) - Two columns, more compact
        mod_x = 455
        mod_y = 52
        popup_surf.blit(tiny_font.render(f"Role: {sel.get_role().capitalize()}", True, WHITE), (mod_x, mod_y)); mod_y += 14
        popup_surf.blit(tiny_font.render(f"MODULES ({len(sel.modules)})", True, (170, 200, 255)), (mod_x, mod_y)); mod_y += 14

        # Two-column module display (max ~16 visible)
        col1_x = mod_x
        col2_x = mod_x + 95
        col1_y = mod_y
        col2_y = mod_y
        display_limit = 16
        for i, m in enumerate(sel.modules):
            if i >= display_limit:
                break
            color = (255, 120, 120) if m.damaged else (100, 255, 150)
            rank_str = {1: "", 2: "II", 3: "III", 4: "IV"}.get(m.rank, str(m.rank))
            text = f"{m.type.capitalize()}{rank_str}"
            if i < 8:
                popup_surf.blit(tiny_font.render(text, True, color), (col1_x, col1_y)); col1_y += 12
            else:
                popup_surf.blit(tiny_font.render(text, True, color), (col2_x, col2_y)); col2_y += 12

        if len(sel.modules) > display_limit:
            popup_surf.blit(tiny_font.render(f"+{len(sel.modules)-display_limit} more", True, (180, 180, 190)), (mod_x, max(col1_y, col2_y) + 2))

        # === Emotional State + Thought ===
        popup_surf.blit(tiny_font.render(f"Emotion: {sel.dominant_emotion}", True, (255, 200, 120)), (285, 240))
        thought = sel.get_thought()
        popup_surf.blit(small_font.render(thought, True, (180, 220, 255)), (285, 255))

        # === Neural Activation Visualizer (Larger + Centered + Labels) ===
        viz_x = 285
        viz_y = 195
        viz_x = 285
        viz_y = 275
        popup_surf.blit(small_font.render("NEURAL ACTIVATION", True, WHITE), (viz_x, viz_y)); viz_y += 10

        layer_spacing = 46
        node_radius = 6
        start_y = viz_y + 5

        input_x  = viz_x + 65
        hidden_x = viz_x + 65 + layer_spacing
        output_x = viz_x + 65 + layer_spacing * 2

        # Connection lines
        line_color = (60, 60, 80)
        for i in range(6):
            iy = start_y + i * 11
            for j in range(8):
                hy = start_y + j * 9
                pygame.draw.line(popup_surf, line_color, (input_x, iy), (hidden_x, hy), 1)
            for k in range(6):
                oy = start_y + k * 11
                pygame.draw.line(popup_surf, line_color, (hidden_x, hy), (output_x, oy), 1)

        # Input-side neural values (neutral text)
        if sel.last_nn_outputs is not None and len(sel.last_nn_outputs) >= 6:
            nn = sel.last_nn_outputs
            labels = ["MoveX", "MoveY", "Dep", "Soc", "Exp", "Hunt"]
            for i in range(6):
                y = start_y + i * 11
                popup_surf.blit(tiny_font.render(f"{labels[i]} {nn[i]:+.2f}", True, (200, 220, 255)), (viz_x, y - 3))

        # Input nodes (color Dep/Soc/Exp/Hunt nodes based on value)
        if sel.last_nn_outputs is not None and len(sel.last_nn_outputs) >= 6:
            nn = sel.last_nn_outputs
            for i in range(6):
                y = start_y + i * 11 + 5   # small downward offset for alignment
                if i < 2:
                    pygame.draw.circle(popup_surf, (100, 200, 255), (input_x, y), node_radius)
                else:
                    val = nn[i]
                    if val > 0.3:
                        color = (255, 200, 80)
                    elif val < -0.3:
                        color = (120, 160, 255)
                    else:
                        color = (180, 180, 200)
                    pygame.draw.circle(popup_surf, color, (input_x, y), node_radius)
        else:
            for i in range(6):
                y = start_y + i * 11 + 3
                pygame.draw.circle(popup_surf, (100, 200, 255), (input_x, y), node_radius)

        # Hidden nodes
        for i in range(8):
            y = start_y + i * 9 + 2
            pygame.draw.circle(popup_surf, (255, 230, 120), (hidden_x, y), node_radius)

        # Output nodes + values
        if sel.last_nn_outputs is not None and len(sel.last_nn_outputs) >= 6:
            for i in range(6):
                y = start_y + i * 11 + 3
                val = sel.last_nn_outputs[i]
                if val > 0.3:
                    color = (255, 200, 80)
                elif val < -0.3:
                    color = (120, 160, 255)
                else:
                    color = (180, 180, 200)
                pygame.draw.circle(popup_surf, color, (output_x, y), node_radius)
                popup_surf.blit(tiny_font.render(f"{val:+.2f}", True, color), (output_x + 11, y - 3))
        else:
            for i in range(6):
                y = start_y + i * 11 + 3
                pygame.draw.circle(popup_surf, (140, 140, 180), (output_x, y), node_radius)

        # MEMORY (maintain gap, near bottom)
        mem_y = 365
        popup_surf.blit(tiny_font.render("MEMORY", True, (170, 200, 255)), (viz_x, mem_y)); mem_y += 11
        popup_surf.blit(tiny_font.render(f"Food:  {sel.memory_food.length():.2f}", True, (120, 255, 200)), (viz_x, mem_y)); mem_y += 10
        popup_surf.blit(tiny_font.render(f"Threat:{sel.memory_threat.length():.2f}", True, (255, 140, 140)), (viz_x, mem_y))

        screen.blit(popup_surf, (popup_x, popup_y))

        # Zoom button handling
        mx, my = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            btn_x = popup_x + zoom_size + 30
            if popup_y + btn_y <= my <= popup_y + btn_y + 17:
                if btn_x <= mx <= btn_x + 20:
                    zoom_level = max(2.5, zoom_level - 0.5)
                elif btn_x + 25 <= mx <= btn_x + 45:
                    zoom_level = min(9.0, zoom_level + 0.5)

    # === Atmospheric Day/Night Tint (Map only) ===
    t = get_time_of_day()
    if not is_day(t):
        # Cool night overlay
        night_overlay = pygame.Surface((WIDTH, HEIGHT - BOTTOM_PANEL_HEIGHT), pygame.SRCALPHA)
        night_overlay.fill((40, 60, 120, 35))  # Subtle cool blue
        screen.blit(night_overlay, (0, 0))
    else:
        # Very subtle warm day overlay
        day_overlay = pygame.Surface((WIDTH, HEIGHT - BOTTOM_PANEL_HEIGHT), pygame.SRCALPHA)
        day_overlay.fill((255, 230, 180, 12))  # Soft amber
        screen.blit(day_overlay, (0, 0))

    # === v718: Basic Profiling Output ===
    if profiling_enabled and profile_frame_count > 0:
        current_time = time.time()
        if current_time - last_profile_print > 5.0:  # Print every 5 seconds
            avg_update = (internal_update_time / profile_frame_count) * 1000
            avg_draw = (internal_draw_time / profile_frame_count) * 1000
            print(f"[Profile] Internal Update: {avg_update:.3f} ms | Internal Draw: {avg_draw:.3f} ms | Frames: {profile_frame_count}")
            # Reset counters
            internal_update_time = 0.0
            internal_draw_time = 0.0
            profile_frame_count = 0
            last_profile_print = current_time

    pygame.display.flip()

pygame.quit()
print("Simulation ended.")