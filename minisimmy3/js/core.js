// ==================== FULL PROGRESS SAVING (Chunk 37) ====================
// Now also saves Gene Vault slots

function saveProgress() {
  try {
    const progress = {
      eggs: eggs,
      highRollerPoints: highRollerPoints,
      aetheriumCrystals: aetheriumCrystals,
      geneVaultSlots: geneVaultSlots,
      lastSaved: Date.now()
    };
    localStorage.setItem('minisimmy3_progress', JSON.stringify(progress));
  } catch (e) {
    console.warn('[MiniSimmy3] Could not save full progress');
  }
}

function loadProgress() {
  try {
    const saved = localStorage.getItem('minisimmy3_progress');
    if (saved) {
      const data = JSON.parse(saved);
      if (data.eggs) eggs = data.eggs;
      if (data.highRollerPoints) highRollerPoints = data.highRollerPoints;
      if (data.aetheriumCrystals) aetheriumCrystals = data.aetheriumCrystals;
      if (data.geneVaultSlots) geneVaultSlots = data.geneVaultSlots;
    }
  } catch (e) {
    // ignore
  }
}

// autoSaveEggs already calls saveProgress, so Gene Vault is now saved automatically too.