import math
import pygame
import math
import os
import sys
import time
import pygame

from audio import AudioInput
from config import GameConfig
from screen import Screen


def load_image(path):
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return None


def main():
    config = GameConfig()
    audio = AudioInput()
    pygame.init()
    info = pygame.display.Info()
    width, height = 800, 600
    surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption("weird-tuber")
    clock = pygame.time.Clock()

    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    from avatar import Avatar

    avatar = Avatar.load_from_dir(assets_dir)

    font = pygame.font.Font(None, 24)
    screen = Screen(surface, font)

    # start audio input
    audio_started = audio.start()
    if audio_started:
        print("audio input started")
    else:
        print("audio input not available:", audio.get_last_error())

    show_debug = False
    scale = 1.0
    is_speaking = False
    manual_speaking = False
    speak_timer = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case config.quit_key:
                            running = False
                        case config.debug_key | config.debug_alt_key:
                            show_debug = not show_debug
                        case config.speak_key:
                            manual_speaking = not manual_speaking
                        case pygame.K_r:
                            audio.stop()
                            if audio.start():
                                print("audio input started on retry")
                            else:
                                print("audio retry failed:", audio.get_last_error())

        # update audio
        audio.update(
            dt,
            {
                "audio_smoothing": config.audio_smoothing,
                "audio_threshold": config.audio_threshold,
            },
        )
        if audio.is_available():
            audio_detected = audio.is_speaking(
                {"audio_threshold": config.audio_threshold}
            )
            is_speaking = manual_speaking or audio_detected

        if is_speaking:
            speak_timer += dt
        else:
            speak_timer *= 0.9

        # drawing
        screen.fill((0, 177, 64))
        w, h = screen.get_size()

        # draw avatar or parts; avatar.draw now returns (scale, anim_strength)
        scale, anim_strength = avatar.draw(
            surface, config, speak_timer, is_speaking, w, h, dt
        )

        screen.draw_debug(
            clock,
            audio,
            show_debug,
            avatar.top_img if avatar else None,
            avatar.bottom_img if avatar else None,
            avatar.avatar_img if avatar else None,
            scale,
            speak_timer,
            is_speaking,
            config,
            audio_detected=audio_detected if "audio_detected" in locals() else False,
            manual_speaking=manual_speaking,
            anim_strength=anim_strength,
        )

        screen.draw_text_center("Press Esc to quit", w / 2, h - 36, (180, 180, 180))

        screen.flip()

    audio.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
