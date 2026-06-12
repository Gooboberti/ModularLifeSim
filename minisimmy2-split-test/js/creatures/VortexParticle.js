class VortexParticle {
  constructor(fromEdge = false) {
    if (fromEdge) {
      let angle = random(TWO_PI);
      let d = random(450, 570);
      this.x = centerX + cos(angle) * d;
      this.y = centerY + sin(angle) * d;
    } else {
      this.x = random(width);
      this.y = random(height);
    }
    this.life = 9999;
    this.size = random(1.6, 2.8);
  }

  update(vortexDir, vortexStrength) {
    let dx = this.x - centerX;
    let dy = this.y - centerY;
    let distToCenter = sqrt(dx * dx + dy * dy) || 1;
    if (distToCenter < 3.5) { this.life = 0; return; }

    let tangentX = -dy, tangentY = dx;
    let len = sqrt(tangentX * tangentX + tangentY * tangentY) || 1;

    this.x += (tangentX / len) * 1.25 * vortexStrength * vortexDir;
    this.y += (tangentY / len) * 1.25 * vortexStrength * vortexDir;

    let pull = 0.82 * vortexStrength;
    this.x += (centerX - this.x) * pull / (distToCenter + 0.8);
    this.y += (centerY - this.y) * pull / (distToCenter + 0.8);

    if (musicEnabled && musicData.bass > 0.35) {
      let jerk = (musicData.bass - 0.35) * 2.8;
      this.x += random(-jerk, jerk);
      this.y += random(-jerk, jerk);
    }
  }

  show() {
    fill(255, 255, 255, 185);
    noStroke();
    circle(this.x, this.y, this.size);
  }
}