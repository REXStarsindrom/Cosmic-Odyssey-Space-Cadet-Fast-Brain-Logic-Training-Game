"""
scenes/demo_scene.py
─────────────────────
Demo utama yang menampilkan beberapa konsep grafkom sekaligus:
  1. Objek 3D Pseudo (Isometric Cube) dengan flat shading
  2. Clipping region dengan garis random
  3. Bezier curve interaktif (drag control point)
  4. Wireframe polygon + filled polygon berbeda
Navigasi panel kiri atas, semua teknik divisualisasikan.
"""

import pygame
import math
import random
from core.math2d import (rotate, scale, translate, multiply,
                          transform_points, normalize, flat_shade,
                          bezier_points, cohen_sutherland, lerp)
from core.draw_utils import (draw_grid, draw_panel, draw_text_centered,
                               draw_line_clipped, draw_bezier_curve,
                               draw_axes, draw_fps)
from core.particle import ParticleSystem
import numpy as np


# ── Definisi Kubus Isometrik (8 vertex, 12 edge) ───────────────────
# Proyeksi isometric sederhana dari koordinat 3D → 2D
def iso_project(x3, y3, z3, scale=1.0):
    """Proyeksi orthographic isometric ke layar 2D."""
    sx = (x3 - z3) * math.cos(math.radians(30)) * scale
    sy = (x3 + z3) * math.sin(math.radians(30)) * scale - y3 * scale
    return sx, sy


# Vertex kubus satuan di ruang 3D (x,y,z)  y=atas
CUBE_V3 = [
    (-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1),  # belakang
    (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1),  # depan
]
# Face kubus: (indeks vertex, normal arah, warna dasar)
CUBE_FACES = [
    ([4,5,6,7], ( 0,  0,  1), (60, 160, 255)),   # depan  (cyan)
    ([0,1,2,3], ( 0,  0, -1), (40, 100, 180)),   # belakang
    ([0,1,5,4], ( 0, -1,  0), (40,  80, 160)),   # bawah
    ([3,2,6,7], ( 0,  1,  0), (80, 200, 255)),   # atas   (terang)
    ([1,2,6,5], ( 1,  0,  0), (50, 130, 220)),   # kanan
    ([0,3,7,4], (-1,  0,  0), (30,  80, 150)),   # kiri
]
CUBE_EDGES = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (0,4),(1,5),(2,6),(3,7),
]


class DemoScene:
    def __init__(self, screen: pygame.Surface, manager):
        self.screen  = screen
        self.manager = manager
        self.W, self.H = screen.get_size()

        self.font      = pygame.font.SysFont("consolas", 16)
        self.font_bold = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_sm   = pygame.font.SysFont("consolas", 13)

        self._timer    = 0.0
        self._cube_rot = 0.0           # rotasi kubus (derajat)
        self._auto_rot = True

        # ── Bezier control points ──
        self._cp = [
            (self.W * 0.55, self.H * 0.65),
            (self.W * 0.65, self.H * 0.35),
            (self.W * 0.80, self.H * 0.60),
            (self.W * 0.90, self.H * 0.30),
        ]
        self._drag_idx = None

        # ── Clipping region ──
        self._clip_rect = (int(self.W*0.55), int(self.H*0.08),
                            int(self.W*0.90), int(self.H*0.45))
        self._rand_lines = []
        self._regen_lines()

        self.particles = ParticleSystem()

    def _regen_lines(self):
        """Generate ulang garis random untuk demo clipping."""
        self._rand_lines = []
        xmin, ymin, xmax, ymax = self._clip_rect
        cx, cy = (xmin+xmax)//2, (ymin+ymax)//2
        pad = 160
        for _ in range(20):
            x0 = random.randint(xmin-pad, xmax+pad)
            y0 = random.randint(ymin-pad, ymax+pad)
            x1 = random.randint(xmin-pad, xmax+pad)
            y1 = random.randint(ymin-pad, ymax+pad)
            self._rand_lines.append(((x0,y0),(x1,y1)))

    # ──────────────────────────────────────────────────────────────
    def update(self, dt, events):
        self._timer += dt
        if self._auto_rot:
            self._cube_rot = (self._cube_rot + 36 * dt) % 360

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._regen_lines()
                if event.key == pygame.K_SPACE:
                    self._auto_rot = not self._auto_rot
                if event.key == pygame.K_e:
                    # Burst partikel di tengah kubus
                    cx = self.W // 4
                    cy = self.H // 2
                    self.particles.emit_burst(cx, cy, 30, speed=150)

            # Drag bezier control points
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, (px, py) in enumerate(self._cp):
                    if math.hypot(mx-px, my-py) < 14:
                        self._drag_idx = i
                        break
            if event.type == pygame.MOUSEBUTTONUP:
                self._drag_idx = None
            if event.type == pygame.MOUSEMOTION and self._drag_idx is not None:
                self._cp[self._drag_idx] = event.pos

        self.particles.update(dt)

    def render(self):
        self.screen.fill((10, 10, 20))
        draw_grid(self.screen, color=(20, 26, 40), cell=40)

        self._draw_cube_section()
        self._draw_clipping_section()
        self._draw_bezier_section()
        self._draw_hud()

        self.particles.draw(self.screen)
        draw_fps(self.screen, self.font_sm, pygame.time.Clock().get_fps())

    # ── KUBUS ISOMETRIK ───────────────────────────────────────────
    def _draw_cube_section(self):
        cx = self.W // 4
        cy = self.H // 2 + 20
        s  = 90          # skala
        rot_y = self._cube_rot
        rot_x = 20       # sedikit miring ke bawah

        # Proyeksi vertex dengan rotasi Y
        def vert_proj(vi):
            vx, vy, vz = CUBE_V3[vi]
            # Rotasi Y sederhana
            rad = math.radians(rot_y)
            nx = vx*math.cos(rad) + vz*math.sin(rad)
            nz = -vx*math.sin(rad) + vz*math.cos(rad)
            # Rotasi X
            radx = math.radians(rot_x)
            ny2 = vy*math.cos(radx) - nz*math.sin(radx)
            nz2 = vy*math.sin(radx) + nz*math.cos(radx)
            # Isometric project
            px, py = iso_project(nx, ny2, nz2, scale=s)
            return (cx + int(px), cy + int(py))

        # Urutkan face by z-depth (painter algorithm sederhana)
        faces_depth = []
        for face_verts, normal, base_col in CUBE_FACES:
            pts3 = [CUBE_V3[i] for i in face_verts]
            # Rata-rata z dunia (setelah rotasi)
            avg_z = 0
            for vx, vy, vz in pts3:
                rad = math.radians(rot_y)
                nz_rot = -vx*math.sin(rad) + vz*math.cos(rad)
                avg_z += nz_rot
            avg_z /= len(pts3)
            faces_depth.append((avg_z, face_verts, normal, base_col))
        faces_depth.sort(key=lambda f: f[0])

        # Arah cahaya (atas-kiri) dinormalisasi
        light = normalize((-0.5, -1.0))

        for _, face_verts, normal_3d, base_col in faces_depth:
            pts2 = [vert_proj(i) for i in face_verts]
            # Normal 2D proyeksi (pakai X & Y dari normal 3D)
            n2 = normalize((normal_3d[0], normal_3d[1]))
            shaded = flat_shade(n2, light, base_col, ambient=0.3)
            pygame.draw.polygon(self.screen, shaded, pts2)
            pygame.draw.polygon(self.screen, (0, 220, 255), pts2, 1)

        # Label section
        draw_panel(self.screen, (10, 10, 340, 72),
                   color=(10,20,40), border_color=(0,160,220), alpha=180)
        self.screen.blit(self.font_bold.render("Isometric Cube  |  Flat Shading", True, (0,220,255)), (20,18))
        self.screen.blit(self.font_sm.render("SPACE: toggle rotasi  |  E: burst partikel", True, (100,160,200)), (20,42))
        self.screen.blit(self.font_sm.render("Teknik: Rotasi 3D → Proyeksi Iso → Painter → Flat Shade", True, (80,120,160)), (20, 60))

        draw_axes(self.screen, (cx - 10, cy + 10), length=60)

    # ── CLIPPING ──────────────────────────────────────────────────
    def _draw_clipping_section(self):
        xmin, ymin, xmax, ymax = self._clip_rect
        # Latar region clipping
        draw_panel(self.screen,
                   (xmin, ymin, xmax-xmin, ymax-ymin),
                   color=(5,15,30), border_color=(255,180,0), alpha=120)

        for (p0, p1) in self._rand_lines:
            # Garis asli (redup)
            pygame.draw.line(self.screen, (50,50,80), p0, p1, 1)
            # Garis ter-clip (terang)
            draw_line_clipped(self.screen, (255,200,60),
                               p0, p1, (xmin,ymin,xmax,ymax), width=2)

        # Label
        lx, ly = xmin + 8, ymin + 8
        self.screen.blit(self.font_bold.render("Cohen-Sutherland Clipping", True, (255,200,60)), (lx, ly))
        self.screen.blit(self.font_sm.render("R: regen garis random", True, (160,130,60)), (lx, ly+22))
        self.screen.blit(self.font_sm.render("⬛ garis asli   🟡 hasil clip", True, (140,120,60)), (lx, ly+38))

    # ── BEZIER ───────────────────────────────────────────────────
    def _draw_bezier_section(self):
        # Tangent garis kontrol
        pygame.draw.line(self.screen, (60,80,100),
                          (int(self._cp[0][0]), int(self._cp[0][1])),
                          (int(self._cp[1][0]), int(self._cp[1][1])), 1)
        pygame.draw.line(self.screen, (60,80,100),
                          (int(self._cp[2][0]), int(self._cp[2][1])),
                          (int(self._cp[3][0]), int(self._cp[3][1])), 1)

        # Kurva Bezier
        draw_bezier_curve(self.screen, (0,220,255), self._cp,
                           steps=80, width=3)

        # Control points
        for i, (px, py) in enumerate(self._cp):
            col  = (255,100,80) if i in (0,3) else (255,200,60)
            pygame.draw.circle(self.screen, col, (int(px), int(py)), 10)
            pygame.draw.circle(self.screen, (255,255,255), (int(px), int(py)), 10, 2)
            lbl = self.font_sm.render(f"P{i}", True, (200,200,200))
            self.screen.blit(lbl, (int(px)+12, int(py)-8))

        # Label
        lx = int(self._cp[0][0]) - 20
        ly = self.H - 70
        self.screen.blit(self.font_bold.render("Bezier Kubik (De Casteljau)", True, (0,220,255)),
                          (int(self.W*0.55), self.H - 70))
        self.screen.blit(self.font_sm.render("Drag titik kontrol P0–P3", True, (80,160,200)),
                          (int(self.W*0.55), self.H - 48))

    # ── HUD ──────────────────────────────────────────────────────
    def _draw_hud(self):
        draw_panel(self.screen, (10, self.H-50, 320, 40),
                   color=(5,10,20), border_color=(40,80,120), alpha=180)
        self.screen.blit(self.font_sm.render("ESC: Menu Utama", True, (80,120,160)),
                          (20, self.H-38))
