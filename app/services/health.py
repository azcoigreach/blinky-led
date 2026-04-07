from __future__ import annotations

from app.core.models import Severity, WidgetData


def doom_index(widget_data: dict[str, WidgetData]) -> int:
    score = 0
    for item in widget_data.values():
        if item.severity == Severity.warning:
            score += 1
        elif item.severity == Severity.critical:
            score += 2
    return score
