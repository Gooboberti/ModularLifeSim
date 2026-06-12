// ==================== LAST SAVED DISPLAY (Chunk 40) ====================

function updateLastSavedDisplay() {
  const el = document.getElementById('last-saved-info');
  if (!el) return;

  try {
    const saved = localStorage.getItem('minisimmy3_progress');
    if (saved) {
      const data = JSON.parse(saved);
      if (data.lastSaved) {
        const date = new Date(data.lastSaved);
        const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        el.innerHTML = `Last saved: ${timeStr}`;
      }
    } else {
      el.innerHTML = 'No saved progress yet';
    }
  } catch (e) {
    el.innerHTML = '';
  }
}

// Call this when opening the Game Guide
// We can hook it into showGameGuide() later if needed.

// For now, we update it when the manual save button is used
function manualSaveProgress() {
  saveProgress();
  showSaveToast('Progress saved manually');
  updateLastSavedDisplay();
}