// ==================== MANUAL SAVE (Chunk 39) ====================

function manualSaveProgress() {
  saveProgress();
  showSaveToast('Progress saved manually');
}

// ==================== SAVING SYSTEM NOTES ====================
// - saveProgress() saves: eggs, highRollerPoints, aetheriumCrystals, geneVaultSlots
// - autoSaveEggs() is called after important egg actions (extract, move, delete, prestige)
// - loadProgress() runs on setup() and refreshes the top bar
// - All saving uses localStorage under the key 'minisimmy3_progress'
// - Designed to be easily extended later for full game state or Ranch game export
// =============================================================