"""
scenes/transform_scene.py
──────────────────────────
Demo interaktif transformasi 2D dengan matriks homogen 3×3:
  - Translasi (WASD)
  - Rotasi    (Q / E)
  - Scaling   (Z scaledown / X scaleup)
  - Reset     (R)
  - Tampilkan matriks hasil transformasi secara live
  - Toggle wireframe / filled (F)
Objek: Polygon bintang 7 ujung.
"""

import pygame
import math
from core.math2d import (identity, translate, rotate, scale,
                          multiply, transform_points, flat_shade, normalize)
from core.draw_utils import (draw_grid, draw_panel, draw_axes,
                               draw_text_centered, draw_fps)
import numpy as np


def star_polygon(cx, cy, n, r_outer, r_inner):
    """Hasilkan vertex bintang n-ujung."""
    pts = []
    for i in range(n * 2):
        r   = r_outer if i % 2 == 0 else r_inner
        ang = math.radians(i * 180 / n - 90)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


class TransformScene:
    SHAPE_COLOR  = (0, 180, 255)
    OUTLINE_COL  = (0, 220, 255)
    LABEL_COL    = (160, 200, 240)

    def __init__(self, screen: pygame.Surface, manager):
        self.screen  = screen
        self.manager = manager
        self.W, self.H = screen.get_size()

        self.font      = pygame.font.SysFont("consolas", 16)
        self.font_bold = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_sm   = pygame.font.SysFont("consolas", 13)
        self.font_mat  = pygame.font.SysFont("consolas", 14)

        # Objek: bintang 7 ujung di pusat layar
        self._origin_pts = star_polygon(0, 0, 7, 100, 45)

        # Matriks akumulasi transformasi
        self._M = identity()

        # State UI
        self._wireframe = False
        self._timer     = 0.0
        self._info_msg  = ""
        self._info_t    = 0.0

        # Translate speed (px/s), rotate speed (deg/s), scale step
        self.TRANS_SPEED = 180.0
        self.ROT_SPEED   = 90.0
        self.SCALE_STEP  = 0.02

        # Offset awal ke tengah layar
        self._M = multiply(translate(self.W//2, self.H//2), self._M)

    def _show(self, msg: str):
        self._info_msg = msg
        self._info_t   = 2.0

    def update(self, dt, events):
        self._timer += dt
        if self._info_t > 0:
            self._info_t -= dt

        keys = pygame.key.get_pressed()
        # Translasi
        if keys[pygame.K_w]:
            self._M = multiply(translate(0, -self.TRANS_SPEED * dt), self._M)
            self._show("Translasi  ↑")
        if keys[pygame.K_s]:
            self._M = multiply(translate(0,  self.TRANS_SPEED * dt), self._M)
            self._show("Translasi  ↓")
        if keys[pygame.K_a]:
            self._M = multiply(translate(-self.TRANS_SPEED * dt, 0), self._M)
            self._show("Translasi  ←")
        if keys[pygame.K_d]:
            self._M = multiply(translate( self.TRANS_SPEED * dt, 0), self._M)
            self._show("Translasi  →")

        # Pivot = posisi pusat objek saat ini (kolom 2 matriks)
        px, py = self._M[0,2], self._M[1,2]
        # Rotasi
        if keys[pygame.K_q]:
            self._M = multiply(rotate(-self.ROT_SPEED * dt, px, py), self._M)
            self._show("Rotasi  ↺")
        if keys[pygame.K_e]:
            self._M = multiply(rotate( self.ROT_SPEED * dt, px, py), self._M)
            self._show("Rotasi  ↻")
        # Scaling
        if keys[pygame.K_z]:
            f = 1.0 - self.SCALE_STEP
            self._M = multiply(scale(f, f, px, py), self._M)
            self._show("Scale  ↓")
        if keys[pygame.K_x]:
            f = 1.0 + self.SCALE_STEP
            self._M = multiply(scale(f, f, px, py), self._M)
            self._show("Scale  ↑")

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._M = multiply(translate(self.W//2, self.H//2), identity())
                    self._show("Reset!")
                if event.key == pygame.K_f:
                    self._wireframe = not self._wireframe
                    self._show("Wireframe: " + ("ON" if self._wireframe else "OFF"))

    def render(self):
        self.screen.fill((10, 10, 20))
        draw_grid(self.screen, color=(20, 26, 40), cell=40)

        # ── Gambar objek yang ditransformasi ──
        pts = transform_points(self._M, self._origin_pts)
        ipts = [(int(x), int(y)) for x, y in pts]

        if not self._wireframe:
            # Flat shade berdasarkan orientasi
            pygame.draw.polygon(self.screen, (0, 100, 180), ipts)
        pygame.draw.polygon(self.screen, self.OUTLINE_COL, ipts, 2)

        # Titik centroid (kolom tx, ty dari matriks)
        cx_obj = int(self._M[0, 2])
        cy_obj = int(self._M[1, 2])
        pygame.draw.circle(self.screen, (255, 200, 60), (cx_obj, cy_obj), 5)
        draw_axes(self.screen, (cx_obj, cy_obj), length=50)

        # ── Panel Kontrol ──
        draw_panel(self.screen, (10, 10, 300, 230),
                   color=(10,20,40), border_color=(0,160,220), alpha=190)
        lines = [
            ("Transformasi Interaktif", (0,220,255), self.font_bold),
            ("", None, None),
            ("WASD    = Translasi",     self.LABEL_COL, self.font),
            ("Q / E   = Rotasi  ↺ ↻",  self.LABEL_COL, self.font),
            ("Z / X   = Scale  ↓ ↑",   self.LABEL_COL, self.font),
            ("F       = Wireframe",     self.LABEL_COL, self.font),
            ("R       = Reset",         self.LABEL_COL, self.font),
            ("ESC     = Menu",          self.LABEL_COL, self.font),
        ]
        for i, (txt, col, fnt) in enumerate(lines):
            if txt and fnt:
                lbl = fnt.render(txt, True, col)
                self.screen.blit(lbl, (20, 18 + i*26))

        # ── Panel Matriks ──
        self._draw_matrix_panel()

        # ── Info msg ──
        if self._info_t > 0:
            alpha = min(255, int(self._info_t * 180))
            msg   = self.font_bold.render(self._info_msg, True, (255, 220, 60))
            self.screen.blit(msg, (self.W//2 - msg.get_width()//2, self.H - 80))

        draw_fps(self.screen, self.font_sm, pygame.time.Clock().get_fps())

    def _draw_matrix_panel(self):
        """Tampilkan matriks transformasi 3×3 secara live."""
        px, py = 10, 260
        pw, ph = 300, 150
        draw_panel(self.screen, (px, py, pw, ph),
                   color=(5,15,35), border_color=(80,120,180), alpha=200)

        self.screen.blit(self.font_bold.render("Matriks M (3×3)", True, (100,180,255)),
                          (px+10, py+10))
        M = self._M
        for row in range(3):
            row_str = "  ".join(f"{M[row,col]:+7.2f}" for col in range(3))
            lbl = self.font_mat.render(row_str, True, (160,220,180))
            self.screen.blit(lbl, (px+10, py+38 + row*32))

        # Determinan
        det = np.linalg.det(M)
        det_lbl = self.font_sm.render(f"det(M) = {det:.4f}", True, (120,160,120))
        self.screen.blit(det_lbl, (px+10, py+130))
