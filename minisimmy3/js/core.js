// Note (Chunk 62):
// updateUI() is called in draw() and after major actions like:
// - Extracting to egg
// - Moving egg to vault
// - Deleting egg
// - Prestige
// - Loading progress
// This ensures the top bar and egg badge stay accurate at all times.