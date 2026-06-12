// ==================== MAIN SIMULATION FLOW ====================
// 
// The simulation runs in a continuous loop:
// 
// 1. setup()       - Initializes canvas, loads saved progress, creates initial creatures
// 2. draw()        - Main loop called every frame:
//    - Updates day/night cycle
//    - Updates pheromones, vortex particles, and creatures
//    - Handles reproduction and death
//    - Draws everything
//    - Updates UI and stats
//    - Advances simTime
// 
// Key supporting functions:
// - updateUI()              : Refreshes top bar and egg badge
// - updateHighRollerPoints(): Calculates and updates score (includes Furnace multiplier)
// - updateFurnace()         : Manages Furnace timer and UI
// - updateInspector()       : Refreshes the creature inspector panel
// ============================================================