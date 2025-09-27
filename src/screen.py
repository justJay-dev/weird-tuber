import pygame
from typing import Tuple


class Screen:
    def __init__(self, surface: pygame.Surface, font: pygame.font.Font):
        self.surface = surface
        self.font = font

    def fill(self, color: Tuple[int, int, int]):
        self.surface.fill(color)

    def get_size(self):
        return self.surface.get_size()

    def blit(self, surf: pygame.Surface, rect: pygame.Rect | Tuple[int, int]):
        self.surface.blit(surf, rect)

    def draw_text(self, text: str, x: int, y: int, color=(255, 255, 255)):
        surf = self.font.render(text, True, color)
        self.surface.blit(surf, (x, y))

    def draw_text_center(self, text: str, x: float, y: float, color=(255, 255, 255)):
        surf = self.font.render(text, True, color)
        r = surf.get_rect(center=(int(x), int(y)))
        self.surface.blit(surf, r)

    def flip(self):
        pygame.display.flip()

    def draw_debug(
        self,
        clock,
        audio,
        show_debug: bool,
        top_img,
        bottom_img,
        avatar,
        scale: float,
        speak_timer: float,
        is_speaking: bool,
        config,
        audio_detected: bool = False,
        manual_speaking: bool = False,
        anim_strength: float | None = None,
    ):
        if not show_debug:
            return

        w, h = self.get_size()
        fps = int(clock.get_fps())
        self.draw_text(f"FPS: {fps}", 8, 8, (255, 255, 255))
        self.draw_text(f"Audio level: {audio.get_level():.4f}", 8, 28, (255, 255, 255))
        audio_err = audio.get_last_error()
        if audio_err:
            self.draw_text(f"Audio error: {audio_err}", 8, 68, (255, 153, 153))
            self.draw_text(
                "Press R to retry audio start (may prompt OS)", 8, 88, (255, 255, 255)
            )

        if top_img and bottom_img:
            top_w, top_h = top_img.get_size()
            bot_w, bot_h = bottom_img.get_size()
            self.draw_text(
                f"top: {top_w}x{top_h}, bottom: {bot_w}x{bot_h}, scale: {scale:.2f}",
                8,
                48,
            )
        elif avatar:
            img_w, img_h = avatar.get_size()
            self.draw_text(f"avatar: {img_w}x{img_h}, scale: {scale:.2f}", 8, 28)

        self.draw_text(f"Toggle debug: ` | Speak toggle: Space | Quit: Esc", 8, h - 48)
        self.draw_text(f"Speaking: {is_speaking}", 8, h - 28)

        # small indicator in top-right: green=audio, blue=manual, gray=silent
        ind_radius = 8
        ind_x = w - 16
        ind_y = 16
        if audio_detected:
            color = (0, 220, 0)
        elif manual_speaking:
            color = (0, 120, 255)
        else:
            color = (120, 120, 120)
        pygame.draw.circle(self.surface, color, (ind_x, ind_y), ind_radius)
        # anim strength bar (debug)
        # prefer an explicit anim_strength if provided, otherwise fall back to
        # the debug probe on config (kept for backward compatibility)
        if anim_strength is None:
            try:
                anim_strength = getattr(config, "_debug_anim_strength", None)
            except Exception:
                anim_strength = None
        if anim_strength is not None:
            bar_w = 60
            bar_h = 6
            bar_x = w - 16 - bar_w
            bar_y = ind_y - bar_h // 2
            # background
            pygame.draw.rect(self.surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
            fill_w = int(bar_w * max(0.0, min(1.0, anim_strength)))
            pygame.draw.rect(self.surface, (255, 200, 0), (bar_x, bar_y, fill_w, bar_h))
