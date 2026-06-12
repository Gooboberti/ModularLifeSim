// ==================== MAIN ENTRY POINT (Cleaned) ====================

// NOTE: Most globals are now in globals.js to avoid duplicates

let cheatsModalOpen = false;
let musicModalOpen = false;

// ==================== SETUP ====================
function setup() {
  let canvas = createCanvas(820, 580);
  canvas.parent('canvas-container');
  canvas.mousePressed(handleMousePress);

  centerX = width / 2;
  centerY = height / 2;

  greenZone = { x: 200, y: 290, baseR: 105, minR: 36, food: 320, maxFood: 420 };
  blueZone  = { x: 620, y: 290, baseR: 105, minR: 36, food: 320, maxFood: 420 };

  for (let i = 0; i < 12; i++) {
    creatures.push(new Creature(random(width), random(height)));
  }

  for (let i = 0; i < 110; i++) {
    vortexParticles.push(new VortexParticle());
  }

  for (let i = 0; i < 6; i++) {
    redHazards.push(new RedHazard());
  }

  if (creatures.length > 0) {
    selectCreature(creatures[0]);
  }

  console.log("MiniSimmy2 Split Test - Setup complete");
}

// ==================== DRAW ====================
function draw() {
  if (paused) return;

  background(12, 14, 22);

  let vortexStrength = settings.vortexMultiplier;
  let vortexDir = 1;

  // Draw zones
  fill(16, 185, 129, 65);
  circle(greenZone.x, greenZone.y, greenZone.baseR * 2);
  fill(56, 189, 248, 65);
  circle(blueZone.x, blueZone.y, blueZone.baseR * 2);

  // Update + draw creatures
  for (let c of creatures) {
    if (typeof c.update === 'function') c.update(true, vortexDir, vortexStrength, timeScale);
    if (typeof c.show === 'function') c.show();
  }

  // Draw vortex particles
  for (let p of vortexParticles) {
    if (typeof p.update === 'function') p.update(vortexDir, vortexStrength);
    if (typeof p.show === 'function') p.show();
  }

  // Draw red hazards
  for (let h of redHazards) {
    if (typeof h.update === 'function') h.update();
    if (typeof h.show === 'function') h.show();
  }

  // Floating texts
  for (let i = floatingTexts.length - 1; i >= 0; i--) {
    floatingTexts[i].update();
    floatingTexts[i].show();
    if (floatingTexts[i].life <= 0) floatingTexts.splice(i, 1);
  }

  if (frameCount % 30 === 0) {
    if (typeof updateMainStats === 'function') updateMainStats();
  }
}

// ==================== BASIC HELPERS ====================
function handleMousePress() {
  for (let c of creatures) {
    if (dist(mouseX, mouseY, c.x, c.y) < 14) {
      trackAlpha = false;
      selectCreature(c);
      return;
    }
  }
}

function selectCreature(c) {
  selectedCreature = c;
  console.log("Selected:", c ? c.name : null);
}

function addFloatingText(x, y, text, color = '#34d399') {
  floatingTexts.push(new FloatingText(x, y, text, color));
}

// Minimal FloatingText (in case utils file is missing)
if (typeof FloatingText === 'undefined') {
  class FloatingText {
    constructor(x, y, text, color = '#34d399') {
      this.x = x; this.y = y; this.text = text; this.color = color;
      this.life = 52; this.vy = -1.35; this.alpha = 255;
    }
    update() { this.y += this.vy; this.life--; this.alpha = map(this.life, 0, 52, 0, 255); }
    show() {
      if (this.life <= 0) return;
      push();
      translate(this.x, this.y);
      fill(red(this.color), green(this.color), blue(this.color), this.alpha);
      textAlign(CENTER); textSize(12);
      text(this.text, 0, 0);
      pop();
    }
  }
  window.FloatingText = FloatingText;
}

// Keyboard
function keyPressed() {
  if (key === ' ') paused = !paused;
  if (key === '+') timeScale = min(timeScale * 2, 8);
  if (key === '-') timeScale = max(timeScale / 2, 0.25);
}