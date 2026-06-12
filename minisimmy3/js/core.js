// ==================== EXPANDED SAVING SYSTEM (Chunk 35) ====================
// Now saves more game state: Eggs + HRP + Aetherium Crystals

// Save full progress
function saveProgress() {
  try {
    const progress = {
      eggs: eggs,
      highRollerPoints: highRollerPoints,
      aetheriumCrystals: aetheriumCrystals,
      lastSaved: Date.now()
    };
    localStorage.setItem('minisimmy3_progress', JSON.stringify(progress));
  } catch (e) {
    console.warn('[MiniSimmy3] Could not save progress');
  }
}

function autoSaveEggs() {
  saveProgress(); // Now saves full progress
}

// Load full progress on startup
function loadProgress() {
  try {
    const saved = localStorage.getItem('minisimmy3_progress');
    if (saved) {
      const data = JSON.parse(saved);
      if (data.eggs) eggs = data.eggs;
      if (data.highRollerPoints) highRollerPoints = data.highRollerPoints;
      if (data.aetheriumCrystals) aetheriumCrystals = data.aetheriumCrystals;
      console.log('%c[MiniSimmy3] Loaded saved progress', 'color:#64748b');
    }
  } catch (e) {
    console.warn('[MiniSimmy3] Could not load progress');
  }
}

// Update the prestige function to also save full progress
// (already calls autoSaveEggs which now calls saveProgress)

// Call loadProgress() early in setup() or at the start of the simulation
// This ensures HRP and Aetherium persist across sessions.