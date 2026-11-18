"""
main.py
───────
COSMIC ODESA: SPACE CADET
Entry point utama runner game.
"""

import pygame
import sys
from core.scene_manager import SceneManager
from scenes.menu_scene import MenuScene
from scenes.rocket_scene import RocketScene
from scenes.collector_scene import CollectorScene
from scenes.pattern_scene import PatternScene

WINDOW_TITLE  = "Cosmic Odesa: Space Cadet — Fast Brain & Logic Training"
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
TARGET_FPS    = 60


def main():
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock  = pygame.time.Clock()

    # --- Setup Scene Manager ---
    manager = SceneManager(screen)
    manager.register("menu",      MenuScene)
    manager.register("rocket",    RocketScene)
    manager.register("collector", CollectorScene)
    manager.register("pattern",   PatternScene)

    # Mulai dari menu utama
    manager.switch("menu")

    # --- Game Loop ---
    running = True
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0
        dt = min(dt, 0.05)  # clamp delta time

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and manager.current_name == "menu":
                    running = False

        manager.update(dt, events)
        manager.render()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
