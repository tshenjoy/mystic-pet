"""Sprite loading and frame management."""

import os
import json
from PyQt6.QtGui import QPixmap, QTransform


ANIMATION_NAMES = ["idle", "walk", "walk_to_idle", "idle_to_walk", "stalk", "chase", "trash_can"]


class SpriteRenderer:
    """Loads sprite frames from assets/template/<anim>/*.png.

    If an animation folder is missing, it reuses the walk frames.
    Sprite size is auto-detected from the first loaded frame.
    Pre-caches horizontally flipped frames to avoid per-frame transforms.
    """

    def __init__(self, assets_dir):
        self.assets_dir = assets_dir
        self.frames = {}         # {"walk": [QPixmap, ...]}
        self.frames_flipped = {} # {"walk": [QPixmap, ...]} — pre-flipped
        self.metadata = {}
        self.sprite_w = 174
        self.sprite_h = 128
        self._load_metadata()
        self._load_sprites()

    def _load_metadata(self):
        meta_path = os.path.join(self.assets_dir, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                self.metadata = json.load(f)

    def _load_sprites(self):
        template_dir = os.path.join(self.assets_dir, "template")

        for anim_name in ANIMATION_NAMES:
            anim_dir = os.path.join(template_dir, anim_name)
            frames = self._load_frames_from_dir(anim_dir)
            if frames:
                self.frames[anim_name] = frames

        # Auto-detect sprite size
        for frames in self.frames.values():
            if frames:
                self.sprite_w = frames[0].width()
                self.sprite_h = frames[0].height()
                break

        # Fill missing animations with walk frames
        walk_frames = self.frames.get("walk", [])
        for anim_name in ANIMATION_NAMES:
            if not self.frames.get(anim_name):
                self.frames[anim_name] = walk_frames

        self._build_flipped_cache()

    def _load_frames_from_dir(self, anim_dir):
        if not os.path.isdir(anim_dir):
            return []
        files = sorted(f for f in os.listdir(anim_dir) if f.endswith(".png"))
        frames = []
        for fname in files:
            px = QPixmap(os.path.join(anim_dir, fname))
            if not px.isNull():
                frames.append(px)
        return frames

    def _build_flipped_cache(self):
        flip = QTransform().scale(-1, 1)
        self.frames_flipped = {}
        for name, frames in self.frames.items():
            self.frames_flipped[name] = [f.transformed(flip) for f in frames]

    def reload_sprites(self, custom_dir=None):
        if custom_dir:
            for anim_name in ANIMATION_NAMES:
                anim_dir = os.path.join(custom_dir, anim_name)
                frames = self._load_frames_from_dir(anim_dir)
                if frames:
                    self.frames[anim_name] = frames

            walk_frames = self.frames.get("walk", [])
            for anim_name in ANIMATION_NAMES:
                if not self.frames.get(anim_name):
                    self.frames[anim_name] = walk_frames
        else:
            self._load_sprites()

        self._build_flipped_cache()

    def get_frame(self, animation_name, frame_index, flipped=False):
        source = self.frames_flipped if flipped else self.frames
        anim_frames = source.get(animation_name, source.get("walk", []))
        if not anim_frames:
            return QPixmap(self.sprite_w, self.sprite_h)
        return anim_frames[frame_index % len(anim_frames)]

    def frame_count(self, animation_name):
        return len(self.frames.get(animation_name, []))
