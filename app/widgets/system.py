from __future__ import annotations

import os
import socket
import time
from datetime import UTC, datetime
from typing import Any

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

from app.core.models import DataOrigin, Freshness, HealthState, Severity, WidgetData
from app.widgets.base import Widget


class SystemWidget(Widget):
    async def fetch_primary(self) -> WidgetData:
        metrics: dict[str, Any] = {}
        missing_metrics: list[str] = []
        source = "psutil" if psutil is not None else "os"

        metrics["hostname"] = socket.gethostname()
        metrics["timestamp"] = datetime.now(UTC).isoformat()

        try:
            load1, load5, load15 = os.getloadavg()
            metrics["load_avg"] = {"1m": round(load1, 2), "5m": round(load5, 2), "15m": round(load15, 2)}
        except OSError:
            missing_metrics.append("load_avg")

        if psutil is not None:
            self._collect_psutil_metrics(metrics, missing_metrics)
        else:
            self._collect_os_metrics(metrics, missing_metrics)

        cpu = float(metrics.get("cpu_percent", 0.0))
        mem = float(metrics.get("memory_percent", 0.0))
        load = metrics.get("load_avg", {}).get("1m", 0.0) if isinstance(metrics.get("load_avg"), dict) else 0.0

        severity = Severity.ok
        if cpu >= 95 or mem >= 95:
            severity = Severity.critical
        elif cpu >= 85 or mem >= 90:
            severity = Severity.warning

        fidelity = "full" if not missing_metrics else "degraded"
        value = f"CPU {cpu:.0f}% MEM {mem:.0f}% LD {float(load):.1f}"
        status_summary = "system metrics collected"
        health_state = HealthState.healthy
        if missing_metrics:
            status_summary = "system metrics partially unavailable"
            health_state = HealthState.degraded

        return self.normalized(
            "System",
            value,
            severity=severity,
            source_label=source,
            health_state=health_state,
            status_summary=status_summary,
            extra={
                "metrics": metrics,
                "missing_metrics": missing_metrics,
                "fidelity": fidelity,
                "display": value,
            },
            debug={
                "psutil_available": psutil is not None,
                "missing_metric_count": len(missing_metrics),
            },
        )

    def _collect_psutil_metrics(self, metrics: dict[str, Any], missing_metrics: list[str]) -> None:
        try:
            metrics["cpu_percent"] = float(psutil.cpu_percent(interval=None))
        except Exception:  # noqa: BLE001
            missing_metrics.append("cpu_percent")

        try:
            metrics["memory_percent"] = float(psutil.virtual_memory().percent)
        except Exception:  # noqa: BLE001
            missing_metrics.append("memory_percent")

        disk_path = str(self.config.get("disk_path", "/"))
        try:
            metrics["disk"] = {
                "path": disk_path,
                "used_percent": float(psutil.disk_usage(disk_path).percent),
            }
        except Exception:  # noqa: BLE001
            missing_metrics.append("disk")

        try:
            boot_ts = float(psutil.boot_time())
            metrics["uptime_seconds"] = max(0, int(time.time() - boot_ts))
        except Exception:  # noqa: BLE001
            missing_metrics.append("uptime")

        try:
            temps = psutil.sensors_temperatures()
            metrics["cpu_temp_c"] = self._extract_cpu_temp(temps)
            if metrics["cpu_temp_c"] is None:
                missing_metrics.append("cpu_temp")
        except Exception:  # noqa: BLE001
            missing_metrics.append("cpu_temp")

    def _collect_os_metrics(self, metrics: dict[str, Any], missing_metrics: list[str]) -> None:
        missing_metrics.extend(["cpu_percent", "memory_percent", "disk", "cpu_temp"])
        try:
            metrics["uptime_seconds"] = max(0, int(self._read_proc_uptime_seconds()))
        except Exception:  # noqa: BLE001
            missing_metrics.append("uptime")
        metrics.setdefault("cpu_percent", 0.0)
        metrics.setdefault("memory_percent", 0.0)

    def _read_proc_uptime_seconds(self) -> float:
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            return float(f.read().split()[0])

    def _extract_cpu_temp(self, temps: dict[str, Any] | None) -> float | None:
        if not temps:
            return None
        for key in ("cpu_thermal", "coretemp", "soc_thermal"):
            values = temps.get(key)
            if values:
                current = getattr(values[0], "current", None)
                if current is not None:
                    return float(current)
        for values in temps.values():
            if values:
                current = getattr(values[0], "current", None)
                if current is not None:
                    return float(current)
        return None

    def build_fallback(self, error: Exception | None, last_known: WidgetData | None) -> WidgetData:
        if last_known is not None:
            fallback = last_known.model_copy(deep=True)
            fallback.freshness = Freshness.stale
            fallback.data_origin = DataOrigin.cache
            fallback.health_state = HealthState.degraded
            fallback.status_summary = "system fallback using last known"
            fallback.debug.update({"error": str(error) if error else "system primary unavailable"})
            return fallback

        message = str(error) if error else "system metrics unavailable"
        return self.normalized(
            "System",
            "SYS ERR",
            severity=Severity.critical,
            freshness=Freshness.fallback,
            data_origin=DataOrigin.synthetic,
            health_state=HealthState.failed,
            source_label="system:fallback",
            status_summary="system fallback synthetic",
            debug={"error": message},
            extra={"metrics": {}, "missing_metrics": ["all"], "fidelity": "none"},
        )
