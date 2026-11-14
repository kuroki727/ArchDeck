from __future__ import annotations

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget


class ProcessPage(QWidget):
    """A small page for an explicitly requested, read-only system command."""

    def __init__(self, title: str, description: str, button_text: str, program: str, arguments: list[str], empty_text: str) -> None:
        super().__init__()
        self.program = program
        self.arguments = arguments
        self.empty_text = empty_text
        self.process = QProcess(self)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._error)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        eyebrow = QLabel("ARCHDECK · ПРОСМОТР")
        eyebrow.setObjectName("eyebrow")
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        description_label = QLabel(description)
        description_label.setObjectName("muted")
        description_label.setWordWrap(True)
        self.action = QPushButton(button_text)
        self.action.setObjectName("primary")
        self.action.clicked.connect(self.run_command)
        self.status = QLabel("Команда не запускалась")
        self.status.setObjectName("small")
        self.listing = QListWidget()
        self.listing.setObjectName("panel")
        self.listing.setMinimumHeight(260)
        layout.addWidget(eyebrow)
        layout.addWidget(heading)
        layout.addWidget(description_label)
        layout.addWidget(self.action, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.status)
        layout.addWidget(self.listing, 1)
        layout.addStretch()

    def run_command(self) -> None:
        if self.process.state() != QProcess.ProcessState.NotRunning:
            return
        self.listing.clear()
        self.status.setText(f"Выполняется: {self.program} {' '.join(self.arguments)}")
        self.action.setEnabled(False)
        self.process.start(self.program, self.arguments)

    def _finished(self, exit_code: int, _exit_status) -> None:
        self.action.setEnabled(True)
        raw = bytes(self.process.readAllStandardOutput()).decode(errors="replace").strip()
        error = bytes(self.process.readAllStandardError()).decode(errors="replace").strip()
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        self.status.setText(f"Активных служб: {len(lines)}" if exit_code == 0 else "Не удалось получить список служб.")
        self.listing.addItems(lines or [error or self.empty_text])

    def _error(self, _error) -> None:
        self.action.setEnabled(True)
        self.status.setText("Команда недоступна в системе.")
        self.listing.addItem(f"Не найдено: {self.program}")
