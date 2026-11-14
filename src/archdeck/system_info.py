from __future__ import annotations

import shutil
import time
from pathlib import Path


class SystemInfo:
    """Small read-only probes using Linux procfs and statvfs."""

    def __init__(self) -> None:
        self._cpu = self._read_cpu_counters()

    @staticmethod
    def _read_cpu_counters() -> tuple[int, int] | None:
        try:
            fields = Path("/proc/stat").read_text().splitlines()[0].split()[1:]
            values = [int(value) for value in fields]
            idle = values[3] + (values[4] if len(values) > 4 else 0)
            return sum(values), idle
        except (OSError, ValueError, IndexError):
            return None

    def cpu_percent(self) -> int | None:
        time.sleep(0.08)
        current = self._read_cpu_counters()
        previous, self._cpu = self._cpu, current
        if previous is None or current is None:
            return None
        total_delta = current[0] - previous[0]
        idle_delta = current[1] - previous[1]
        if total_delta <= 0:
            return 0
        return max(0, min(100, round(100 * (1 - idle_delta / total_delta))))

    @staticmethod
    def memory() -> tuple[int, int, int] | None:
        try:
            values: dict[str, int] = {}
            for line in Path("/proc/meminfo").read_text().splitlines():
                key, raw = line.split(":", 1)
                values[key] = int(raw.strip().split()[0])
            total = values["MemTotal"]
            available = values["MemAvailable"]
            used = total - available
            return round(used / 1024), round(total / 1024), round(100 * used / total)
        except (OSError, ValueError, KeyError, ZeroDivisionError):
            return None

    @staticmethod
    def disk() -> tuple[float, float, int] | None:
        try:
            usage = shutil.disk_usage("/")
            used = usage.used / (1024**3)
            total = usage.total / (1024**3)
            return used, total, round(100 * usage.used / usage.total)
        except OSError:
            return None
