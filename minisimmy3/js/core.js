// ==================== LOADING + UI REFRESH (Chunk 38) ====================

function loadProgress() {
  try {
    const saved = localStorage.getItem('minisimmy3_progress');
    if (saved) {
      const data = JSON.parse(saved);
      if (data.eggs) eggs = data.eggs;
      if (data.highRollerPoints) highRollerPoints = data.highRollerPoints;
      if (data.aetheriumCrystals) aetheriumCrystals = data.aetheriumCrystals;
      if (data.geneVaultSlots) geneVaultSlots = data.geneVaultSlots;

      // Refresh top bar stats after loading
      setTimeout(() => {
        updateUI();
        const scoreEl = document.getElementById('stat-score');
        if (scoreEl) scoreEl.innerText = highRollerPoints.toLocaleString();
        const crystalsEl = document.getElementById('stat-crystals');
        if (crystalsEl) crystalsEl.innerText = aetheriumCrystals;
      }, 100);
    }
  } catch (e) {
    // ignore corrupt data
  }
}