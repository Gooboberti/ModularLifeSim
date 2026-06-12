// ==================== FURNACE SYSTEM ====================
// 
// The Furnace allows players to burn Aetherium Crystals for a temporary
// but powerful score multiplier (x100 per crystal).
// 
// Key Functions:
// - showFurnaceModal() / hideFurnaceModal()
// - burnCrystals(amount)
// - updateFurnace()
// - getBurningMultiplier()
// 
// Behavior:
// - Burning crystals gives x100 score per crystal
// - Timer is 5 minutes per burn session (resets when adding more)
// - Multiplier is applied in updateHighRollerPoints()
// ============================================================