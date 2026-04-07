from __future__ import annotations

from app.core.models import Severity


def severity_color(severity: Severity) -> tuple[int, int, int]:
    palette = {
        Severity.ok: (0, 200, 0),
        Severity.info: (80, 160, 255),
        Severity.warning: (255, 190, 0),
        Severity.critical: (220, 40, 40),
    }
    return palette[severity]
