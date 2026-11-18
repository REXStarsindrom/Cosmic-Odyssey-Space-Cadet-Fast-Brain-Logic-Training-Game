"""
scenes/pattern_scene.py
───────────────────────
Mission 3: Cyber Matrix — Number Sequence & Logic Code Breaker
Dirancang untuk usia SMA (~16 tahun):
- Melatih logika pola bilangan (Deret Aritmatika, Geometri, Fibonacci, Deret Bertingkat/TPA).
- Tampilan Sci-Fi Cyber Matrix dengan animasi terminal antariksa.
- Penjelasan rumus pola setelah menjawab agar menambah wawasan matematika.
"""

import pygame
import random
from core.draw_utils import draw_panel, draw_button, draw_fps
from core.particle import ParticleSystem
from core.audio_utils import SoundManager


class PatternScene:
    def __init__(self, screen: pygame.Surface, manager):
        self.screen = screen
        self.manager = manager
        self.W, self.H = screen.get_size()

        self.font_title = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_seq   = pygame.font.SysFont("consolas", 40, bold=True)
        self.font_hud   = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_btn   = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_sub   = pygame.font.SysFont("consolas", 18)
        self.font_hint  = pygame.font.SysFont("consolas", 20, bold=True)

        self.particles = ParticleSystem()
        self.sound = SoundManager.get()

        self.score = 0
        self.streak = 0
        self.round_num = 1

        self.btn_back_rect = (30, 24, 150, 42)

        # 4 pilihan tombol
        btn_w, btn_h = 320, 58
        start_x = self.W // 2 - 340
        start_y = self.H - 210
        self.btn_rects = [
            (start_x, start_y, btn_w, btn_h),
            (start_x + 360, start_y, btn_w, btn_h),
            (start_x, start_y + 75, btn_w, btn_h),
            (start_x + 360, start_y + 75, btn_w, btn_h)
        ]

        self.sequence = []
        self.correct_ans = 0
        self.options = []
        self.correct_idx = 0
        self.explanation = ""

        self.feedback_text = ""
        self.feedback_color = (0, 220, 255)
        self.show_expl_timer = 0.0

        self.generate_pattern()

    def on_enter(self):
        self.particles.clear()
        self.score = 0
        self.streak = 0
        self.round_num = 1
        self.generate_pattern()

    def generate_pattern(self):
        """Menghasilkan pola deret bilangan logika tingkat SMA/TPA."""
        p_type = random.choice(["arith", "geom", "fibo", "powers", "diff_inc", "alternating"])

        if p_type == "arith":
            # Deret Aritmatika: a, a+d, a+2d, a+3d
            start = random.randint(3, 20)
            diff = random.choice([3, 4, 6, 7, 8, 9, 12])
            seq = [start + i * diff for i in range(5)]
            ans = start + 5 * diff
            expl = f"Pola Aritmatika: Setiap angka bertambah +{diff}"

        elif p_type == "geom":
            # Deret Geometri: r = 2 atau 3
            start = random.choice([2, 3, 4, 5])
            r = random.choice([2, 3])
            seq = [start * (r ** i) for i in range(4)]
            ans = start * (r ** 4)
            expl = f"Pola Geometri: Setiap angka dikalikan ×{r}"

        elif p_type == "fibo":
            # Deret Fibonacci-style: Un = Un-1 + Un-2
            a = random.randint(1, 4)
            b = random.randint(2, 5)
            seq = [a, b]
            for _ in range(4):
                seq.append(seq[-1] + seq[-2])
            ans = seq[-1] + seq[-2]
            expl = "Pola Fibonacci: Penjumlahan dua angka sebelumnya"

        elif p_type == "powers":
            # Deret Kuadrat: 1^2, 2^2, 3^2, ... atau offset
            base = random.randint(1, 4)
            seq = [(base + i)**2 for i in range(5)]
            ans = (base + 5)**2
            expl = f"Pola Kuadrat n²: {(base+5)}² = {ans}"

        elif p_type == "diff_inc":
            # Beda bertingkat: +2, +4, +6, +8, ...
            val = random.randint(2, 10)
            seq = [val]
            step = random.choice([2, 3])
            for i in range(4):
                val += (i + 1) * step
                seq.append(val)
            ans = val + 5 * step
            expl = f"Pola Selisih Bertingkat: Selisih naik bertahap sebesar +{step}"

        else: # alternating
            # Operasi bergantian: misal ×2 lalu -1
            val = random.randint(3, 8)
            seq = [val]
            for i in range(2):
                val = val * 2
                seq.append(val)
                val = val - 2
                seq.append(val)
            ans = val * 2
            expl = "Pola Selang-Seling: Operasi ×2 lalu -2 secara bergantian"

        self.sequence = seq
        self.correct_ans = ans
        self.explanation = expl

        # Distractors
        distractors = set()
        diffs = [-2, 2, -1, 1, -diff if 'diff' in locals() else -5, 5, -10, 10]
        random.shuffle(diffs)
        for d in diffs:
            w = ans + d
            if w != ans and w > 0:
                distractors.add(w)
            if len(distractors) == 3:
                break
        while len(distractors) < 3:
            w = ans + random.randint(-15, 15)
            if w != ans and w > 0:
                distractors.add(w)

        opts = list(distractors) + [ans]
        random.shuffle(opts)
        self.options = opts
        self.correct_idx = opts.index(ans)

    def check_answer(self, idx: int):
        if idx == self.correct_idx:
            self.streak += 1
            self.round_num += 1
            added = 150 * self.streak
            self.score += added
            self.feedback_text = f"CODE DECRYPTED! +{added} PTS (STREAK x{self.streak})"
            self.feedback_color = (0, 255, 180)
            self.sound.play("correct")
            self.particles.emit_burst(self.W // 2, 240, count=40, speed=260, color=(0, 255, 200))
        else:
            self.streak = 0
            self.feedback_text = f"ACCESS DENIED! The code was {self.correct_ans}"
            self.feedback_color = (255, 70, 90)
            self.sound.play("wrong")

        self.show_expl_timer = 2.0
        self.generate_pattern()

    def update(self, dt: float, events):
        if self.show_expl_timer > 0:
            self.show_expl_timer -= dt

        self.particles.update(dt)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.manager.switch("menu")
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
                bx, by, bw, bh = self.btn_back_rect
                if bx <= mx <= bx+bw and by <= my <= by+bh:
                    self.manager.switch("menu")
                    return

                for i, (bx, by, bw, bh) in enumerate(self.btn_rects):
                    if bx <= mx <= bx+bw and by <= my <= by+bh:
                        self.check_answer(i)
                        break

    def render(self):
        self.screen.fill((6, 12, 20))

        # Cyber Grid Background
        for x in range(0, self.W, 60):
            pygame.draw.line(self.screen, (14, 25, 42), (x, 0), (x, self.H))
        for y in range(0, self.H, 60):
            pygame.draw.line(self.screen, (14, 25, 42), (0, y), (self.W, y))

        self.particles.draw(self.screen)

        # ── Header HUD ──
        draw_panel(self.screen, (0, 0, self.W, 70), color=(10, 18, 30), border_color=(0, 220, 255))

        # Back Button
        mx, my = pygame.mouse.get_pos()
        bx, by, bw, bh = self.btn_back_rect
        hover_b = bx <= mx <= bx+bw and by <= my <= by+bh
        draw_button(self.screen, self.font_hud, "← BACK [ESC]", self.btn_back_rect, hover=hover_b)

        # Title
        t_surf = self.font_title.render("MISSION 3: CYBER MATRIX CODE BREAKER", True, (0, 220, 255))
        self.screen.blit(t_surf, (self.W//2 - t_surf.get_width()//2, 18))

        # Score & Round HUD
        sc_surf = self.font_hud.render(f"SCORE: {self.score}", True, (255, 200, 60))
        st_surf = self.font_hud.render(f"STREAK: {self.streak}", True, (0, 255, 180))
        self.screen.blit(sc_surf, (self.W - 250, 12))
        self.screen.blit(st_surf, (self.W - 250, 38))

        # ── Tampilan Deret Bilangan Matrix ──
        panel_w, panel_h = 920, 140
        px = self.W // 2 - panel_w // 2
        py = 180
        draw_panel(self.screen, (px, py, panel_w, panel_h), color=(12, 20, 36), border_color=(0, 200, 255))

        # Format deret dengan slot '?'
        seq_str = "    ".join([str(n) for n in self.sequence]) + "    [ ? ]"
        seq_surf = self.font_seq.render(seq_str, True, (0, 240, 255))
        self.screen.blit(seq_surf, (self.W//2 - seq_surf.get_width()//2, py + 46))

        # Feedback & Explanation Banner
        if self.show_expl_timer > 0:
            fb_surf = self.font_hint.render(self.feedback_text, True, self.feedback_color)
            self.screen.blit(fb_surf, (self.W//2 - fb_surf.get_width()//2, py + 160))

            ex_surf = self.font_sub.render(f"Analisis: {self.explanation}", True, (200, 220, 255))
            self.screen.blit(ex_surf, (self.W//2 - ex_surf.get_width()//2, py + 195))
        else:
            hint_msg = "Tebak angka selanjutnya pada pola deret di atas! [Pilih 1, 2, 3, 4 atau Klik]"
            hm_surf = self.font_sub.render(hint_msg, True, (130, 160, 200))
            self.screen.blit(hm_surf, (self.W//2 - hm_surf.get_width()//2, py + 175))

        # ── 4 Tombol Pilihan Jawaban ──
        labels = ["A", "B", "C", "D"]
        for i, (bx, by, bw, bh) in enumerate(self.btn_rects):
            val = self.options[i] if i < len(self.options) else ""
            txt = f"[{labels[i]}]  {val}"
            hover = bx <= mx <= bx+bw and by <= my <= by+bh
            draw_button(self.screen, self.font_btn, txt, (bx, by, bw, bh), hover=hover)

        draw_fps(self.screen, self.font_sub, pygame.time.Clock().get_fps())
