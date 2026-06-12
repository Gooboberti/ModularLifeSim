// ==================== HAZARDS + RED PARTICLES ====================

class RedHazard {
  constructor() {
    this.x = random(width);
    this.y = random(height);
    this.vx = random(-1.2, 1.2);
    this.vy = random(-1.2, 1.2);
    this.size = random(4, 7);
    this.life = 9999;
    this.damage = 2.8;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;

    if (this.x < 0 || this.x > width) this.vx *= -1;
    if (this.y < 0 || this.y > height) this.vy *= -1;

    this.x = constrain(this.x, 0, width);
    this.y = constrain(this.y, 0, height);
  }

  show() {
    fill(239, 68, 68, 220);
    noStroke();
    circle(this.x, this.y, this.size);

    fill(255, 200, 200, 180);
    circle(this.x, this.y, this.size * 0.5);
  }
}

// Add more hazard-related functions here (spawnRedHazards, updateRedHazards, etc.)

function toggleRedHazardsQuick() {
  redHazardsEnabled = !redHazardsEnabled;
  const btn = document.getElementById('quick-red-btn');
  if (btn) {
    if (redHazardsEnabled) {
      btn.style.borderColor = '#f87171';
      btn.style.color = '#f87171';
    } else {
      btn.style.borderColor = '';
      btn.style.color = '';
    }
  }
}