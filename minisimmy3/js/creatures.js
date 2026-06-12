/**
 * MiniSimmy3 - Creature Class
 * 
 * This file defines the Creature class, which handles:
 * - Movement and behavior
 * - Module system and specialization
 * - Reproduction
 * - Visual rendering
 * 
 * The class is designed to be self-contained and easy to understand.
 */

class Creature {
  constructor(x, y, parentModules = null, generation = 1, parentTraits = null) {
    this.x = x;
    this.y = y;
    this.vx = random(-0.32, 0.32);
    this.vy = random(-0.32, 0.32);
    this.energy = parentModules ? 44 : 54 + random(14);
    this.name = generateSciFiName();
    this.isPredator = false;
    this.generation = generation;
    this.childrenCount = 0;
    this.reproCooldown = 0;
    this.specialization = 'balanced';
    this.role = 'Balanced';

    // Inherit or create traits
    if (parentTraits) {
      this.traits = { ...parentTraits };
    } else {
      this.traits = {
        pheromoneSensitivity: 1.0 + random(-0.11, 0.11),
        explorationBias: 1.0 + random(-0.11, 0.11),
        vortexResistance: 1.0 + random(-0.11, 0.11)
      };
    }

    // Module setup
    let types = ['harvester', 'sensor', 'mover', 'resistant', 'explorer', 'communicator'];
    let colors = {
      'harvester': '#34d399',
      'sensor': '#38bdf8',
      'mover': '#a78bfa',
      'resistant': '#f472b6',
      'explorer': '#fbbf24',
      'communicator': '#c084fc'
    };

    this.modules = parentModules ? parentModules.map(m => ({ ...m })) : [];

    // Give starting module with some chance
    if (!parentModules && random() < 0.52) {
      let t = random(types);
      let ang = random(TWO_PI);
      let di = random(5, 8);
      this.modules.push({
        type: t,
        color: colors[t],
        offsetX: cos(ang) * di,
        offsetY: sin(ang) * di,
        tier: 1
      });
    }

    this.updateSpecialization();
  }

  // ==================== HELPER METHODS ====================
  getModuleCount(type) {
    return this.modules.filter(m => m.type === type).length;
  }

  getTieredModuleCount(type) {
    return this.modules
      .filter(m => m.type === type)
      .reduce((sum, m) => sum + (m.tier || 1), 0);
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

    let maxT = null;
    let maxC = 0;
    for (let t in counts) {
      if (counts[t] > maxC) {
        maxC = counts[t];
        maxT = t;
      }
    }

    this.specialization = maxT || 'balanced';

    const tiered = this.getTieredModuleCount(this.specialization);
    if (tiered >= 3) this.role = 'Advanced ' + this.specialization;
    else if (tiered >= 2) this.role = 'Specialized ' + this.specialization;
    else this.role = this.specialization.charAt(0).toUpperCase() + this.specialization.slice(1);
  }

  reproduce() {
    return new Creature(
      this.x + random(-6, 6),
      this.y + random(-6, 6),
      this.modules.map(m => ({ ...m })),
      this.generation + 1,
      this.traits
    );
  }

  // ==================== UPDATE (Behavior) ====================
  update(isDay, vortexDir, vortexStrength, timeScale = 1, pheromones = []) {
    if (this.reproCooldown > 0) this.reproCooldown--;

    // Energy drain (reduced by Resistant modules)
    let drain = 0.25;
    const resistantBonus = this.getTieredModuleCount('resistant') * 0.035;
    this.energy -= (drain - resistantBonus) * timeScale;

    // Food zone attraction (stronger with Harvester modules)
    let tgt = isDay ? greenZone : blueZone;
    let d = dist(this.x, this.y, tgt.x, tgt.y);
    if (d > 10) {
      let pull = 0.042 + this.getTieredModuleCount('harvester') * 0.012;
      this.vx += (tgt.x - this.x) / d * pull;
      this.vy += (tgt.y - this.y) / d * pull;
    }

    // Vortex behavior (Mover/Explorer help escape)
    let cdist = dist(this.x, this.y, centerX, centerY);
    if (cdist > 15 && cdist < 390) {
      let tx = -(this.y - centerY);
      let ty = this.x - centerX;
      let len = sqrt(tx * tx + ty * ty) || 1;

      let escapeBonus = (this.getTieredModuleCount('mover') + this.getTieredModuleCount('explorer')) * 0.08;
      let vF = (0.55 + escapeBonus) * vortexStrength * vortexDir * (1 - (this.traits.vortexResistance - 1) * 0.25);

      this.vx += (tx / len) * vF;
      this.vy += (ty / len) * vF;

      let pull = 0.28 * vortexStrength;
      this.vx += (centerX - this.x) * pull / (cdist + 6);
      this.vy += (centerY - this.y) * pull / (cdist + 6);
    }

    // Pheromone attraction (stronger with Communicator modules)
    let pSense = this.traits.pheromoneSensitivity + this.getTieredModuleCount('communicator') * 0.08;
    for (let p of pheromones) {
      let pd = dist(this.x, this.y, p.x, p.y);
      if (pd < 70 && pd > 3) {
        let str = map(pd, 3, 70, 1.1, 0.18) * pSense * 0.75;
        this.vx += (p.x - this.x) / pd * str;
        this.vy += (p.y - this.y) / pd * str;
      }
    }

    // Predator behavior
    if (this.isPredator) {
      this.energy -= 0.12 * timeScale;
      for (let other of creatures) {
        if (other !== this && !other.isPredator && other.modules.length <= 1) {
          let od = dist(this.x, this.y, other.x, other.y);
          if (od < 55) {
            other.energy -= 18;
            this.energy += 12;
            if (other.energy <= 0 && random() < 0.6) {
              this.becomePredator();
            }
          }
        }
      }
    }

    // Apply velocity with friction
    this.x += this.vx;
    this.y += this.vy;
    this.vx *= 0.84;
    this.vy *= 0.84;

    // Keep on screen
    this.x = constrain(this.x, 8, width - 8);
    this.y = constrain(this.y, 8, height - 8);
  }

  // ==================== DRAW ====================
  show() {
    push();
    translate(this.x, this.y);

    let s = 6.8 + this.modules.length * 0.17;

    // Core color based on specialization
    let coreColor = this.isPredator ? '#f87171' : '#facc15';
    if (this.specialization === 'harvester') coreColor = '#34d399';
    if (this.specialization === 'sensor') coreColor = '#38bdf8';
    if (this.specialization === 'mover') coreColor = '#a78bfa';
    if (this.specialization === 'resistant') coreColor = '#f472b6';
    if (this.specialization === 'explorer') coreColor = '#fbbf24';
    if (this.specialization === 'communicator') coreColor = '#c084fc';

    // Predator glow
    if (this.isPredator) {
      fill(239, 68, 68, 40);
      noStroke();
      circle(0, 0, s + 7);
    }

    // Main body
    fill(coreColor);
    stroke(this.isPredator ? '#fecaca' : '#fef08c');
    strokeWeight(1.5);
    circle(0, 0, s);

    // Draw modules
    for (let m of this.modules) {
      fill(m.color);
      let tier = m.tier || 1;
      let size = 3.1 + (tier - 1) * 0.55;
      circle(m.offsetX || 0, m.offsetY || 0, size);

      if (tier > 1) {
        stroke(tier === 5 ? '#fde047' : '#fbbf24');
        strokeWeight(tier > 3 ? 1.5 : 1.1);
        noFill();
        circle(m.offsetX || 0, m.offsetY || 0, size + 1.5);
        fill(m.color);
      }
    }

    if (this.isPredator) {
      stroke(239, 68, 68, 220);
      strokeWeight(2.5);
      noFill();
      circle(0, 0, s + 5);
    }

    pop();
  }
}