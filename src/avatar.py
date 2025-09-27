import os
import math
import pygame
from typing import Optional, Tuple


class Avatar:
    def __init__(
        self,
        top_img: Optional[pygame.Surface],
        bottom_img: Optional[pygame.Surface],
        avatar_img: Optional[pygame.Surface],
    ):
        self.top_img = top_img
        self.bottom_img = bottom_img
        self.avatar_img = avatar_img
        self.anim_strength = 0.0

    @classmethod
    def load_from_dir(cls, assets_dir: str):
        def load(path: str) -> Optional[pygame.Surface]:
            try:
                return pygame.image.load(path).convert_alpha()
            except Exception:
                return None

        top = load(os.path.join(assets_dir, "top.png"))
        bottom = load(os.path.join(assets_dir, "bottom.png"))
        avatar = None
        if not (top and bottom):
            avatar = load(os.path.join(assets_dir, "avatar.png"))
        return cls(top, bottom, avatar)

    def has_parts(self) -> bool:
        return bool(self.top_img and self.bottom_img)

    def draw(
        self,
        surface: pygame.Surface,
        config,
        speak_timer: float,
        is_speaking: bool,
        w: int,
        h: int,
        dt: float,
    ) -> Tuple[float, float]:
        """Draw the avatar or parts to the given surface. Returns the scale used and the current anim_strength."""
        if self.has_parts():
            top_w, top_h = self.top_img.get_size()
            bot_w, bot_h = self.bottom_img.get_size()

            total_h = top_h + config.gap + bot_h
            available_h = h - config.margin * 2
            scale = min(1.0, available_h / total_h)

            scaled_top_w = top_w * scale
            scaled_top_h = top_h * scale
            scaled_bot_w = bot_w * scale
            scaled_bot_h = bot_h * scale

            total_scaled_h = scaled_top_h + config.gap * scale + scaled_bot_h

            center_x = w / 2
            start_y = (h - total_scaled_h) / 2

            # ease animation strength toward target to avoid abrupt start/stop
            target = 1.0 if is_speaking else 0.0
            # use config values for tau when available
            start_tau = getattr(config, "anim_start_tau", 0.08)
            stop_tau = getattr(config, "anim_stop_tau", 0.9)
            tau = start_tau if target > self.anim_strength else stop_tau
            if dt > 0:
                alpha = 1.0 - math.exp(-dt / tau)
                self.anim_strength += (target - self.anim_strength) * alpha

            phase = math.sin(speak_timer * math.pi * 2 * config.speak_frequency)
            bob = 0.0
            rot = 0.0
            if self.anim_strength > 0:
                if is_speaking:
                    raw_bob = phase * (config.speak_amplitude * scale)
                    bob = raw_bob * self.anim_strength
                    # trigger rotation only on stronger phases to make it rarer
                    rotation_threshold = getattr(
                        config, "speak_rotation_threshold", 0.7
                    )
                    if phase > rotation_threshold:
                        rotation_freq = getattr(
                            config,
                            "speak_rotation_frequency",
                            config.speak_frequency * 1.5,
                        )
                        raw_rot = (
                            math.sin(speak_timer * math.pi * 2 * rotation_freq)
                            * config.speak_rotation_amplitude
                            * scale
                        )
                        # scale rotation amplitude down so when it does occur it's subtle
                        rot_scale = getattr(config, "speak_rotation_scale", 0.6)
                        rot = raw_rot * self.anim_strength * rot_scale

            # determine positioning and prevent overlap
            top_center_y = start_y + scaled_top_h / 2
            desired_top_center_y = top_center_y + bob
            bottom_top_y = start_y + scaled_top_h + config.gap * scale

            hw = scaled_top_w / 2
            hh = scaled_top_h / 2
            ext = abs(hh * math.cos(rot)) + abs(hw * math.sin(rot))
            lowest_allowed = bottom_top_y - ext
            if desired_top_center_y > lowest_allowed:
                desired_top_center_y = lowest_allowed

            # draw top with rotation
            top_surf = pygame.transform.rotozoom(
                self.top_img, -math.degrees(rot), scale
            )
            top_rect = top_surf.get_rect(center=(center_x, desired_top_center_y))
            surface.blit(top_surf, top_rect)

            bottom_surf = pygame.transform.rotozoom(self.bottom_img, 0, scale)
            bottom_rect = bottom_surf.get_rect()
            bottom_rect.x = int(center_x - scaled_bot_w / 2)
            bottom_rect.y = int(start_y + scaled_top_h + config.gap * scale)
            surface.blit(bottom_surf, bottom_rect)

            return scale, self.anim_strength

        elif self.avatar_img:
            img_w, img_h = self.avatar_img.get_size()
            scale = min(1.0, (h - 80) / img_h, (w - 80) / img_w)
            avatar_surf = pygame.transform.rotozoom(self.avatar_img, 0, scale)
            rect = avatar_surf.get_rect(center=(w / 2, h / 2))
            surface.blit(avatar_surf, rect)
            return scale, self.anim_strength

        return 1.0, self.anim_strength
