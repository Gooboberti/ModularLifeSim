// MiniSimmy3 - Creature Class (Extracted & Cleaned)

class Creature {
  constructor(x, y, parentModules = null, generation = 1, parentTraits = null) {
    this.x = x;
    this.y = y;
    this.vx = random(-0.4, 0.4);
    this.vy = random(-0.4, 0.4);
    this.energy = parentModules ? 39 : 50 + random(18);
    this.name = generateSciFiName();
    this.isPredator = false;
    this.honey = 0;
    this.generation = generation;
    this.childrenCount = 0;
    this.killCount = 0;
    this.reproCooldown = 0;
    this.currentThought = "Exploring...";
    this.damageFlash = 0;
    this.purpleFlash = 0;
    this.mustEatWhite = false;
    this.adaptationLevel = 0;
    this.specialization = 'balanced';
    this.role = 'Balanced';

    // Traits
    if (parentTraits) {
      this.traits = { ...parentTraits };
    } else {
      this.traits = {
        pheromoneSensitivity: 1.0 + random(-0.13, 0.13),
        explorationBias: 1.0 + random(-0.13, 0.13),
        vortexResistance: 1.0 + random(-0.13, 0.13),
        hazardAvoidance: 1.0 + random(-0.13, 0.13)
      };
    }

    // Modules
    let types = ['harvester', 'sensor', 'mover', 'resistant', 'explorer', 'communicator'];
    let colors = {
      'harvester': '#34d399', 'sensor': '#38bdf8', 'mover': '#a78bfa',
      'resistant': '#f472b6', 'explorer': '#fbbf24', 'communicator': '#c084fc'
    };

    if (parentModules) {
      this.modules = parentModules.map(m => ({ ...m }));
    } else {
      this.modules = [];
      if (random() < 0.48) {
        let t = random(types);
        let ang = random(TWO_PI);
        let di = random(5, 9);
        this.modules.push({
          type: t, color: colors[t],
          offsetX: cos(ang) * di, offsetY: sin(ang) * di, tier: 1
        });
      }
    }

    this.updateSpecialization();
  }

  getModuleCount(type) {
    return this.modules.filter(m => m.type === type).length;
  }

  getTieredModuleCount(type) {
    return this.modules.filter(m => m.type === type).reduce((sum, m) => sum + (m.tier || 1), 0);
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
    // Role logic simplified for now
    this.role = this.specialization.charAt(0).toUpperCase() + this.specialization.slice(1);
  }

  reproduce() {
    let newModules = this.modules.map(m => ({...m}));
    // Tier upgrade logic can be added here later
    return new Creature(this.x + random(-6,6), this.y + random(-6,6), newModules, this.generation + 1, this.traits);
  }

  update(isDay, vortexDir, vortexStrength, timeScale = 1) {
    // Simplified update for initial modular version
    if (this.reproCooldown > 0) this.reproCooldown--;
    this.energy -= 0.28 * timeScale;

    // Basic movement toward zones
    let tgt = isDay ? {x: 200, y: 290} : {x: 620, y: 290};
    let d = dist(this.x, this.y, tgt.x, tgt.y);
    if (d > 10) {
      this.vx += (tgt.x - this.x) / d * 0.04;
      this.vy += (tgt.y - this.y) / d * 0.04;
    }

    this.x += this.vx;
    this.y += this.vy;
    this.vx *= 0.82;
    this.vy *= 0.82;

    this.x = constrain(this.x, 10, width - 10);
    this.y = constrain(this.y, 10, height - 10);
  }

  show() {
    push();
    translate(this.x, this.y);
    let s = 7 + this.modules.length * 0.2;

    let coreColor = this.isPredator ? '#f87171' : '#facc15';
    if (this.specialization === 'harvester') coreColor = '#34d399';
    if (this.specialization === 'sensor') coreColor = '#38bdf8';
    // ... add other specializations as needed

    fill(coreColor);
    stroke(this.isPredator ? '#fecaca' : '#fef08c');
    strokeWeight(1);
    circle(0, 0, s);

    // Draw modules
    for (let m of this.modules) {
      fill(m.color);
      const tier = m.tier || 1;
      const size = 3.2 + (tier - 1) * 0.6;
      circle(m.offsetX || 0, m.offsetY || 0, size);
    }
    pop();
  }
}