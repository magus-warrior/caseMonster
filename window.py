"""wxPython GUI entry point for caseMonster."""

from __future__ import annotations

from ui.main_frame import CaseMonsterFrame as MONSTERcase, launch_app

__all__ = ["MONSTERcase", "launch_app"]


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(launch_app())
