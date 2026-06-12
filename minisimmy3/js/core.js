// MiniSimmy3 - Core Game Loop (with Pheromones)

let creatures = [];
let vortexParticles = [];
let pheromones = [];
let centerX, centerY;
let timeScale = 1;
let paused = false;
let simTime = 0;
let isDay = true;

let greenZone = { x: 200, y: 290, baseR: 105, food: 420 };
let blueZone  = { x: 620, y: 290, baseR: 105, food: 420 };

function setup() {
  let canvas = createCanvas(820, 580);
  canvas.parent('canvas-container');

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

  // Draw food zones
  fill(16, 185, 129, 50);
  circle(greenZone.x, greenZone.y, greenZone.baseR * 2);
  fill(56, 189, 248, 50);
  circle(blueZone.x, blueZone.y, blueZone.baseR * 2);

  // Update & draw pheromones
  for (let i = pheromones.length - 1; i >= 0; i--) {
    let p = pheromones[i];
    p.life -= timeScale;
    if (p.life <= 0) {
      pheromones.splice(i, 1);
      continue;
    }
    fill(p.isGreen ? '#34d399' : '#38bdf8', map(p.life, 0, 220, 30, 140));
    noStroke();
    circle(p.x, p.y, 4);
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
      continue;
    }

    // Reproduction
    if (c.energy > 72 && c.reproCooldown <= 0 && random() < 0.0035 * timeScale) {
      let child = c.reproduce();
      creatures.push(child);
      c.energy -= 16;
      c.reproCooldown = 160;
    }
  }

  // Draw creatures (on top)
  for (let c of creatures) {
    c.show();
  }

  // UI
  fill(255);
  textSize(13);
  text(`MiniSimmy3 | Pop: ${creatures.length}`, 20, 25);
  text(`Time: ${floor(simTime/60)}:${nf(floor(simTime%60),2)}`, 20, 45);

  simTime += timeScale;
}