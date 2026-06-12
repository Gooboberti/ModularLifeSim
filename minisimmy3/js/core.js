/**
 * MiniSimmy3 - Core Simulation Loop & Systems
 * 
 * This file contains the main game loop, saving system, and core mechanics.
 * The code is intentionally kept modular and well-commented for maintainability.
 */

// ==================== GLOBAL STATE ====================
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
let burningCrystals = 0;
let furnaceEndTime = 0;
let lastScoreUpdate = 0;

const MAX_EGGS = 10;

// Food zones
let greenZone = { x: 200, y: 290, baseR: 105, food: 420 };
let blueZone  = { x: 620, y: 290, baseR: 105, food: 420 };

// ==================== SETUP ====================
function setup() {
  let canvas = createCanvas(820, 580);
  canvas.parent('canvas-container');
  canvas.mousePressed(handleMousePress);

  centerX = width / 2;
  centerY = height / 2;

  // Load saved progress on startup
  if (typeof loadProgress === 'function') {
    loadProgress();
  }

  // Initial creatures
  for (let i = 0; i < 18; i++) {
    creatures.push(new Creature(random(width), random(height)));
  }

  // Vortex particles
  for (let i = 0; i < 170; i++) {
    vortexParticles.push(new VortexParticle());
  }
}

// ==================== MAIN DRAW LOOP ====================
function draw() {
  if (paused) return;

  background(12, 14, 22);

  // Day/Night cycle
  if (frameCount % 550 === 0) isDay = !isDay;

  // Draw food zones
  fill(16, 185, 129, 50);
  circle(greenZone.x, greenZone.y, greenZone.baseR * 2);
  fill(56, 189, 248, 50);
  circle(blueZone.x, blueZone.y, blueZone.baseR * 2);

  // Update and draw pheromones
  for (let i = pheromones.length - 1; i >= 0; i--) {
    let p = pheromones[i];
    p.life -= timeScale * 0.9;
    if (p.life <= 0) { pheromones.splice(i, 1); continue; }
    fill(p.isGreen ? '#34d399' : '#38bdf8', map(p.life, 0, 200, 20, 130));
    circle(p.x, p.y, 3.5);
  }

  // Update vortex particles
  for (let p of vortexParticles) {
    p.update(1, 1.15);
    p.show();
  }

  // Update creatures
  for (let i = creatures.length - 1; i >= 0; i--) {
    let c = creatures[i];
    c.update(isDay, 1, 1.15, timeScale, pheromones);

    if (c.energy <= 0) {
      creatures.splice(i, 1);
      if (selectedCreature === c) {
        selectedCreature = null;
        document.getElementById('inspector').classList.add('hidden');
      }
      continue;
    }

    // Reproduction
    if (c.energy > 70 && c.reproCooldown <= 0 && random() < 0.003 * timeScale) {
      creatures.push(c.reproduce());
      c.energy -= 15;
      c.reproCooldown = 150;
    }
  }

  // Draw creatures
  for (let c of creatures) c.show();

  // Highlight selected creature
  if (selectedCreature) {
    stroke(255, 255, 255, 160);
    strokeWeight(2);
    noFill();
    circle(selectedCreature.x, selectedCreature.y, 18);
  }

  // Update UI
  updateUI();
  if (selectedCreature) updateInspector();
  updateHighRollerPoints();
  updateFurnace();

  simTime += timeScale;
}

// ==================== UI UPDATE ====================
function updateUI() {
  const popEl = document.getElementById('stat-pop');
  const timeEl = document.getElementById('stat-time');
  const scoreEl = document.getElementById('stat-score');
  const crystalsEl = document.getElementById('stat-crystals');
  const badge = document.getElementById('egg-count-badge');

  if (popEl) popEl.innerText = creatures.length;
  if (timeEl) timeEl.innerText = `${floor(simTime/60)}:${nf(floor(simTime%60),2)}`;
  if (scoreEl) scoreEl.innerText = highRollerPoints.toLocaleString();
  if (crystalsEl) crystalsEl.innerText = aetheriumCrystals;
  if (badge) badge.innerText = `${eggs.length}/${MAX_EGGS}`;
}

// Note: Saving, Prestige, and other major systems are defined in later sections of this file.
// The code is intentionally broken into clear sections for readability.