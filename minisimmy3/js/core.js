// MiniSimmy3 - Core + Enhanced Gene Vault (Chunk 11)

let creatures = [];
let vortexParticles = [];
let pheromones = [];
let geneVaultSlots = Array(10).fill(null);
let centerX, centerY;
let timeScale = 1;
let paused = false;
let simTime = 0;
let isDay = true;
let selectedCreature = null;

let greenZone = { x: 200, y: 290, baseR: 105, food: 420 };
let blueZone  = { x: 620, y: 290, baseR: 105, food: 420 };

function setup() {
  let canvas = createCanvas(820, 580);
  canvas.parent('canvas-container');
  canvas.mousePressed(handleMousePress);

  centerX = width / 2;
  centerY = height / 2;

  for (let i = 0; i < 18; i++) {
    creatures.push(new Creature(random(width), random(height)));
  }
  for (let i = 0; i < 170; i++) {
    vortexParticles.push(new VortexParticle());
  }
}

function draw() {
  if (paused) return;

  background(12, 14, 22);

  if (frameCount % 550 === 0) isDay = !isDay;

  fill(16, 185, 129, 50);
  circle(greenZone.x, greenZone.y, greenZone.baseR * 2);
  fill(56, 189, 248, 50);
  circle(blueZone.x, blueZone.y, blueZone.baseR * 2);

  for (let i = pheromones.length - 1; i >= 0; i--) {
    let p = pheromones[i];
    p.life -= timeScale * 0.9;
    if (p.life <= 0) { pheromones.splice(i, 1); continue; }
    fill(p.isGreen ? '#34d399' : '#38bdf8', map(p.life, 0, 200, 20, 130));
    circle(p.x, p.y, 3.5);
  }

  for (let p of vortexParticles) {
    p.update(1, 1.15);
    p.show();
  }

  for (let i = creatures.length - 1; i >= 0; i--) {
    let c = creatures[i];
    c.update(isDay, 1, 1.15, timeScale, pheromones);

    if (c.energy <= 0) {
      creatures.splice(i, 1);
      if (selectedCreature === c) { selectedCreature = null; document.getElementById('inspector').classList.add('hidden'); }
      continue;
    }

    if (c.energy > 70 && c.reproCooldown <= 0 && random() < 0.003 * timeScale) {
      creatures.push(c.reproduce());
      c.energy -= 15;
      c.reproCooldown = 150;
    }
  }

  for (let c of creatures) c.show();

  if (selectedCreature) {
    stroke(255, 255, 255, 160);
    strokeWeight(2);
    noFill();
    circle(selectedCreature.x, selectedCreature.y, 18);
  }

  updateUI();
  if (selectedCreature) updateInspector();
  simTime += timeScale;
}

// ==================== GENE VAULT (Enhanced - Chunk 11) ====================
function showGeneVault() {
  const modal = document.getElementById('gene-vault-modal');
  const container = document.getElementById('gene-vault-slots');
  container.innerHTML = '';

  for (let i = 0; i < 10; i++) {
    const slot = document.createElement('div');
    slot.className = 'bg-[#0a0a0f] border border-white/10 rounded-2xl p-3 min-h-[130px] flex flex-col transition-colors';

    if (i < 2) {
      if (geneVaultSlots[i]) {
        const egg = geneVaultSlots[i];
        slot.className += ' hover:border-emerald-400/60 cursor-pointer';
        slot.innerHTML = `
          <div class="flex justify-between items-start">
            <div>
              <div class="text-xs text-emerald-400 font-semibold">Slot ${i+1}</div>
              <div class="text-sm mt-0.5 font-medium">${egg.name}</div>
            </div>
            <div class="text-right">
              <div class="text-[10px] text-white/50">Gen ${egg.generation}</div>
              <div class="text-[10px] text-emerald-400/70">${egg.modules.length} modules</div>
            </div>
          </div>
          <div class="mt-auto pt-3 flex gap-2">
            <button onclick="event.stopImmediatePropagation(); viewEggInVault(${i});" 
                    class="flex-1 text-xs px-3 py-1 bg-white/10 hover:bg-white/20 rounded-xl">View</button>
            <button onclick="event.stopImmediatePropagation(); removeFromVault(${i});" 
                    class="flex-1 text-xs px-3 py-1 bg-red-500/80 hover:bg-red-500 rounded-xl text-white">Remove</button>
          </div>
        `;
        slot.onclick = () => viewEggInVault(i);
      } else {
        slot.innerHTML = `
          <div class="text-xs text-emerald-400 font-semibold">Slot ${i+1} (Unlocked)</div>
          <div class="text-[10px] text-white/50 mt-2">Empty</div>
          <div class="mt-auto">
            <button onclick="event.stopImmediatePropagation(); placeSelectedCreatureInVault(${i});" 
                    class="mt-2 w-full text-xs px-3 py-1.5 bg-emerald-500/90 hover:bg-emerald-500 rounded-xl text-[#05070f] font-medium">
              Place Selected
            </button>
          </div>
        `;
      }
    } else {
      slot.innerHTML = `
        <div class="text-xs text-white/40 font-semibold">Slot ${i+1}</div>
        <div class="mt-5 flex justify-center">
          <i class="fa-solid fa-lock text-white/30 text-2xl"></i>
        </div>
        <div class="text-[10px] text-center text-white/40 mt-1">Locked</div>
      `;
    }

    container.appendChild(slot);
  }

  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function hideGeneVault() {
  const modal = document.getElementById('gene-vault-modal');
  modal.classList.remove('flex');
  modal.classList.add('hidden');
}

function placeSelectedCreatureInVault(slotIndex) {
  if (!selectedCreature) {
    alert("Select a creature in the inspector first.");
    return;
  }
  if (slotIndex >= 2) return;

  const eggData = {
    name: selectedCreature.name,
    generation: selectedCreature.generation,
    modules: JSON.parse(JSON.stringify(selectedCreature.modules)),
    killCount: selectedCreature.killCount || 0,
    childrenCount: selectedCreature.childrenCount || 0
  };

  geneVaultSlots[slotIndex] = eggData;
  hideGeneVault();
  showGeneVault();
  addFloatingText(selectedCreature.x, selectedCreature.y - 25, "Stored in Gene Vault", '#a78bfa');
}

function viewEggInVault(slotIndex) {
  const egg = geneVaultSlots[slotIndex];
  if (!egg) return;

  // Create a nice detail modal
  const detailHTML = `
    <div onclick="this.remove()" class="fixed inset-0 bg-black/80 flex items-center justify-center z-[200]">
      <div onclick="event.stopImmediatePropagation()" class="bg-[#121218] border border-white/10 rounded-3xl max-w-md w-full mx-4 p-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <div class="text-xl font-semibold text-emerald-400">${egg.name}</div>
            <div class="text-xs text-white/50">Generation ${egg.generation} • ${egg.modules.length} modules</div>
          </div>
          <button onclick="this.closest('.fixed').remove()" class="text-white/60 hover:text-white text-2xl">&times;</button>
        </div>

        <div class="bg-[#0a0a0f] rounded-2xl p-4 text-sm space-y-1 mb-4">
          <div class="flex justify-between"><span class="text-white/50">Kills</span> <span class="font-mono">${egg.killCount || 0}</span></div>
          <div class="flex justify-between"><span class="text-white/50">Children</span> <span class="font-mono">${egg.childrenCount || 0}</span></div>
        </div>

        <div class="text-xs text-white/50 mb-1">Modules</div>
        <div class="bg-[#0a0a0f] border border-white/10 rounded-xl p-3 text-xs max-h-32 overflow-auto">
          ${egg.modules.map(m => `<div class="flex justify-between py-px"><span style="color:${m.color}">${m.type}</span> <span class="text-amber-400">T${m.tier || 1}</span></div>`).join('')}
        </div>

        <div class="mt-5 flex gap-3">
          <button onclick="removeFromVault(${slotIndex}); this.closest('.fixed').remove()" 
                  class="flex-1 px-4 py-2.5 bg-red-500/90 hover:bg-red-500 rounded-2xl text-sm">Remove from Vault</button>
          <button onclick="this.closest('.fixed').remove()" 
                  class="flex-1 px-4 py-2.5 bg-white/10 hover:bg-white/20 rounded-2xl text-sm">Close</button>
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', detailHTML);
}

function removeFromVault(slotIndex) {
  if (confirm('Remove this brain from the Gene Vault?')) {
    geneVaultSlots[slotIndex] = null;
    hideGeneVault();
    showGeneVault();
  }
}

// ... rest of previous functions stay the same