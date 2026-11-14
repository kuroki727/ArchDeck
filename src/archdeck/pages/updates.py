from __future__ import annotations

import re
import shutil
from datetime import datetime

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)


UPDATE_LINE = re.compile(r"^(\S+)\s+(\S+)\s+->\s+(\S+)$")


def parse_updates(output: str) -> list[tuple[str, str, str]]:
    updates = []
    for line in output.splitlines():
        match = UPDATE_LINE.fullmatch(line.strip())
        if match:
            updates.append(match.groups())
    return updates


def package_word(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return "пакет"
    if count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        return "пакета"
    return "пакетов"


class UpdatesPage(QWidget):
    """Inspect repository and AUR updates without modifying packages."""

    def __init__(self) -> None:
        super().__init__()
        self.updates: list[tuple[str, str, str, str]] = []
        self.pending: set[str] = set()
        self.processes: dict[str, QProcess] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(14)

        heading = QHBoxLayout()
        intro = QVBoxLayout()
        eyebrow = QLabel("ARCHDECK · ПАКЕТЫ")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Центр обновлений")
        title.setObjectName("pageTitle")
        description = QLabel("Проверка официальных репозиториев и AUR. Пакеты устанавливаются только вне ArchDeck.")
        description.setObjectName("muted")
        description.setWordWrap(True)
        intro.addWidget(eyebrow)
        intro.addWidget(title)
        intro.addWidget(description)
        heading.addLayout(intro, 1)
        self.check_button = QPushButton("Проверить обновления")
        self.check_button.setObjectName("primary")
        self.check_button.clicked.connect(self.check_updates)
        heading.addWidget(self.check_button, alignment=Qt.AlignmentFlag.AlignBottom)
        outer.addLayout(heading)

        summary = QHBoxLayout()
        repo_card, self.repo_count = self._summary_card("РЕПОЗИТОРИИ")
        aur_card, self.aur_count = self._summary_card("AUR")
        summary.addWidget(repo_card)
        summary.addWidget(aur_card)
        outer.addLayout(summary)

        self.repo_status = QLabel("Официальные пакеты ещё не проверялись")
        self.repo_status.setObjectName("small")
        self.aur_status = QLabel("AUR ещё не проверялся" if shutil.which("yay") else "yay не установлен; проверка AUR недоступна")
        self.aur_status.setObjectName("small")
        outer.addWidget(self.repo_status)
        outer.addWidget(self.aur_status)

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(14, 14, 14, 14)
        panel_layout.setSpacing(10)
        filter_row = QHBoxLayout()
        label = QLabel("ДОСТУПНЫЕ ОБНОВЛЕНИЯ")
        label.setObjectName("cardTitle")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск по пакетам…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._render)
        filter_row.addWidget(label)
        filter_row.addStretch()
        filter_row.addWidget(self.search)
        panel_layout.addLayout(filter_row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Источник", "Пакет", "Установлено", "Доступно"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        panel_layout.addWidget(self.table, 1)
        outer.addWidget(panel, 1)

        self.footer = QLabel("Проверка ещё не запускалась")
        self.footer.setObjectName("footer")
        outer.addWidget(self.footer)

        for key in ("repo", "aur"):
            process = QProcess(self)
            process.finished.connect(lambda code, status, source=key: self._finished(source, code))
            process.errorOccurred.connect(lambda error, source=key: self._error(source))
            self.processes[key] = process

    @staticmethod
    def _summary_card(title: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        heading = QLabel(title)
        heading.setObjectName("cardTitle")
        value = QLabel("—")
        value.setObjectName("metric")
        layout.addWidget(heading)
        layout.addWidget(value)
        return card, value

    def check_updates(self) -> None:
        if self.pending:
            return
        self.updates.clear()
        self._render()
        self.repo_count.setText("…")
        self.aur_count.setText("…" if shutil.which("yay") else "—")
        self.repo_status.setText("Проверяю официальные пакеты…")
        self.aur_status.setText("Проверяю AUR…" if shutil.which("yay") else "yay не установлен; проверка AUR недоступна")
        self.check_button.setEnabled(False)
        self.check_button.setText("Проверка…")

        if shutil.which("checkupdates"):
            self.repo_command = "checkupdates"
            self.repo_hint = "Синхронизированные данные checkupdates"
            self.processes["repo"].start("checkupdates", [])
        else:
            self.repo_command = "pacman -Qu"
            self.repo_hint = "Локальная база pacman; список может быть устаревшим"
            self.processes["repo"].start("pacman", ["-Qu"])
        self.pending.add("repo")

        if shutil.which("yay"):
            self.pending.add("aur")
            self.processes["aur"].start("yay", ["-Qua"])

    def _finished(self, source: str, exit_code: int) -> None:
        if source not in self.pending:
            return
        process = self.processes[source]
        output = bytes(process.readAllStandardOutput()).decode(errors="replace").strip()
        error = bytes(process.readAllStandardError()).decode(errors="replace").strip()
        parsed = parse_updates(output)
        valid_empty = not output and not error and exit_code in (0, 1)
        if exit_code == 0 or valid_empty:
            self.updates.extend((source, *item) for item in parsed)
            count = len(parsed)
            if source == "repo":
                self.repo_count.setText(str(count))
                self.repo_status.setText(f"Официальные пакеты: {count}. {self.repo_hint}")
            else:
                self.aur_count.setText(str(count))
                self.aur_status.setText(f"AUR: {count} {package_word(count)}")
            if output and len(parsed) != len(output.splitlines()):
                target = self.repo_status if source == "repo" else self.aur_status
                target.setText(target.text() + "; часть строк не распознана")
        else:
            message = error.splitlines()[-1] if error else f"Команда завершилась с кодом {exit_code}"
            self._set_error(source, message)
        self._render()
        self._done(source)

    def _error(self, source: str) -> None:
        if source in self.pending:
            self._set_error(source, "Не удалось запустить команду")
            self._done(source)

    def _set_error(self, source: str, message: str) -> None:
        if source == "repo":
            self.repo_count.setText("!")
            self.repo_status.setText(f"Ошибка проверки репозиториев: {message}")
        else:
            self.aur_count.setText("!")
            self.aur_status.setText(f"Ошибка проверки AUR: {message}")

    def _done(self, source: str) -> None:
        self.pending.discard(source)
        if not self.pending:
            self.check_button.setEnabled(True)
            self.check_button.setText("Проверить ещё раз")
            self.footer.setText(f"Последняя проверка: {datetime.now().astimezone():%d.%m.%Y %H:%M}")

    def _render(self) -> None:
        query = self.search.text().casefold().strip()
        visible = [item for item in self.updates if query in item[1].casefold()]
        self.table.setRowCount(len(visible))
        for row, (source, name, installed, available) in enumerate(visible):
            for column, value in enumerate(("AUR" if source == "aur" else "Репозиторий", name, installed, available)):
                cell = QTableWidgetItem(value)
                if column == 0:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, cell)
