// ==================== AUDIO SYSTEM ====================

function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    masterGain = audioCtx.createGain();
    compressor = audioCtx.createDynamicsCompressor();

    compressor.threshold.value = -18;
    compressor.knee.value = 8;
    compressor.ratio.value = 12;
    compressor.attack.value = 0.003;
    compressor.release.value = 0.25;

    masterGain.gain.value = masterVolume;
    masterGain.connect(compressor);
    compressor.connect(audioCtx.destination);
  }

  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

function playTone(freq, type = null, duration = 0.28, volume = 0.055, detune = 0, attack = 0.012, release = 0.22) {
  if (activeVoices > MAX_VOICES) return;
  activeVoices++;

  const ctx = getAudioContext();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  const filter = ctx.createBiquadFilter();

  osc.type = type || defaultWaveform;
  osc.frequency.value = freq * pitchShift;
  if (detune) osc.detune.value = detune;

  filter.type = 'lowpass';
  filter.frequency.value = 2100;

  const finalVol = volume * effectsVolume;
  gain.gain.value = 0;
  gain.gain.linearRampToValueAtTime(finalVol, ctx.currentTime + attack);
  gain.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + duration);

  osc.connect(filter);
  filter.connect(gain);
  gain.connect(masterGain);

  osc.start();

  setTimeout(() => {
    try { osc.stop(); } catch(e){}
    activeVoices = Math.max(0, activeVoices - 1);
  }, (duration + 0.12) * 1000);
}

function playBirthSound() {
  playTone(880, 'sine', 0.38, 0.04, 0, 0.02, 0.32);
  setTimeout(() => playTone(1108, 'sine', 0.30, 0.032, 12, 0.015, 0.26), 55);
  setTimeout(() => playTone(1320, 'sine', 0.24, 0.026, -8, 0.01, 0.22), 105);
}

function playEatSound(isGreenZone = true) {
  if (activeVoices > MAX_VOICES - 4) return;
  if (creatures.length > 90 && Math.random() > 0.25) return;
  if (Math.random() > soundDensity * 0.55) return;
  const base = isGreenZone ? 620 : 780;
  playTone(base, 'triangle', 0.20, 0.032, 0, 0.006, 0.18);
  setTimeout(() => playTone(base * 1.5, 'triangle', 0.13, 0.02, 5, 0.004, 0.12), 22);
}

function playDeathSound() {
  if (creatures.length > 110 && Math.random() > 0.4) return;
  playTone(220, 'sawtooth', 0.48, 0.038, 0, 0.02, 0.42);
  setTimeout(() => playTone(175, 'sine', 0.38, 0.028, -10, 0.012, 0.32), 75);
}

function playDepositSound() {
  playTone(540, 'sine', 0.24, 0.028, 0, 0.012, 0.22);
  setTimeout(() => playTone(680, 'sine', 0.17, 0.022, 8, 0.008, 0.15), 38);
}

function playPredatorFeedSound() {
  playTone(165, 'sawtooth', 0.22, 0.042, 0, 0.01, 0.20);
  setTimeout(() => playTone(210, 'sine', 0.16, 0.032, 15, 0.006, 0.14), 28);
}

function playExplosionSound() {
  if (activeVoices > MAX_VOICES + 1) return;

  const ctx = getAudioContext();

  const osc1 = ctx.createOscillator();
  const gain1 = ctx.createGain();
  const filter1 = ctx.createBiquadFilter();

  osc1.type = 'sawtooth';
  osc1.frequency.value = 85;
  filter1.type = 'lowpass';
  filter1.frequency.value = 420;

  gain1.gain.value = 0.16 * effectsVolume;
  gain1.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + 0.65);

  osc1.connect(filter1);
  filter1.connect(gain1);
  gain1.connect(masterGain);
  osc1.start();

  setTimeout(() => { try { osc1.stop(); } catch(e){} }, 720);

  setTimeout(() => {
    const osc2 = ctx.createOscillator();
    const gain2 = ctx.createGain();
    const noise = ctx.createBufferSource();
    const noiseFilter = ctx.createBiquadFilter();
    const noiseGain = ctx.createGain();

    osc2.type = 'square';
    osc2.frequency.value = 180;

    const buffer = ctx.createBuffer(1, ctx.sampleRate * 0.4, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < data.length; i++) {
      data[i] = Math.random() * 2 - 1;
    }
    noise.buffer = buffer;

    noiseFilter.type = 'bandpass';
    noiseFilter.frequency.value = 1200;
    noiseFilter.Q.value = 1.8;

    noiseGain.gain.value = 0.08 * effectsVolume;
    noiseGain.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + 0.45);

    osc2.connect(noiseFilter);
    noise.connect(noiseFilter);
    noiseFilter.connect(noiseGain);
    noiseGain.connect(masterGain);

    osc2.start();
    noise.start();

    setTimeout(() => {
      try { osc2.stop(); noise.stop(); } catch(e){}
    }, 500);
  }, 32);
}

function playWallBreakSound(sizeMult = 1) {
  if (activeVoices > MAX_VOICES + 2) return;
  activeVoices++;

  const ctx = getAudioContext();

  const noise = ctx.createBufferSource();
  const noiseFilter = ctx.createBiquadFilter();
  const noiseGain = ctx.createGain();

  const buffer = ctx.createBuffer(1, ctx.sampleRate * 0.55, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < data.length; i++) {
    data[i] = Math.random() * 2 - 1;
  }
  noise.buffer = buffer;

  noiseFilter.type = 'bandpass';
  noiseFilter.frequency.value = 2650 + sizeMult * 350;
  noiseFilter.Q.value = 4.2;

  noiseGain.gain.value = 0.26 * effectsVolume * Math.min(sizeMult, 1.7);
  noiseGain.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + 0.48);

  noise.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(masterGain);
  noise.start();

  setTimeout(() => {
    try { noise.stop(); } catch(e){}
    activeVoices = Math.max(0, activeVoices - 1);
  }, 550);

  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  const filter = ctx.createBiquadFilter();

  osc.type = 'sine';
  osc.frequency.value = 1720 + sizeMult * 280;

  filter.type = 'highpass';
  filter.frequency.value = 1350;

  gain.gain.value = 0.19 * effectsVolume;
  gain.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + 0.28);

  osc.connect(filter);
  filter.connect(gain);
  gain.connect(masterGain);
  osc.start();

  setTimeout(() => {
    try { osc.stop(); } catch(e){}
  }, 340);
}

// Add more audio functions (playShipShootSound, playBulletImpactSound, playAbsorbSound, etc.) as needed...