// ==================== RUNTIME SAFETY GUARDS (Chunk 86) ====================

// Defensive helper - prevents crashes if a function is missing
window.safeCall = function(fnName, ...args) {
  if (typeof window[fnName] === 'function') {
    return window[fnName](...args);
  }
  console.warn(`[MiniSimmy3] Function ${fnName} not found`);
};

// Ensure critical globals exist
if (typeof creatures === 'undefined') window.creatures = [];
if (typeof eggs === 'undefined') window.eggs = [];
if (typeof geneVaultSlots === 'undefined') window.geneVaultSlots = Array(10).fill(null);
if (typeof highRollerPoints === 'undefined') window.highRollerPoints = 0;
if (typeof aetheriumCrystals === 'undefined') window.aetheriumCrystals = 0;

// Note: If any core functions are missing at runtime, they should be added to core.js or creatures.js.