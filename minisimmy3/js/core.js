// ==================== GLOBAL VARIABLES ====================
// 
// Core simulation state:
// - creatures: Array of all active Creature objects
// - vortexParticles: Visual particles in the central vortex
// - pheromones: Chemical signals released by Communicator creatures
// 
// Progression & Economy:
// - highRollerPoints: Main score currency
// - aetheriumCrystals: Prestige currency (earned from HRP)
// - burningCrystals / furnaceEndTime: Furnace state
// 
// Player Systems:
// - eggs: Inventory of extracted creatures
// - geneVaultSlots: Preserved creatures for long-term progression
// 
// Simulation State:
// - paused, timeScale, simTime, isDay
// - selectedCreature: Currently inspected creature
// ============================================================