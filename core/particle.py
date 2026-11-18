"""
core/particle.py
────────────────
Sistem partikel sederhana untuk efek visual.
Mendukung:
  - Emisi burst / stream
  - Gravity, fade, shrink
  - Warna gradient lerp
"""

import pygame
import random
import math
from core.math2d import lerp
from typing import Tuple, List


class Particle:
    def __init__(self, x, y, vx, vy,
                 color_start, color_end,
                 lifetime: float,
                 size: float = 4.0,
                 gravity: float = 0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color_start = color_start
        self.color_end   = color_end
        self.lifetime    = lifetime
        self.max_life    = lifetime
        self.size        = size
        self.gravity     = gravity
        self.alive       = True

    def update(self, dt: float):
        self.vy += self.gravity * dt
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surf: pygame.Surface):
        if not self.alive:
            return
        t  = 1.0 - (self.lifetime / self.max_life)   # 0 → 1 seiring waktu
        cr = int(lerp(self.color_start[0], self.color_end[0], t))
        cg = int(lerp(self.color_start[1], self.color_end[1], t))
        cb = int(lerp(self.color_start[2], self.color_end[2], t))
        a  = int(lerp(255, 0, t))
        sz = max(1, int(self.size * (1.0 - t * 0.6)))

        # Gambar ke surface temp untuk mendukung alpha
        tmp = pygame.Surface((sz*2, sz*2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (cr, cg, cb, a), (sz, sz), sz)
        surf.blit(tmp, (int(self.x) - sz, int(self.y) - sz))


class ParticleSystem:
    def __init__(self):
        self._particles: List[Particle] = []

    def emit_burst(self, x, y, count: int,
                   speed: float = 120,
                   color_start=(0,220,255),
                   color_end=(255,80,0),
                   lifetime: float = 1.2,
                   size: float = 5.0,
                   gravity: float = 60.0,
                   color=None):
        """Semburkan `count` partikel ke segala arah dari titik (x, y)."""
        if color is not None:
            color_start = color
            color_end = color
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            spd   = random.uniform(speed * 0.4, speed)
            vx    = math.cos(angle) * spd
            vy    = math.sin(angle) * spd
            lt    = random.uniform(lifetime * 0.5, lifetime)
            sz    = random.uniform(size * 0.5, size)
            self._particles.append(
                Particle(x, y, vx, vy,
                         color_start, color_end,
                         lt, sz, gravity)
            )

    def emit_stream(self, x, y,
                    angle_deg: float = -90,
                    spread_deg: float = 20,
                    speed: float = 80,
                    color_start=(255,200,60),
                    color_end=(255,60,0),
                    lifetime: float = 0.8,
                    size: float = 3.0,
                    gravity: float = 20.0,
                    count: int = 2):
        """Semburkan stream terarah (cocok untuk trail / thruster)."""
        base_rad = math.radians(angle_deg)
        half_sp  = math.radians(spread_deg / 2)
        for _ in range(count):
            a   = random.uniform(base_rad - half_sp, base_rad + half_sp)
            spd = random.uniform(speed * 0.6, speed)
            vx  = math.cos(a) * spd
            vy  = math.sin(a) * spd
            lt  = random.uniform(lifetime * 0.5, lifetime)
            sz  = random.uniform(size * 0.5, size)
            self._particles.append(
                Particle(x, y, vx, vy,
                         color_start, color_end,
                         lt, sz, gravity)
            )

    def update(self, dt: float):
        for p in self._particles:
            p.update(dt)
        self._particles = [p for p in self._particles if p.alive]

    def draw(self, surf: pygame.Surface):
        for p in self._particles:
            p.draw(surf)

    def clear(self):
        self._particles.clear()

    @property
    def count(self):
        return len(self._particles)
