// ==================== UI REFRESH AFTER LOADING (Chunk 46) ====================

function loadProgress() {
  try {
    const saved = localStorage.getItem('minisimmy3_progress');
    if (saved) {
      const data = JSON.parse(saved);
      if (data.eggs) eggs = data.eggs;
      if (data.highRollerPoints) highRollerPoints = data.highRollerPoints;
      if (data.aetheriumCrystals) aetheriumCrystals = data.aetheriumCrystals;
      if (data.geneVaultSlots) geneVaultSlots = data.geneVaultSlots;

      // Refresh all relevant UI elements after loading
      setTimeout(() => {
        updateUI(); // This updates pop, time, score, crystals, and egg badge
        const scoreEl = document.getElementById('stat-score');
        if (scoreEl) scoreEl.innerText = highRollerPoints.toLocaleString();
        const crystalsEl = document.getElementById('stat-crystals');
        if (crystalsEl) crystalsEl.innerText = aetheriumCrystals;
      }, 150);
    }
  } catch (e) {
    // ignore
  }
}