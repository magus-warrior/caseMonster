"""Asset loading utilities for the Kivy-based UI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture
from kivy.resources import resource_add_path

_ASSET_ROOT = Path(__file__).resolve().parent.parent


def get_asset_path(name: str) -> Path:
    """Return the absolute path to a bundled asset and register it with Kivy."""

    path = _ASSET_ROOT / name
    resource_add_path(str(path.parent))
    return path


def load_texture(name: str) -> Optional[Texture]:
    """Return a Kivy texture for the requested image, if it exists."""

    path = get_asset_path(name)
    if not path.exists():
        return None
    image = CoreImage(str(path))
    return image.texture


def icon_path(name: str) -> Optional[str]:
    """Return the filesystem path to an icon if present."""

    path = get_asset_path(name)
    return str(path) if path.exists() else None


__all__ = ["get_asset_path", "load_texture", "icon_path"]
