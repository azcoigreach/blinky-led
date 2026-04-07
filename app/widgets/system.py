from __future__ import annotations

import os

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

from app.core.models import Severity
from app.widgets.base import Widget


class SystemWidget(Widget):
    async def fetch(self):
        if psutil is None:
            load = os.getloadavg()[0]
            return self.normalized("System", f"Load {load:.2f}", severity=Severity.info, source_label="os")
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        severity = Severity.warning if cpu > 85 or mem > 90 else Severity.ok
        return self.normalized("System", f"CPU {cpu:.0f}% MEM {mem:.0f}%", severity=severity, source_label="psutil")
