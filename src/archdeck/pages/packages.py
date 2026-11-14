from __future__ import annotations

from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPlainTextEdit,
    QPushButton, QSplitter, QVBoxLayout, QWidget,
)


class PackagesPage(QWidget):
    """Read-only installed package browser backed by pacman."""

    def __init__(self) -> None:
        super().__init__()
        self.packages: list[tuple[str, str]] = []
        self.selected_package: str | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(14)

        eyebrow = QLabel("ARCHDECK · ЛОКАЛЬНАЯ БАЗА PACMAN")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Пакеты")
        title.setObjectName("pageTitle")
        description = QLabel("Поиск по установленным пакетам и просмотр сведений. Изменения системы здесь пока недоступны.")
        description.setObjectName("muted")
        description.setWordWrap(True)
        outer.addWidget(eyebrow)
        outer.addWidget(title)
        outer.addWidget(description)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Фильтр установленных пакетов…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter_packages)
        self.refresh_button = QPushButton("Загрузить список")
        self.refresh_button.setObjectName("primary")
        self.refresh_button.clicked.connect(self.load_packages)
        toolbar.addWidget(self.search, 1)
        toolbar.addWidget(self.refresh_button)
        outer.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        left = QFrame()
        left.setObjectName("panel")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 12, 12)
        self.count = QLabel("Список ещё не загружен")
        self.count.setObjectName("small")
        self.listing = QListWidget()
        self.listing.itemSelectionChanged.connect(self._selection_changed)
        left_layout.addWidget(self.count)
        left_layout.addWidget(self.listing, 1)

        right = QFrame()
        right.setObjectName("panel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(16, 14, 16, 14)
        self.detail_title = QLabel("Сведения о пакете")
        self.detail_title.setObjectName("cardTitle")
        self.detail_status = QLabel("Выбери пакет в списке слева.")
        self.detail_status.setObjectName("small")
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Описание, версия, зависимости и размер появятся здесь.")
        self.details.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.details.setFont(QFont("monospace", 10))
        right_layout.addWidget(self.detail_title)
        right_layout.addWidget(self.detail_status)
        right_layout.addWidget(self.details, 1)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([320, 520])
        outer.addWidget(splitter, 1)

        self.list_process = QProcess(self)
        self.list_process.finished.connect(self._packages_loaded)
        self.list_process.errorOccurred.connect(self._list_error)

    def load_packages(self) -> None:
        if self.list_process.state() != QProcess.ProcessState.NotRunning:
            return
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Загружаю…")
        self.count.setText("Читаю локальную базу pacman…")
        self.listing.clear()
        self.packages.clear()
        self.details.clear()
        self.list_process.start("pacman", ["-Q"])

    def _packages_loaded(self, exit_code: int, _exit_status) -> None:
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Обновить список")
        output = bytes(self.list_process.readAllStandardOutput()).decode(errors="replace")
        error = bytes(self.list_process.readAllStandardError()).decode(errors="replace").strip()
        if exit_code != 0:
            self.count.setText("Не удалось прочитать базу pacman")
            self.details.setPlainText(error or "Команда pacman -Q завершилась с ошибкой.")
            return
        for line in output.splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                self.packages.append((parts[0], parts[1]))
        self._filter_packages(self.search.text())

    def _list_error(self, _error) -> None:
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Повторить")
        self.count.setText("Команда pacman недоступна")
        self.details.setPlainText("Проверь, что pacman установлен и доступен в PATH.")

    def _filter_packages(self, query: str) -> None:
        needle = query.casefold().strip()
        self.listing.clear()
        visible = [(name, version) for name, version in self.packages
                   if needle in name.casefold() or needle in version.casefold()]
        for name, version in visible:
            self.listing.addItem(f"{name}   ·   {version}")
        if self.packages:
            self.count.setText(f"{len(visible)} из {len(self.packages)} пакетов")
        elif not self.list_process.state() == QProcess.ProcessState.NotRunning:
            self.count.setText("Читаю локальную базу pacman…")
        else:
            self.count.setText("Нажми «Загрузить список», чтобы начать.")

    def _selection_changed(self) -> None:
        items = self.listing.selectedItems()
        if not items:
            return
        name = items[0].text().split("   ·   ", maxsplit=1)[0]
        self.selected_package = name
        self.detail_title.setText(name)
        self.detail_status.setText("Запрашиваю сведения…")
        self.details.clear()

        process = QProcess(self)
        process.finished.connect(
            lambda code, status, proc=process, package=name: self._package_info_loaded(proc, package, code)
        )
        process.errorOccurred.connect(
            lambda _error, proc=process, package=name: self._package_info_error(proc, package)
        )
        process.start("pacman", ["-Qi", name])

    def _package_info_loaded(self, process: QProcess, name: str, exit_code: int) -> None:
        output = bytes(process.readAllStandardOutput()).decode(errors="replace").strip()
        error = bytes(process.readAllStandardError()).decode(errors="replace").strip()
        if self.selected_package == name:
            self.details.setPlainText(output or error or "Сведения не найдены.")
            self.detail_status.setText("Информация из локальной базы pacman" if exit_code == 0 else "Не удалось получить сведения")
        process.deleteLater()

    def _package_info_error(self, process: QProcess, name: str) -> None:
        if self.selected_package == name:
            self.detail_status.setText("Не удалось запустить pacman.")
        process.deleteLater()
