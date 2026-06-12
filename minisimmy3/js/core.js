// ==================== SAVING SYSTEM + DELETE EGG (Chunk 31) ====================
// Focused on completing the saving system and adding Delete functionality.
// All changes are refinements — no visual redesign.

// Save eggs to localStorage
function saveEggsToLocalStorage() {
  try {
    localStorage.setItem('minisimmy3_eggs', JSON.stringify(eggs));
  } catch (e) {
    console.warn('[MiniSimmy3] Could not save eggs to localStorage');
  }
}

// Load eggs from localStorage
function loadEggsFromLocalStorage() {
  try {
    const saved = localStorage.getItem('minisimmy3_eggs');
    if (saved) {
      eggs = JSON.parse(saved);
    }
  } catch (e) {
    eggs = [];
  }
}

function autoSaveEggs() {
  saveEggsToLocalStorage();
}

// Export eggs as JSON
function exportEggs() {
  if (eggs.length === 0) {
    alert("No eggs to export.");
    return;
  }
  const dataStr = JSON.stringify(eggs, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', `minisimmy3_eggs_${new Date().toISOString().slice(0,10)}.json`);
  linkElement.click();
  addFloatingText(width/2, 100, "Eggs exported", '#fbbf24');
}

// Import eggs from JSON
function importEggs(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const imported = JSON.parse(e.target.result);
      if (Array.isArray(imported)) {
        const existing = new Set(eggs.map(e => `${e.name}-${e.generation}`));
        let added = 0;
        for (let egg of imported) {
          const key = `${egg.name}-${egg.generation}`;
          if (!existing.has(key) && eggs.length < MAX_EGGS) {
            eggs.push(egg);
            existing.add(key);
            added++;
          }
        }
        autoSaveEggs();
        updateUI();
        showInventory();
        addFloatingText(width/2, 100, `Imported ${added} eggs`, '#10b981');
      }
    } catch (err) {
      alert("Import failed. Invalid file.");
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

// Delete an egg from inventory
function deleteEgg(index) {
  if (!confirm("Delete this egg permanently?")) return;

  eggs.splice(index, 1);
  autoSaveEggs();
  hideInventory();
  showInventory();
  updateUI();
  addFloatingText(width/2, 100, "Egg deleted", '#f87171');
}

// Note: In a future small chunk we can add a Delete button in the inventory cards.
// The function is ready and will be wired up cleanly.