// ==================== SAVING SYSTEM (Updated Chunk 30) ====================
// Auto-save is now hooked into key egg actions for seamless persistence.

// Save eggs to localStorage (auto-save)
function saveEggsToLocalStorage() {
  try {
    localStorage.setItem('minisimmy3_eggs', JSON.stringify(eggs));
  } catch (e) {
    console.warn('[MiniSimmy3] Could not save eggs to localStorage:', e);
  }
}

// Load eggs from localStorage on startup
function loadEggsFromLocalStorage() {
  try {
    const saved = localStorage.getItem('minisimmy3_eggs');
    if (saved) {
      eggs = JSON.parse(saved);
      console.log('%c[MiniSimmy3] Loaded saved eggs from localStorage', 'color:#64748b');
    }
  } catch (e) {
    console.warn('[MiniSimmy3] Could not load eggs from localStorage:', e);
    eggs = [];
  }
}

// Export eggs as downloadable JSON file
function exportEggs() {
  if (eggs.length === 0) {
    alert("No eggs to export.");
    return;
  }

  const dataStr = JSON.stringify(eggs, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

  const exportFileDefaultName = `minisimmy3_eggs_${new Date().toISOString().slice(0,10)}.json`;

  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();

  addFloatingText(width/2, 100, "Eggs exported successfully", '#fbbf24');
}

// Import eggs from JSON file
function importEggs(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const importedEggs = JSON.parse(e.target.result);
      if (Array.isArray(importedEggs)) {
        const existingKeys = new Set(eggs.map(e => `${e.name}-${e.generation}`));
        let added = 0;

        for (let egg of importedEggs) {
          const key = `${egg.name}-${egg.generation}`;
          if (!existingKeys.has(key) && eggs.length < MAX_EGGS) {
            eggs.push(egg);
            existingKeys.add(key);
            added++;
          }
        }

        autoSaveEggs();
        updateUI();
        showInventory();
        addFloatingText(width/2, 100, `Imported ${added} egg(s)`, '#10b981');
      }
    } catch (err) {
      alert("Failed to import eggs. The file may be invalid.");
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

// Auto-save wrapper (call this after any egg change)
function autoSaveEggs() {
  saveEggsToLocalStorage();
}

// ==================== HOOK AUTO-SAVE INTO EGG ACTIONS ====================

// Modified version of extractCreatureToEgg that auto-saves
function extractCreatureToEgg() {
  if (!selectedCreature) return;
  if (eggs.length >= MAX_EGGS) {
    alert("Inventory is full (max 10 eggs).");
    return;
  }

  const eggData = {
    name: selectedCreature.name,
    generation: selectedCreature.generation,
    modules: JSON.parse(JSON.stringify(selectedCreature.modules)),
    killCount: selectedCreature.killCount || 0,
    childrenCount: selectedCreature.childrenCount || 0
  };

  eggs.push(eggData);

  const index = creatures.indexOf(selectedCreature);
  if (index > -1) creatures.splice(index, 1);

  selectedCreature = null;
  document.getElementById('inspector').classList.add('hidden');

  autoSaveEggs();           // <-- Auto-save after extraction
  updateUI();
  addFloatingText(width/2, 80, "Egg extracted to Inventory!", '#fbbf24');
}

// Modified version of moveEggToVault that auto-saves
function moveEggToVault(eggIndex) {
  if (geneVaultSlots.filter(s => s !== null).length >= 2) {
    alert("Gene Vault is full (only 2 slots unlocked).");
    return;
  }

  const egg = eggs[eggIndex];
  for (let i = 0; i < 2; i++) {
    if (!geneVaultSlots[i]) {
      geneVaultSlots[i] = egg;
      eggs.splice(eggIndex, 1);
      autoSaveEggs();       // <-- Auto-save after moving to vault
      hideInventory();
      showGeneVault();
      return;
    }
  }
}

// Note: deleteEgg function (if implemented later) should also call autoSaveEggs()

// Load saved eggs when the simulation starts
// This is called early so eggs persist across browser sessions.