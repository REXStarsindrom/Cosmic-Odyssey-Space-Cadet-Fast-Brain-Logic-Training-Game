"""
test_headless.py
────────────────
Test otomatis memuat dan me-render semua scene game tanpa display fisik.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from core.scene_manager import SceneManager
from core.audio_utils import SoundManager
from scenes.menu_scene import MenuScene
from scenes.rocket_scene import RocketScene
from scenes.collector_scene import CollectorScene
from scenes.pattern_scene import PatternScene

pygame.init()
screen = pygame.display.set_mode((1280, 720))
manager = SceneManager(screen)

manager.register("menu",      MenuScene)
manager.register("rocket",    RocketScene)
manager.register("collector", CollectorScene)
manager.register("pattern",   PatternScene)

snd = SoundManager.get()
snd.play("correct")
snd.play("star")
snd.play("launch")

scenes_to_test = ["menu", "rocket", "collector", "pattern"]

for name in scenes_to_test:
    manager.switch(name)
    manager.update(0.016, [])
    manager.render()
    print(f'Scene "{name}" OK')

print("\n=== Semua scene game anak SMA load & render 100% OK! ===")
pygame.quit()
