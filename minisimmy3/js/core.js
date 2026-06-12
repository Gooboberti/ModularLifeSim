function setup() {
  try {
    let canvas = createCanvas(820, 580);
    
    const container = document.getElementById('canvas-container');
    if (container) {
      canvas.parent(container);
    }

    centerX = width / 2;
    centerY = height / 2;

    if (typeof loadProgress === 'function') loadProgress();

    for (let i = 0; i < 18; i++) {
      creatures.push(new Creature(random(width), random(height)));
    }

    for (let i = 0; i < 170; i++) {
      vortexParticles.push(new VortexParticle());
    }

  } catch (e) {
    console.error('Setup error:', e);
  }
}