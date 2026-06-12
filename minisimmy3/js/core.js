// ==================== UI UPDATE (Chunk 54) ====================
// Updates all visible stats in the top bar and egg count badge.
// Called regularly from the draw loop and after important actions.
function updateUI() {
  const popEl = document.getElementById('stat-pop');
  const timeEl = document.getElementById('stat-time');
  const scoreEl = document.getElementById('stat-score');
  const crystalsEl = document.getElementById('stat-crystals');
  const badge = document.getElementById('egg-count-badge');

  if (popEl) popEl.innerText = creatures.length;
  if (timeEl) timeEl.innerText = `${floor(simTime/60)}:${nf(floor(simTime%60),2)}`;
  if (scoreEl) scoreEl.innerText = highRollerPoints.toLocaleString();
  if (crystalsEl) crystalsEl.innerText = aetheriumCrystals;
  if (badge) badge.innerText = `${eggs.length}/${MAX_EGGS}`;
}