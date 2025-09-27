import math
import os
import json
from dataclasses import dataclass
import pygame
from typing import Optional


@dataclass
class GameConfig:
    # speaking animation
    speak_amplitude: float = 32  # pixels at scale=1 (exaggerated)
    speak_frequency: float = 3
    speak_rotation_frequency: float = 1
    speak_rotation_amplitude: float = math.radians(40)
    speak_rotation_threshold: float = 0.7
    speak_rotation_scale: float = 0.6
    anim_start_tau: float = 0.08
    anim_stop_tau: float = 0.9

    # layout
    gap: int = 2
    margin: int = 40

    # keybinds (map to pygame key constants)
    debug_key: int = pygame.K_BACKQUOTE  # '`'
    debug_alt_key: int = pygame.K_BACKQUOTE
    speak_key: int = pygame.K_SPACE
    quit_key: int = pygame.K_ESCAPE

    # audio detection
    audio_threshold: float = 0.02
    audio_smoothing: float = 0.85

    # assets paths
    assets_directory: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "assets"
    )
    icon_path: str = os.path.join(assets_directory, "avatar.png")

    # persisted preferences (saved to user_config.json)
    preferred_input_device: Optional[int] = None

    def _user_config_path(self) -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "user_config.json"
        )

    def load_user_config(self) -> None:
        path = self._user_config_path()
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # only load known keys
                if "preferred_input_device" in data:
                    self.preferred_input_device = data["preferred_input_device"]
        except Exception:
            # don't crash on malformed user config; ignore
            pass

    def save_user_config(self) -> None:
        path = self._user_config_path()
        try:
            data = {"preferred_input_device": self.preferred_input_device}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            # best-effort save; ignore errors
            pass
