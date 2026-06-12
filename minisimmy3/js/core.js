// ==================== SAVING FEEDBACK + PRESTIGE INTEGRATION (Chunk 34) ====================

// Simple toast notification for saving actions
function showSaveToast(message) {
  const toast = document.createElement('div');
  toast.className = 'fixed bottom-6 left-1/2 -translate-x-1/2 bg-[#121218] border border-white/20 text-white/90 px-4 py-2 rounded-2xl text-sm flex items-center gap-x-2 shadow-xl z-[200]';
  toast.innerHTML = `
    <i class="fa-solid fa-check text-emerald-400"></i>
    <span>${message}</span>
  `;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'all 0.3s ease';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 1800);
}

// Override autoSaveEggs to include feedback
function autoSaveEggs() {
  saveEggsToLocalStorage();
  // Optional: showSaveToast('Progress saved'); // Uncomment if you want constant feedback
}

// Hook auto-save into Prestige
function prestige() {
  if (!confirm('Prestige now?\n\nThis resets the simulation but keeps your Gene Vault and converts HRP into Aetherium.')) {
    return;
  }

  // Convert HRP to Aetherium
  const crystalsGained = Math.floor(highRollerPoints / 30000);
  aetheriumCrystals += Math.max(1, crystalsGained);

  // Reset simulation
  creatures = [];
  pheromones = [];
  vortexParticles = [];
  simTime = 0;
  highRollerPoints = 0;
  selectedCreature = null;
  document.getElementById('inspector').classList.add('hidden');

  for (let i = 0; i < 170; i++) {
    vortexParticles.push(new VortexParticle());
  }

  for (let i = 0; i < 16; i++) {
    creatures.push(new Creature(random(width), random(height)));
  }

  highRollerPoints = 20000;

  updateUI();
  const scoreEl = document.getElementById('stat-score');
  if (scoreEl) scoreEl.innerText = highRollerPoints.toLocaleString();

  // Save progress on Prestige
  autoSaveEggs();
  showSaveToast(`Prestiged! +${crystalsGained} Aetherium`);

  addFloatingText(width/2, height/2 - 40, `Prestiged! +${crystalsGained} Aetherium`, '#a78bfa');
}

// Note: The showSaveToast function can be used in other places (extract, delete, etc.) for better UX.