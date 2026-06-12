// ==================== MAIN ENTRY POINT ====================

let audioCtx, masterGain, compressor;
let masterVolume = 0.12;
let effectsVolume = 0.65;
let ambientVolume = 1.6;
let pitchShift = 0.98;
let soundDensity = 1.55;
let defaultWaveform = 'triangle';
let activeVoices = 0;
const MAX_VOICES = 26;

let musicEnabled = false;
let musicData = { subBass: 0, bass: 0, lowMids: 0, mids: 0, highMids: 0, highs: 0, volume: 0 };

let settings = {
  energyDrain: 0.28,
  particleFoodValue: 1.3,
  reproductionChance: 0.008,
  zoneAttraction: 0.075,
  socialResist: 0.14,
  vortexMultiplier: 4.5,
  pheromoneDeposit: 3.4,
  zonePullStrength: 0.5
};

let environmentPhase = 0;
let envPhaseProgress = 0;
let envCycleLength = 2200;

let redHazardsEnabled = true;
let redHazardIntensity = 1;
let cursorHazardActive = false;
let placedHazards = [];
let energyWalls = [];
let spaceshipActive = false;
let bullets = [];
let lastShotTime = 0;
let shipX = 400, shipY = 80;

let isDrawingWall = false;
let wallStartX = 0, wallStartY = 0;
let currentWallPreview = null;
let currentWallFilterMode = "repel_all";

let trackAlpha = true;
let isInspectorLocked = false;

let hidePrestigeWarning = false;

let geneVaultSlots = new Array(10).fill(null);
let eggs = [];
const MAX_EGGS = 10;

let totalScore = 0;
let totalPredatorKills = 0;
let aetheriumCrystals = 0;
let aetheriumDust = 0;
let burningCrystals = 0;
let furnaceEndTime = 0;

let greenZone, blueZone;
let centerX, centerY;
let selectedCreature = null;
let simTime = 0;
let timeScale = 1;
let paused = false;
let zoomLevel = 1.0;

let creatures = [];
let vortexParticles = [];
let pheromones = [];
let foodBlooms = [];
let staticFoodPatches = [];
let energyOrbs = [];
let redHazards = [];
let explosions = [];
let spawnEffects = [];
let floatingTexts = [];
let vortexProjectiles = [];

let evolutionHistory = [];
let graphData = { pop: [], modules: [], predators: [], greenFood: [], blueFood: [], hr: [] };

let miniChartCtx = null;
let envLabelElement = null;

let musicModalOpen = false;
let cheatsModalOpen = false;

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

  // Auto-select first creature
  if (creatures.length > 0) {
    selectCreature(creatures[0]);
  }

  createEnvLabel();
  updateMainStats();
  console.log("MiniSimmy2 Split Test - Setup complete");
}

// ==================== DRAW ====================
function draw() {
  if (paused) return;

  background(12, 14, 22);

  // Simple vortex + creatures for now
  let vortexStrength = settings.vortexMultiplier;
  let vortexDir = 1;

  // Draw zones
  fill(16, 185, 129, 65);
  circle(greenZone.x, greenZone.y, greenZone.baseR * 2);
  fill(56, 189, 248, 65);
  circle(blueZone.x, blueZone.y, blueZone.baseR * 2);

  // Update + draw creatures
  for (let c of creatures) {
    c.update(true, vortexDir, vortexStrength, timeScale);
    c.show();
  }

  // Draw vortex particles
  for (let p of vortexParticles) {
    p.update(vortexDir, vortexStrength);
    p.show();
  }

  // Draw red hazards
  for (let h of redHazards) {
    h.update();
    h.show();
  }

  // Simple floating text
  for (let i = floatingTexts.length - 1; i >= 0; i--) {
    floatingTexts[i].update();
    floatingTexts[i].show();
    if (floatingTexts[i].life <= 0) floatingTexts.splice(i, 1);
  }

  // Basic UI updates
  if (frameCount % 30 === 0) {
    updateMainStats();
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
  // TODO: Update inspector UI
  console.log("Selected:", c.name);
}

function createEnvLabel() {
  // Placeholder
}

function addFloatingText(x, y, text, color = '#34d399') {
  floatingTexts.push(new FloatingText(x, y, text, color));
}

class FloatingText {
  constructor(x, y, text, color = '#34d399') {
    this.x = x; this.y = y; this.text = text; this.color = color;
    this.life = 52; this.vy = -1.35; this.alpha = 255;
  }
  update() {
    this.y += this.vy; this.life--;
    this.alpha = map(this.life, 0, 52, 0, 255);
  }
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

// Keyboard controls
function keyPressed() {
  if (key === ' ') {
    paused = !paused;
  }
  if (key === '+') timeScale = min(timeScale * 2, 8);
  if (key === '-') timeScale = max(timeScale / 2, 0.25);
}