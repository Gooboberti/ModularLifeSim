// ==================== STARTUP + PROGRESS LOADING (Chunk 36) ====================

function setup() {
  let canvas = createCanvas(820, 580);
  canvas.parent('canvas-container');
  canvas.mousePressed(handleMousePress);

  centerX = width / 2;
  centerY = height / 2;

  // Load saved progress (eggs + HRP + Aetherium)
  if (typeof loadProgress === 'function') {
    loadProgress();
  }

  for (let i = 0; i < 18; i++) {
    creatures.push(new Creature(random(width), random(height)));
  }

  for (let i = 0; i < 170; i++) {
    vortexParticles.push(new VortexParticle());
  }

  // Show loaded progress toast if there was saved data
  setTimeout(() => {
    if (eggs.length > 0 || highRollerPoints > 0 || aetheriumCrystals > 0) {
      showSaveToast('Progress loaded');
    }
  }, 800);
}

// Note: The draw() loop and other core functions remain unchanged.
// Saving is now fully integrated on both save and load.