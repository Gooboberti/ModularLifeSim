// MiniSimmy3 - Core Game Loop (Improved)

let creatures = [];
let vortexParticles = [];
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

  // Spawn initial creatures
  for (let i = 0; i < 14; i++) {
    creatures.push(new Creature(random(width), random(height)));
  }

  // Spawn vortex particles
  for (let i = 0; i < 140; i++) {
    vortexParticles.push(new VortexParticle());
  }
}

function draw() {
  if (paused) return;

  background(12, 14, 22);

  // Simple day/night cycle
  if (frameCount % 550 === 0) {
    isDay = !isDay;
  }

  // Draw food zones
  fill(16, 185, 129, 55);
  circle(greenZone.x, greenZone.y, greenZone.baseR * 2);
  fill(56, 189, 248, 55);
  circle(blueZone.x, blueZone.y, blueZone.baseR * 2);

  // Update vortex particles
  for (let p of vortexParticles) {
    p.update(1, 1.2);
    p.show();
  }

  // Update creatures
  for (let i = creatures.length - 1; i >= 0; i--) {
    let c = creatures[i];
    c.update(isDay, 1, 1.2, timeScale);

    // Death
    if (c.energy <= 0) {
      // Release some energy orbs (simplified)
      creatures.splice(i, 1);
      continue;
    }

    // Basic reproduction
    if (c.energy > 75 && random() < 0.004 * timeScale && c.reproCooldown <= 0) {
      let child = c.reproduce();
      creatures.push(child);
      c.energy -= 18;
      c.reproCooldown = 180;
    }
  }

  // Draw creatures
  for (let c of creatures) {
    c.show();
  }

  // Simple UI
  fill(255);
  textSize(13);
  text(`MiniSimmy3 | Creatures: ${creatures.length}`, 20, 25);
  text(`Time: ${floor(simTime / 60)}:${nf(floor(simTime % 60), 2)}`, 20, 45);

  simTime += timeScale;
}

// Simple Vortex Particle class (temporary, can be moved later)
class VortexParticle {
  constructor() {
    let angle = random(TWO_PI);
    let d = random(380, 520);
    this.x = centerX + cos(angle) * d;
    this.y = centerY + sin(angle) * d;
    this.size = random(1.8, 2.8);
  }

  update(vortexDir, vortexStrength) {
    let dx = this.x - centerX;
    let dy = this.y - centerY;
    let distToCenter = sqrt(dx * dx + dy * dy) || 1;

    if (distToCenter < 5) {
      // Respawn at edge
      let angle = random(TWO_PI);
      let d = random(380, 520);
      this.x = centerX + cos(angle) * d;
      this.y = centerY + sin(angle) * d;
      return;
    }

    let tangentX = -dy;
    let tangentY = dx;
    let len = sqrt(tangentX * tangentX + tangentY * tangentY) || 1;

    this.x += (tangentX / len) * 1.1 * vortexStrength * vortexDir;
    this.y += (tangentY / len) * 1.1 * vortexStrength * vortexDir;

    let pull = 0.75 * vortexStrength;
    this.x += (centerX - this.x) * pull / (distToCenter + 1);
    this.y += (centerY - this.y) * pull / (distToCenter + 1);
  }

  show() {
    fill(255, 255, 255, 160);
    noStroke();
    circle(this.x, this.y, this.size);
  }
}