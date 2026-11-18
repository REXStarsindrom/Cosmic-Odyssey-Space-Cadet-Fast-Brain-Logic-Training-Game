"""
scenes/menu_scene.py
─────────────────────
Scene menu utama (Front Page):
- Tetap mempertahankan layout estetik asli:
  - Judul beranimasi wave (Bezier cubic)
  - Grid latar & partikel ambient melayang
  - Tombol-tombol navigasi interaktif dengan hover effect
  - Footer informasi
- Terkoneksi dengan 3 Misi Pembelajaran Edukasi Sains & Logika SMA.
- Memulai musik latar (BGM) jika tersedia di assets/music/bgm.mp3.
"""

import pygame
import math
import random
from core.draw_utils import draw_button, draw_grid, draw_fps
from core.particle import ParticleSystem
from core.math2d import bezier_cubic
from core.audio_utils import SoundManager


class MenuScene:
    BUTTONS = [
        ("rocket",    "🚀  Mission 1: Rocket Speed Warp"),
        ("collector", "🛸  Mission 2: Star Drifter Asteroid"),
        ("pattern",   "🪐  Mission 3: Cyber Matrix Code Breaker"),
    ]

    def __init__(self, screen: pygame.Surface, manager):
        self.screen  = screen
        self.manager = manager
        self.W, self.H = screen.get_size()

        self.font_title = pygame.font.SysFont("consolas", 48, bold=True)
        self.font_sub   = pygame.font.SysFont("consolas", 18)
        self.font_btn   = pygame.font.SysFont("consolas", 21, bold=True)

        self.particles = ParticleSystem()
        self.sound = SoundManager.get()
        self._timer    = 0.0
        self._title_y  = 0.0

        self._btn_rects = []
        btn_w, btn_h = 580, 56
        total = len(self.BUTTONS)
        start_y = self.H // 2 - 20
        for i in range(total):
            x = self.W // 2 - btn_w // 2
            y = start_y + i * (btn_h + 18)
            self._btn_rects.append((x, y, btn_w, btn_h))

    def on_enter(self):
        self.particles.clear()
        # Putar background music jika tersedia
        self.sound.play_music(loop=True)

    def update(self, dt: float, events):
        self._timer += dt

        # Partikel ambient floating bintang kosmik
        if int(self._timer * 12) % 2 == 0:
            self.particles.emit_stream(
                x=random.randint(0, self.W),
                y=self.H + 10,
                angle_deg=-90,
                spread_deg=60,
                speed=45,
                color_start=(0, 140, 220),
                color_end=(0, 240, 255),
                lifetime=4.5,
                size=2.5,
                gravity=-15,
                count=1
            )
        self.particles.update(dt)

        # Judul beranimasi wave (Bezier Curve)
        t_wave = (math.sin(self._timer * 1.5) + 1) / 2
        self._title_y = bezier_cubic(
            (0, self.H * 0.14),
            (0.3, self.H * 0.12),
            (0.7, self.H * 0.16),
            (1.0, self.H * 0.14),
            t_wave
        )[1]

        # Handle klik tombol
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, (name, _) in enumerate(self.BUTTONS):
                    rx, ry, rw, rh = self._btn_rects[i]
                    if rx <= mx <= rx+rw and ry <= my <= ry+rh:
                        self.sound.play("star")
                        self.manager.switch(name)

    def render(self):
        self.screen.fill((10, 10, 20))
        draw_grid(self.screen, color=(22, 28, 44), cell=50)
        self.particles.draw(self.screen)

        # ── Judul Animasi ──
        title = "COSMIC ODYSSEY: SPACE CADET"
        t_surf = self.font_title.render(title, True, (0, 220, 255))
        cx = self.W // 2 - t_surf.get_width() // 2
        self.screen.blit(t_surf, (cx, int(self._title_y)))

        sub = self.font_sub.render(
            "Sci-Fi Fast Brain & Logic Training  |  High Velocity Edition",
            True, (120, 170, 220))
        self.screen.blit(sub, (self.W//2 - sub.get_width()//2,
                                int(self._title_y) + 58))

        # ── Tombol Navigasi Menu ──
        mx, my = pygame.mouse.get_pos()
        for i, (name, label) in enumerate(self.BUTTONS):
            rx, ry, rw, rh = self._btn_rects[i]
            hover = rx <= mx <= rx+rw and ry <= my <= ry+rh
            draw_button(self.screen, self.font_btn, label,
                        (rx, ry, rw, rh), hover=hover)

        # ── Footer ──
        foot = self.font_sub.render("ESC → Keluar  |  Audio & BGM: assets/music/ & assets/sounds/", True, (70, 100, 140))
        self.screen.blit(foot, (self.W//2 - foot.get_width()//2, self.H - 36))

        draw_fps(self.screen, self.font_sub, pygame.time.Clock().get_fps())
