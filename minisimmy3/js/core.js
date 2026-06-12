// ==================== IMPROVED SCORING SYSTEM (Chunk 88) ====================

// Calculate the 'value' of a creature for scoring purposes
function calculateCreatureValue(creature) {
  if (!creature) return 1;

  let value = 1;

  // Base value from modules
  value += creature.modules.length * 2;

  // Value from module tiers
  for (let m of creature.modules) {
    value += (m.tier || 1) * 3;
  }

  // Bonus for specialization
  if (creature.isPredator) value *= 1.5;

  return Math.max(1, Math.floor(value));
}

// Apply global multipliers to score gains
function applyScoreMultipliers(baseScore) {
  let multiplier = 1.0;

  // Population multiplier (more creatures = slightly higher score per action)
  const pop = creatures.length;
  if (pop > 0) {
    multiplier *= (1 + Math.min(pop / 200, 0.8)); // up to +80% at 200+ pop
  }

  // Predator multiplier
  const predatorCount = creatures.filter(c => c.isPredator).length;
  if (predatorCount > 0) {
    multiplier *= (1 + Math.min(predatorCount / 15, 0.6)); // up to +60%
  }

  // Average module count multiplier
  if (creatures.length > 0) {
    let totalModules = 0;
    for (let c of creatures) totalModules += c.modules.length;
    const avgModules = totalModules / creatures.length;
    multiplier *= (1 + Math.min(avgModules / 8, 0.5)); // up to +50%
  }

  return Math.floor(baseScore * multiplier);
}

// Example usage when a creature contributes to score (e.g. killed or dies)
// You can call applyScoreMultipliers(calculateCreatureValue(creature)) when awarding points.