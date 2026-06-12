// ============================================================
// SAVING SYSTEM SUMMARY (as of Chunk 47)
// ============================================================
// - saveProgress() : Saves eggs, HRP, Aetherium, Gene Vault
// - autoSaveEggs() : Called after key actions (extract, move, delete, prestige)
// - loadProgress() : Loads everything on startup + refreshes UI
// - manualSaveProgress() : Manual save button in Game Guide
// - clearSavedProgress() : Reset button in Game Guide
// - showSaveToast() : Visual feedback for save actions
// - Last saved time displayed in Game Guide
// All saving uses localStorage under 'minisimmy3_progress'
// Designed to be clean, reliable, and easy to extend later
// ============================================================