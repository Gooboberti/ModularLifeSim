// MiniSimmy3 - Core + Expanded Inspector

let creatures = [];
let vortexParticles = [];
let pheromones = [];
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

  for (let i = 0; i < 16; i++) {
    creatures.push(new Creature(random(width), random(height)));
  }
  for (let i = 0; i < 160; i++) {
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

function handleMousePress() {
  for (let c of creatures) {
    if (dist(mouseX, mouseY, c.x, c.y) < 14) {
      selectedCreature = c;
      document.getElementById('inspector').classList.remove('hidden');
      updateInspector();
      return;
    }
  }
  selectedCreature = null;
  document.getElementById('inspector').classList.add('hidden');
}

function updateUI() {
  const popEl = document.getElementById('stat-pop');
  const timeEl = document.getElementById('stat-time');
  if (popEl) popEl.innerText = creatures.length;
  if (timeEl) timeEl.innerText = `${floor(simTime/60)}:${nf(floor(simTime%60),2)}`;
}

function updateInspector() {
  if (!selectedCreature) return;

  const c = selectedCreature;
  document.getElementById('inspect-name').innerText = c.name;
  document.getElementById('inspect-role').innerText = c.role || c.specialization;
  document.getElementById('inspect-gen').innerText = c.generation;
  document.getElementById('inspect-energy').innerText = Math.floor(c.energy);
  document.getElementById('inspect-module-count').innerText = c.modules.length;

  // Modules list
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
        <span class="text-amber-400">${tier > 1 ? 'T' + tier : ''}</span>
      `;
      modContainer.appendChild(div);
    });
  }
}

function deselectCreature() {
  selectedCreature = null;
  document.getElementById('inspector').classList.add('hidden');
}

function setTimeScale(scale) { timeScale = scale; }

function togglePause() {
  paused = !paused;
  const btn = document.getElementById('pause-btn');
  const text = document.getElementById('pause-text');
  if (paused) {
    btn.classList.add('bg-red-500/80');
    text.innerText = 'Resume';
  } else {
    btn.classList.remove('bg-red-500/80');
    text.innerText = 'Pause';
  }
}