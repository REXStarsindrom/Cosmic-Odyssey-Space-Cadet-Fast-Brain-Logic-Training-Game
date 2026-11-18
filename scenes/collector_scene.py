"""
scenes/collector_scene.py
─────────────────────────
Mission 2: Star Drifter — Kinetic Navigation & Reflex Challenge
Kontrol: Hybrid WASD / Tombol Panah ATAU Mouse Steering.
Tujuan:
- Kumpulkan 15 Cosmic Energy Cores (Bintang Kristal) di sabuk asteroid.
- Hindari benturan dengan asteroid yang melayang bebas.
- Shield = 0 → GAME OVER (pesawat hancur!).
- Fisika kapal ruang angkasa halus dengan inersia, rotasi, tilt/banking, & partikel thruster.
"""

import pygame
import random
import math
from core.draw_utils import draw_panel, draw_button, draw_fps
from core.particle import ParticleSystem
from core.audio_utils import SoundManager


class StarItem:
    def __init__(self, w, h):
        self.x = random.randint(80, w - 80)
        self.y = random.randint(100, h - 80)
        self.radius = 12
        self.pulse = random.random() * math.pi

    def update(self, dt):
        self.pulse += dt * 4.0

    def draw(self, surf):
        r = self.radius + math.sin(self.pulse) * 3
        # Glow
        pygame.draw.circle(surf, (100, 200, 255), (int(self.x), int(self.y)), int(r + 6), 2)
        # Core
        pygame.draw.circle(surf, (255, 230, 80), (int(self.x), int(self.y)), int(r))
        pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)), int(r * 0.4))


class Asteroid:
    def __init__(self, w, h):
        self.W = w
        self.H = h
        self.x = random.randint(50, w - 50)
        self.y = random.randint(80, h - 80)
        self.vx = random.uniform(-60, 60)
        self.vy = random.uniform(-60, 60)
        self.radius = random.randint(16, 26)
        self.angle = 0.0
        self.spin = random.uniform(-2, 2)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.spin * dt

        # Bounce screen edge
        if self.x - self.radius < 0 or self.x + self.radius > self.W:
            self.vx = -self.vx
            self.x = max(self.radius, min(self.W - self.radius, self.x))
        if self.y - self.radius < 70 or self.y + self.radius > self.H:
            self.vy = -self.vy
            self.y = max(70 + self.radius, min(self.H - self.radius, self.y))

    def draw(self, surf):
        pygame.draw.circle(surf, (80, 85, 100), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (120, 130, 150), (int(self.x), int(self.y)), self.radius, 2)
        # Kawah
        kx = self.x + math.cos(self.angle) * (self.radius * 0.4)
        ky = self.y + math.sin(self.angle) * (self.radius * 0.4)
        pygame.draw.circle(surf, (50, 55, 70), (int(kx), int(ky)), int(self.radius * 0.3))


class CollectorScene:
    TARGET_STARS = 15

    def __init__(self, screen: pygame.Surface, manager):
        self.screen = screen
        self.manager = manager
        self.W, self.H = screen.get_size()

        self.font_title = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_hud   = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_sub   = pygame.font.SysFont("consolas", 18)
        self.font_win   = pygame.font.SysFont("consolas", 46, bold=True)
        self.font_over  = pygame.font.SysFont("consolas", 52, bold=True)

        self.particles = ParticleSystem()
        self.sound = SoundManager.get()

        # Ship physics
        self.ship_x = self.W // 2
        self.ship_y = self.H // 2
        self.ship_vx = 0.0
        self.ship_vy = 0.0
        self.ship_angle = -math.pi / 2
        self.ship_radius = 18

        # Tilt / Banking — skew faktor untuk efek pseudo-3D
        self.tilt = 0.0           # -1.0 (miring kiri penuh) .. +1.0 (miring kanan penuh)
        self.tilt_target = 0.0

        self.shield = 100.0
        self.stars_collected = 0
        self.is_won = False
        self.is_dead = False         # GAME OVER state
        self.death_timer = 0.0       # Animasi ledakan sebelum overlay muncul
        self.death_particles_done = False

        self.stars = []
        self.asteroids = []

        self.btn_back_rect = (30, 20, 150, 40)
        self.reset_game()

    def reset_game(self):
        self.ship_x = self.W // 2
        self.ship_y = self.H // 2
        self.ship_vx = 0.0
        self.ship_vy = 0.0
        self.ship_angle = -math.pi / 2
        self.tilt = 0.0
        self.tilt_target = 0.0
        self.shield = 100.0
        self.stars_collected = 0
        self.is_won = False
        self.is_dead = False
        self.death_timer = 0.0
        self.death_particles_done = False
        self.particles.clear()

        # Spawn initial 5 stars
        self.stars = [StarItem(self.W, self.H) for _ in range(5)]
        # Spawn 6 asteroids
        self.asteroids = [Asteroid(self.W, self.H) for _ in range(6)]

    def on_enter(self):
        self.reset_game()

    def update(self, dt: float, events):
        # ── GAME OVER state ──────────────────────────────────────────
        if self.is_dead:
            self.death_timer += dt
            self.particles.update(dt)

            # Ledakan bertahap selama 1.5 detik pertama
            if self.death_timer < 1.5 and not self.death_particles_done:
                if int(self.death_timer * 20) % 2 == 0:
                    ox = self.ship_x + random.uniform(-20, 20)
                    oy = self.ship_y + random.uniform(-20, 20)
                    self.particles.emit_burst(ox, oy, count=8, speed=140,
                                              color=(255, random.randint(60, 180), 0))
                if self.death_timer >= 1.4:
                    self.death_particles_done = True

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.manager.switch("menu")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Cek tombol back dulu
                    mx, my = event.pos
                    bx, by, bw, bh = self.btn_back_rect
                    if bx <= mx <= bx+bw and by <= my <= by+bh:
                        self.manager.switch("menu")
                    elif self.death_timer > 1.5:
                        self.reset_game()
            return

        # ── VICTORY state ────────────────────────────────────────────
        if self.is_won:
            self.particles.update(dt)
            for event in events:
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                    self.reset_game()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.manager.switch("menu")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.reset_game()
            return

        # ── GAMEPLAY AKTIF ───────────────────────────────────────────
        # Input keyboard & mouse
        keys = pygame.key.get_pressed()
        ax, ay = 0.0, 0.0
        accel = 500.0
        lateral_input = 0.0   # -1 kiri, +1 kanan (untuk tilt)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            ay -= accel
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            ay += accel
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            ax -= accel
            lateral_input -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ax += accel
            lateral_input += 1.0

        # Mouse assistance steering (jika digerakkan atau klik kiri ditahan)
        mouse_buttons = pygame.mouse.get_pressed()
        mx, my = pygame.mouse.get_pos()
        if mouse_buttons[0]:
            ddx = mx - self.ship_x
            ddy = my - self.ship_y
            dist = math.hypot(ddx, ddy)
            if dist > 20:
                ax += (ddx / dist) * accel
                ay += (ddy / dist) * accel
                # Hitung lateral relatif terhadap arah hadap untuk tilt dari mouse
                perp = math.cos(self.ship_angle) * ddy - math.sin(self.ship_angle) * ddx
                lateral_input += max(-1.0, min(1.0, perp / dist * 2.0))

        # ── Tilt / Banking Animation ─────────────────────────────────
        # Tilt target berdasarkan input lateral, clamped ke [-1, 1]
        self.tilt_target = max(-1.0, min(1.0, lateral_input))
        # Smooth lerp menuju target, lalu decay kembali ke 0 jika tidak ada input
        lerp_speed = 8.0 if abs(lateral_input) > 0.1 else 4.0
        self.tilt += (self.tilt_target - self.tilt) * lerp_speed * dt

        # Update ship velocity with damping
        self.ship_vx += ax * dt
        self.ship_vy += ay * dt
        self.ship_vx *= 0.96
        self.ship_vy *= 0.96

        self.ship_x += self.ship_vx * dt
        self.ship_y += self.ship_vy * dt

        # Boundary clamping
        self.ship_x = max(self.ship_radius, min(self.W - self.ship_radius, self.ship_x))
        self.ship_y = max(70 + self.ship_radius, min(self.H - self.ship_radius, self.ship_y))

        # Ship angle towards velocity or mouse
        v_speed = math.hypot(self.ship_vx, self.ship_vy)
        if v_speed > 15:
            target_angle = math.atan2(self.ship_vy, self.ship_vx)
            # Emit engine thruster
            ex = self.ship_x - math.cos(target_angle) * self.ship_radius
            ey = self.ship_y - math.sin(target_angle) * self.ship_radius
            self.particles.emit_stream(
                x=ex, y=ey,
                angle_deg=math.degrees(target_angle) + 180,
                spread_deg=30, speed=160,
                color_start=(0, 240, 255), color_end=(255, 120, 20),
                lifetime=0.35, size=3.0, gravity=0, count=1
            )
            self.ship_angle = target_angle
        else:
            ddx = mx - self.ship_x
            ddy = my - self.ship_y
            if math.hypot(ddx, ddy) > 10:
                self.ship_angle = math.atan2(ddy, ddx)

        # Update stars
        for s in self.stars:
            s.update(dt)
            # Check collection
            if math.hypot(self.ship_x - s.x, self.ship_y - s.y) < (self.ship_radius + s.radius):
                self.stars.remove(s)
                self.stars_collected += 1
                self.sound.play("star")
                self.particles.emit_burst(s.x, s.y, count=30, speed=220, color=(255, 230, 80))
                # Spawn new star until target reached
                if (self.stars_collected + len(self.stars)) < self.TARGET_STARS:
                    self.stars.append(StarItem(self.W, self.H))
                break

        # Check win condition
        if self.stars_collected >= self.TARGET_STARS:
            self.is_won = True
            self.sound.play("win")
            self.particles.emit_burst(self.W // 2, self.H // 2, count=120, speed=350, color=(0, 255, 200))

        # Update Asteroids & collision
        for ast in self.asteroids:
            ast.update(dt)
            # Cek tabrakan dengan kapal
            dist = math.hypot(self.ship_x - ast.x, self.ship_y - ast.y)
            if dist < (self.ship_radius + ast.radius):
                # Repel
                angle = math.atan2(self.ship_y - ast.y, self.ship_x - ast.x)
                self.ship_vx += math.cos(angle) * 300
                self.ship_vy += math.sin(angle) * 300
                self.shield = max(0.0, self.shield - 8.0)
                self.sound.play("hit")
                self.particles.emit_burst(self.ship_x, self.ship_y, count=20, speed=180, color=(255, 80, 80))

                # ── SHIELD HABIS = GAME OVER ─────────────────────────
                if self.shield <= 0:
                    self.is_dead = True
                    self.death_timer = 0.0
                    self.death_particles_done = False
                    self.sound.play("wrong")
                    # Ledakan besar
                    self.particles.emit_burst(self.ship_x, self.ship_y,
                                              count=80, speed=300, color=(255, 160, 0))
                    self.particles.emit_burst(self.ship_x, self.ship_y,
                                              count=50, speed=200, color=(255, 60, 30))
                    self.particles.emit_burst(self.ship_x, self.ship_y,
                                              count=30, speed=120, color=(255, 255, 200))

        self.particles.update(dt)

        # Handle events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.manager.switch("menu")
                elif event.key == pygame.K_r:
                    self.reset_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                bx, by, bw, bh = self.btn_back_rect
                if bx <= mx <= bx+bw and by <= my <= by+bh:
                    self.manager.switch("menu")

    def render(self):
        self.screen.fill((8, 10, 22))

        # Background nebula & stars
        for i in range(50):
            sx = (i * 137) % self.W
            sy = ((i * 179) + 40) % self.H
            pygame.draw.circle(self.screen, (90, 110, 160), (sx, sy), 1 + (i % 2))

        # Draw Asteroids
        for ast in self.asteroids:
            ast.draw(self.screen)

        # Draw Stars / Cores
        for s in self.stars:
            s.draw(self.screen)

        # Draw Engine Particles
        self.particles.draw(self.screen)

        # Draw Sci-fi Player Ship (hanya jika belum mati / masih di awal ledakan)
        if not self.is_dead or self.death_timer < 0.3:
            self._draw_ship()

        # ── HUD Bar Atas ──
        draw_panel(self.screen, (0, 0, self.W, 64), color=(12, 16, 30), border_color=(0, 180, 240))

        # Back Button
        mx, my = pygame.mouse.get_pos()
        bx, by, bw, bh = self.btn_back_rect
        hover_b = bx <= mx <= bx+bw and by <= my <= by+bh
        draw_button(self.screen, self.font_hud, "← BACK [ESC]", self.btn_back_rect, hover=hover_b)

        # Title
        t_surf = self.font_title.render("MISSION 2: STAR DRIFTER", True, (0, 220, 255))
        self.screen.blit(t_surf, (self.W//2 - t_surf.get_width()//2, 16))

        # Stars Collected
        sc_txt = f"CORES: {self.stars_collected}/{self.TARGET_STARS}"
        sc_surf = self.font_hud.render(sc_txt, True, (255, 220, 60))
        self.screen.blit(sc_surf, (self.W - 320, 12))

        # Shield Bar (teks + visual bar)
        sh_txt = f"SHIELD: {int(self.shield)}%"
        sh_color = (0, 240, 255) if self.shield > 50 else ((255, 200, 40) if self.shield > 25 else (255, 60, 60))
        sh_surf = self.font_hud.render(sh_txt, True, sh_color)
        self.screen.blit(sh_surf, (self.W - 320, 36))

        # Visual shield bar di samping teks
        bar_x, bar_y, bar_w, bar_h = self.W - 180, 40, 150, 10
        pygame.draw.rect(self.screen, (30, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        fill_w = int(bar_w * max(0, self.shield) / 100.0)
        if fill_w > 0:
            pygame.draw.rect(self.screen, sh_color, (bar_x, bar_y, fill_w, bar_h), border_radius=5)

        # Guide Controls info
        guide_txt = "Controls: WASD / Arrow Keys or Hold Mouse to Drift  |  [R] Reset"
        g_surf = self.font_sub.render(guide_txt, True, (120, 160, 200))
        self.screen.blit(g_surf, (self.W//2 - g_surf.get_width()//2, self.H - 32))

        # ── Victory Screen ──
        if self.is_won:
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((5, 15, 30, 200))
            self.screen.blit(overlay, (0, 0))

            w_surf = self.font_win.render("HYPERDRIVE CHARGED!", True, (0, 255, 200))
            sub_w = self.font_hud.render("All Energy Cores Collected. Mission Accomplished!", True, (255, 255, 255))
            inst = self.font_sub.render("Press SPACE or CLICK to Play Again  |  [ESC] Menu", True, (255, 200, 60))

            cx = self.W // 2
            self.screen.blit(w_surf, (cx - w_surf.get_width()//2, self.H//2 - 60))
            self.screen.blit(sub_w, (cx - sub_w.get_width()//2, self.H//2 + 10))
            self.screen.blit(inst, (cx - inst.get_width()//2, self.H//2 + 55))

        # ── GAME OVER Screen ──
        if self.is_dead and self.death_timer > 1.5:
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            # Fade-in overlay: alpha naik dari 0 ke 210 selama 0.8 detik setelah delay
            fade_t = min(1.0, (self.death_timer - 1.5) / 0.8)
            overlay.fill((20, 5, 5, int(210 * fade_t)))
            self.screen.blit(overlay, (0, 0))

            if fade_t > 0.3:
                # Judul GAME OVER berkedip merah
                blink = int(self.death_timer * 3) % 2 == 0
                go_color = (255, 50, 50) if blink else (200, 30, 30)
                go_surf = self.font_over.render("SHIP DESTROYED", True, go_color)
                cx = self.W // 2
                self.screen.blit(go_surf, (cx - go_surf.get_width()//2, self.H//2 - 70))

                sub1 = self.font_hud.render("Shield depleted. Your ship has been obliterated.", True, (220, 180, 180))
                sub2 = self.font_hud.render(f"Energy Cores collected: {self.stars_collected}/{self.TARGET_STARS}", True, (255, 220, 60))
                inst = self.font_sub.render("Press SPACE or CLICK to Retry  |  [ESC] Menu", True, (200, 200, 200))

                self.screen.blit(sub1, (cx - sub1.get_width()//2, self.H//2))
                self.screen.blit(sub2, (cx - sub2.get_width()//2, self.H//2 + 35))
                self.screen.blit(inst, (cx - inst.get_width()//2, self.H//2 + 80))

        draw_fps(self.screen, self.font_sub, pygame.time.Clock().get_fps())

    def _draw_ship(self):
        """
        Menggambar kapal antariksa dengan Tilt / Banking Animation.
        Ketika berbelok ke kiri/kanan, sayap sisi dalam menyempit (scaling)
        memberikan ilusi pseudo-3D seolah pesawat miring.
        """
        cx, cy = self.ship_x, self.ship_y
        ang = self.ship_angle
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)

        # ── Tilt memengaruhi lebar sayap kiri vs kanan ──
        # tilt = -1 → miring kiri penuh (sayap kiri menyempit, kanan melebar)
        # tilt = +1 → miring kanan penuh (sayap kanan menyempit, kiri melebar)
        # Ini mensimulasikan scaling transformasi pada satu sisi polygon
        wing_base = 16.0
        wing_left_span  = wing_base * (1.0 - self.tilt * 0.55)   # tilt +1 → kecil
        wing_right_span = wing_base * (1.0 + self.tilt * 0.55)   # tilt +1 → besar

        def rot(px, py):
            """Rotasi titik (px, py) relatif terhadap pusat kapal."""
            return (cx + px * cos_a - py * sin_a,
                    cy + px * sin_a + py * cos_a)

        # Titik-titik kapal dengan sayap asimetris (tilt-aware)
        nose    = rot(24, 0)
        wing_l  = rot(-16, -wing_left_span)
        wing_r  = rot(-16,  wing_right_span)
        tail    = rot(-10, 0)
        # Sayap inner detail
        inner_l = rot(-8, -wing_left_span * 0.4)
        inner_r = rot(-8,  wing_right_span * 0.4)

        # ── Layer 1: Shadow / Depth layer (sisi yang "jauh") ──
        shadow_offset = self.tilt * 3.0
        shadow_pts = [
            (nose[0] + sin_a * shadow_offset, nose[1] - cos_a * shadow_offset),
            (wing_l[0] + sin_a * shadow_offset, wing_l[1] - cos_a * shadow_offset),
            (tail[0] + sin_a * shadow_offset, tail[1] - cos_a * shadow_offset),
            (wing_r[0] + sin_a * shadow_offset, wing_r[1] - cos_a * shadow_offset),
        ]
        pygame.draw.polygon(self.screen, (40, 60, 90), shadow_pts)

        # ── Layer 2: Body utama ──
        body = [nose, wing_l, tail, wing_r]
        pygame.draw.polygon(self.screen, (190, 220, 255), body)
        pygame.draw.polygon(self.screen, (0, 200, 255), body, 2)

        # ── Layer 3: Stripe / Panel lines (detail futuristik) ──
        pygame.draw.line(self.screen, (100, 160, 220), inner_l, nose, 1)
        pygame.draw.line(self.screen, (100, 160, 220), inner_r, nose, 1)

        # ── Layer 4: Sayap kecil delta (wingtips) ──
        tip_l = rot(-18, -wing_left_span * 0.7)
        tip_r = rot(-18,  wing_right_span * 0.7)
        mid_l = rot(-12, -wing_left_span * 0.9)
        mid_r = rot(-12,  wing_right_span * 0.9)
        pygame.draw.polygon(self.screen, (0, 140, 220), [wing_l, mid_l, tip_l])
        pygame.draw.polygon(self.screen, (0, 140, 220), [wing_r, mid_r, tip_r])

        # ── Layer 5: Nozzle engine glow ──
        noz_l = rot(-14, -4)
        noz_r = rot(-14,  4)
        noz_c = rot(-16,  0)
        glow_intensity = 180 + int(math.sin(pygame.time.get_ticks() / 80.0) * 60)
        pygame.draw.circle(self.screen, (0, glow_intensity, 255),
                           (int(noz_c[0]), int(noz_c[1])), 4)

        # ── Layer 6: Cockpit dome (berkilau) ──
        cockpit = rot(6, 0)
        pygame.draw.circle(self.screen, (0, 255, 255), (int(cockpit[0]), int(cockpit[1])), 6)
        # Specular highlight
        spec = rot(4, -2)
        pygame.draw.circle(self.screen, (220, 255, 255), (int(spec[0]), int(spec[1])), 2)
