/* Flappy Bird Clone – Canvas Implementation */
(function () {
  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');

  // World constants
  const W = canvas.width;
  const H = canvas.height;
  const GROUND_H = 60;
  const SKY_H = H - GROUND_H;

  // Game tuning
  const GRAVITY = 0.5;
  const FLAP_VY = -8.5;
  const PIPE_GAP = 140;
  const PIPE_SPEED = 2.6;
  const PIPE_INTERVAL = 1500; // ms
  const MIN_PIPE_TOP = 60;

  // Bird
  const BIRD_X = 100;
  const BIRD_R = 16;

  let state = 'ready'; // 'ready' | 'running' | 'gameover'
  let score = 0;
  let best = 0;
  let birdY = SKY_H / 2;
  let birdVy = 0;
  let pipes = []; // { x, top, gap }
  let lastSpawn = 0;
  let lastTime = 0;

  function resetGame() {
    state = 'ready';
    score = 0;
    birdY = SKY_H / 2;
    birdVy = 0;
    pipes = [];
    lastSpawn = 0;
    lastTime = performance.now();
  }

  function startGame() {
    if (state === 'ready' || state === 'gameover') {
      state = 'running';
      score = 0;
      birdY = SKY_H / 2;
      birdVy = 0;
      pipes = [];
      lastSpawn = 0;
    }
  }

  function flap() {
    if (state === 'ready') startGame();
    if (state === 'running') birdVy = FLAP_VY;
    if (state === 'gameover') resetGame();
  }

  function spawnPipe() {
    const maxTop = SKY_H - PIPE_GAP - MIN_PIPE_TOP;
    const top = Math.floor(Math.random() * (maxTop - MIN_PIPE_TOP + 1)) + MIN_PIPE_TOP;
    pipes.push({ x: W + 40, top, gap: PIPE_GAP, scored: false });
  }

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  function circleRectCollide(cx, cy, cr, rx, ry, rw, rh) {
    const nx = clamp(cx, rx, rx + rw);
    const ny = clamp(cy, ry, ry + rh);
    const dx = cx - nx;
    const dy = cy - ny;
    return dx * dx + dy * dy <= cr * cr;
  }

  function update(dt) {
    if (state !== 'running') return;

    // Bird physics
    birdVy += GRAVITY;
    birdY += birdVy;

    // Ground collision
    if (birdY + BIRD_R >= SKY_H) {
      birdY = SKY_H - BIRD_R;
      gameOver();
    }

    // Pipes
    for (const p of pipes) {
      p.x -= PIPE_SPEED * (dt / 16.67); // scale with dt, baseline ~60fps
    }
    // Remove offscreen
    pipes = pipes.filter(p => p.x + 60 > -10);

    // Spawn timing
    lastSpawn += dt;
    if (lastSpawn >= PIPE_INTERVAL) {
      lastSpawn = 0;
      spawnPipe();
    }

    // Collision and scoring
    for (const p of pipes) {
      // Top pipe rect
      const topRect = { x: p.x, y: 0, w: 60, h: p.top };
      // Bottom pipe rect
      const bottomRect = { x: p.x, y: p.top + p.gap, w: 60, h: SKY_H - (p.top + p.gap) };

      const hitTop = circleRectCollide(BIRD_X, birdY, BIRD_R, topRect.x, topRect.y, topRect.w, topRect.h);
      const hitBottom = circleRectCollide(BIRD_X, birdY, BIRD_R, bottomRect.x, bottomRect.y, bottomRect.w, bottomRect.h);
      if (hitTop || hitBottom) {
        gameOver();
        break;
      }

      // Score when passing the center of the pipes once
      const centerX = p.x + topRect.w / 2;
      if (!p.scored && centerX < BIRD_X) {
        p.scored = true;
        score += 1;
        best = Math.max(best, score);
      }
    }
  }

  function gameOver() {
    state = 'gameover';
  }

  function drawBackground() {
    // Sky gradient is set via canvas bg; add subtle clouds
    ctx.save();
    ctx.globalAlpha = 0.15;
    ctx.fillStyle = '#ffffff';
    for (let i = 0; i < 6; i++) {
      const x = (i * 90 + (Date.now() / 50) % 90) % W;
      const y = 50 + (i % 3) * 40;
      ctx.beginPath();
      ctx.ellipse(x, y, 35, 18, 0, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  function drawGround() {
    ctx.fillStyle = '#a0522d';
    ctx.fillRect(0, SKY_H, W, GROUND_H);
    ctx.fillStyle = '#c18f5a';
    for (let x = 0; x < W; x += 20) {
      ctx.fillRect(x, SKY_H, 14, 8);
    }
  }

  function drawPipes() {
    for (const p of pipes) {
      ctx.fillStyle = '#2ecc71';
      // Top pipe
      ctx.fillRect(p.x, 0, 60, p.top);
      ctx.fillStyle = '#27ae60';
      ctx.fillRect(p.x - 2, p.top - 18, 64, 18);

      // Bottom pipe
      const by = p.top + p.gap;
      ctx.fillStyle = '#2ecc71';
      ctx.fillRect(p.x, by, 60, SKY_H - by);
      ctx.fillStyle = '#27ae60';
      ctx.fillRect(p.x - 2, by, 64, 18);
    }
  }

  function drawBird() {
    const tilt = Math.max(-0.5, Math.min(0.6, birdVy / 12));
    ctx.save();
    ctx.translate(BIRD_X, birdY);
    ctx.rotate(tilt);
    // Body
    ctx.fillStyle = '#f1c40f';
    ctx.beginPath();
    ctx.arc(0, 0, BIRD_R, 0, Math.PI * 2);
    ctx.fill();
    // Wing
    ctx.fillStyle = '#f39c12';
    ctx.beginPath();
    ctx.ellipse(-4, 2, 8, 6, -0.3, 0, Math.PI * 2);
    ctx.fill();
    // Eye
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(6, -5, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#2c3e50';
    ctx.beginPath();
    ctx.arc(8, -5, 2, 0, Math.PI * 2);
    ctx.fill();
    // Beak
    ctx.fillStyle = '#e67e22';
    ctx.beginPath();
    ctx.moveTo(18, -2);
    ctx.lineTo(26, 0);
    ctx.lineTo(18, 2);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  function drawScore() {
    ctx.fillStyle = '#ffffffdd';
    ctx.font = 'bold 48px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(String(score), W / 2, 72);

    ctx.fillStyle = '#ffffffbb';
    ctx.font = '14px system-ui, sans-serif';
    ctx.fillText(`Best: ${best}`, W / 2, 96);
  }

  function drawUI() {
    if (state === 'ready') {
      ctx.fillStyle = '#ffffffee';
      ctx.font = 'bold 24px system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Klik / Spasi untuk mulai', W / 2, H / 2 - 20);
      ctx.font = '16px system-ui, sans-serif';
      ctx.fillText('Lewati pipa sebanyak mungkin!', W / 2, H / 2 + 10);
    } else if (state === 'gameover') {
      ctx.fillStyle = '#ffffffee';
      ctx.font = 'bold 26px system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Game Over', W / 2, H / 2 - 10);
      ctx.font = '16px system-ui, sans-serif';
      ctx.fillText(`Skor: ${score}  ·  Best: ${best}`, W / 2, H / 2 + 18);
      ctx.fillText('Tekan R untuk restart', W / 2, H / 2 + 42);
    }
  }

  function render() {
    ctx.clearRect(0, 0, W, H);
    drawBackground();
    drawPipes();
    drawBird();
    drawGround();
    drawScore();
    drawUI();
  }

  function loop(ts) {
    if (!lastTime) lastTime = ts;
    const dt = Math.min(34, ts - lastTime); // clamp large frames
    lastTime = ts;

    update(dt);
    render();
    requestAnimationFrame(loop);
  }

  // Input
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
      e.preventDefault();
      flap();
    }
    if (e.code === 'KeyR') {
      resetGame();
    }
  });
  canvas.addEventListener('mousedown', flap);
  canvas.addEventListener('touchstart', (e) => { e.preventDefault(); flap(); }, { passive: false });

  // Start
  resetGame();
  requestAnimationFrame(loop);
})();

