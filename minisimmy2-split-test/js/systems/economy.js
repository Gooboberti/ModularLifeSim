// ==================== ECONOMY + SCORING + PRESTIGE + FURNACE ====================

function updateMainStats() {
  const popEl = document.getElementById('stat-pop');
  const predEl = document.getElementById('stat-pred');
  const modEl = document.getElementById('stat-modules');

  if (popEl) popEl.innerText = creatures.length;
  if (predEl) predEl.innerText = predators ? predators.length : 0;

  if (modEl && creatures.length > 0) {
    let total = 0;
    for (let c of creatures) total += c.modules.length;
    modEl.innerText = (total / creatures.length).toFixed(1);
  }
}

function updateVegasScore() {
  const scoreEl = document.getElementById('top-score');
  if (scoreEl) scoreEl.innerText = formatScore(totalScore);
}

function prestige() {
  if (burningCrystals > 0 && !hidePrestigeWarning) {
    showPrestigeWarningModal();
    return;
  }

  if (burningCrystals > 0) {
    const loss = burningCrystals * 0.15;
    aetheriumDust += Math.floor(burningCrystals - loss);
    burningCrystals = 0;
    furnaceEndTime = 0;
  }

  if (totalScore < 1000) {
    addFloatingText(width/2, height/2 - 40, "Need at least 1,000 points to prestige", '#f87171');
    return;
  }

  const dustGained = totalScore / 100000;
  aetheriumDust += dustGained;

  playTone(660, 'sine', 0.18, 0.6);
  setTimeout(() => playTone(880, 'sine', 0.22, 0.55), 90);
  setTimeout(() => playTone(1100, 'sine', 0.28, 0.5), 200);

  resetSim();
  totalScore = 0;
  updateMainStats();
  updateAetheriumUI();
  updateFurnaceUI();
}

// Add more economy functions here (convertCrystalsToDust, convertDustToCrystals, etc.)

function updateAetheriumUI() {
  const topDust = document.getElementById('top-dust');
  const topCrystals = document.getElementById('top-crystals');

  if (topDust) topDust.innerText = aetheriumDust.toFixed(2);
  if (topCrystals) topCrystals.innerText = aetheriumCrystals;
}

function updateTopFurnaceUI() {
  // Furnace timer + bonus display logic
  const timerEl = document.getElementById('top-furnace-timer');
  const bonusEl = document.getElementById('top-furnace-bonus');

  const isBurning = burningCrystals > 0 && furnaceEndTime > Date.now();
  const mult = getBurningMultiplier();

  if (timerEl) {
    if (isBurning) {
      const remaining = Math.max(0, Math.floor((furnaceEndTime - Date.now()) / 1000));
      timerEl.innerText = `${Math.floor(remaining / 60)}:${(remaining % 60).toString().padStart(2, '0')}`;
      timerEl.classList.remove('hidden');
      timerEl.classList.add('flex');
    } else {
      timerEl.classList.add('hidden');
      timerEl.classList.remove('flex');
    }
  }

  if (bonusEl) {
    if (isBurning && mult > 1) {
      bonusEl.innerText = `x${mult}`;
      bonusEl.classList.remove('hidden');
      bonusEl.classList.add('flex');
    } else {
      bonusEl.classList.add('hidden');
      bonusEl.classList.remove('flex');
    }
  }
}

function getBurningMultiplier() {
  if (burningCrystals > 0 && furnaceEndTime > Date.now()) {
    return burningCrystals * 100;
  }
  return 1;
}

function addDustToFurnace(amountMg) {
  if (aetheriumDust < amountMg) {
    addFloatingText(width/2, 100, "Not enough dust!", '#f87171');
    return;
  }
  aetheriumDust -= amountMg;
  burningCrystals += amountMg;
  furnaceEndTime = Date.now() + (5 * 60 * 1000);
  updateFurnaceUI();
  updateAetheriumUI();
}

// More furnace and economy functions can be added here...