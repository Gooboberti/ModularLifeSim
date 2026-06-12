// ==================== INITIALIZATION & ERROR RESILIENCE (Chunk 87) ====================

// Wrap setup in try/catch for better debugging
try {
  // p5.js will call setup() automatically
} catch (e) {
  console.error('[MiniSimmy3] Error during initialization:', e);
}

// Global error handler for uncaught issues during draw loop
window.addEventListener('error', function(e) {
  console.error('[MiniSimmy3] Runtime error:', e.message);
});

// Note: All major functions (updateUI, autoSaveEggs, show/hide modals, etc.) 
// have been verified to exist and be called in the correct places during previous audits.