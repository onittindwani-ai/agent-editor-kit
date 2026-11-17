# Pure function helpers

Small, dependency free helpers for any frame renderer. Each takes numbers and returns numbers. None reads a clock or a random source. Use them in Remotion components (pass the frame from the framework) or in a plain Python frame loop.

## Timeline file

One JSON file per graphic, seconds only, grouped by scene:

```json
{
  "fps": 30,
  "scenes": {
    "intro": { "enter": 0.2, "exit": 3.4 },
    "reason1": { "word": 3.4, "enter": 3.27, "exit": 6.1 }
  }
}
```

`frame = round(seconds * fps)`. Offsets relative to a beat (`reason1.word - 0.12`) are fine. Never type a literal start time inside a component.

## TypeScript

```ts
// cubic bezier easing (same maths as CSS), solved by Newton iterations with a bisection fallback
export function bezier(x1: number, y1: number, x2: number, y2: number) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sx = (t: number) => ((ax * t + bx) * t + cx) * t;
  const sy = (t: number) => ((ay * t + by) * t + cy) * t;
  const dx = (t: number) => (3 * ax * t + 2 * bx) * t + cx;
  return (x: number): number => {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 8; i++) {
      const err = sx(t) - x;
      if (Math.abs(err) < 1e-6) return sy(t);
      const d = dx(t);
      if (Math.abs(d) < 1e-6) break;
      t -= err / d;
    }
    let lo = 0, hi = 1; t = x;
    while (lo < hi && hi - lo > 1e-6) {
      const v = sx(t);
      if (Math.abs(v - x) < 1e-6) break;
      if (x > v) lo = t; else hi = t;
      t = (hi + lo) / 2;
    }
    return sy(t);
  };
}

export const easeOut = bezier(0.16, 1, 0.3, 1);
export const easeIn = bezier(0.6, 0, 0.9, 0.35);
export const easeInOut = bezier(0.65, 0, 0.35, 1);

// progress 0..1 between two frames with an easing
export const prog = (f: number, f0: number, f1: number, ease = easeOut) =>
  ease(Math.min(1, Math.max(0, (f - f0) / Math.max(1, f1 - f0))));

// derive one value from another instead of giving it its own clock
export const band = (x: number, a: number, b: number) => Math.min(1, Math.max(0, (x - a) / (b - a)));

// seeded hash random in [0,1): same input, same output, forever
export function rand(seed: number): number {
  let h = (seed | 0) + 0x6d2b79f5;
  h = Math.imul(h ^ (h >>> 15), h | 1);
  h ^= h + Math.imul(h ^ (h >>> 7), h | 61);
  return ((h ^ (h >>> 14)) >>> 0) / 4294967296;
}

// closed form damped spring, no state between frames
export function spring(f: number, f0: number, damping = 14, stiffness = 140, mass = 0.8, fps = 30): number {
  const t = Math.max(0, (f - f0) / fps);
  const w0 = Math.sqrt(stiffness / mass);
  const zeta = damping / (2 * Math.sqrt(stiffness * mass));
  if (zeta < 1) {
    const wd = w0 * Math.sqrt(1 - zeta * zeta);
    return 1 - Math.exp(-zeta * w0 * t) * (Math.cos(wd * t) + (zeta * w0 / wd) * Math.sin(wd * t));
  }
  return 1 - Math.exp(-w0 * t) * (1 + w0 * t); // critically damped approximation
}
```

Blur to sharp entrance as a style from the frame:

```ts
const p = prog(frame, startFrame, startFrame + 8, easeOut);
const style = { opacity: p, filter: `blur(${(1 - p) * 10}px)`, transform: `scale(${0.94 + 0.06 * p})` };
```

(Opacity on a small chip is fine. For a full frame graphic that replaces the face, see `ae-transitions-and-blur`: use blur only, no opacity fade.)

## Python (for a Pillow or numpy frame loop)

```python
def bezier(x1, y1, x2, y2):
    cx, bx = 3 * x1, 3 * (x2 - x1) - 3 * x1
    ax = 1 - cx - bx
    cy, by = 3 * y1, 3 * (y2 - y1) - 3 * y1
    ay = 1 - cy - by
    sx = lambda t: ((ax * t + bx) * t + cx) * t
    sy = lambda t: ((ay * t + by) * t + cy) * t

    def ease(x):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(40):  # bisection, deterministic
            mid = (lo + hi) / 2
            if sx(mid) < x: lo = mid
            else: hi = mid
        return sy((lo + hi) / 2)
    return ease

ease_out = bezier(0.16, 1, 0.3, 1)

def prog(f, f0, f1, ease=ease_out):
    return ease(min(1.0, max(0.0, (f - f0) / max(1, f1 - f0))))

def draw(frame, timeline, fps=30):
    """Return an image for this frame. Reads only its arguments."""
    ...
```

The frame loop is `for frame in range(total): save(draw(frame, timeline))`. Rendering in parallel chunks gives identical output because `draw` has no state.

## Sanity tests (cheap, run before a long render)

1. Render frame 120 twice, in separate processes; the files must be byte identical.
2. Render frames 119, 120, 121 in a different order than 120, 121, 119; each must equal its earlier render.
3. Grep the source for `Math.random`, `Date.now`, `performance.now`, `transition:`, `@keyframes` and `animation:`; the count must be zero.
