// MiniSimmy3 - Core + Extract to Egg in Inspector (Chunk 15)

let creatures = [];
let vortexParticles = [];
let pheromones = [];
let geneVaultSlots = Array(10).fill(null);
let eggs = [];
let centerX, centerY;
let timeScale = 1;
let paused = false;
let simTime = 0;
let isDay = true;
let selectedCreature = null;
let highRollerPoints = 0;
let lastScoreUpdate = 0;

const MAX_EGGS = 10;

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
  updateHighRollerPoints();
  simTime += timeScale;
}

function updateHighRollerPoints() {
  const now = Date.now();
  if (now - lastScoreUpdate < 400) return;
  lastScoreUpdate = now;

  let score = Math.floor(simTime / 8);
  const pop = creatures.length;
  if (pop > 25) score += (pop - 25) * 3;
  else if (pop < 10) score += (10 - pop) * 2;

  let predators = 0;
  for (let c of creatures) if (c.isPredator) predators++;
  score += predators * 28;

  highRollerPoints = Math.floor(score);

  const scoreEl = document.getElementById('stat-score');
  if (scoreEl) scoreEl.innerText = highRollerPoints.toLocaleString();
}

function updateUI() {
  const popEl = document.getElementById('stat-pop');
  const timeEl = document.getElementById('stat-time');
  const badge = document.getElementById('egg-count-badge');
  if (popEl) popEl.innerText = creatures.length;
  if (timeEl) timeEl.innerText = `${floor(simTime/60)}:${nf(floor(simTime%60),2)}`;
  if (badge) badge.innerText = `${eggs.length}/${MAX_EGGS}`;
}

function updateInspector() {
  if (!selectedCreature) return;
  const c = selectedCreature;

  document.getElementById('inspect-name').innerText = c.name;
  document.getElementById('inspect-role').innerText = c.role || c.specialization;
  document.getElementById('inspect-gen').innerText = c.generation;
  document.getElementById('inspect-energy').innerText = Math.floor(c.energy);
  document.getElementById('inspect-module-count').innerText = c.modules.length;

  const modContainer = document.getElementById('inspect-modules');
  modContainer.innerHTML = '';

  if (c.modules.length === 0) {
    modContainer.innerHTML = `<div class="text-white/50">No modules</div>`;
  } else {
    c.modules.forEach(m => {
      const tier = m.tier || 1;
      const div = document.createElement('div');
      div.className = 'flex justify-between text-xs py-px';
      div.innerHTML = `
        <span style="color: ${m.color}">${m.type}</span>
        <span class="text-amber-400">T${tier}</span>
      `;
      modContainer.appendChild(div);
    });
  }

  // Add Extract to Egg button if not already present
  let extractBtn = document.getElementById('extract-egg-btn');
  if (!extractBtn) {
    extractBtn = document.createElement('button');
    extractBtn.id = 'extract-egg-btn';
    extractBtn.className = 'mt-3 w-full flex items-center justify-center gap-x-2 px-3 py-2 bg-amber-500/90 hover:bg-amber-500 rounded-2xl text-xs font-medium text-[#05070f] transition-colors';
    extractBtn.innerHTML = `<i class="fa-solid fa-egg"></i> <span>Extract to Egg (Inventory)</span>`;
    extractBtn.onclick = () => {
      extractCreatureToEgg();
    };
    // Insert after modules list
    const modulesSection = document.getElementById('inspect-modules').parentNode;
    modulesSection.parentNode.appendChild(extractBtn);
  }
}

// ==================== EXTRACT TO EGG ====================
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

  // Remove from simulation
  const index = creatures.indexOf(selectedCreature);
  if (index > -1) creatures.splice(index, 1);

  const removedCreature = selectedCreature;
  selectedCreature = null;
  document.getElementById('inspector').classList.add('hidden');

  updateUI();
  addFloatingText(removedCreature.x, removedCreature.y - 20, "Egg extracted!", '#fbbf24');
}

// Gene Vault, Inventory, Prestige functions remain from previous chunks...