// Note (Chunk 63):
// autoSaveEggs() should be called after any action that modifies eggs or geneVaultSlots.
// Current call sites:
// - extractCreatureToEgg()
// - moveEggToVault()
// - deleteEgg()
// - prestige()
// - burnCrystals() / import actions
// This ensures progress is never lost.