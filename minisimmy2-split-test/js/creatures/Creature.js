class Creature {
  constructor(x, y, parentModules = null, generation = 1, parentTraits = null) {
    this.x = x; this.y = y;
    this.vx = random(-0.4, 0.4); this.vy = random(-0.4, 0.4);
    this.energy = parentModules ? 39 : 50 + random(18);
    this.name = generateSciFiName();
    this.isPredator = false; this.honey = 0;
    this.generation = generation; this.children = []; this.childrenCount = 0;
    this.killCount = 0; this.reproCooldown = 0; this.currentThought = "Exploring...";
    this.damageFlash = 0;
    this.purpleFlash = 0;
    this.mustEatWhite = false;
    this.ateWhiteParticle = false;
    this.hazardsAvoided = 0;
    this.hazardDamageTaken = 0;
    this.adaptationLevel = 0;
    this.role = 'Balanced';

    if (parentTraits) {
      this.traits = {
        pheromoneSensitivity: constrain(parentTraits.pheromoneSensitivity + random(-0.07, 0.07), 0.62, 1.55),
        explorationBias: constrain(parentTraits.explorationBias + random(-0.07, 0.07), 0.62, 1.55),
        vortexResistance: constrain(parentTraits.vortexResistance + random(-0.07, 0.07), 0.62, 1.55),
        hazardAvoidance: constrain(parentTraits.hazardAvoidance + random(-0.07, 0.07), 0.62, 1.55)
      };
    } else {
      this.traits = {
        pheromoneSensitivity: 1.0 + random(-0.13, 0.13),
        explorationBias: 1.0 + random(-0.13, 0.13),
        vortexResistance: 1.0 + random(-0.13, 0.13),
        hazardAvoidance: 1.0 + random(-0.13, 0.13)
      };
    }

    let types = ['harvester', 'sensor', 'mover', 'resistant', 'explorer', 'communicator'];
    let colors = { 'harvester': '#34d399', 'sensor': '#38bdf8', 'mover': '#a78bfa', 'resistant': '#f472b6', 'explorer': '#fbbf24', 'communicator': '#c084fc' };

    if (parentModules) {
      this.modules = parentModules.map(m => ({ ...m }));
      if (random() < 0.42 && this.modules.length < 7) {
        let nt = random(types), ang = random(TWO_PI), di = random(5, 9);
        this.modules.push({ type: nt, color: colors[nt], offsetX: cos(ang) * di, offsetY: sin(ang) * di, tier: 1 });
      }
    } else {
      this.modules = [];
      if (random() < 0.48) {
        let t = random(types), ang = random(TWO_PI), di = random(5, 9);
        this.modules.push({ type: t, color: colors[t], offsetX: cos(ang) * di, offsetY: sin(ang) * di, tier: 1 });
      }
    }

    this.updateSpecialization();
  }

  getModuleCount(type) { return this.modules.filter(m => m.type === type).length; }

  getTieredModuleCount(type) {
    return this.modules.filter(m => m.type === type).reduce((sum, m) => sum + (m.tier || 1), 0);
  }

  getEfficiencyBonus() {
    let bonus = 0;
    const harv = this.getTieredModuleCount('harvester');
    const res = this.getTieredModuleCount('resistant');
    bonus += harv * 0.0035;
    bonus += res * 0.0025;
    return bonus;
  }

  getSimilarNeighborCount() {
    let count = 0;
    const myTypes = new Set(this.modules.map(m => m.type));
    for (let o of creatures) {
      if (o === this) continue;
      const otherTypes = new Set(o.modules.map(m => m.type));
      let shared = 0;
      for (let t of myTypes) if (otherTypes.has(t)) shared++;
      if (shared >= 1 && dist(this.x, this.y, o.x, o.y) < 50) count++;
    }
    return count;
  }

  getLocalGroup(radius) {
    let group = [];
    for (let o of creatures) {
      if (o !== this && dist(this.x, this.y, o.x, o.y) < radius) {
        group.push(o);
      }
    }
    return group;
  }

  getNearestHazardInfo() {
    let nearestDist = Infinity;
    let nearestAngle = 0;
    let nearbyCount = 0;
    const dangerRadius = 130;

    for (let h of redHazards) {
      let d = dist(this.x, this.y, h.x, h.y);
      if (d < dangerRadius) nearbyCount++;
      if (d < nearestDist) {
        nearestDist = d;
        nearestAngle = atan2(h.y - this.y, h.x - this.x);
      }
    }

    let normDist = (nearestDist < Infinity) ? constrain(1 - (nearestDist / dangerRadius), 0, 1) : 0;

    return {
      dist: normDist,
      angle: nearestAngle,
      count: nearbyCount
    };
  }

  pruneExcessModules() {
    const maxModules = 11;
    if (this.modules.length <= maxModules) return;

    let byType = {};
    for (let m of this.modules) {
      if (!byType[m.type]) byType[m.type] = [];
      byType[m.type].push(m);
    }

    let newModules = [];

    for (let type in byType) {
      byType[type].sort((a, b) => (b.tier || 1) - (a.tier || 1));
      newModules.push(byType[type][0]);
    }

    const dominant = this.specialization;
    if (dominant && byType[dominant]) {
      let extras = byType[dominant].slice(1);
      while (newModules.length < maxModules && extras.length > 0) {
        newModules.push(extras.shift());
      }
    }

    if (newModules.length < maxModules) {
      let remaining = [];
      for (let type in byType) {
        if (type === dominant) continue;
        remaining = remaining.concat(byType[type].slice(1));
      }
      remaining.sort((a, b) => (b.tier || 1) - (a.tier || 1));
      while (newModules.length < maxModules && remaining.length > 0) {
        newModules.push(remaining.shift());
      }
    }

    this.modules = newModules;
    this.updateSpecialization();
  }

  updateSpecialization() {
    if (this.modules.length === 0) {
      this.specialization = 'balanced';
      this.role = 'Balanced';
      return;
    }

    let counts = {};
    for (let m of this.modules) {
      counts[m.type] = (counts[m.type] || 0) + (m.tier || 1);
    }

    let maxType = null;
    let maxCount = 0;
    for (let type in counts) {
      if (counts[type] > maxCount) {
        maxCount = counts[type];
        maxType = type;
      }
    }

    this.specialization = maxType || 'balanced';

    const tieredCount = this.getTieredModuleCount(this.specialization);
    if (tieredCount >= 4) {
      if (this.specialization === 'harvester') this.role = 'Master Harvester';
      else if (this.specialization === 'sensor') this.role = 'Hazard Warden';
      else if (this.specialization === 'mover') this.role = 'Vortex Runner';
      else if (this.specialization === 'resistant') this.role = 'Survivor Core';
      else if (this.specialization === 'explorer') this.role = 'Wanderer Elite';
      else if (this.specialization === 'communicator') this.role = 'Signal Leader';
      else this.role = 'Elite ' + this.specialization;
    } else if (tieredCount >= 2) {
      this.role = 'Specialized ' + this.specialization;
    } else {
      this.role = this.specialization.charAt(0).toUpperCase() + this.specialization.slice(1);
    }
  }

  reproduce() {
    let newModules = this.modules.map(m => ({...m}));

    let typeTierCounts = {};
    for (let m of newModules) {
      const key = m.type + '-' + (m.tier || 1);
      typeTierCounts[key] = (typeTierCounts[key] || 0) + 1;
    }

    for (let key in typeTierCounts) {
      if (typeTierCounts[key] >= 3) {
        const [type, tierStr] = key.split('-');
        const currentTier = parseInt(tierStr);
        const nextTier = Math.min(5, currentTier + 1);

        for (let m of newModules) {
          if (m.type === type && (m.tier || 1) === currentTier) {
            m.tier = nextTier;
            break;
          }
        }
      }
    }

    let child = new Creature(this.x + random(-6, 6), this.y + random(-6, 6), newModules, this.generation + 1, this.traits);
    return child;
  }

  update(isDay, vortexDir, vortexStrength, timeScale = 1, envMods = null) {
    // ... (full update logic from original - truncated here for length, will continue in next aggressive push)
    if (this.reproCooldown > 0) this.reproCooldown--;
    if (!this.isPredator && this.energy < 14) this.isPredator = true;

    let baseDrain = settings.energyDrain - this.getEfficiencyBonus();
    let finalDrain = baseDrain;
    if (envMods) finalDrain *= envMods.drainMult;

    this.energy -= Math.max(0.004, finalDrain * timeScale);

    // ... rest of the very long update() method ...
  }

  show() {
    push();
    translate(this.x, this.y);
    let s = 7 + this.modules.length * 0.16;

    if (selectedCreature === this) {
      stroke(255, 255, 255, 170);
      strokeWeight(2.2);
      circle(0, 0, s + 6);
      stroke(52, 211, 153, 110);
      strokeWeight(1.3);
      circle(0, 0, s + 10);
    }

    let coreColor = this.isPredator ? '#f87171' : '#facc15';
    if (this.specialization === 'harvester') coreColor = '#34d399';
    if (this.specialization === 'sensor') coreColor = '#38bdf8';
    if (this.specialization === 'mover') coreColor = '#a78bfa';
    if (this.specialization === 'resistant') coreColor = '#f472b6';
    if (this.specialization === 'explorer') coreColor = '#fbbf24';
    if (this.specialization === 'communicator') coreColor = '#c084fc';

    fill(coreColor);
    stroke(this.isPredator ? '#fecaca' : '#fef08c');
    strokeWeight(1);
    circle(0, 0, s);
    noStroke();
    fill(255, 255, 255, 42);
    circle(-s * 0.08, -s * 0.08, s * 0.15);

    if (this.honey > 2.5) {
      fill('#f59e0b');
      circle(2.5, -2.5, 2.3 + min(this.honey * 0.07, 5.5));
    }

    if (this.damageFlash > 0 || this.purpleFlash > 0) {
      let alpha = this.purpleFlash > 0 ? 190 + sin(frameCount * 0.6) * 40 : 150 + sin(frameCount * 0.55) * 35;
      fill(167, 139, 250, alpha);
      circle(0, 0, s * 1.15);
    }

    if (this.role.includes('Master') || this.role.includes('Warden') || this.role.includes('Leader')) {
      noFill();
      stroke(255, 255, 255, 32);
      strokeWeight(1.3);
      circle(0, 0, s + 8 + sin(frameCount * 0.13) * 1.8);
    }

    for (let m of this.modules) {
      fill(m.color);
      stroke(255, 255, 255, 3);
      strokeWeight(0.12);

      const tier = m.tier || 1;
      const size = 3.2 + (tier - 1) * 0.6;

      circle(m.offsetX, m.offsetY, size);

      if (tier > 1) {
        if (tier === 5) {
          stroke('#fde047');
          strokeWeight(1.9);
          noFill();
          circle(m.offsetX, m.offsetY, size + 1.9);
          fill(m.color);
        } else {
          stroke('#fbbf24');
          strokeWeight(tier === 2 ? 1 : tier === 3 ? 1.4 : 1.7);
          noFill();
          circle(m.offsetX, m.offsetY, size + 1.3);
          fill(m.color);
        }
      }
    }
    pop();
  }
}