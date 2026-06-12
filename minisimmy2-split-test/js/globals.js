// Globals extracted from original MiniSimmy2
// TODO: Move all global variable declarations here

let creatures = [];
let eggs = [];
const MAX_EGGS = 10;
let vortexParticles = [];
let pheromones = [];
let foodBlooms = [];
let energyOrbs = [];
let redHazards = [];
let explosions = [];
let floatingTexts = [];
let energyWalls = [];

let centerX, centerY;
let timeScale = 1;
let paused = false;
let simTime = 0;
let zoomLevel = 1.0;
let selectedCreature = null;
let trackAlpha = true;

let totalScore = 0;
let aetheriumCrystals = 0;
let aetheriumDust = 0;
let burningCrystals = 0;
let furnaceEndTime = 0;

let greenZone, blueZone;
let environmentPhase = 0;
let envPhaseProgress = 0;

// Add more globals as extracted...