"""
scenes/rocket_scene.py
──────────────────────
Mission 1: Rocket Warp — Speed Mental Math & Algebra Challenge
Dirancang untuk usia SMA (~16 tahun):
- Hitung cepat: Perkalian, Pembagian, Kuadrat, dan Aljabar Linier cepat.
- Fitur: Timer bar dinamis, Combo multiplier, Particle warp engine, Efek audio.
"""

import pygame
import random
import math
from core.draw_utils import draw_panel, draw_button, draw_text_centered, draw_fps
from core.particle import ParticleSystem
from core.audio_utils import SoundManager


class RocketScene:
    def __init__(self, screen: pygame.Surface, manager):
        self.screen = screen
        self.manager = manager
        self.W, self.H = screen.get_size()

        self.font_title = pygame.font.SysFont("consolas", 32, bold=True)
        self.font_sub   = pygame.font.SysFont("consolas", 18)
        self.font_q     = pygame.font.SysFont("consolas", 44, bold=True)
        self.font_btn   = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_hud   = pygame.font.SysFont("consolas", 20, bold=True)

        self.particles = ParticleSystem()
        self.sound = SoundManager.get()

        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.speed_kmh = 1000

        self.time_per_q = 12.0  # detik
        self.timer = self.time_per_q

        # Tombol kembali ke menu
        self.btn_back_rect = (30, 24, 150, 42)

        # Tombol 4 pilihan jawaban
        self.btn_rects = []
        btn_w, btn_h = 320, 60
        start_x = self.W // 2 - 340
        start_y = self.H - 220
        # 2x2 grid
        self.btn_rects = [
            (start_x, start_y, btn_w, btn_h),
            (start_x + 360, start_y, btn_w, btn_h),
            (start_x, start_y + 80, btn_w, btn_h),
            (start_x + 360, start_y + 80, btn_w, btn_h)
        ]

        self.current_q = ""
        self.q_type = ""
        self.options = []
        self.correct_idx = 0
        self.feedback_text = ""
        self.feedback_color = (0, 220, 255)
        self.feedback_timer = 0.0

        # Posisi roket
        self.rocket_y = self.H // 2 - 40
        self.rocket_target_y = self.rocket_y
        self.shake_x = 0.0

        self.generate_question()

    def on_enter(self):
        self.particles.clear()
        self.score = 0
        self.combo = 0
        self.timer = self.time_per_q
        self.speed_kmh = 1000
        self.generate_question()

    def generate_question(self):
        """Menghasilkan soal matematika cepat level SMA."""
        q_type = random.choice(["mult", "mult_hard", "div", "sq", "algebra"])
        self.q_type = q_type

        if q_type == "mult":
            a = random.randint(6, 15)
            b = random.randint(4, 9)
            ans = a * b
            q_text = f"{a}  ×  {b}  =  ?"
        elif q_type == "mult_hard":
            a = random.randint(11, 19)
            b = random.choice([3, 4, 5, 6, 7])
            ans = a * b
            q_text = f"{a}  ×  {b}  =  ?"
        elif q_type == "div":
            b = random.randint(6, 12)
            ans = random.randint(5, 14)
            a = b * ans
            q_text = f"{a}  ÷  {b}  =  ?"
        elif q_type == "sq":
            a = random.choice([7, 8, 9, 11, 12, 13, 14, 15, 16])
            ans = a * a
            q_text = f"{a}²  =  ?"
        else: # algebra
            x_val = random.randint(2, 9)
            m = random.choice([2, 3, 4, 5])
            c = random.randint(1, 15)
            rhs = m * x_val + c
            ans = x_val
            q_text = f"Solve for x:  {m}x + {c} = {rhs}"

        self.current_q = q_text
        self.correct_ans = ans

        # 3 opsi salah yang mirip (believable distractors)
        distractors = set()
        offsets = [-10, 10, -2, 2, -1, 1, -5, 5, -3, 3]
        random.shuffle(offsets)
        for off in offsets:
            wrong = ans + off
            if wrong != ans and wrong > 0:
                distractors.add(wrong)
            if len(distractors) == 3:
                break
        while len(distractors) < 3:
            wrong = ans + random.randint(-15, 15)
            if wrong != ans and wrong > 0:
                distractors.add(wrong)

        opts = list(distractors) + [ans]
        random.shuffle(opts)
        self.options = opts
        self.correct_idx = opts.index(ans)
        self.timer = self.time_per_q

    def check_answer(self, chosen_idx: int):
        if chosen_idx == self.correct_idx:
            # Jawaban Benar
            self.combo += 1
            if self.combo > self.max_combo:
                self.max_combo = self.combo
            added = 100 * self.combo
            self.score += added
            self.speed_kmh += 500 * self.combo

            self.feedback_text = f"CORRECT! +{added} PTS  (COMBO x{self.combo}!)"
            self.feedback_color = (80, 255, 120)
            self.feedback_timer = 1.2
            self.sound.play("correct")
            self.sound.play("launch")

            # Partikel semburan warp engine
            rx = self.W // 2
            ry = self.rocket_y + 70
            self.particles.emit_burst(rx, ry, count=35, speed=280, color=(0, 220, 255))
            self.particles.emit_burst(rx, ry, count=25, speed=220, color=(255, 200, 60))
            self.rocket_target_y = max(180, self.rocket_y - 25)
        else:
            # Jawaban Salah
            self.combo = 0
            self.feedback_text = f"MISSED! Correct was {self.correct_ans}"
            self.feedback_color = (255, 80, 100)
            self.feedback_timer = 1.5
            self.shake_x = 12.0
            self.sound.play("wrong")
            self.rocket_target_y = min(self.H // 2 + 30, self.rocket_y + 15)

        self.generate_question()

    def update(self, dt: float, events):
        # Timer countdown
        self.timer -= dt
        if self.timer <= 0:
            # Timeout = missed
            self.check_answer(-1)

        if self.feedback_timer > 0:
            self.feedback_timer -= dt

        # Rocket smoothing
        self.rocket_y += (self.rocket_target_y - self.rocket_y) * 5.0 * dt

        # Shake decay
        if abs(self.shake_x) > 0.1:
            self.shake_x = -self.shake_x * 0.85
        else:
            self.shake_x = 0.0

        # Partikel knalpot roket terus mengalir
        rx = self.W // 2 + self.shake_x
        ry = self.rocket_y + 60
        self.particles.emit_stream(
            x=rx, y=ry, angle_deg=90, spread_deg=25, speed=120 + self.combo * 25,
            color_start=(0, 220, 255), color_end=(255, 100, 0),
            lifetime=0.5, size=3.5, gravity=10, count=2
        )
        self.particles.update(dt)

        # Event handling
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.manager.switch("menu")
                # Shortcut angka 1, 2, 3, 4
                elif event.key in (pygame.K_1, pygame.K_KP1):
                    self.check_answer(0)
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.check_answer(1)
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.check_answer(2)
                elif event.key in (pygame.K_4, pygame.K_KP4):
                    self.check_answer(3)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Cek tombol back
                bx, by, bw, bh = self.btn_back_rect
                if bx <= mx <= bx+bw and by <= my <= by+bh:
                    self.manager.switch("menu")
                    return

                # Cek tombol jawaban
                for i, (rx, ry, rw, rh) in enumerate(self.btn_rects):
                    if rx <= mx <= rx+rw and ry <= my <= ry+rh:
                        self.check_answer(i)
                        break

    def render(self):
        self.screen.fill((8, 12, 24))

        # Efek bintang antariksa meluncur ke bawah
        t = pygame.time.get_ticks() / 1000.0
        for i in range(40):
            sx = (i * 97) % self.W
            sy = ((i * 131) + int(t * (100 + (i % 5) * 80))) % self.H
            pygame.draw.circle(self.screen, (100, 150, 220), (sx, sy), 1 + (i % 2))

        # Partikel mesin roket
        self.particles.draw(self.screen)

        # Gambar Roket Futuristik
        rx = self.W // 2 + self.shake_x
        ry = self.rocket_y
        self._draw_rocket(rx, ry)

        # ── HUD Atas ──
        # Tombol Back
        mx, my = pygame.mouse.get_pos()
        bx, by, bw, bh = self.btn_back_rect
        hover_back = bx <= mx <= bx+bw and by <= my <= by+bh
        draw_button(self.screen, self.font_hud, "← BACK [ESC]", self.btn_back_rect, hover=hover_back)

        # Title
        t_surf = self.font_title.render("MISSION 1: ROCKET SPEED WARP", True, (0, 220, 255))
        self.screen.blit(t_surf, (self.W//2 - t_surf.get_width()//2, 24))

        # Skor & Speed HUD
        hud_score = self.font_hud.render(f"SCORE: {self.score}", True, (255, 200, 60))
        hud_speed = self.font_hud.render(f"VELOCITY: {self.speed_kmh} KM/S", True, (0, 220, 255))
        self.screen.blit(hud_score, (self.W - 240, 24))
        self.screen.blit(hud_speed, (self.W - 240, 52))

        if self.combo > 1:
            hud_combo = self.font_hud.render(f"🔥 COMBO x{self.combo}!", True, (255, 120, 40))
            self.screen.blit(hud_combo, (self.W - 240, 80))

        # ── Timer Bar ──
        bar_w, bar_h = 680, 12
        bar_x = self.W // 2 - bar_w // 2
        bar_y = 75
        ratio = max(0.0, min(1.0, self.timer / self.time_per_q))
        pygame.draw.rect(self.screen, (30, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        bar_col = (80, 255, 120) if ratio > 0.4 else ((255, 200, 40) if ratio > 0.2 else (255, 60, 60))
        pygame.draw.rect(self.screen, bar_col, (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=6)

        # ── Panel Pertanyaan ──
        panel_w, panel_h = 680, 90
        px = self.W // 2 - panel_w // 2
        py = self.H - 330
        draw_panel(self.screen, (px, py, panel_w, panel_h), color=(16, 22, 38), border_color=(0, 200, 255))

        q_surf = self.font_q.render(self.current_q, True, (255, 255, 255))
        self.screen.blit(q_surf, (self.W//2 - q_surf.get_width()//2, py + 22))

        # Feedback text
        if self.feedback_timer > 0:
            fb_surf = self.font_hud.render(self.feedback_text, True, self.feedback_color)
            self.screen.blit(fb_surf, (self.W//2 - fb_surf.get_width()//2, py - 35))

        # ── 4 Tombol Pilihan Jawaban ──
        labels = ["A", "B", "C", "D"]
        for i, (bx, by, bw, bh) in enumerate(self.btn_rects):
            val = self.options[i] if i < len(self.options) else ""
            txt = f"[{labels[i]}]  {val}"
            hover = bx <= mx <= bx+bw and by <= my <= by+bh
            draw_button(self.screen, self.font_btn, txt, (bx, by, bw, bh), hover=hover)

        draw_fps(self.screen, self.font_sub, pygame.time.Clock().get_fps())

    def _draw_rocket(self, cx, cy):
        """Menggambar roket futuristik berkecepatan tinggi."""
        # Body
        body_points = [
            (cx, cy - 45),        # Ujung hidung roket
            (cx + 22, cy + 20),   # Sisi kanan
            (cx + 16, cy + 55),   # Bawah kanan
            (cx - 16, cy + 55),   # Bawah kiri
            (cx - 22, cy + 20),   # Sisi kiri
        ]
        pygame.draw.polygon(self.screen, (220, 235, 255), body_points)
        pygame.draw.polygon(self.screen, (0, 220, 255), body_points, 2)

        # Sayap kiri & kanan
        pygame.draw.polygon(self.screen, (0, 160, 240), [(cx - 16, cy + 30), (cx - 38, cy + 60), (cx - 16, cy + 55)])
        pygame.draw.polygon(self.screen, (0, 160, 240), [(cx + 16, cy + 30), (cx + 38, cy + 60), (cx + 16, cy + 55)])

        # Kaca Cockpit bercahaya
        pygame.draw.circle(self.screen, (0, 255, 255), (int(cx), int(cy - 5)), 9)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(cx - 3), int(cy - 8)), 3)
