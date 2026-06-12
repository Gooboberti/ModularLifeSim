// ==================== INVENTORY + DELETE EGG (Chunk 33) ====================

function showInventory() {
  const modal = document.getElementById('inventory-modal');
  const list = document.getElementById('inventory-list');
  list.innerHTML = '';

  if (eggs.length === 0) {
    list.innerHTML = `<div class="text-center py-8 text-white/50 text-sm">No eggs in inventory yet.</div>`;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    return;
  }

  eggs.forEach((egg, index) => {
    const div = document.createElement('div');
    div.className = 'bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl p-3 transition-colors';
    
    div.innerHTML = `
      <div class="flex justify-between items-start">
        <div>
          <div class="font-medium text-emerald-400">${egg.name}</div>
          <div class="text-xs text-white/50">Gen ${egg.generation} • ${egg.modules.length} modules</div>
        </div>
        <div class="text-right text-xs">
          <div class="text-amber-400">${egg.killCount || 0} kills</div>
        </div>
      </div>

      <div class="flex gap-2 mt-3">
        <button onclick="event.stopImmediatePropagation(); moveEggToVault(${index});" 
                class="flex-1 text-xs px-3 py-1.5 bg-emerald-500/90 hover:bg-emerald-500 rounded-xl text-[#05070f] font-medium">
          Move to Vault
        </button>
        <button onclick="event.stopImmediatePropagation(); deleteEgg(${index});" 
                class="flex-1 text-xs px-3 py-1.5 bg-red-500/80 hover:bg-red-500 rounded-xl text-white font-medium">
          Delete
        </button>
      </div>
    `;
    
    list.appendChild(div);
  });

  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function hideInventory() {
  const modal = document.getElementById('inventory-modal');
  modal.classList.remove('flex');
  modal.classList.add('hidden');
}

// Delete egg is already defined in previous chunk with autoSaveEggs()