"""
core/draw_utils.py
──────────────────
Helper rendering: menggambar primitif grafkom ke pygame.Surface.
Semua fungsi menerima Surface sebagai target.
"""

import pygame
import math
from typing import List, Tuple, Optional
from core.math2d import bresenham, cohen_sutherland, transform_points, Mat3


# ── Warna utilitas ──────────────────────────────────────────────────
def color_lerp(c0, c1, t):
    """Interpolasi warna RGB."""
    return tuple(int(c0[i] + (c1[i]-c0[i])*t) for i in range(3))


# ══════════════════════════════════════════════════════════════════
#  PRIMITIF DASAR
# ══════════════════════════════════════════════════════════════════

def draw_line_bresenham(surf: pygame.Surface,
                        color, x0: int, y0: int,
                        x1: int, y1: int):
    """
    Gambar garis menggunakan algoritma Bresenham (manual piksel per piksel).
    Cocok untuk memvisualisasikan rasterisasi.
    """
    for px, py in bresenham(x0, y0, x1, y1):
        surf.set_at((px, py), color)


def draw_line_clipped(surf: pygame.Surface, color,
                      p0, p1, clip_rect: Tuple[int,int,int,int],
                      width: int = 1):
    """
    Gambar garis dengan clipping Cohen-Sutherland.
    clip_rect = (xmin, ymin, xmax, ymax)
    """
    result = cohen_sutherland(p0, p1, clip_rect)
    if result:
        a, b = result
        pygame.draw.line(surf, color,
                         (int(a[0]), int(a[1])),
                         (int(b[0]), int(b[1])), width)


def draw_polygon_transformed(surf: pygame.Surface, color,
                              vertices: List[Tuple[float,float]],
                              M: Mat3,
                              filled: bool = True, width: int = 2):
    """
    Gambar polygon setelah ditransformasi oleh matriks M (3×3 homogen).
    """
    pts = transform_points(M, vertices)
    ipts = [(int(x), int(y)) for x, y in pts]
    if len(ipts) >= 3:
        if filled:
            pygame.draw.polygon(surf, color, ipts)
        else:
            pygame.draw.polygon(surf, color, ipts, width)


def draw_bezier_curve(surf: pygame.Surface, color,
                      control_pts: List[Tuple[float,float]],
                      steps: int = 60, width: int = 2):
    """
    Gambar kurva Bezier kubik (harus 4 control points).
    """
    if len(control_pts) != 4:
        return
    from core.math2d import bezier_points
    pts = bezier_points(*control_pts, steps=steps)
    ipts = [(int(p[0]), int(p[1])) for p in pts]
    if len(ipts) >= 2:
        pygame.draw.lines(surf, color, False, ipts, width)


def draw_grid(surf: pygame.Surface,
              color=(40, 40, 60),
              cell: int = 40):
    """Gambar grid background."""
    w, h = surf.get_size()
    for x in range(0, w, cell):
        pygame.draw.line(surf, color, (x, 0), (x, h))
    for y in range(0, h, cell):
        pygame.draw.line(surf, color, (0, y), (w, y))


def draw_axes(surf: pygame.Surface, origin: Tuple[int,int],
              length: int = 80):
    """Gambar sumbu X (merah) dan Y (hijau) di titik origin."""
    ox, oy = origin
    pygame.draw.line(surf, (220, 60, 60), (ox, oy), (ox+length, oy), 2)
    pygame.draw.line(surf, (60, 220, 60), (ox, oy), (ox, oy-length), 2)
    # Label
    font = pygame.font.SysFont("consolas", 14)
    surf.blit(font.render("X", True, (220,60,60)),  (ox+length+4, oy-8))
    surf.blit(font.render("Y", True, (60,220,60)),  (ox-14, oy-length-4))


# ══════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════

def draw_panel(surf: pygame.Surface,
               rect: Tuple[int,int,int,int],
               color=(20, 20, 40),
               border_color=(0, 220, 255),
               border_width: int = 2,
               alpha: int = 200):
    """Gambar panel semi-transparan (glassmorphism-lite)."""
    x, y, w, h = rect
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((*color, alpha))
    surf.blit(panel, (x, y))
    pygame.draw.rect(surf, border_color, rect, border_width, border_radius=6)


def draw_button(surf: pygame.Surface, font: pygame.font.Font,
                text: str, rect: Tuple[int,int,int,int],
                color=(0, 220, 255), hover: bool = False) -> bool:
    """
    Gambar tombol, return True jika mouse sedang hover.
    """
    x, y, w, h = rect
    bg   = (30, 60, 80) if hover else (15, 30, 45)
    bord = (0, 255, 200) if hover else color
    draw_panel(surf, rect, color=bg[:3], border_color=bord, alpha=220)
    label = font.render(text, True, bord)
    lx    = x + (w - label.get_width())  // 2
    ly    = y + (h - label.get_height()) // 2
    surf.blit(label, (lx, ly))
    mx, my = pygame.mouse.get_pos()
    return x <= mx <= x+w and y <= my <= y+h


def draw_text_centered(surf: pygame.Surface, font: pygame.font.Font,
                       text: str, cx: int, cy: int,
                       color=(255,255,255)):
    img = font.render(text, True, color)
    surf.blit(img, (cx - img.get_width()//2, cy - img.get_height()//2))


def draw_fps(surf: pygame.Surface, font: pygame.font.Font,
             fps: float):
    color = (100, 255, 100) if fps >= 55 else (255, 200, 60) if fps >= 30 else (255, 60, 60)
    img   = font.render(f"FPS: {fps:.0f}", True, color)
    surf.blit(img, (surf.get_width() - img.get_width() - 10, 10))
