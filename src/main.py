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
from avatar import Avatar


def load_image(path):
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return None


def main():
    config = GameConfig()
    # load persisted user preferences (preferred input device)
    config.load_user_config()
    audio = AudioInput()
    pygame.init()

    # assets paths are provided by the GameConfig
    assets_dir = config.assets_directory
    icon_path = config.icon_path
    icon_set = False
    if os.path.exists(icon_path):
        try:
            img = pygame.image.load(icon_path)
            # try a few conversion options and sizes to increase chance OS accepts it
            for conv in ("convert", "convert_alpha"):
                try:
                    icon_surf = getattr(img, conv)() if hasattr(img, conv) else img
                except Exception:
                    # fallback to raw surface
                    icon_surf = img

                # try common icon sizes
                for size in (32, 48, 64):
                    try:
                        if icon_surf.get_size() != (size, size):
                            scaled = pygame.transform.smoothscale(
                                icon_surf, (size, size)
                            )
                        else:
                            scaled = icon_surf
                        pygame.display.set_icon(scaled)
                        print(
                            f"set pygame icon from {icon_path} (size={size}, conv={conv})"
                        )
                        icon_set = True
                        break
                    except Exception:
                        continue

                if icon_set:
                    break
        except Exception as e:
            print("failed to load icon:", e)

    if not icon_set:
        # Some platforms (macOS) ignore the window icon for the dock/titlebar; set_icon may still be ignored.
        print(
            "using default pygame icon (no valid icon found or platform ignored set_icon)"
        )

    info = pygame.display.Info()
    width, height = 800, 600
    surface = pygame.display.set_mode((width, height))

    # call set_icon again after creating the window just in case
    try:
        if icon_set:
            pygame.display.set_icon(pygame.display.get_icon() or None)
    except Exception:
        pass
    pygame.display.set_caption("weird-tuber")
    clock = pygame.time.Clock()

    avatar = Avatar.load_from_dir(assets_dir)

    font = pygame.font.Font(None, 24)
    screen = Screen(surface, font)

    # start audio input
    # initial audio device: read from config.preferred_input_device if set
    current_device_index = config.preferred_input_device
    audio_started = audio.start(current_device_index)
    if audio_started:
        print("audio input started")
        # show toast
        # font/screen haven't been created yet, so we'll show a print; after screen exists, show toasts on restarts
    else:
        print("audio input not available", audio.get_last_error())

    show_debug = False
    scale = 1.0
    is_speaking = False
    manual_speaking = False
    speak_timer = 0.0

    running = True
    # device menu state
    device_menu_open = False
    device_list = []
    device_selected_idx = 0
    # in-game main menu state (opened by quit_key)
    menu_open = False
    main_menu_items = [
        "Resume",
        "Toggle Debug",
        "Toggle Speaking",
        "Audio Retry",
        "Select Audio Device",
        "Exit Game",
    ]
    menu_selected_idx = 0
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case config.quit_key:
                            # open the in-game menu instead of quitting immediately
                            menu_open = True
                            menu_selected_idx = 0
                        case config.debug_key | config.debug_alt_key:
                            show_debug = not show_debug
                        case config.speak_key:
                            manual_speaking = not manual_speaking
                        case pygame.K_r:
                            audio.stop()
                            if audio.start():
                                print("audio input started on retry")
                                screen.show_toast("Audio restarted")
                            else:
                                print("audio retry failed:", audio.get_last_error())
                                screen.show_toast(
                                    f"Audio retry failed: {audio.get_last_error()}"
                                )
                        case pygame.K_d:
                            # open device selection menu
                            device_list = audio.list_input_devices()
                            device_selected_idx = 0
                            device_menu_open = True
                        case pygame.K_UP:
                            if device_menu_open and device_list:
                                device_selected_idx = max(0, device_selected_idx - 1)
                            elif menu_open:
                                menu_selected_idx = max(0, menu_selected_idx - 1)
                        case pygame.K_DOWN:
                            if device_menu_open and device_list:
                                device_selected_idx = min(
                                    len(device_list) - 1, device_selected_idx + 1
                                )
                            elif menu_open:
                                menu_selected_idx = min(
                                    len(main_menu_items) - 1, menu_selected_idx + 1
                                )
                        case pygame.K_RETURN:
                            if device_menu_open and device_list:
                                chosen = device_list[device_selected_idx]
                                chosen_idx = chosen.get("index")
                                # restart audio on chosen device
                                audio.stop()
                                current_device_index = chosen_idx
                                if audio.start(current_device_index):
                                    msg = f"Audio started on device {chosen_idx}: {chosen.get('name')}"
                                    print(msg)
                                    screen.show_toast(msg)
                                    # persist preference
                                    config.preferred_input_device = current_device_index
                                    config.save_user_config()
                                else:
                                    err = audio.get_last_error()
                                    print("failed to start audio on device:", err)
                                    screen.show_toast(f"Failed to start audio: {err}")
                                device_menu_open = False
                            elif menu_open:
                                # handle main menu selection
                                sel = menu_selected_idx
                                choice = main_menu_items[sel]
                                if choice == "Resume":
                                    menu_open = False
                                elif choice == "Toggle Debug":
                                    show_debug = not show_debug
                                    screen.show_toast(
                                        f"Debug {'on' if show_debug else 'off'}"
                                    )
                                elif choice == "Toggle Speaking":
                                    manual_speaking = not manual_speaking
                                    screen.show_toast(
                                        f"Manual speaking {'on' if manual_speaking else 'off'}"
                                    )
                                elif choice == "Audio Retry":
                                    audio.stop()
                                    if audio.start(current_device_index):
                                        screen.show_toast("Audio restarted")
                                    else:
                                        screen.show_toast(
                                            f"Audio retry failed: {audio.get_last_error()}"
                                        )
                                elif choice == "Select Audio Device":
                                    device_list = audio.list_input_devices()
                                    device_selected_idx = 0
                                    device_menu_open = True
                                elif choice == "Exit Game":
                                    running = False
                                    err = audio.get_last_error()
                            # (menu closing handled by ESC key and selection actions)

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

        # render in-game main menu (underneath)
        if menu_open:
            screen.draw_menu("Menu", main_menu_items, menu_selected_idx)

        # if device menu open, render a modal backdrop and then the device menu on top
        if device_menu_open:
            screen.draw_modal_backdrop(alpha=180)
            device_menu_items = [f"{d['index']}: {d['name']}" for d in device_list]
            if not device_menu_items:
                device_menu_items = ["No input devices found"]
            screen.draw_menu(
                "Select audio input device (Enter to choose)",
                device_menu_items,
                device_selected_idx,
            )

        # draw any active toast
        screen._draw_toast()

        screen.flip()

    audio.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
