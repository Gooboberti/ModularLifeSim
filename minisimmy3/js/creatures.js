// MiniSimmy3 - Creature Class (Improved)

class Creature {
  constructor(x, y, parentModules = null, generation = 1, parentTraits = null) {
    this.x = x;
    this.y = y;
    this.vx = random(-0.35, 0.35);
    this.vy = random(-0.35, 0.35);
    this.energy = parentModules ? 42 : 52 + random(16);
    this.name = generateSciFiName();
    this.isPredator = false;
    this.generation = generation;
    this.childrenCount = 0;
    this.killCount = 0;
    this.reproCooldown = 0;
    this.currentThought = "Exploring...";
    this.damageFlash = 0;
    this.specialization = 'balanced';

    // Traits
    if (parentTraits) {
      this.traits = { ...parentTraits };
    } else {
      this.traits = {
        pheromoneSensitivity: 1.0 + random(-0.12, 0.12),
        explorationBias: 1.0 + random(-0.12, 0.12),
        vortexResistance: 1.0 + random(-0.12, 0.12),
        hazardAvoidance: 1.0 + random(-0.12, 0.12)
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
      if (random() < 0.5) {
        let t = random(types);
        let ang = random(TWO_PI);
        let di = random(5, 8.5);
        this.modules.push({ type: t, color: colors[t], offsetX: cos(ang)*di, offsetY: sin(ang)*di, tier: 1 });
      }
    }

    this.updateSpecialization();
  }

  getModuleCount(type) { return this.modules.filter(m => m.type === type).length; }
  getTieredModuleCount(type) { return this.modules.filter(m => m.type === type).reduce((sum, m) => sum + (m.tier || 1), 0); }

  updateSpecialization() {
    if (this.modules.length === 0) {
      this.specialization = 'balanced'; return;
    }
    let counts = {};
    for (let m of this.modules) counts[m.type] = (counts[m.type] || 0) + (m.tier || 1);

    let maxType = null, maxCount = 0;
    for (let t in counts) if (counts[t] > maxCount) { maxCount = counts[t]; maxType = t; }
    this.specialization = maxType || 'balanced';
  }

  reproduce() {
    let newModules = this.modules.map(m => ({...m}));
    return new Creature(this.x + random(-7,7), this.y + random(-7,7), newModules, this.generation + 1, this.traits);
  }

  update(isDay, vortexDir, vortexStrength, timeScale = 1) {
    if (this.reproCooldown > 0) this.reproCooldown--;

    // Energy drain
    this.energy -= 0.26 * timeScale;

    // Zone attraction
    let tgt = isDay ? greenZone : blueZone;
    let d = dist(this.x, this.y, tgt.x, tgt.y);
    if (d > 12) {
      let pull = 0.045 + this.getTieredModuleCount('harvester') * 0.008;
      this.vx += (tgt.x - this.x) / d * pull;
      this.vy += (tgt.y - this.y) / d * pull;
    }

    // Vortex influence
    let cdist = dist(this.x, this.y, centerX, centerY);
    if (cdist > 18 && cdist < 380) {
      let tx = -(this.y - centerY);
      let ty = (this.x - centerX);
      let len = sqrt(tx*tx + ty*ty) || 1;
      let vForce = 0.65 * vortexStrength * vortexDir * (1 - (this.traits.vortexResistance - 1) * 0.3);
      this.vx += (tx / len) * vForce;
      this.vy += (ty / len) * vForce;

      let pull = 0.32 * vortexStrength;
      this.vx += (centerX - this.x) * pull / (cdist + 8);
      this.vy += (centerY - this.y) * pull / (cdist + 8);
    }

    // Apply velocity
    this.x += this.vx;
    this.y += this.vy;
    this.vx *= 0.83;
    this.vy *= 0.83;

    this.x = constrain(this.x, 8, width - 8);
    this.y = constrain(this.y, 8, height - 8);
  }

  show() {
    push();
    translate(this.x, this.y);
    let s = 6.5 + this.modules.length * 0.18;

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

    // Modules
    for (let m of this.modules) {
      fill(m.color);
      let tier = m.tier || 1;
      let size = 3 + (tier - 1) * 0.55;
      circle(m.offsetX || 0, m.offsetY || 0, size);

      if (tier > 1) {
        stroke(tier === 5 ? '#fde047' : '#fbbf24');
        strokeWeight(tier === 2 ? 1 : tier === 3 ? 1.3 : 1.6);
        noFill();
        circle(m.offsetX || 0, m.offsetY || 0, size + 1.4);
        fill(m.color);
      }
    }
    pop();
  }
}