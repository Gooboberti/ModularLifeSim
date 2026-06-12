// MiniSimmy3 - Core Game Loop

let creatures = [];
let centerX, centerY;
let timeScale = 1;
let paused = false;
let simTime = 0;

let greenZone = { x: 200, y: 290, baseR: 105 };
let blueZone  = { x: 620, y: 290, baseR: 105 };

let isDay = true;

function setup() {
  let canvas = createCanvas(820, 580);
  canvas.parent('canvas-container');

  centerX = width / 2;
  centerY = height / 2;

  // Spawn initial creatures
  for (let i = 0; i < 12; i++) {
    creatures.push(new Creature(random(width), random(height)));
  }

  // Initial vortex particles (simplified)
  // ... can be expanded later
}

function draw() {
  if (paused) return;

  background(12, 14, 22);

  // Simple day/night cycle
  if (frameCount % 600 === 0) {
    isDay = !isDay;
  }

  // Update creatures
  for (let c of creatures) {
    c.update(isDay, 1, 1, timeScale);
  }

  // Draw creatures
  for (let c of creatures) {
    c.show();
  }

  // Simple UI text
  fill(255);
  textSize(14);
  text(`MiniSimmy3 - Modular | Creatures: ${creatures.length}`, 20, 30);
  text(`Sim Time: ${Math.floor(simTime / 60)}:${nf(floor(simTime % 60), 2)}`, 20, 50);

  simTime += timeScale;
}