// MiniSimmy3 - Core + Aetherium + Improved Prestige (Chunk 16)

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
let aetheriumCrystals = 0;
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

function prestige() {
  if (!confirm('Prestige now? This will reset the simulation but keep your Gene Vault and convert some HRP into Aetherium Crystals.')) {
    return;
  }

  // Convert some HRP into Aetherium Crystals (simple conversion for now)
  const crystalsGained = Math.floor(highRollerPoints / 50000);
  aetheriumCrystals += crystalsGained;

  // Reset simulation
  creatures = [];
  pheromones = [];
  vortexParticles = [];
  simTime = 0;
  highRollerPoints = 0;
  selectedCreature = null;
  document.getElementById('inspector').classList.add('hidden');

  for (let i = 0; i < 170; i++) {
    vortexParticles.push(new VortexParticle());
  }

  for (let i = 0; i < 16; i++) {
    creatures.push(new Creature(random(width), random(height)));
  }

  highRollerPoints = 15000; // Starting bonus

  updateUI();
  const scoreEl = document.getElementById('stat-score');
  if (scoreEl) scoreEl.innerText = highRollerPoints.toLocaleString();

  addFloatingText(width/2, height/2 - 30, `Prestiged! +${crystalsGained} Aetherium Crystals`, '#a78bfa');
}

// Gene Vault, Inventory, and other functions remain from previous chunks...