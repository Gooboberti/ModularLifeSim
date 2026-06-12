// MiniSimmy3 - Core + Gene Vault scaffolding

let creatures = [];
let vortexParticles = [];
let pheromones = [];
let geneVaultSlots = Array(10).fill(null); // 10 slots, initially empty
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

// ==================== GENE VAULT ====================
function showGeneVault() {
  const modal = document.getElementById('gene-vault-modal');
  const container = document.getElementById('gene-vault-slots');
  container.innerHTML = '';

  for (let i = 0; i < 10; i++) {
    const slot = document.createElement('div');
    slot.className = 'bg-[#0a0a0f] border border-white/10 rounded-2xl p-3 min-h-[110px] flex flex-col';

    if (i < 2) {
      // First 2 slots unlocked
      if (geneVaultSlots[i]) {
        slot.innerHTML = `
          <div class="text-xs text-emerald-400 font-semibold">Slot ${i+1}</div>
          <div class="text-sm mt-1">${geneVaultSlots[i].name}</div>
          <div class="text-[10px] text-white/50">Gen ${geneVaultSlots[i].generation} • ${geneVaultSlots[i].modules.length} modules</div>
        `;
      } else {
        slot.innerHTML = `
          <div class="text-xs text-emerald-400 font-semibold">Slot ${i+1} (Unlocked)</div>
          <div class="text-[10px] text-white/50 mt-2">Empty - Place egg from Inventory</div>
        `;
      }
    } else {
      // Locked slots
      slot.innerHTML = `
        <div class="text-xs text-white/40 font-semibold">Slot ${i+1}</div>
        <div class="mt-4 flex justify-center">
          <i class="fa-solid fa-lock text-white/30 text-xl"></i>
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

// ... (rest of previous functions stay the same)