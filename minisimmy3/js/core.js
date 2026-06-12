// ==================== SAVING SYSTEM ====================
// 
// Purpose: Persist player progress (eggs, economy, Gene Vault) across sessions.
// 
// Key Functions:
// - saveProgress()     : Saves current state to localStorage
// - loadProgress()     : Loads state on game startup
// - autoSaveEggs()     : Wrapper called after important egg actions
// - manualSaveProgress(): Called from Game Guide button
// - clearSavedProgress(): Developer/testing reset function
// 
// Data Saved:
// - eggs
// - highRollerPoints
// - aetheriumCrystals
// - geneVaultSlots
// 
// Notes:
// - Uses localStorage under key 'minisimmy3_progress'
// - Designed to be easily extended later for full game state export (Ranch game)
// - All critical actions should call autoSaveEggs() or saveProgress()
// ============================================================