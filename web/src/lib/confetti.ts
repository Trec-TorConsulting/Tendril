"use client";

import confetti from "canvas-confetti";

/** Colorful burst from center — for grow completion, onboarding done */
export function fireBurst() {
  const defaults = {
    spread: 360,
    ticks: 70,
    gravity: 0.2,
    decay: 0.95,
    startVelocity: 20,
    colors: ["#22c55e", "#16a34a", "#4ade80", "#86efac", "#fbbf24", "#f59e0b"],
  };

  confetti({ ...defaults, particleCount: 50, scalar: 1.2, shapes: ["circle", "square"] });

  setTimeout(() => {
    confetti({ ...defaults, particleCount: 30, scalar: 0.8, shapes: ["circle"] });
  }, 150);
}

/** Side cannons — for harvest milestones */
export function fireCannons() {
  const end = Date.now() + 400;
  const colors = ["#22c55e", "#16a34a", "#fbbf24", "#f59e0b"];

  (function frame() {
    confetti({
      particleCount: 3,
      angle: 60,
      spread: 55,
      origin: { x: 0, y: 0.65 },
      colors,
    });
    confetti({
      particleCount: 3,
      angle: 120,
      spread: 55,
      origin: { x: 1, y: 0.65 },
      colors,
    });

    if (Date.now() < end) requestAnimationFrame(frame);
  })();
}

/** Subtle rain — for task streak completion */
export function fireRain() {
  confetti({
    particleCount: 40,
    spread: 100,
    origin: { y: 0 },
    gravity: 0.6,
    startVelocity: 10,
    ticks: 100,
    colors: ["#22c55e", "#86efac"],
    shapes: ["circle"],
    scalar: 0.7,
  });
}
