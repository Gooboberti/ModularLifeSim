// ==================== CANVAS INITIALIZATION FIX (Chunk 92) ====================

function setup() {
  try {
    let canvas = createCanvas(820, 580);
    
    // Try to attach to container, fallback to body if not found
    const container = document.getElementById('canvas-container');
    if (container) {
      canvas.parent('canvas-container');
    } else {
      console.warn('[MiniSimmy3] #canvas-container not found, attaching to body');
    }

    centerX = width / 2;
    centerY = height / 2;

    // Load saved progress
    if (typeof loadProgress === 'function') {
      loadProgress();
    }

    // Spawn initial creatures
    for (let i = 0; i < 18; i++) {
      creatures.push(new Creature(random(width), random(height)));
    }

    // Create vortex particles
    for (let i = 0; i < 170; i++) {
      vortexParticles.push(new VortexParticle());
    }

  } catch (e) {
    console.error('[MiniSimmy3] Error in setup():', e);
  }
}