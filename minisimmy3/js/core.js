// ==================== GLOBALS (MUST BE AT VERY TOP) ====================
let creatures = [];
let vortexParticles = [];
let centerX, centerY;
let timeScale = 1;
let paused = false;
let selectedCreature = null;

// ==================== SETUP ====================
function setup() {
  try {
    let canvas = createCanvas(820, 580);
    const container = document.getElementById('canvas-container');
    
    if (container) {
      canvas.parent(container);
    } else {
      console.warn('No #canvas-container found');
    }

    centerX = width / 2;
    centerY = height / 2;

    // Spawn some creatures so we can see something
    for (let i = 0; i < 12; i++) {
      creatures.push(new Creature(random(width), random(height)));
    }

    // Spawn some vortex particles
    for (let i = 0; i < 80; i++) {
      vortexParticles.push(new VortexParticle());
    }

    console.log('Setup completed successfully. Creatures:', creatures.length);

  } catch (e) {
    console.error('Setup failed:', e);
  }
}