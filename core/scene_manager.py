"""
core/scene_manager.py
─────────────────────
Manajemen scene sederhana:
  - register(name, SceneClass) → daftarkan scene
  - switch(name)               → ganti scene aktif
  - update(dt, events)         → teruskan ke scene aktif
  - render()                   → gambar scene aktif ke screen
"""

import pygame


class SceneManager:
    def __init__(self, screen: pygame.Surface):
        self.screen       = screen
        self._registry    = {}   # name → SceneClass
        self._scene       = None  # instance aktif
        self.current_name = None

    # ── Public API ─────────────────────────────────────────────────
    def register(self, name: str, scene_cls):
        self._registry[name] = scene_cls

    def switch(self, name: str):
        if name not in self._registry:
            raise KeyError(f"Scene '{name}' belum di-register!")
        # Bersihkan scene lama
        if self._scene is not None and hasattr(self._scene, "on_exit"):
            self._scene.on_exit()
        # Buat instance baru & masukkan referensi manager
        self._scene = self._registry[name](self.screen, self)
        self.current_name = name
        if hasattr(self._scene, "on_enter"):
            self._scene.on_enter()

    def update(self, dt: float, events):
        if self._scene:
            self._scene.update(dt, events)

    def render(self):
        if self._scene:
            self._scene.render()
