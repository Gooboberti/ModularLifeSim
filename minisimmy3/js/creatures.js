  // ==================== UPDATE (Behavior) ====================
  // Handles all creature logic each frame:
  // - Energy drain (modified by Resistant modules)
  // - Attraction to food zones (modified by Harvester modules)
  // - Vortex interaction (modified by Mover/Explorer modules)
  // - Pheromone attraction (modified by Communicator modules)
  // - Predator behavior (if this creature is a predator)
  // - Basic physics (velocity + friction + screen bounds)
  update(isDay, vortexDir, vortexStrength, timeScale = 1, pheromones = []) {
    // ... existing code ...
  }

  // ==================== DRAW ====================
  // Renders the creature and its modules on screen.
  // - Core color changes based on specialization and predator state
  // - Modules are drawn as colored circles with tier rings
  // - Predators get an extra glow outline
  show() {
    // ... existing code ...
  }