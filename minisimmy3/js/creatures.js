// ==================== MODULE TIER SYSTEM (Extended to Tier X) ====================

// Maximum tier supported
const MAX_MODULE_TIER = 10;

// When adding modules or merging, respect the new max tier
// The existing merging logic should continue to work up to Tier X

// Helper to get tier color (for future UI use)
function getTierColor(tier) {
  if (tier >= 8) return '#fde047';      // Gold/Yellow for very high tiers
  if (tier >= 6) return '#fbbf24';      // Amber
  if (tier >= 4) return '#f59e0b';      // Orange
  if (tier >= 2) return '#fbbf24';
  return '#9ca3af';                     // Default gray
}

// Note: The module merging logic in updateSpecialization() and when adding modules
// should now support going up to Tier 10 using the same 3-of-a-kind merging philosophy.