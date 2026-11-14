from __future__ import annotations

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget,
)


class CleanupPage(QWidget):
    """Read-only inspection of package cache and orphaned packages."""

    def __init__(self) -> None:
        super().__init__()
        self.processes: dict[str, QProcess] = {}
        self.running: set[str] = set()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(14)

        eyebrow = QLabel("ARCHDECK · АНАЛИЗ PACMAN")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Очистка")
        title.setObjectName("pageTitle")
        description = QLabel(
            "Посмотри, сколько места занимает кэш пакетов и какие пакеты отмечены как сироты. "
            "Этот экран ничего не удаляет."
        )
        description.setObjectName("muted")
        description.setWordWrap(True)
        outer.addWidget(eyebrow)
        outer.addWidget(title)
        outer.addWidget(description)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        self.inspect_button = QPushButton("Проверить систему")
        self.inspect_button.setObjectName("primary")
        self.inspect_button.clicked.connect(self.inspect)
        toolbar.addWidget(self.inspect_button)
        outer.addLayout(toolbar)

        self.cache_panel = self._panel("КЭШ ПАКЕТОВ")
        cache_layout = self.cache_panel.layout()
        self.cache_value = QLabel("Проверка ещё не запускалась")
        self.cache_value.setObjectName("systemValue")
        self.cache_value.setWordWrap(True)
        self.cache_hint = QLabel("Файлы в /var/cache/pacman/pkg; временные каталоги не учитываются")
        self.cache_hint.setObjectName("small")
        cache_layout.addWidget(self.cache_value)
        cache_layout.addWidget(self.cache_hint)
        outer.addWidget(self.cache_panel)

        self.orphans_panel = self._panel("ПАКЕТЫ-СИРОТЫ")
        orphan_layout = self.orphans_panel.layout()
        self.orphans_status = QLabel("Проверка ещё не запускалась")
        self.orphans_status.setObjectName("small")
        self.orphans_list = QListWidget()
        self.orphans_list.setMinimumHeight(180)
        orphan_layout.addWidget(self.orphans_status)
        orphan_layout.addWidget(self.orphans_list)
        outer.addWidget(self.orphans_panel, 1)

        self.note = QLabel("Список сирот формирует pacman. Удаление в ArchDeck пока недоступно.")
        self.note.setObjectName("footer")
        outer.addWidget(self.note)

        cache_process = QProcess(self)
        cache_process.finished.connect(self._cache_finished)
        cache_process.errorOccurred.connect(lambda error: self._process_error("cache", error))
        orphan_process = QProcess(self)
        orphan_process.finished.connect(self._orphans_finished)
        orphan_process.errorOccurred.connect(lambda error: self._process_error("orphans", error))
        self.processes = {"cache": cache_process, "orphans": orphan_process}

    @staticmethod
    def _panel(title: str) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(9)
        heading = QLabel(title)
        heading.setObjectName("cardTitle")
        layout.addWidget(heading)
        return panel

    def inspect(self) -> None:
        if self.running:
            return
        self.running = {"cache", "orphans"}
        self.inspect_button.setEnabled(False)
        self.inspect_button.setText("Проверяю…")
        self.cache_value.setText("Считаю размер кэша…")
        self.orphans_status.setText("Читаю локальную базу pacman…")
        self.orphans_list.clear()
        self.processes["cache"].start(
            "find", ["/var/cache/pacman/pkg", "-maxdepth", "1", "-type", "f", "-printf", "%s\n"]
        )
        self.processes["orphans"].start("pacman", ["-Qdtq"])

    def _cache_finished(self, exit_code: int, _exit_status) -> None:
        process = self.processes["cache"]
        output = bytes(process.readAllStandardOutput()).decode(errors="replace").strip()
        error = bytes(process.readAllStandardError()).decode(errors="replace").strip()
        if exit_code == 0:
            try:
                sizes = [int(line) for line in output.splitlines()]
            except ValueError:
                self.cache_value.setText("Не удалось прочитать размеры файлов кэша")
            else:
                self.cache_value.setText(f"{self._format_size(sum(sizes))} · {len(sizes)} файлов")
        else:
            self.cache_value.setText(error or "Не удалось измерить кэш")
        self._done("cache")

    def _orphans_finished(self, exit_code: int, _exit_status) -> None:
        process = self.processes["orphans"]
        output = bytes(process.readAllStandardOutput()).decode(errors="replace").strip()
        error = bytes(process.readAllStandardError()).decode(errors="replace").strip()
        if exit_code != 0:
            self.orphans_status.setText(error or "Не удалось прочитать базу pacman")
        else:
            packages = [line.strip() for line in output.splitlines() if line.strip()]
            self.orphans_list.addItems(packages)
            self.orphans_status.setText(
                f"Найдено пакетов: {len(packages)}" if packages else "Пакетов-сирот не найдено"
            )
        self._done("orphans")

    def _process_error(self, key: str, _error) -> None:
        if key == "cache":
            self.cache_value.setText("Команда find недоступна или каталог кэша не читается")
        else:
            self.orphans_status.setText("Не удалось запустить pacman")
        self._done(key)

    @staticmethod
    def _format_size(size: int) -> str:
        value = float(size)
        for unit in ("Б", "КиБ", "МиБ", "ГиБ", "ТиБ"):
            if value < 1024 or unit == "ТиБ":
                return f"{value:.1f} {unit}" if unit != "Б" else f"{size} Б"
            value /= 1024
        raise AssertionError("unreachable")

    def _done(self, key: str) -> None:
        self.running.discard(key)
        if not self.running:
            self.inspect_button.setEnabled(True)
            self.inspect_button.setText("Проверить ещё раз")
