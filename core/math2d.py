"""
core/math2d.py
──────────────
Utilitas matematika grafkom 2D berbasis MATRIKS HOMOGEN 3×3.

Transformasi yang didukung:
  - identity()           → matriks identitas
  - translate(tx, ty)    → translasi
  - scale(sx, sy)        → scaling (pivot opsional)
  - rotate(deg)          → rotasi sudut (derajat, CCW)
  - multiply(A, B)       → perkalian 2 matriks 3×3
  - transform_point(M,p) → terapkan matriks ke titik (x,y)
  - transform_points(M,pts) → terapkan ke list titik

Rasterisasi & Geometri:
  - lerp(a, b, t)             → interpolasi linier
  - bezier_cubic(p0,p1,p2,p3,t) → titik di kurva Bezier kubik
  - cohen_sutherland(p1,p2,rect) → clipping garis ke persegi
  - bresenham(x0,y0,x1,y1)   → piksel-piksel garis Bresenham

Lighting:
  - flat_shade(normal, light_dir, base_color) → warna hasil shading
"""

import math
import numpy as np
from typing import List, Tuple, Optional


# ── Alias Tipe ──────────────────────────────────────────────────────
Vec2  = Tuple[float, float]
Point = Tuple[float, float]
Mat3  = np.ndarray   # shape (3, 3)


# ══════════════════════════════════════════════════════════════════
#  TRANSFORMASI MATRIKS 3×3
# ══════════════════════════════════════════════════════════════════

def identity() -> Mat3:
    return np.eye(3, dtype=float)


def translate(tx: float, ty: float) -> Mat3:
    """Matriks translasi homogen."""
    M = identity()
    M[0, 2] = tx
    M[1, 2] = ty
    return M


def scale(sx: float, sy: float,
          cx: float = 0, cy: float = 0) -> Mat3:
    """
    Matriks scaling dengan titik pivot (cx, cy).
    Pivot default = origin.
    """
    T_in  = translate(-cx, -cy)
    S     = np.diag([sx, sy, 1.0])
    T_out = translate(cx, cy)
    return multiply(T_out, multiply(S, T_in))


def rotate(deg: float,
           cx: float = 0, cy: float = 0) -> Mat3:
    """
    Matriks rotasi (derajat, berlawanan jarum jam)
    dengan titik pivot (cx, cy).
    """
    rad   = math.radians(deg)
    c, s  = math.cos(rad), math.sin(rad)
    T_in  = translate(-cx, -cy)
    R     = np.array([[c, -s, 0],
                      [s,  c, 0],
                      [0,  0, 1]], dtype=float)
    T_out = translate(cx, cy)
    return multiply(T_out, multiply(R, T_in))


def multiply(A: Mat3, B: Mat3) -> Mat3:
    """Perkalian dua matriks 3×3."""
    return A @ B


def transform_point(M: Mat3, p: Point) -> Vec2:
    """Terapkan matriks M ke satu titik p=(x,y), hasilkan (x',y')."""
    v = np.array([p[0], p[1], 1.0])
    r = M @ v
    return (r[0], r[1])


def transform_points(M: Mat3, pts: List[Point]) -> List[Vec2]:
    """Batch-transform list titik."""
    # Susun jadi matriks Nx3
    arr = np.array([[p[0], p[1], 1.0] for p in pts])  # (N,3)
    res = (M @ arr.T).T                                 # (N,3)
    return [(r[0], r[1]) for r in res]


# ══════════════════════════════════════════════════════════════════
#  INTERPOLASI & KURVA
# ══════════════════════════════════════════════════════════════════

def lerp(a: float, b: float, t: float) -> float:
    """Interpolasi linier a→b dengan parameter t ∈ [0,1]."""
    return a + (b - a) * t


def lerp2(p0: Vec2, p1: Vec2, t: float) -> Vec2:
    """Lerp 2D."""
    return (lerp(p0[0], p1[0], t),
            lerp(p0[1], p1[1], t))


def bezier_cubic(p0: Vec2, p1: Vec2,
                 p2: Vec2, p3: Vec2,
                 t: float) -> Vec2:
    """
    Kurva Bezier kubik De Casteljau.
    t ∈ [0, 1]
    """
    def _lerp(a, b, tt):
        return (a[0] + (b[0]-a[0])*tt, a[1] + (b[1]-a[1])*tt)
    q0 = _lerp(p0, p1, t)
    q1 = _lerp(p1, p2, t)
    q2 = _lerp(p2, p3, t)
    r0 = _lerp(q0, q1, t)
    r1 = _lerp(q1, q2, t)
    return _lerp(r0, r1, t)


def bezier_points(p0, p1, p2, p3, steps=60):
    """Hasilkan list titik di sepanjang kurva Bezier kubik."""
    return [bezier_cubic(p0, p1, p2, p3, i/steps) for i in range(steps+1)]


# ══════════════════════════════════════════════════════════════════
#  CLIPPING — Cohen-Sutherland
# ══════════════════════════════════════════════════════════════════

INSIDE = 0
LEFT   = 1
RIGHT  = 2
BOTTOM = 4
TOP    = 8


def _region_code(x, y, xmin, ymin, xmax, ymax) -> int:
    code = INSIDE
    if x < xmin:   code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin:   code |= TOP      # layar: y bertambah ke bawah
    elif y > ymax: code |= BOTTOM
    return code


def cohen_sutherland(p1: Vec2, p2: Vec2,
                     rect: Tuple[int,int,int,int]
                     ) -> Optional[Tuple[Vec2, Vec2]]:
    """
    Clip garis p1-p2 ke rect=(xmin,ymin,xmax,ymax).
    Return (p1_clip, p2_clip) atau None jika garis sepenuhnya di luar.
    """
    xmin, ymin, xmax, ymax = rect
    x0, y0 = float(p1[0]), float(p1[1])
    x1, y1 = float(p2[0]), float(p2[1])
    code0  = _region_code(x0, y0, xmin, ymin, xmax, ymax)
    code1  = _region_code(x1, y1, xmin, ymin, xmax, ymax)

    while True:
        if not (code0 | code1):        # keduanya di dalam
            return ((x0, y0), (x1, y1))
        elif code0 & code1:            # keduanya di luar sisi yg sama
            return None
        else:
            code_out = code1 if code1 > code0 else code0
            if code_out & BOTTOM:
                x = x0 + (x1-x0) * (ymax - y0) / (y1-y0)
                y = ymax
            elif code_out & TOP:
                x = x0 + (x1-x0) * (ymin - y0) / (y1-y0)
                y = ymin
            elif code_out & RIGHT:
                y = y0 + (y1-y0) * (xmax - x0) / (x1-x0)
                x = xmax
            else:  # LEFT
                y = y0 + (y1-y0) * (xmin - x0) / (x1-x0)
                x = xmin
            if code_out == code0:
                x0, y0 = x, y
                code0 = _region_code(x0, y0, xmin, ymin, xmax, ymax)
            else:
                x1, y1 = x, y
                code1 = _region_code(x1, y1, xmin, ymin, xmax, ymax)


# ══════════════════════════════════════════════════════════════════
#  RASTERISASI — Bresenham's Line
# ══════════════════════════════════════════════════════════════════

def bresenham(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int,int]]:
    """
    Algoritma Bresenham: hasilkan list piksel (x, y) garis x0,y0 → x1,y1.
    """
    pixels = []
    dx =  abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        pixels.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0  += sx
        if e2 <= dx:
            err += dx
            y0  += sy
    return pixels


# ══════════════════════════════════════════════════════════════════
#  FLAT SHADING (Lighting sederhana)
# ══════════════════════════════════════════════════════════════════

def flat_shade(normal: Vec2, light_dir: Vec2,
               base_color: Tuple[int,int,int],
               ambient: float = 0.25) -> Tuple[int,int,int]:
    """
    Flat shading 2D:
      intensity = clamp(dot(normal, light_dir), 0, 1) + ambient
      warna_out = base_color * intensity
    normal & light_dir harus sudah dinormalisasi.
    """
    dot = normal[0]*light_dir[0] + normal[1]*light_dir[1]
    intensity = min(1.0, max(0.0, dot) + ambient)
    r = int(min(255, base_color[0] * intensity))
    g = int(min(255, base_color[1] * intensity))
    b = int(min(255, base_color[2] * intensity))
    return (r, g, b)


def normalize(v: Vec2) -> Vec2:
    """Normalisasi vektor 2D."""
    mag = math.hypot(v[0], v[1])
    if mag == 0:
        return (0.0, 0.0)
    return (v[0]/mag, v[1]/mag)
