import math
from dataclasses import dataclass
import pygame


@dataclass
class GameConfig:
    # speaking animation
    speak_amplitude: float = 32  # pixels at scale=1 (exaggerated)
    speak_frequency: float = 3
    speak_rotation_frequency: float = 1
    speak_rotation_amplitude: float = math.radians(40)

    # layout
    gap: int = 8
    margin: int = 40

    # keybinds (map to pygame key constants)
    debug_key: int = pygame.K_BACKQUOTE  # '`'
    debug_alt_key: int = pygame.K_BACKQUOTE
    speak_key: int = pygame.K_SPACE
    quit_key: int = pygame.K_ESCAPE

    # audio detection
    audio_threshold: float = 0.01
    audio_smoothing: float = 0.85
