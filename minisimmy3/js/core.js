// ==================== CLEAR SAVED DATA (Chunk 45) ====================

function clearSavedProgress() {
  if (!confirm('Clear all saved progress? This cannot be undone.')) return;

  localStorage.removeItem('minisimmy3_progress');
  localStorage.removeItem('minisimmy3_eggs');

  // Reset in-memory data
  eggs = [];
  geneVaultSlots = Array(10).fill(null);
  highRollerPoints = 0;
  aetheriumCrystals = 0;

  updateUI();
  showSaveToast('Saved progress cleared');

  // Reload the page to fully reset the simulation
  setTimeout(() => {
    location.reload();
  }, 800);
}