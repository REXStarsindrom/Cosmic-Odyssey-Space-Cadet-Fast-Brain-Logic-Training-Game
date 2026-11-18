"""
scenes/particle_scene.py
─────────────────────────
Demo visual sistem partikel dengan berbagai mode emisi:
  1  → Burst ledakan
  2  → Stream api (thruster)
  3  → Rain / hujan partikel
  Klik kiri → emit burst di posisi kursor
  SPACE     → ganti mode emisi
  C         → clear semua partikel
"""

import pygame
import math
import random
from core.particle import ParticleSystem
from core.draw_utils import draw_panel, draw_grid, draw_fps, draw_text_centered


class ParticleScene:
    MODES = [
        "1 - Burst Ledakan",
        "2 - Stream Api",
        "3 - Rain Partikel",
    ]

    def __init__(self, screen: pygame.Surface, manager):
        self.screen  = screen
        self.manager = manager
        self.W, self.H = screen.get_size()

        self.font      = pygame.font.SysFont("consolas", 16)
        self.font_bold = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_sm   = pygame.font.SysFont("consolas", 13)

        self.ps    = ParticleSystem()
        self._mode = 0    # indeks mode saat ini
        self._timer = 0.0
        self._stream_x = self.W // 2
        self._stream_y = self.H // 2

    def update(self, dt, events):
        self._timer += dt

        # Stream & Rain auto emit
        if self._mode == 1:
            # Stream api mengikuti posisi mouse
            mx, my = pygame.mouse.get_pos()
            self.ps.emit_stream(
                mx, my,
                angle_deg=-90, spread_deg=30,
                speed=100,
                color_start=(255,230,80),
                color_end=(200,30,0),
                lifetime=0.9, size=5.0,
                gravity=25,
                count=4
            )
        elif self._mode == 2:
            # Hujan dari atas
            if int(self._timer * 20) % 1 == 0:
                self.ps.emit_stream(
                    random.randint(0, self.W), -10,
                    angle_deg=100, spread_deg=10,
                    speed=250,
                    color_start=(100,180,255),
                    color_end=(50,80,180),
                    lifetime=1.4, size=2.0,
                    gravity=0,
                    count=3
                )

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self._mode = 0
                elif event.key == pygame.K_2:
                    self._mode = 1
                elif event.key == pygame.K_3:
                    self._mode = 2
                elif event.key == pygame.K_SPACE:
                    self._mode = (self._mode + 1) % 3
                elif event.key == pygame.K_c:
                    self.ps.clear()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._mode == 0:
                    self.ps.emit_burst(
                        *event.pos, 60,
                        speed=200,
                        color_start=(0, 220, 255),
                        color_end=(255, 60, 0),
                        lifetime=1.5,
                        size=6.0,
                        gravity=80
                    )

        self.ps.update(dt)

    def render(self):
        self.screen.fill((8, 8, 15))
        draw_grid(self.screen, color=(18, 20, 32), cell=50)
        self.ps.draw(self.screen)

        # ── Panel Info ──
        draw_panel(self.screen, (10, 10, 350, 160),
                   color=(10,15,30), border_color=(0,160,220), alpha=200)
        self.screen.blit(self.font_bold.render("Particle System Demo", True, (0,220,255)), (20,18))
        self.screen.blit(self.font.render(f"Mode: {self.MODES[self._mode]}", True, (255,200,60)), (20,46))
        self.screen.blit(self.font.render(f"Partikel aktif: {self.ps.count}", True, (100,220,160)), (20,70))
        self.screen.blit(self.font_sm.render("1 / 2 / 3 atau SPACE → ganti mode", True, (100,140,180)), (20,96))
        self.screen.blit(self.font_sm.render("Klik kiri → burst (mode 1)", True, (100,140,180)), (20,116))
        self.screen.blit(self.font_sm.render("C → clear | ESC → menu", True, (80,110,150)), (20,136))

        # ── Mode hint di tengah bawah ──
        hint = {
            0: "Klik di mana saja → Burst Explosion",
            1: "Gerakkan mouse → Fire Stream mengikuti",
            2: "Partikel hujan otomatis dari atas",
        }
        lbl = self.font.render(hint[self._mode], True, (140,180,220))
        self.screen.blit(lbl, (self.W//2 - lbl.get_width()//2, self.H - 50))

        draw_fps(self.screen, self.font_sm, pygame.time.Clock().get_fps())
