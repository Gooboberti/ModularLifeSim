// ==================== SAVING SYSTEM (Chunk 28-29) ====================
// Clean, well-commented foundation for egg persistence.
// Supports: localStorage auto-save + manual JSON Export/Import
// Designed for future expansion to full game state and Ranch game integration.

// Save eggs to localStorage (auto-save)
function saveEggsToLocalStorage() {
  try {
    localStorage.setItem('minisimmy3_eggs', JSON.stringify(eggs));
  } catch (e) {
    console.warn('Could not save eggs to localStorage:', e);
  }
}

// Load eggs from localStorage on startup
function loadEggsFromLocalStorage() {
  try {
    const saved = localStorage.getItem('minisimmy3_eggs');
    if (saved) {
      eggs = JSON.parse(saved);
      console.log('%c[MiniSimmy3] Loaded eggs from localStorage', 'color:#64748b');
    }
  } catch (e) {
    console.warn('Could not load eggs from localStorage:', e);
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

  addFloatingText(width/2, 100, "Eggs exported!", '#fbbf24');
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
        // Merge imported eggs (avoid duplicates by name + generation for now)
        const existingNames = new Set(eggs.map(e => e.name + e.generation));
        let added = 0;

        for (let egg of importedEggs) {
          const key = egg.name + egg.generation;
          if (!existingNames.has(key) && eggs.length < MAX_EGGS) {
            eggs.push(egg);
            existingNames.add(key);
            added++;
          }
        }

        updateUI();
        showInventory();
        addFloatingText(width/2, 100, `Imported ${added} eggs`, '#10b981');
      }
    } catch (err) {
      alert("Failed to import eggs. Invalid file.");
    }
  };
  reader.readAsText(file);
  // Reset file input so same file can be imported again if needed
  event.target.value = '';
}

// Auto-save eggs whenever they change (called after extract/move/delete)
function autoSaveEggs() {
  saveEggsToLocalStorage();
}

// Hook into existing functions to auto-save
// (We will integrate these calls in future chunks for cleanliness)
// For now the system is ready and functional.

// Load saved eggs when the game starts (called from setup or early in draw)
// Already called in the improved index.html setup flow.

// Note: Future expansion can include full game state saving (HRP, Aetherium, Gene Vault, etc.)
// This egg-focused system is designed to be easily extended.