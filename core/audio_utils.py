"""
core/audio_utils.py
───────────────────
Audio Manager untuk efek suara dan musik latar (BGM).
Fitur:
- Otomatis memuat file audio eksternal dari folder assets/music dan assets/sounds (jika ada).
- Fallback ke suara sintetis via numpy jika file belum dimasukkan (sehingga tidak pernah error/crash).
- Mendukung ganti lagu / SFX kapan saja hanya dengan menaruh file di assets/.
"""

import os
import pygame
import numpy as np


class SoundManager:
    _instance = None

    def __init__(self, base_assets_dir: str = "assets"):
        self.enabled = False
        self.base_dir = base_assets_dir
        self.music_dir = os.path.join(base_assets_dir, "music")
        self.sounds_dir = os.path.join(base_assets_dir, "sounds")

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.enabled = True
        except Exception:
            self.enabled = False

        self.custom_sounds = {}
        self.synth_sounds = {}

        if self.enabled:
            self._load_all_sounds()

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def _load_all_sounds(self):
        sound_keys = ["correct", "wrong", "launch", "star", "win", "hit"]
        for key in sound_keys:
            loaded = False
            # Cek apakah ada file kustom (.wav, .mp3, .ogg)
            for ext in [".wav", ".mp3", ".ogg"]:
                path = os.path.join(self.sounds_dir, f"{key}{ext}")
                if os.path.exists(path):
                    try:
                        self.custom_sounds[key] = pygame.mixer.Sound(path)
                        loaded = True
                        break
                    except Exception:
                        pass
            # Jika belum ada file, generate suara sintetis
            if not loaded:
                self.synth_sounds[key] = self._generate_synth_sound(key)

    def play(self, sound_name: str):
        if not self.enabled:
            return
        snd = self.custom_sounds.get(sound_name) or self.synth_sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def play_music(self, loop: bool = True):
        """Memutar musik latar dari assets/music/bgm.mp3 (atau .ogg / .wav)."""
        if not self.enabled:
            return
        for ext in [".mp3", ".ogg", ".wav"]:
            path = os.path.join(self.music_dir, f"bgm{ext}")
            if os.path.exists(path):
                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(0.4)
                    pygame.mixer.music.play(-1 if loop else 0)
                    return
                except Exception:
                    pass

    def stop_music(self):
        if self.enabled:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    # ── Generator Suara Sintetis (Retro Sci-Fi) ──────────────────────
    def _generate_synth_sound(self, key: str) -> pygame.mixer.Sound:
        sample_rate = 22050
        try:
            if key == "correct":
                # Double chime nada tinggi
                t1 = np.linspace(0, 0.1, int(sample_rate * 0.1), False)
                t2 = np.linspace(0, 0.18, int(sample_rate * 0.18), False)
                s1 = np.sin(2 * np.pi * 587.33 * t1) * np.linspace(0.8, 0.3, len(t1))
                s2 = np.sin(2 * np.pi * 880.00 * t2) * np.linspace(0.9, 0.0, len(t2))
                audio = np.concatenate([s1, s2])
            elif key == "wrong":
                # Low buzz lembut
                t = np.linspace(0, 0.22, int(sample_rate * 0.22), False)
                audio = np.sin(2 * np.pi * 160.0 * t) * np.linspace(0.6, 0.0, len(t))
            elif key == "launch":
                # Warp sweep naik
                dur = 0.35
                n = int(sample_rate * dur)
                t = np.linspace(0, dur, n, False)
                freqs = np.linspace(200, 750, n)
                phase = 2 * np.pi * np.cumsum(freqs) / sample_rate
                audio = np.sin(phase) * np.linspace(0.5, 0.0, n)
            elif key == "star":
                # Crystal sparkle
                t = np.linspace(0, 0.15, int(sample_rate * 0.15), False)
                audio = np.sin(2 * np.pi * 1174.66 * t) * np.linspace(0.7, 0.0, len(t))
            elif key == "hit":
                # Thud
                t = np.linspace(0, 0.15, int(sample_rate * 0.15), False)
                audio = (np.random.rand(len(t)) * 2 - 1) * np.linspace(0.5, 0.0, len(t))
            elif key == "win":
                # Tri-tone victory
                notes = [523.25, 659.25, 783.99, 1046.50]
                parts = []
                for f in notes:
                    t = np.linspace(0, 0.12, int(sample_rate * 0.12), False)
                    parts.append(np.sin(2 * np.pi * f * t) * np.linspace(0.8, 0.2, len(t)))
                audio = np.concatenate(parts)
            else:
                t = np.linspace(0, 0.1, int(sample_rate * 0.1), False)
                audio = np.sin(2 * np.pi * 440.0 * t) * 0.2

            mono = (audio * 0.3 * 32767).astype(np.int16)
            stereo = np.column_stack((mono, mono))
            return pygame.sndarray.make_sound(stereo)
        except Exception:
            return pygame.mixer.Sound(buffer=bytes([0]*100))
