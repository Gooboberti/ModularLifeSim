// Game Guide functions
function showGameGuide() {
  const modal = document.getElementById('game-guide-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function hideGameGuide() {
  const modal = document.getElementById('game-guide-modal');
  if (modal) {
    modal.classList.remove('flex');
    modal.classList.add('hidden');
  }
}

// Note: The old showLegendModal() has been replaced by the comprehensive Game Guide above.
// All content is designed to serve as a long-term reference for the game mechanics and systems.