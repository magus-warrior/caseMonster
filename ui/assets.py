"""Asset loading utilities for packaged resources."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import wx

_ASSET_ROOT = Path(__file__).resolve().parent.parent


def get_asset_path(name: str) -> Path:
    return _ASSET_ROOT / name


def load_bitmap(name: str) -> Optional[wx.Bitmap]:
    path = get_asset_path(name)
    if not path.exists():
        return None
    image = wx.Image(str(path))
    if not image.IsOk():
        return None
    image.SetMaskColour(255, 255, 255)
    return image.ConvertToBitmap()


def load_icon(name: str) -> wx.Icon:
    path = get_asset_path(name)
    icon = wx.Icon()
    if path.exists():
        icon.LoadFile(str(path), wx.BITMAP_TYPE_ANY)
    return icon


__all__ = ["get_asset_path", "load_bitmap", "load_icon"]
