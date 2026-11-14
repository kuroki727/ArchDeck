from __future__ import annotations

import os
import platform
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from archdeck.system_info import SystemInfo


class SystemPage(QWidget):
    """Read-only summary of host and operating system details."""

    def __init__(self) -> None:
        super().__init__()
        self.info = SystemInfo()
        self.values: dict[str, QLabel] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(14)

        eyebrow = QLabel("ARCHDECK · ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Система")
        title.setObjectName("pageTitle")
        description = QLabel("Сведения об устройстве и ресурсах. Данные читаются локально, без запуска системных команд.")
        description.setObjectName("muted")
        description.setWordWrap(True)
        outer.addWidget(eyebrow)
        outer.addWidget(title)
        outer.addWidget(description)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        self.refresh_button = QPushButton("Обновить сведения")
        self.refresh_button.setObjectName("secondary")
        self.refresh_button.clicked.connect(self.refresh)
        toolbar.addWidget(self.refresh_button)
        outer.addLayout(toolbar)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        entries = [
            ("УСТРОЙСТВО", "hostname"), ("ДИСТРИБУТИВ", "distro"),
            ("ЯДРО", "kernel"), ("ПРОЦЕССОР", "cpu"),
            ("ПАМЯТЬ", "memory"), ("КОРНЕВОЙ РАЗДЕЛ", "disk"),
            ("ВРЕМЯ РАБОТЫ", "uptime"), ("АРХИТЕКТУРА", "architecture"),
        ]
        for index, (heading, key) in enumerate(entries):
            card = QFrame()
            card.setObjectName("card")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(17, 15, 17, 15)
            layout.setSpacing(8)
            label = QLabel(heading)
            label.setObjectName("cardTitle")
            value = QLabel("—")
            value.setObjectName("systemValue")
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(label)
            layout.addWidget(value)
            self.values[key] = value
            grid.addWidget(card, index // 2, index % 2)
        outer.addLayout(grid)
        self.updated = QLabel("")
        self.updated.setObjectName("small")
        outer.addWidget(self.updated)
        outer.addStretch()
        self.refresh()

    def refresh(self) -> None:
        self.values["hostname"].setText(platform.node() or "Неизвестно")
        self.values["distro"].setText(self._distribution())
        self.values["kernel"].setText(platform.release() or "Неизвестно")
        self.values["cpu"].setText(self._processor())
        self.values["memory"].setText(self._memory())
        self.values["disk"].setText(self._disk())
        self.values["uptime"].setText(self._uptime())
        self.values["architecture"].setText(platform.machine() or "Неизвестно")
        self.updated.setText(f"Обновлено: {datetime.now().astimezone().strftime('%H:%M:%S')}")

    @staticmethod
    def _distribution() -> str:
        try:
            data: dict[str, str] = {}
            with open("/etc/os-release", encoding="utf-8") as os_release:
                for line in os_release:
                    key, separator, value = line.rstrip().partition("=")
                    if separator:
                        data[key] = value.strip('"')
            return data.get("PRETTY_NAME") or data.get("NAME") or "Неизвестно"
        except OSError:
            return "Не удалось определить"

    @staticmethod
    def _processor() -> str:
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as cpuinfo:
                for line in cpuinfo:
                    if line.lower().startswith(("model name", "hardware")):
                        model = line.partition(":")[2].strip()
                        cores = os.cpu_count()
                        return f"{model} · {cores} потоков" if cores else model
        except OSError:
            pass
        return f"{os.cpu_count()} потоков" if os.cpu_count() else "Не удалось определить"

    def _memory(self) -> str:
        result = self.info.memory()
        if not result:
            return "Не удалось прочитать"
        used, total, percent = result
        return f"{used:,} / {total:,} MiB · {percent}% занято".replace(",", " ")

    def _disk(self) -> str:
        result = self.info.disk()
        if not result:
            return "Не удалось прочитать"
        used, total, percent = result
        return f"{used:.1f} / {total:.1f} GiB · {percent}% занято"

    @staticmethod
    def _uptime() -> str:
        try:
            with open("/proc/uptime", encoding="ascii") as uptime:
                seconds = int(float(uptime.read().split()[0]))
        except (OSError, ValueError, IndexError):
            return "Не удалось определить"
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes = seconds // 60
        parts = []
        if days:
            parts.append(f"{days} д")
        if hours or days:
            parts.append(f"{hours} ч")
        parts.append(f"{minutes} мин")
        return " ".join(parts)
